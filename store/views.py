from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from .models import Collection, Product
from .serializers import CollectionSerializer, ProductSerializer

# Create your views here.

"""
class ProductList - Inherited by ListCreateAPIView Generic Views
HTTP Requests supported: GET, POST
"""


class ProductList(ListCreateAPIView):
    def get_queryset(self):
        return Product.objects.select_related("collection").all()

    def get_serializer_class(self):
        return ProductSerializer

    def get_serializer_context(self):
        return {"request": self.request}


"""
class ProductDetail - Inherited by RetrieveUpdateDestroyAPIView Generic Views
HTTP Requests supported: GET, POST, PUT, DELETE
"""


class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # lookup_field = "id"

    def delete(self, request, id):

        """
        overriding delete method of the parent class
        """
        product = get_object_or_404(Product, pk=id)
        if product.orderitems.count() > 0:
            return Response(
                {
                    "error": "Product cannot be deleted becasue it is associated with an item on order"
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        serializer = ProductSerializer(product)
        serializer.data.id = product.id
        product.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


"""
CollectionList - Inherited by ListCreateAPIView Generic Views
HTTP Requests supported: GET, POST
"""


class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer


"""
class CollectionDetail - Inherited by RetrieveUpdateDestroyAPIView Generic Views
HTTP Requests supported: GET, POST, PUT, DELETE
"""


class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        """
        overriding delete method of the parent class
        """
        collection = Collection.objects.annotate(products_count=Count("products")).all()
        if collection.products.count() > 0:
            return Response(
                {
                    "error": "Product cannot be deleted becasue it is associated with an item on order"
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        serializer = CollectionSerializer(collection)
        serializer.data.id = collection.id
        collection.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
