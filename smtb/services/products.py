from smtb.models import (
    SMTBAdvertisedProduct,
    AdvertisedProductStatus,
)


def get_product(product_id):
    """Return an advertised product by its public ID."""
    return SMTBAdvertisedProduct.objects.select_related(
        'restock__category'
    ).filter(
        product_id=product_id
    ).first()


def check_product_availability(product_id):
    """Check whether an advertised product is currently available."""
    product = get_product(product_id)

    if not product:
        return {
            'available': False,
            'message': 'Product not found.'
        }

    if product.status != AdvertisedProductStatus.AVAILABLE:
        return {
            'available': False,
            'message': f'Product is currently {product.get_status_display().lower()}.',
            'product': product,
        }

    return {
        'available': True,
        'message': 'Product is available.',
        'product': product,
    }


def get_product_details(product_id):
    """Return customer-facing information about an advertised product."""
    product = get_product(product_id)

    if not product:
        return None

    return {
        'product_id': product.product_id,
        'category': product.restock.category.name,
        'description': product.description,
        'gender': product.get_gender_display(),
        'waist_size': product.waist_size,
        'other_size': product.other_size,
        'length': product.length,
        'color': product.color,
        'price': product.advertised_price,
        'status': product.get_status_display(),
        'image_url': product.image_url,
    }