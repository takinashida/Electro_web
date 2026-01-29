from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import NetworkNode, Product


class NetworkNodeSerializer(serializers.ModelSerializer):
    products= serializers.SerializerMethodField()

    class Meta:
        model = NetworkNode
        fields = "__all__"
        read_only_fields = ("debt",)

    def get_products(self, obj):
        products = obj.products.all()
        serializer = ProductSerializer(products, many=True)
        return serializer.data

    def validate(self, attrs):
        node_type = attrs.get("node_type")
        supplier = attrs.get("supplier")

        if node_type == "factory" and supplier is not None:
            raise serializers.ValidationError({"supplier": "У узла типа factory не может быть поставщика"})

        if node_type == "retail":
            if supplier is None:
                raise serializers.ValidationError(
                    {"supplier": "Для retail необходимо указать поставщика"}
                )
            if supplier.node_type != "factory":
                raise serializers.ValidationError({"supplier": "Поставщиком для retail может быть только factory"})

        if node_type == "entrepreneur":
            if supplier is None:
                raise serializers.ValidationError({"supplier": "Для entrepreneur необходимо указать поставщика"})
            if supplier.node_type not in ("factory", "retail"):
                raise serializers.ValidationError({"supplier": "Поставщиком для entrepreneur может быть factory или retail"})

        return attrs


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"