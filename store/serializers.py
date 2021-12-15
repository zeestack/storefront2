import collections
from decimal import Decimal
from re import search

from django.db.models.query import QuerySet
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.relations import HyperlinkedRelatedField
from typing_extensions import Required

from store.models import Cart, CartItem, Collection, Product, Reviews


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "title", "products_count"]

    products_count = serializers.IntegerField(read_only=True)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        # fields = "__all__" # bad practice
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "inventory",
            "unit_price",
            "price_with_tax",
            "collection",
        ]

    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    # price = serializers.DecimalField(
    #     max_digits=6, decimal_places=2, source="unit_price"
    # )
    # # calculated field in serializer class
    price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax")

    # # serialize by primary key
    # # collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
    # # serialize by string
    # # collection = serializers.StringRelatedField()
    # # serialize by nested object
    # # collection = CollectionSerializer()
    # # serialize by hyperlink

    # collection = HyperlinkedRelatedField(
    #     queryset=Collection.objects.all(), view_name="collection-detail"
    # )

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)

    # override the validate method of the ModelSerializer class to perform custom validation.
    # def validate(self, attrs):
    #  return super().validate(attrs)

    # we can overwrite the create method if we want to set somefields.
    def create(self, validated_data):
        product = Product(**validated_data)
        product.description = "setting up description by overriding a create method."
        product.save()
        return product

    # similary update method can also be overridden
    # def update(self, instance, validated_data):
    # in    stance.unit_price = validated_data.get("unit_price")
    # instance.save()
    # return instance


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ["id", "date", "name", "description"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        return Reviews.objects.create(product_id=product_id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "unit_price"]


class CartItemsSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemsSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    def get_total_price(self, cart: Cart):

        return sum(
            [item.quantity * item.product.unit_price for item in cart.items.all()]
        )

    # net_price = 0
    # for item in cart.items:
    #     net_price += item.total_price
    # return net_price

    class Meta:
        model = Cart
        fields = ["id", "created_at", "items", "total_price"]
