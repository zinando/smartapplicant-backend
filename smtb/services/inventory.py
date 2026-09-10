from django.db.models import Sum

from smtb.models import (
    SMTBCategory,
    SMTBRestock,
    SMTBSaleItem,
)


def get_category_stock(category):
    total_restocked = (
        SMTBRestock.objects
        .filter(category=category)
        .aggregate(total=Sum('quantity'))['total'] or 0
    )

    total_sold = (
        SMTBSaleItem.objects
        .filter(restock__category=category)
        .aggregate(total=Sum('quantity'))['total'] or 0
    )

    return total_restocked - total_sold


def get_category_stock_value(category):
    stock = get_category_stock(category)
    return stock * category.standard_price


def get_category_inventory(category):
    stock = get_category_stock(category)

    return {
        'category': category.name,
        'standard_price': category.standard_price,
        'total_restocked': (
            SMTBRestock.objects
            .filter(category=category)
            .aggregate(total=Sum('quantity'))['total'] or 0
        ),
        'total_sold': (
            SMTBSaleItem.objects
            .filter(restock__category=category)
            .aggregate(total=Sum('quantity'))['total'] or 0
        ),
        'current_stock': stock,
        'stock_value': stock * category.standard_price,
    }