"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from core import views

urlpatterns = [
    path('', views.index, name='index'),
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

