from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings
from core import views

def cognito_logout(request):
    logout(request)
    cognito_logout_url = (
        f"{settings.COGNITO_DOMAIN}/logout"
        f"?client_id={settings.COGNITO_APP_CLIENT_ID}"
        f"&logout_uri=http://localhost:8000/entrar/"
    )
    return redirect(cognito_logout_url)

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('entrar/', TemplateView.as_view(template_name='login.html'), name='login_page'),
    path('cadastrar/', TemplateView.as_view(template_name='register.html'), name='register_page'),
    path('oportunidades/', TemplateView.as_view(template_name='opportunities.html'), name='opportunities'),
    path('oportunidades/detalhes/', TemplateView.as_view(template_name='opportunity-details.html'), name='opportunity_detail'),
    path('voluntario/painel/', TemplateView.as_view(template_name='volunteer-dashboard.html'), name='volunteer_dashboard'),
    path('voluntario/candidaturas/', TemplateView.as_view(template_name='my-applications.html'), name='my_applications'),
    path('voluntario/perfil/', TemplateView.as_view(template_name='volunteer-profile.html'), name='volunteer_profile'),
    path('ong/painel/', TemplateView.as_view(template_name='ngo-dashboard.html'), name='ngo_dashboard'),
    path('ong/oportunidades/', TemplateView.as_view(template_name='ngo-opportunities.html'), name='ngo_opportunities'),
    path('ong/oportunidades/nova/', TemplateView.as_view(template_name='create-opportunity.html'), name='create_opportunity'),
    path('ong/oportunidades/editar/', TemplateView.as_view(template_name='edit-opportunity.html'), name='edit_opportunity'),
    path('ong/candidatos/', TemplateView.as_view(template_name='ngo-applicants.html'), name='ngo_applicants'),
    path('ong/perfil/', TemplateView.as_view(template_name='ngo-profile.html'), name='ngo_profile'),
    path('admin/painel/', TemplateView.as_view(template_name='admin-dashboard.html'), name='admin_dashboard'),
    path('admin/usuarios/', TemplateView.as_view(template_name='admin-users.html'), name='admin_users'),
    path('admin/ongs/', TemplateView.as_view(template_name='admin-ngos.html'), name='admin_ngos'),
    path('admin/auditoria/', TemplateView.as_view(template_name='audit-logs.html'), name='audit_logs'),

    path('accounts/logout/', cognito_logout, name='account_logout'),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),

    # Native REST API endpoints
    path('api/csrf/', views.csrf_token_view, name='api_csrf'),
    path('api/profile/', views.profile_view, name='api_profile'),
    path('api/vacancies/', views.vacancies_list_create_view, name='api_vacancies'),
    path('api/vacancies/<int:vacancy_id>/', views.vacancy_detail_view, name='api_vacancy_detail'),
    path('api/vacancies/<int:vacancy_id>/apply/', views.apply_vacancy_view, name='api_vacancy_apply'),
    path('api/applications/', views.applications_list_view, name='api_applications'),
    path('api/applications/<int:application_id>/', views.application_detail_view, name='api_application_detail'),
]