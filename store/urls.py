from django.urls import path
from django.urls.resolvers import URLPattern

from . import views

# URL Configuration

urlpatterns = [
    path("products/", views.product_list),
    path("products/<int:id>", views.product_details),
    path("collections/", views.collection_list),
    path("collections/<int:pk>", views.collection_detail, name="collection-detail"),
]
