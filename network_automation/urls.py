from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('devices/', views.devices, name='devices'),
    path('configure/', views.configure, name='config' ),
    path('verify_config/', views.verify_config, name='verify'),
    path('log/', views.log, name='log'),
    path('update/<device_id>', views.update, name='update'),
    path('delete/<device_id>', views.delete, name='delete'),
    path('create/', views.create, name='create'),
    path('register/', views.usercreate, name='register'),
    path('logout/', views.logoutView, name="logout"),
    path('', views.loginView, name="login"),
    path('login/', views.loginView, name="login"),
    path('accounts/login/', views.loginView, name="login")

]