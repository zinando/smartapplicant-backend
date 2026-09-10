from django.contrib import admin
from .models import (
    SMTBCategory,
    SMTBRestock,
    SMTBAdvertisedProduct,
    SMTBCustomer,
    SMTBOrder,
    SMTBOrderItem,
    SMTBDeliveryCharges,
    SMTBSale,
    SMTBSaleItem,
)


@admin.register(SMTBCategory)
class SMTBCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'standard_price', 'created_at')
    search_fields = ('name',)


@admin.register(SMTBRestock)
class SMTBRestockAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'category',
        'quantity',
        'total_cost',
        'supplier',
        'date_received',
    )
    list_filter = ('category', 'date_received')
    search_fields = ('supplier', 'category__name')


@admin.register(SMTBAdvertisedProduct)
class SMTBAdvertisedProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_id',
        'restock',
        'gender',
        'advertised_price',
        'status',
        'created_at',
    )
    list_filter = ('gender', 'status')
    search_fields = (
        'product_id',
        'description',
        'color',
    )
    readonly_fields = ('product_id',)


@admin.register(SMTBCustomer)
class SMTBCustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'created_at')
    search_fields = ('name', 'phone')

class SMTBOrderItemInline(admin.TabularInline):
    model = SMTBOrderItem
    extra = 0


@admin.register(SMTBOrder)
class SMTBOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'fulfillment_method',
        'status',
        'delivery_fee',
        'created_at',
    )
    list_filter = ('fulfillment_method', 'status')
    search_fields = (
        'customer__name',
        'customer__phone',
    )
    inlines = [SMTBOrderItemInline]


# @admin.register(SMTBOrderItem)
# class SMTBOrderItemAdmin(admin.ModelAdmin):
#     list_display = (
#         'order',
#         'advertised_product',
#         'sale_price',
#         'created_at',
#     )
#     search_fields = ('advertised_product__product_id',)


@admin.register(SMTBDeliveryCharges)
class SMTBDeliveryChargesAdmin(admin.ModelAdmin):
    list_display = ('id', 'fee', 'type', 'country', 'state', 'city', 'location_names', 'created_at', 'updated_at')
    list_filter = ('type',)

class SMTBSaleItemInline(admin.TabularInline):
    model = SMTBSaleItem
    extra = 1

@admin.register(SMTBSale)
class SMTBSaleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer_name',
        'payment_method',
        'payment_status',
        'sale_date',
    )
    list_filter = ('payment_method', 'payment_status', 'sale_date',)
    search_fields = ('customer_name',)
    inlines = [SMTBSaleItemInline]


@admin.register(SMTBSaleItem)
class SMTBSaleItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'sale',
        'advertised_product',
        'restock',
        'sales_price',
        'quantity',
    )
    search_fields = ('advertised_product__product_id',)