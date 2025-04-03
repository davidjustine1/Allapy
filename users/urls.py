from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('houseboat/<int:houseboat_id>/', views.houseboat_detail, name='houseboat_detail'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('booking/<int:houseboat_id>/', views.booking, name='booking'),
]