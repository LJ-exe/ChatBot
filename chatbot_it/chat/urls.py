"""URLs pour l'application chat."""
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Utilisateur
    path('', views.dashboard, name='dashboard'),
    path('send/', views.send_message, name='send_message'),
    path('feedback/<int:message_id>/', views.submit_feedback, name='submit_feedback'),
    path('history/', views.history, name='history'),
    path('message/<int:pk>/delete/', views.delete_message, name='delete_message'),

    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),

    # Admin - Utilisateurs
    path('admin-panel/users/', views.admin_users_list, name='admin_users_list'),
    path('admin-panel/users/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin-panel/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin-panel/users/<int:pk>/history/', views.admin_user_history, name='admin_user_history'),

    # Admin - FAQ
    path('admin-panel/faq/', views.admin_faq_list, name='admin_faq_list'),
    path('admin-panel/faq/new/', views.admin_faq_create, name='admin_faq_create'),
    path('admin-panel/faq/<int:pk>/edit/', views.admin_faq_edit, name='admin_faq_edit'),
    path('admin-panel/faq/<int:pk>/delete/', views.admin_faq_delete, name='admin_faq_delete'),

    # Admin - Conversations
    path('admin-panel/conversations/', views.admin_conversations, name='admin_conversations'),
]
