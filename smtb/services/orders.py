from django.db import transaction
from django.utils import timezone
from smtb.services.delivery import (
    determine_delivery_type,
    get_delivery_charge,
)
from api.models import Country, State, City, Location

from smtb.models import (
    SMTBOrder,
    SMTBOrderItem,
    SMTBAdvertisedProduct,
    AdvertisedProductStatus,
    OrderStatus,
    FulfillmentMethod,
    SMTBSale,
    SMTBSaleItem
)


@transaction.atomic
def create_order(
    customer,
    product_ids,
    fulfillment_method,
    country_id=None,
    state_id=None,
    city_id=None,
    location_id=None,
    delivery_address=None,
):
    """
    Create an order and reserve all requested advertised products.
    """
    delivery_fee = 0
    if fulfillment_method == FulfillmentMethod.WAYBILL:
        country = Country.objects.filter(id=country_id,is_active=True).first()

        if not country:
            raise ValueError("Invalid country.")

        state = None
        city = None
        location = None

        if state_id:
            state = State.objects.filter(id=state_id,country=country,is_active=True).first()

            if not state:
                raise ValueError("Invalid state.")

        if city_id:
            city = City.objects.filter(id=city_id,state=state,is_active=True).first()

            if not city:
                raise ValueError("Invalid city.")

        if location_id:
            location = Location.objects.filter(id=location_id,city=city,is_active=True).first()

            if not location:
                raise ValueError("Invalid location.")
        if not delivery_address:
            raise ValueError("Delivery address is required for waybill orders.")
        
        delivery_type = determine_delivery_type(country_id=country.id,state_id=state.id if state else None,)
        delivery_fee = get_delivery_charge(
            delivery_type=delivery_type,
            country_code=country.country_code,
            state=state.name if state else None,
            city=city.name if city else None,
            location=location.name if location else None,
        )
        if delivery_fee is None:
            raise ValueError("Delivery charge could not be determined.")

    products = []

    for product_id in product_ids:
        product = (
            SMTBAdvertisedProduct.objects
            .select_for_update()
            .get(product_id=product_id)
        )

        if product.status != AdvertisedProductStatus.AVAILABLE:
            raise ValueError(
                f"Product {product_id} is no longer available."
            )
        
        # if fulfillment_method == FulfillmentMethod.WAYBILL:
        #     if not delivery_address:
        #         raise ValueError("Delivery address is required for waybill orders.")

        #     if delivery_fee is None:
        #         raise ValueError("Delivery fee is required for waybill orders.")

        products.append(product)

    order = SMTBOrder.objects.create(
        customer=customer,
        fulfillment_method=fulfillment_method,
        status=OrderStatus.AWAITING_PAYMENT,

        delivery_country=country,
        delivery_state=state,
        delivery_city=city,
        delivery_location=location,
        delivery_type=delivery_type,

        delivery_address=delivery_address,
        delivery_fee=delivery_fee,
    )

    for product in products:
        SMTBOrderItem.objects.create(
            order=order,
            advertised_product=product,
            sales_price=product.advertised_price,
        )

        product.status = AdvertisedProductStatus.RESERVED
        product.save(update_fields=["status"])

    return order

@transaction.atomic
def cancel_order(order):
    order = (
        SMTBOrder.objects
        .select_for_update()
        .get(pk=order.pk)
    )

    if order.status == OrderStatus.CANCELLED:
        return order

    if order.status != OrderStatus.AWAITING_PAYMENT:
        raise ValueError(
            f"Order cannot be cancelled from status {order.status}."
        )

    items = list(
        order.items
        .select_related("advertised_product")
        .select_for_update()
    )

    for item in items:
        product = item.advertised_product

        if product and product.status == AdvertisedProductStatus.RESERVED:
            product.status = AdvertisedProductStatus.AVAILABLE
            product.save(update_fields=["status"])

    order.status = OrderStatus.CANCELLED
    order.save(update_fields=["status", "updated_at"])

    return order

@transaction.atomic
def mark_order_paid(order, payment_method):
    """
    Confirm payment for an order and convert it into a sale.

    Safe against duplicate payment confirmation:
    once an order is PAID, it cannot create another sale.
    """

    if order.status == OrderStatus.PAID:
        return order

    if order.status != OrderStatus.AWAITING_PAYMENT:
        raise ValueError(
            f"Order cannot be marked paid from status {order.status}."
        )

    items = list(
        order.items
        .select_related("advertised_product")
        .select_for_update()
    )

    if not items:
        raise ValueError("Cannot mark an order with no items as paid.")

    # Validate every product before making any changes.
    for item in items:
        product = item.advertised_product

        if not product:
            raise ValueError(
                "Every order item must have an advertised product."
            )

        if product.status != AdvertisedProductStatus.RESERVED:
            raise ValueError(
                f"Product {product.product_id} is not reserved for this order."
            )

    # Create exactly one sale for this order.
    sale = SMTBSale.objects.create(
        order=order,
        customer_name=order.customer.name,
        payment_method=payment_method,
        payment_status="PAID",
        sale_date=timezone.now(),
    )

    # Convert order items into sale items.
    for item in items:
        product = item.advertised_product

        SMTBSaleItem.objects.create(
            sale=sale,
            advertised_product=product,
            restock_id=product.restock_id,
            sales_price=item.sales_price,
            quantity=1,
        )

        product.status = AdvertisedProductStatus.SOLD
        product.save(update_fields=["status"])

    order.status = OrderStatus.PAID
    order.save(update_fields=["status", "updated_at"])

    return order

def start_order_processing(order):
    if order.status != OrderStatus.PAID:
        raise ValueError(
            f"Order cannot be processed from status {order.status}."
        )

    order.status = OrderStatus.PROCESSING
    order.save(update_fields=["status", "updated_at"])
    return order


def mark_order_shipped(order):
    if (
        order.status != OrderStatus.PROCESSING
        or order.fulfillment_method != FulfillmentMethod.WAYBILL
    ):
        raise ValueError("Order cannot be shipped in its current state.")

    order.status = OrderStatus.SHIPPED
    order.save(update_fields=["status", "updated_at"])
    return order


def mark_ready_for_pickup(order):
    if (
        order.status != OrderStatus.PROCESSING
        or order.fulfillment_method != FulfillmentMethod.PICKUP
    ):
        raise ValueError("Order cannot be marked ready for pickup.")

    order.status = OrderStatus.READY_FOR_PICKUP
    order.save(update_fields=["status", "updated_at"])
    return order


def complete_order(order):
    if order.status not in (
        OrderStatus.SHIPPED,
        OrderStatus.READY_FOR_PICKUP,
    ):
        raise ValueError("Order cannot be completed from its current state.")

    order.status = OrderStatus.COMPLETED
    order.save(update_fields=["status", "updated_at"])
    return order