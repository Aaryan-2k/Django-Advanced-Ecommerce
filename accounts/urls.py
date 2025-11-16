from django.urls import path
from . import views

urlpatterns=[
    path('login/', views.login, name='login_route'),
    path('logout/', views.logout, name='logout_route'),
    path('register/', views.register, name='register_route'),
    path('forgotpassword/', views.forgot_password, name='forgotpassword_route'),
    path('resetpassword/<uidb64>/<token>/', views.reset_password, name='restpassword_route'),
    path('reset_password/', views.reset_password, name='changepassword_route'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('dashboard/', views.dashboard, name='dashboard_route'),
    path('orders/', views.orders_list, name='orders_list_route'),
    path('editprofile/', views.editprofile, name='edit_profile_route'),
    path('changepassword/', views.change_password, name='change_password_route'),
]