from django.urls import path
from . import views

urlpatterns=[
    path("", views.cart, name='cart_view'),
    path("add_cart/<slug:product_id>", views.add_cart, name='add_cart'),
    path("remove_cart/<slug:product_id>", views.remove_cart, name='remove_cart'),
    path("quantity_decrease/<slug:product_id>", views.quantity_decrease, name='quantity_decrease'),
]