import json
from functools import wraps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.shortcuts import render, get_object_or_404
from django.db import IntegrityError
from core.models import UserProfile, VolunteerProfile, NGOProfile, Vacancy, Application

def index(request):
    """
    Renders index.html main page.
    """
    return render(request, 'index.html')


# ==========================================
# 🛡️ DECORATORS & HELPERS (RBAC & AUTHENTICATION)
# ==========================================

def api_login_required(view_func):
    """
    Enforces that the user must be authenticated.
    Returns 401 JSON instead of redirecting to login page.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Autenticação necessária.'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view


def volunteer_required(view_func):
    """
    RBAC: Enforces that the user must have a Volunteer profile.
    """
    @wraps(view_func)
    @api_login_required
    def wrapped_view(request, *args, **kwargs):
        try:
            if request.user.profile.role != 'VOLUNTEER':
                return JsonResponse({'error': 'Acesso negado. Apenas voluntários podem realizar esta ação.'}, status=403)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'Perfil de usuário não configurado.'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapped_view


def ngo_required(view_func):
    """
    RBAC: Enforces that the user must have an NGO profile.
    """
    @wraps(view_func)
    @api_login_required
    def wrapped_view(request, *args, **kwargs):
        try:
            if request.user.profile.role != 'NGO':
                return JsonResponse({'error': 'Acesso negado. Apenas ONGs podem realizar esta ação.'}, status=403)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'Perfil de usuário não configurado.'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapped_view


def parse_json(request):
    """
    Parses JSON request body safely.
    """
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return None

# ==========================================
# 🔌 API ENDPOINTS
# ==========================================

@ensure_csrf_cookie
def csrf_token_view(request):
    """
    Endpoint to retrieve/ensure CSRF cookie is set.
    """
    return JsonResponse({'detail': 'CSRF cookie set.'})


@csrf_exempt  # Exempt from CSRF for easy testing, but in production we can require CSRF token
@api_login_required
def profile_view(request):
    """
    Endpoint: /api/profile/
    GET: Retrieves the current user's profile details.
    POST: Creates a profile (Volunteer or NGO).
    PUT: Updates the profile details.
    """
    user = request.user

    # --- GET PROFILE ---
    if request.method == 'GET':
        try:
            profile = user.profile
            data = {
                'has_profile': True,
                'role': profile.role,
                'email': user.email,
                'username': user.username,
            }
            if profile.role == 'VOLUNTEER':
                volunteer = profile.volunteer
                data.update({
                    'cpf': volunteer.cpf,
                    'phone': volunteer.phone,
                    'bio': volunteer.bio,
                })
            elif profile.role == 'NGO':
                ngo = profile.ngo
                data.update({
                    'cnpj': ngo.cnpj,
                    'phone': ngo.phone,
                    'address': ngo.address,
                    'description': ngo.description,
                })
            return JsonResponse(data)
        except UserProfile.DoesNotExist:
            return JsonResponse({'has_profile': False, 'email': user.email, 'username': user.username})

    # --- CREATE PROFILE (POST) ---
    elif request.method == 'POST':
        if hasattr(user, 'profile'):
            return JsonResponse({'error': 'Você já possui um perfil cadastrado.'}, status=400)

        data = parse_json(request)
        if not data:
            return JsonResponse({'error': 'Dados em formato JSON inválido.'}, status=400)

        role = data.get('role')
        if role not in ['VOLUNTEER', 'NGO']:
            return JsonResponse({'error': 'Role inválido. Deve ser VOLUNTEER ou NGO.'}, status=400)

        phone = data.get('phone')
        if not phone:
            return JsonResponse({'error': 'O campo telefone é obrigatório.'}, status=400)

        # Create base UserProfile
        profile = UserProfile.objects.create(user=user, role=role)

        try:
            if role == 'VOLUNTEER':
                cpf = data.get('cpf')
                if not cpf:
                    profile.delete()
                    return JsonResponse({'error': 'O campo CPF é obrigatório para voluntários.'}, status=400)
                
                # Criptografia é feita de forma transparente no save do model
                VolunteerProfile.objects.create(
                    profile=profile,
                    cpf=cpf,
                    phone=phone,
                    bio=data.get('bio', '')
                )
            elif role == 'NGO':
                cnpj = data.get('cnpj')
                address = data.get('address')
                if not cnpj or not address:
                    profile.delete()
                    return JsonResponse({'error': 'Os campos CNPJ e endereço são obrigatórios para ONGs.'}, status=400)

                # Criptografia é feita de forma transparente no save do model
                NGOProfile.objects.create(
                    profile=profile,
                    cnpj=cnpj,
                    phone=phone,
                    address=address,
                    description=data.get('description', '')
                )
        except Exception as e:
            profile.delete()
            return JsonResponse({'error': f'Erro ao criar perfil: {str(e)}'}, status=500)

        return JsonResponse({'message': 'Perfil criado com sucesso!', 'role': role}, status=201)

    # --- UPDATE PROFILE (PUT) ---
    elif request.method == 'PUT':
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'Perfil não encontrado para atualização.'}, status=404)

        data = parse_json(request)
        if not data:
            return JsonResponse({'error': 'Dados em formato JSON inválido.'}, status=400)

        # Update phone (shared by both)
        phone = data.get('phone')

        if profile.role == 'VOLUNTEER':
            volunteer = profile.volunteer
            if phone:
                volunteer.phone = phone
            if 'cpf' in data:
                volunteer.cpf = data['cpf']
            if 'bio' in data:
                volunteer.bio = data['bio']
            volunteer.save()
        elif profile.role == 'NGO':
            ngo = profile.ngo
            if phone:
                ngo.phone = phone
            if 'cnpj' in data:
                ngo.cnpj = data['cnpj']
            if 'address' in data:
                ngo.address = data['address']
            if 'description' in data:
                ngo.description = data['description']
            ngo.save()

        return JsonResponse({'message': 'Perfil atualizado com sucesso!'})

    return JsonResponse({'error': 'Método HTTP não permitido.'}, status=405)


@csrf_exempt
@api_login_required
def vacancies_list_create_view(request):
    """
    Endpoint: /api/vacancies/
    GET: Lists all vacancies in the database.
    POST: Creates a vacancy (NGOs only).
    """
    # --- LIST VACANCIES (GET) ---
    if request.method == 'GET':
        # Proteção SQL Injection: Utiliza estritamente o ORM do Django
        vacancies = Vacancy.objects.all().select_related('ngo__profile__user').order_index_by('-created_at')
        # Wait, order_by instead of order_index_by (which was a typo)
        # Let's fix that
        vacancies = Vacancy.objects.all().select_related('ngo__profile__user').order_by('-created_at')
        
        list_data = []
        for vacancy in vacancies:
            list_data.append({
                'id': vacancy.id,
                'title': vacancy.title,
                'description': vacancy.description,
                'requirements': vacancy.requirements,
                'created_at': vacancy.created_at,
                'ngo': {
                    'name': vacancy.ngo.profile.user.username,
                    'description': vacancy.ngo.description,
                }
            })
        return JsonResponse(list_data, safe=False)

    # --- CREATE VACANCY (POST) ---
    elif request.method == 'POST':
        # RBAC check: Apenas ONGs podem criar vagas
        try:
            profile = request.user.profile
            if profile.role != 'NGO':
                return JsonResponse({'error': 'Acesso negado. Apenas perfis do tipo ONG podem criar vagas.'}, status=403)
            ngo_profile = profile.ngo
        except (UserProfile.DoesNotExist, NGOProfile.DoesNotExist):
            return JsonResponse({'error': 'Perfil de ONG não configurado.'}, status=403)

        data = parse_json(request)
        if not data:
            return JsonResponse({'error': 'Dados em formato JSON inválido.'}, status=400)

        title = data.get('title')
        description = data.get('description')
        if not title or not description:
            return JsonResponse({'error': 'Título e descrição da vaga são obrigatórios.'}, status=400)

        # Proteção SQL Injection: ORM handles parametrization
        vacancy = Vacancy.objects.create(
            ngo=ngo_profile,
            title=title,
            description=description,
            requirements=data.get('requirements', '')
        )

        return JsonResponse({
            'message': 'Vaga criada com sucesso!',
            'vacancy_id': vacancy.id
        }, status=201)

    return JsonResponse({'error': 'Método HTTP não permitido.'}, status=405)


@csrf_exempt
@api_login_required
def vacancy_detail_view(request, vacancy_id):
    """
    Endpoint: /api/vacancies/<id>/
    GET: Details of a vacancy.
    PUT: Updates vacancy details (Owner NGO only).
    DELETE: Deletes vacancy (Owner NGO only).
    """
    # Proteção SQL Injection: ORM parameterization
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    # --- GET DETAILS (GET) ---
    if request.method == 'GET':
        return JsonResponse({
            'id': vacancy.id,
            'title': vacancy.title,
            'description': vacancy.description,
            'requirements': vacancy.requirements,
            'created_at': vacancy.created_at,
            'ngo': {
                'name': vacancy.ngo.profile.user.username,
                'description': vacancy.ngo.description,
            }
        })

    # --- UPDATE VACANCY (PUT) ---
    elif request.method == 'PUT':
        # RBAC & Owner Check: Apenas a ONG dona da vaga pode alterar
        try:
            profile = request.user.profile
            if profile.role != 'NGO' or vacancy.ngo != profile.ngo:
                return JsonResponse({'error': 'Acesso negado. Apenas a ONG criadora desta vaga pode alterá-la.'}, status=403)
        except Exception:
            return JsonResponse({'error': 'Acesso negado.'}, status=403)

        data = parse_json(request)
        if not data:
            return JsonResponse({'error': 'Dados em formato JSON inválido.'}, status=400)

        if 'title' in data:
            vacancy.title = data['title']
        if 'description' in data:
            vacancy.description = data['description']
        if 'requirements' in data:
            vacancy.requirements = data['requirements']
        
        vacancy.save()
        return JsonResponse({'message': 'Vaga atualizada com sucesso!'})

    # --- DELETE VACANCY (DELETE) ---
    elif request.method == 'DELETE':
        # RBAC & Owner Check: Apenas a ONG dona da vaga pode deletar
        try:
            profile = request.user.profile
            if profile.role != 'NGO' or vacancy.ngo != profile.ngo:
                return JsonResponse({'error': 'Acesso negado. Apenas a ONG criadora desta vaga pode deletá-la.'}, status=403)
        except Exception:
            return JsonResponse({'error': 'Acesso negado.'}, status=403)

        vacancy.delete()
        return JsonResponse({'message': 'Vaga deletada com sucesso!'})

    return JsonResponse({'error': 'Método HTTP não permitido.'}, status=405)


@csrf_exempt
@volunteer_required
def apply_vacancy_view(request, vacancy_id):
    """
    Endpoint: /api/vacancies/<id>/apply/
    POST: Volunteer applies to a vacancy (Volunteers only).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método HTTP não permitido. Use POST.'}, status=405)

    volunteer_profile = request.user.profile.volunteer
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    # 🛡️ Validação de Regra de Negócio (Design Inseguro)
    # Evita que o mesmo voluntário crie mais de uma candidatura para a mesma vaga
    try:
        Application.objects.create(
            volunteer=volunteer_profile,
            vacancy=vacancy,
            status='PENDING'
        )
    except IntegrityError:
        return JsonResponse({'error': 'Você já se candidatou a esta vaga.'}, status=400)

    return JsonResponse({'message': 'Candidatura enviada com sucesso!'}, status=201)


@csrf_exempt
@api_login_required
def applications_list_view(request):
    """
    Endpoint: /api/applications/
    GET: Lists applications.
      - Volunteers see their own applications.
      - NGOs see applications submitted to their vacancies.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método HTTP não permitido. Use GET.'}, status=405)

    profile = request.user.profile

    # --- LIST FOR VOLUNTEER ---
    if profile.role == 'VOLUNTEER':
        volunteer = profile.volunteer
        applications = Application.objects.filter(volunteer=volunteer).select_related('vacancy__ngo__profile__user').order_by('-applied_at')
        
        data = []
        for app in applications:
            data.append({
                'id': app.id,
                'status': app.status,
                'applied_at': app.applied_at,
                'vacancy': {
                    'id': app.vacancy.id,
                    'title': app.vacancy.title,
                    'ngo_name': app.vacancy.ngo.profile.user.username,
                }
            })
        return JsonResponse(data, safe=False)

    # --- LIST FOR NGO ---
    elif profile.role == 'NGO':
        ngo = profile.ngo
        applications = Application.objects.filter(vacancy__ngo=ngo).select_related('volunteer__profile__user', 'vacancy').order_by('-applied_at')
        
        data = []
        for app in applications:
            # Dados sensíveis do voluntário (phone) são automaticamente descriptografados pelo custom field
            data.append({
                'id': app.id,
                'status': app.status,
                'applied_at': app.applied_at,
                'vacancy': {
                    'id': app.vacancy.id,
                    'title': app.vacancy.title,
                },
                'volunteer': {
                    'username': app.volunteer.profile.user.username,
                    'email': app.volunteer.profile.user.email,
                    'phone': app.volunteer.phone, # Decrypted automatically
                    'bio': app.volunteer.bio,
                }
            })
        return JsonResponse(data, safe=False)

    return JsonResponse({'error': 'Perfil inválido.'}, status=400)


@csrf_exempt
@api_login_required
def application_detail_view(request, application_id):
    """
    Endpoint: /api/applications/<id>/
    PATCH: Change application status (NGO vacancy owner only).
    DELETE: Cancel/remove application (Volunteer application owner only).
    """
    # Proteção SQL Injection: ORM parameterization
    app = get_object_or_404(Application, id=application_id)
    profile = request.user.profile

    # --- UPDATE STATUS (PATCH) (NGO Only) ---
    if request.method == 'PATCH':
        if profile.role != 'NGO':
            return JsonResponse({'error': 'Acesso negado. Apenas ONGs podem alterar o status de candidaturas.'}, status=403)

        # 🛡️ Controle de Acesso de Propriedade (RBAC & Business Logic)
        # Verifica se a vaga pertence à ONG logada
        if app.vacancy.ngo != profile.ngo:
            return JsonResponse({'error': 'Acesso negado. Você não é dono da vaga desta candidatura.'}, status=403)

        data = parse_json(request)
        if not data:
            return JsonResponse({'error': 'Dados em formato JSON inválido.'}, status=400)

        status = data.get('status')
        if status not in ['ACCEPTED', 'REJECTED']:
            return JsonResponse({'error': 'Status inválido. Deve ser ACCEPTED ou REJECTED.'}, status=400)

        app.status = status
        app.save()
        return JsonResponse({'message': f'Candidatura atualizada para: {app.get_status_display()}.'})

    # --- CANCEL/DELETE (DELETE) (Volunteer Only) ---
    elif request.method == 'DELETE':
        if profile.role != 'VOLUNTEER':
            return JsonResponse({'error': 'Acesso negado. Apenas voluntários podem cancelar candidaturas.'}, status=403)

        # 🛡️ Controle de Acesso de Propriedade (RBAC & Business Logic)
        # Verifica se a candidatura pertence ao voluntário logado
        if app.volunteer != profile.volunteer:
            return JsonResponse({'error': 'Acesso negado. Você só pode cancelar suas próprias candidaturas.'}, status=403)

        app.delete()
        return JsonResponse({'message': 'Candidatura cancelada com sucesso.'})

    return JsonResponse({'error': 'Método HTTP não permitido.'}, status=405)
