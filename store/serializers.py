import collections
from decimal import Decimal

from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.relations import HyperlinkedRelatedField
from typing_extensions import Required

from store.models import Collection, Product


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
    # instance.unit_price = validated_data.get("unit_price")
    # instance.save()
    # return instance
