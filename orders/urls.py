from django.urls import path
from . import views

urlpatterns=[
    path('place_order/', views.place_order, name='placeorder_route'),
    path('stripe_payment_route/', views.stripe_payment, name='stripe_payment_route'),
    path('payments/', views.payment, name='payment_route'),
    path('success/', views.payment_complete, name='payment_complete'),
]