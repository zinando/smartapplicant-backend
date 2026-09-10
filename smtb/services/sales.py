from django.db import transaction

from smtb.models import (
    SMTBSale,
    SMTBSaleItem,
    SMTBAdvertisedProduct,
    AdvertisedProductStatus,
)


@transaction.atomic
def record_sale(
    customer_name,
    payment_method,
    payment_status,
    sale_date,
    items,
):
    """
    Record a physical/manual sale.

    items = [
        {
            'product_id': 'SMTB-0000001',  # optional
            'restock_id': 12,
            'sales_price': 5000,
            'quantity': 1,
        },
        ...
    ]
    """

    sale = SMTBSale.objects.create(
        customer_name=customer_name,
        payment_method=payment_method,
        payment_status=payment_status,
        sale_date=sale_date,
    )

    for item in items:
        product = None

        product_id = item.get('product_id')

        if product_id:
            product = (
                SMTBAdvertisedProduct.objects
                .select_for_update()
                .get(product_id=product_id)
            )

            if product.status != AdvertisedProductStatus.AVAILABLE:
                raise ValueError(
                    f'Product {product_id} is not available.'
                )

            product.status = AdvertisedProductStatus.SOLD
            product.save(update_fields=['status'])

        SMTBSaleItem.objects.create(
            sale=sale,
            advertised_product=product,
            restock_id=item['restock_id'],
            sales_price=item['sales_price'],
            quantity= 1 if product else item['quantity'],
        )

    return sale