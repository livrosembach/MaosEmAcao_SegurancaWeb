from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.db import connection
from django.urls import reverse
from core.models import UserProfile, VolunteerProfile, NGOProfile, Vacancy, Application

class SecurityTests(TestCase):
    def setUp(self):
        # Create users
        self.volunteer_user = User.objects.create_user(username='voluntario1', password='password123', email='v1@test.com')
        self.ngo_user = User.objects.create_user(username='ong1', password='password123', email='ong1@test.com')
        self.ngo_user2 = User.objects.create_user(username='ong2', password='password123', email='ong2@test.com')

        # Create profiles
        self.volunteer_profile = UserProfile.objects.create(user=self.volunteer_user, role='VOLUNTEER')
        self.volunteer = VolunteerProfile.objects.create(
            profile=self.volunteer_profile,
            cpf='12345678901',
            phone='11999999999',
            bio='Voluntário entusiasmado.'
        )

        self.ngo_profile = UserProfile.objects.create(user=self.ngo_user, role='NGO')
        self.ngo = NGOProfile.objects.create(
            profile=self.ngo_profile,
            cnpj='12345678000199',
            phone='11888888888',
            address='Rua da ONG, 123',
            description='ONG que ajuda pessoas.'
        )

        self.ngo_profile2 = UserProfile.objects.create(user=self.ngo_user2, role='NGO')
        self.ngo2 = NGOProfile.objects.create(
            profile=self.ngo_profile2,
            cnpj='98765432000100',
            phone='11777777777',
            address='Outra ONG, 456',
            description='Outra ONG de apoio.'
        )

        # Create a vacancy for NGO 1
        self.vacancy = Vacancy.objects.create(
            ngo=self.ngo,
            title='Vaga de teste',
            description='Venha nos ajudar!',
            requirements='Disponibilidade'
        )

        # HTTP Clients
        self.volunteer_client = Client()
        self.volunteer_client.login(username='voluntario1', password='password123')

        self.ngo_client = Client()
        self.ngo_client.login(username='ong1', password='password123')

        self.ngo2_client = Client()
        self.ngo2_client.login(username='ong2', password='password123')

    # ==========================================
    # 🔒 MECANISMO 5: CRIPTOGRAFIA DE DADOS SENSÍVEIS
    # ==========================================
    def test_database_encryption(self):
        """
        Tests that sensitive fields (CPF, CNPJ, phone numbers) are encrypted 
        when stored in the database, but decrypted automatically when read via ORM.
        """
        # 1. Fetching via ORM should be decrypted
        v = VolunteerProfile.objects.get(id=self.volunteer.id)
        self.assertEqual(v.cpf, '12345678901')
        self.assertEqual(v.phone, '11999999999')

        n = NGOProfile.objects.get(id=self.ngo.id)
        self.assertEqual(n.cnpj, '12345678000199')
        self.assertEqual(n.phone, '11888888888')

        # 2. Querying the database directly via raw SQL should reveal ENCRYPTED ciphertext
        with connection.cursor() as cursor:
            cursor.execute("SELECT cpf, phone FROM core_volunteerprofile WHERE id = %s", [self.volunteer.id])
            row = cursor.fetchone()
            db_cpf = row[0]
            db_phone = row[1]

            # The ciphertext in db should NOT be the plaintext
            self.assertNotEqual(db_cpf, '12345678901')
            self.assertNotEqual(db_phone, '11999999999')
            # Fernet tokens typically start with 'gAAAA'
            self.assertTrue(db_cpf.startswith('gAAAA'))
            self.assertTrue(db_phone.startswith('gAAAA'))

    # ==========================================
    # 🛡️ MECANISMO 1: CONTROLE DE ACESSO POR PERFIL (RBAC)
    # ==========================================
    def test_rbac_create_vacancy(self):
        """
        Tests that ONLY NGOs can create vacancies.
        """
        url = reverse('api_vacancies')
        payload = {'title': 'Nova vaga', 'description': 'Descrição da nova vaga'}

        # 1. Volunteer attempts to create vacancy -> 403 Forbidden
        response = self.volunteer_client.post(url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # 2. NGO attempts to create vacancy -> 201 Created
        response = self.ngo_client.post(url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_rbac_apply_vacancy(self):
        """
        Tests that ONLY Volunteers can apply to vacancies.
        """
        url = reverse('api_vacancy_apply', args=[self.vacancy.id])

        # 1. NGO attempts to apply -> 403 Forbidden
        response = self.ngo_client.post(url, content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # 2. Volunteer attempts to apply -> 201 Created
        response = self.volunteer_client.post(url, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_rbac_update_vacancy_ownership(self):
        """
        Tests that only the owner NGO can update its vacancies.
        """
        url = reverse('api_vacancy_detail', args=[self.vacancy.id])
        payload = {'title': 'Título modificado'}

        # 1. Another NGO attempts to update -> 403 Forbidden
        response = self.ngo2_client.put(url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # 2. Owner NGO attempts to update -> 200 OK
        response = self.ngo_client.put(url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # ==========================================
    # 🛡️ MECANISMO 4: VALIDAÇÃO DE REGRAS DE NEGÓCIO
    # ==========================================
    def test_duplicate_applications_prevented(self):
        """
        Tests that duplicate applications are blocked (Design Inseguro mitigation).
        """
        url = reverse('api_vacancy_apply', args=[self.vacancy.id])

        # 1. First application -> 201 Created
        response = self.volunteer_client.post(url, content_type='application/json')
        self.assertEqual(response.status_code, 201)

        # 2. Duplicate application -> 400 Bad Request
        response = self.volunteer_client.post(url, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_application_lifecycle_security(self):
        """
        Tests that application approval can only be done by the NGO that owns the vacancy,
        and cancellation can only be done by the applying volunteer.
        """
        # Create an application
        app = Application.objects.create(
            volunteer=self.volunteer,
            vacancy=self.vacancy,
            status='PENDING'
        )

        url = reverse('api_application_detail', args=[app.id])

        # 1. Volunteer tries to APPROVE the application -> 403 Forbidden
        response = self.volunteer_client.patch(url, {'status': 'ACCEPTED'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # 2. Non-owner NGO tries to APPROVE -> 403 Forbidden
        response = self.ngo2_client.patch(url, {'status': 'ACCEPTED'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # 3. Owner NGO approves -> 200 OK
        response = self.ngo_client.patch(url, {'status': 'ACCEPTED'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verify status updated
        app.refresh_from_db()
        self.assertEqual(app.status, 'ACCEPTED')

        # 4. NGO tries to CANCEL (DELETE) the application -> 403 Forbidden
        response = self.ngo_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # 5. Volunteer cancels (DELETE) -> 200 OK
        response = self.volunteer_client.delete(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify deleted
        self.assertFalse(Application.objects.filter(id=app.id).exists())
