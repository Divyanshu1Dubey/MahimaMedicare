from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='chat-home'),
    path('logout/', auth_views.LogoutView.as_view(template_name="chat/logout.html"), name='chat-logout'),

    path('home/<int:pk>/', views.home, name='chat-home'),
    path('profile/', views.profile, name='chat-profile'),

    # Chat APIs
    path('send_chat/', views.send_chat, name='chat-send'),
    path('get_messages/', views.get_messages, name='chat-get-messages'),
    path('check_new_messages/', views.check_new_messages, name='chat-check-new-messages'),
]
