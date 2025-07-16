from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('applications/', views.applications_list, name='applications_list'),
    path('application/add/', views.application_create, name='application_add'),
    path('application/<int:pk>/edit/', views.application_update, name='application_edit'),
    path('application/<int:pk>/delete/', views.application_delete, name='application_delete'),
    path('api/notifications/', views.notifications_api, name='notifications_api'),
    path('reminders/', views.reminders_list, name='reminders_list'),
    path('reminders/add/', views.reminder_create, name='reminder_add'),
    path('reminders/<int:pk>/edit/', views.reminder_edit, name='reminder_edit'),
    path('reminders/<int:pk>/delete/', views.reminder_delete, name='reminder_delete'),
    path('reports/', views.reports, name='reports'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),
] 