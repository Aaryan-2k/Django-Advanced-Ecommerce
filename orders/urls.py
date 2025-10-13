from django.urls import path
from . import views

urlpatterns=[
    path('place_order/', views.place_order, name='placeorder_route'),
    path('payments/', views.payment, name='payment_route'),
]