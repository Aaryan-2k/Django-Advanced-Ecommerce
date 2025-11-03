from django.urls import path
from . import views

urlpatterns=[
    path('place_order/', views.place_order, name='placeorder_route'),
    path('stripe_payment_route/', views.stripe_payment, name='stripe_payment_route'),
    path('stripe_payments/', views.payment, name='payment_route'),
    path('success/', views.payment_complete, name='payment_complete'),
    path('failed/', views.payment_failed, name='payment_failed'),
    path('paypal_payment/', views.paypal_payment, name='paypal_payment_route'),
    path('execute_payment_route/', views.execute_payment, name='execute_payment_route'),
]