from django.urls import path
from . import views

urlpatterns=[
    path('login/', views.login, name='login_route'),
    path('logout/', views.logout, name='logout_route'),
    path('register/', views.register, name='register_route'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
]