from django.db import models
from api.models import Country, State, City, Location
# import secrets

# Text Choices class definitions
class Gender(models.TextChoices):
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'
    UNISEX = 'UNISEX', 'Unisex'

class AdvertisedProductStatus(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'Available'
    SOLD = 'SOLD', 'Sold'
    RESERVED = 'RESERVED', 'Reserved'
    INACTIVE = 'INACTIVE', 'Inactive'

class FulfillmentMethod(models.TextChoices):
    PICKUP = 'PICKUP', 'Pickup'
    WAYBILL = 'WAYBILL', 'Waybill'

class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    AWAITING_PAYMENT = 'AWAITING_PAYMENT', 'Awaiting_payment'
    PAID = 'PAID', 'Paid'
    PROCESSING = 'PROCESSING', 'Processing'
    SHIPPED = 'SHIPPED', 'Shipped'
    READY_FOR_PICKUP = 'READY_FOR_PICKUP', 'Ready_for_pickup'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'

class DeliveryType(models.TextChoices):
    INTRASTATE = 'INTRASTATE', 'Intrastate'
    INTERSTATE = 'INTERSTATE', 'Interstate'
    INTERNATIONAL = 'INTERNATIONAL', 'International'

class PaymentMethod(models.TextChoices):
    CASH = 'CASH', 'Cash'
    TRANSFER = 'TRANSFER', 'Transfer'
    POS = 'POS', 'POS'
    OTHER = 'OTHER', 'Other'


class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PAID = 'PAID', 'Paid'
    PARTIAL = 'PARTIAL', 'Partial'
    FAILED = 'FAILED', 'Failed'

# Model classes

class SMTBCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    standard_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class SMTBRestock(models.Model):
    category = models.ForeignKey(SMTBCategory, on_delete=models.PROTECT, related_name='restocks')
    quantity = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    supplier = models.CharField(max_length=100)
    date_received = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Restocked {self.quantity} pcs of {self.category.name} on {self.date_received.strftime("%d-%m-%Y")}.'

class SMTBAdvertisedProduct(models.Model):
    product_id = models.CharField(max_length=20, unique=True, editable=False)
    restock = models.ForeignKey(SMTBRestock, on_delete=models.PROTECT, related_name='advertised_products')
    description = models.TextField()
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.UNISEX)
    waist_size = models.FloatField(null=True, blank=True)
    other_size = models.CharField(max_length=32, null=True, blank=True)  # e.g Medium, hip-44
    length = models.FloatField(null=True, blank=True)
    color = models.CharField(max_length=30, null=True, blank=True)
    image_url = models.URLField()
    advertised_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=AdvertisedProductStatus.choices, default=AdvertisedProductStatus.AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Do this before saving"""
        super().save(*args, **kwargs)

        if not self.product_id:
            self.product_id = f"SMTB-{self.pk:07d}"
            super().save(update_fields=['product_id'])        

    def __str__(self):
        description = f'- {self.description}' if self.description else ''
        return (
            f"{self.restock.category.name}{description}: "
            f"waist-{self.waist_size}, "
            f"length-{self.length}, "
            f"other size info- {self.other_size}, "
            f"color-{self.color}. "
            f"Price: {self.advertised_price}. "
            f"Status: {self.status}."
        )

class SMTBCustomer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=16, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}- {self.phone}"

class  SMTBOrder(models.Model):
    customer = models.ForeignKey(SMTBCustomer, on_delete=models.PROTECT, related_name='orders')
    fulfillment_method = models.CharField(max_length=20, choices=FulfillmentMethod.choices, default=FulfillmentMethod.PICKUP)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    delivery_country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True, related_name='smtb_orders')
    delivery_state = models.ForeignKey(State, on_delete=models.PROTECT, blank=True, null=True, related_name='smtb_orders')
    delivery_city = models.ForeignKey(City, on_delete=models.PROTECT, blank=True, null=True, related_name='smtb_orders')
    delivery_location = models.ForeignKey(Location, on_delete=models.PROTECT, blank=True, null=True, related_name='smtb_orders')
    delivery_type = models.CharField(max_length=20, choices=DeliveryType.choices, null=True, blank=True)
    delivery_address = models.TextField(null=True, blank=True)
    delivery_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order by {self.customer.name}-{self.customer.phone} placed on {self.created_at.strftime('%d-%m-%Y')} and current status is {self.status}."
    
class SMTBOrderItem(models.Model):
    order = models.ForeignKey(SMTBOrder, on_delete=models.CASCADE, related_name='items')
    advertised_product = models.ForeignKey(SMTBAdvertisedProduct, on_delete=models.PROTECT, related_name='order_items')
    sales_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        description = ''
        if self.advertised_product:
            description += f'{self.advertised_product} sold for {self.sale_price}.'
        # elif self.restock:
        #     description += f"1 {self.restock.category.name} sold for {self.sale_price}."
        else:
            description += f'Item is not described, but it is sold for {self.sale_price}.'
        return description

class SMTBDeliveryCharges(models.Model):
    fee = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=20, choices=DeliveryType.choices)
    country = models.CharField(max_length=2, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    location_names = models.JSONField() 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SMTBSale(models.Model):
    customer_name = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    payment_status = models.CharField(max_length=12, choices=PaymentStatus.choices)
    order = models.OneToOneField(SMTBOrder, on_delete=models.PROTECT, null=True, blank=True, related_name="sale")
    sale_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

class SMTBSaleItem(models.Model):
    sale = models.ForeignKey(SMTBSale, on_delete=models.PROTECT, related_name='sale_items')
    advertised_product = models.ForeignKey(SMTBAdvertisedProduct, on_delete=models.PROTECT, related_name='sale_items', null=True, blank=True)
    restock = models.ForeignKey(SMTBRestock, on_delete=models.PROTECT, related_name='sale_items')
    sales_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
