from django.urls import path
from .api import (SMTBProductAPIView, SMTBCreateOrderAPIView, SMTBOrderPaymentAPIView,
    SMTBDeliveryChargeAPIView, SMTBLocationAPIView, SMTBOrderCompleteAPIView, SMTBOrderProcessAPIView,
    SMTBOrderReadyForPickupAPIView, SMTBOrderShipAPIView, SMTBOrderDetailAPIView)


urlpatterns = [
    path(
        'products/<str:product_id>/',
        SMTBProductAPIView.as_view(),
        name='smtb-product',
    ),
    path(
        'orders/',
        SMTBCreateOrderAPIView.as_view(),
        name='smtb-create-order',
    ),
    path(
        'orders/<int:order_id>/payment/',
        SMTBOrderPaymentAPIView.as_view(),
        name='smtb-order-payment',
    ),
    path(
        'delivery-charge/',
        SMTBDeliveryChargeAPIView.as_view(),
        name='smtb-delivery-charge',
    ),
    path(
        'locations/',
        SMTBLocationAPIView.as_view(),
        name='smtb-locations',
    ),
    path(
        "orders/<int:order_id>/process/",
        SMTBOrderProcessAPIView.as_view()
    ),

    path(
        "orders/<int:order_id>/ship/",
        SMTBOrderShipAPIView.as_view()
    ),

    path(
        "orders/<int:order_id>/ready-for-pickup/",
        SMTBOrderReadyForPickupAPIView.as_view()
    ),

    path(
        "orders/<int:order_id>/complete/",
        SMTBOrderCompleteAPIView.as_view()
    ),
    path(
        "orders/<int:order_id>/",
        SMTBOrderDetailAPIView.as_view()
    ),
]