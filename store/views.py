from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Collection, OrderItem, Product, Reviews
from .serializers import CollectionSerializer, ProductSerializer, ReviewSerializer

# Create your views here.


"""
class ProductViewSet - Inherited from ModelViewSet Generic Views
HTTP Requests supported: GET, POST, PUT, DELETE
"""


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        collection_id = self.request.query_params.get("collection_id")
        if collection_id != None:
            return Product.objects.filter(collection_id=collection_id)
        return Product.objects.all()

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs["id"]).count() > 0:
            return Response(
                {
                    "error": "Product cannot be deleted becasue it is associated with an item on order"
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


"""
class CollectionViewSet - Inherited from ModelViewSet Generic Views
HTTP Requests supported: GET, POST, PUT, DELETE
"""


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection=kwargs["pk"]).count() > 0:
            return Response(
                {
                    "error": "collection cannot be deleted becasue it contains one or more products."
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Reviews.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}
