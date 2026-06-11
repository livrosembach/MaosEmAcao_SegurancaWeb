from django.db import models
from django.contrib.auth.models import User
from core.encryption import encrypt, decrypt

class EncryptedCharField(models.TextField):
    """
    A custom field that encrypts data before saving to the database
    and decrypts it when loaded. Inherits from TextField to handle
    the base64 overhead of Fernet encryption.
    """
    description = "Encrypted character field"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return decrypt(value)

    def to_python(self, value):
        if value is None:
            return value
        return decrypt(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return encrypt(str(value))


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('VOLUNTEER', 'Voluntário'),
        ('NGO', 'ONG'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class VolunteerProfile(models.Model):
    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='volunteer')
    cpf = EncryptedCharField(blank=True, null=True)
    phone = EncryptedCharField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Voluntário: {self.profile.user.username}"


class NGOProfile(models.Model):
    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='ngo')
    cnpj = EncryptedCharField(blank=True, null=True)
    phone = EncryptedCharField(blank=True, null=True)
    address = EncryptedCharField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"ONG: {self.profile.user.username}"


class Vacancy(models.Model):
    ngo = models.ForeignKey(NGOProfile, on_delete=models.CASCADE, related_name='vacancies')
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.ngo.profile.user.username}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('ACCEPTED', 'Aceito'),
        ('REJECTED', 'Rejeitado'),
    ]
    volunteer = models.ForeignKey(VolunteerProfile, on_delete=models.CASCADE, related_name='applications')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Business Rule: A volunteer can only apply to a vacancy once.
        unique_together = ('volunteer', 'vacancy')

    def __str__(self):
        return f"{self.volunteer.profile.user.username} -> {self.vacancy.title} ({self.get_status_display()})"
