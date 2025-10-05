from django.urls import path
from . import views
urlpatterns = [
    path("", views.Store, name='store'),
    path("category/<slug:slug>", views.Store, name='category_route'),
    path("category/<slug:slug>/<slug:product_slug>/", views.product_detail, name='product_detail'),
    path("search/", views.search, name='search'),
]
