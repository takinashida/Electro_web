from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import NetworkNode, Product


@admin.action(description="Очистить задолженность перед поставщиком")
def clear_debt(modeladmin, request, queryset):
    queryset.update(debt=0)


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = ("name", "node_type", "city", "supplier", "debt")
    list_filter = ("city",)
    actions = [clear_debt]
    search_fields = ("name",)

    def supplier_link(self, obj):
        if obj.supplier:
            return obj.supplier.name
        return "-"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "release_date", "network_node")
