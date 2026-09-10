from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from smtb.models import SMTBCustomer, FulfillmentMethod, SMTBOrder, OrderStatus
from smtb.services.orders import (create_order, mark_order_paid, start_order_processing,
                                  mark_order_shipped, mark_ready_for_pickup, complete_order)
from smtb.services.delivery import get_delivery_charge, determine_delivery_type
from api.models import Country, State, City, Location

from smtb.services.products import (
    check_product_availability,
    get_product_details,
)


class SMTBLocationAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        country_name = request.query_params.get('country')
        state_name = request.query_params.get('state')
        city_name = request.query_params.get('city')
        location_name = request.query_params.get('location')

        data = {
            'countries': [],
            'states': [],
            'cities': [],
            'locations': [],
        }

        # No filters → return active countries
        if not country_name:
            data['countries'] = list(
                Country.objects.filter(is_active=True)
                .values('id', 'name', 'country_code')
            )

            return Response({
                'status': 1,
                'data': data,
                'message': 'success',
            })

        # Country
        country = Country.objects.filter(
            name__iexact=country_name.strip(),
            is_active=True,
        ).first()

        if not country:
            return Response({
                'status': 0,
                'message': 'Country not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        data['country'] = {
            'id': country.id,
            'name': country.name,
            'country_code': country.country_code,
        }

        # No state supplied → return states
        if not state_name:
            data['states'] = list(
                State.objects.filter(
                    country=country,
                    is_active=True,
                )
                .values('id', 'name')
            )

            return Response({
                'status': 1,
                'data': data,
                'message': 'success',
            })

        # State
        state_obj = State.objects.filter(
            country=country,
            name__iexact=state_name.strip(),
            is_active=True,
        ).first()

        if not state_obj:
            return Response({
                'status': 0,
                'message': 'State not found in the specified country.',
            }, status=status.HTTP_404_NOT_FOUND)

        data['state'] = {
            'id': state_obj.id,
            'name': state_obj.name,
        }

        # No city supplied → return cities
        if not city_name:
            data['cities'] = list(
                City.objects.filter(
                    state=state_obj,
                    is_active=True,
                )
                .values('id', 'name')
            )

            return Response({
                'status': 1,
                'data': data,
                'message': 'success',
            })

        # City
        city_obj = City.objects.filter(
            state=state_obj,
            name__iexact=city_name.strip(),
            is_active=True,
        ).first()

        if not city_obj:
            return Response({
                'status': 0,
                'message': 'City not found in the specified state.',
            }, status=status.HTTP_404_NOT_FOUND)

        data['city'] = {
            'id': city_obj.id,
            'name': city_obj.name,
        }

        # No location supplied → return locations
        if not location_name:
            data['locations'] = list(
                Location.objects.filter(
                    city=city_obj,
                    is_active=True,
                )
                .values('id', 'name')
            )

            return Response({
                'status': 1,
                'data': data,
                'message': 'success',
            })

        # Location
        location_obj = Location.objects.filter(
            city=city_obj,
            name__iexact=location_name.strip(),
            is_active=True,
        ).first()

        if not location_obj:
            return Response({
                'status': 0,
                'data': data,
                'message': 'Location not found in the specified city.',
            }, status=status.HTTP_404_NOT_FOUND)

        data['location'] = {
            'id': location_obj.id,
            'name': location_obj.name,
        }

        return Response({
            'status': 1,
            'data': data,
            'message': 'success',
        })

class SMTBDeliveryChargeAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        try:            
            country_id = request.data.get('country_id')
            state_id = request.data.get('state_id')
            city_id = request.data.get('city_id')
            location_id = request.data.get('location_id')

            delivery_type = determine_delivery_type(
                country_id=country_id,
                state_id=state_id
            )

            # Resolve IDs → canonical names
            country = Country.objects.get(
                id=country_id,
                is_active=True
            )

            state = None
            city = None
            location = None

            if state_id:
                state = State.objects.get(
                    id=state_id,
                    country=country,
                    is_active=True
                )

            if city_id:
                city = City.objects.get(
                    id=city_id,
                    state=state,
                    is_active=True
                )

            if location_id:
                location = Location.objects.get(
                    id=location_id,
                    city=city,
                    is_active=True
                )

            fee = get_delivery_charge(
                delivery_type=delivery_type,
                country=country.name,
                state=state.name if state else None,
                city=city.name if city else None,
                location=location.name if location else None,
            )

            return Response({
                "status": 1,
                "delivery_type": delivery_type,
                "fee_found": fee is not None,
                "delivery_fee": fee,
                "message": "success"
            })

        except (Country.DoesNotExist, State.DoesNotExist,
                City.DoesNotExist, Location.DoesNotExist):
            return Response({
                "status": 0,
                "message": "Invalid location selection."
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'status': 0,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class SMTBOrderPaymentAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            payment_method = request.data.get("payment_method")
            if not payment_method:
                return Response(
                    {
                        "status": 0,
                        "message": "Payment method is required."
                    },
                    status=400,
                )
            order = SMTBOrder.objects.get(id=order_id)

            order = mark_order_paid(order, payment_method)

            return Response({
                'status': 1,
                'order_id': order.id,
                'status': order.status,
                'message': 'Payment confirmed successfully.'
            })

        except SMTBOrder.DoesNotExist:
            return Response({
                'status': 0,
                'message': 'Order not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        except ValueError as e:
            return Response({
                'status': 0,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class SMTBCreateOrderAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = (
            SMTBOrder.objects
            .select_related(
                "customer",
                "delivery_country",
                "delivery_state",
                "delivery_city",
                "delivery_location",
            )
            .order_by("-created_at")
        )

        status_filter = request.query_params.get("status")

        if status_filter:
            if status_filter not in OrderStatus.values:
                return Response({
                    "status": 0,
                    "message": "Invalid order status."
                }, status=400)

            orders = orders.filter(status=status_filter)

        data = []

        for order in orders:
            data.append({
                "order_id": order.id,
                "customer": {
                    "name": order.customer.name,
                    "phone": order.customer.phone,
                },
                "status": order.status,
                "fulfillment_method": order.fulfillment_method,
                "delivery_type": order.delivery_type,
                "delivery_fee": order.delivery_fee,
                "created_at": order.created_at,
            })

        return Response({
            "status": 1,
            "count": len(data),
            "data": data,
            "message": "success",
        })

    def post(self, request):
        try:
            name = request.data.get('name', '').strip()
            phone = request.data.get('phone', '').strip()
            product_ids = request.data.get('product_ids', [])
            fulfillment_method = request.data.get('fulfillment_method')

            if not name or not phone:
                raise ValueError("Customer name and phone are required.")

            if not product_ids:
                raise ValueError("At least one product is required.")

            if fulfillment_method not in FulfillmentMethod.values:
                raise ValueError("Invalid fulfillment method.")

            customer, _ = SMTBCustomer.objects.get_or_create(
                phone=phone,
                defaults={'name': name}
            )

            # Update name if the customer already exists
            if customer.name != name:
                customer.name = name
                customer.save(update_fields=['name'])

            order = create_order(
                customer=customer,
                product_ids=product_ids,
                fulfillment_method=fulfillment_method,
                country_id=request.data.get("country_id"),
                state_id=request.data.get("state_id"),
                city_id=request.data.get("city_id"),
                location_id=request.data.get("location_id"),
                delivery_address=request.data.get("delivery_address"),
            )

            return Response({
                "status": 1,
                "order_id": order.id,
                "delivery_type": order.delivery_type,
                "delivery_fee": order.delivery_fee,
                "message": "Order created successfully."
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'status': 0,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class SMTBProductAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        result = check_product_availability(product_id)

        if not result['available']:
            return Response(
                {
                    'status': 0,
                    'message': result['message'],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                'status': 1,
                'data': get_product_details(product_id),
                'message': 'success',
            },
            status=status.HTTP_200_OK,
        )

class SMTBOrderProcessAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = SMTBOrder.objects.get(id=order_id)

            order = start_order_processing(order)

            return Response({
                "status": 1,
                "order_id": order.id,
                "status": order.status,
                "message": "Order moved to processing."
            })

        except SMTBOrder.DoesNotExist:
            return Response({
                "status": 0,
                "message": "Order not found."
            }, status=status.HTTP_404_NOT_FOUND)

        except ValueError as e:
            return Response({
                "status": 0,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class SMTBOrderShipAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = SMTBOrder.objects.get(id=order_id)

            order = mark_order_shipped(order)

            return Response({
                "status": 1,
                "order_id": order.id,
                "status": order.status,
                "message": "Order marked as shipped."
            })

        except SMTBOrder.DoesNotExist:
            return Response({
                "status": 0,
                "message": "Order not found."
            }, status=404)

        except ValueError as e:
            return Response({
                "status": 0,
                "message": str(e)
            }, status=400)

class SMTBOrderReadyForPickupAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = SMTBOrder.objects.get(id=order_id)

            order = mark_ready_for_pickup(order)

            return Response({
                "status": 1,
                "order_id": order.id,
                "status": order.status,
                "message": "Order is ready for pickup."
            })

        except SMTBOrder.DoesNotExist:
            return Response({
                "status": 0,
                "message": "Order not found."
            }, status=404)

        except ValueError as e:
            return Response({
                "status": 0,
                "message": str(e)
            }, status=400)
        
class SMTBOrderCompleteAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = SMTBOrder.objects.get(id=order_id)

            order = complete_order(order)

            return Response({
                "status": 1,
                "order_id": order.id,
                "status": order.status,
                "message": "Order completed successfully."
            })

        except SMTBOrder.DoesNotExist:
            return Response({
                "status": 0,
                "message": "Order not found."
            }, status=404)

        except ValueError as e:
            return Response({
                "status": 0,
                "message": str(e)
            }, status=400)

class SMTBOrderDetailAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = (
                SMTBOrder.objects
                .select_related(
                    "customer",
                    "delivery_country",
                    "delivery_state",
                    "delivery_city",
                    "delivery_location",
                    "sale",
                )
                .prefetch_related(
                    "items__advertised_product"
                )
                .get(id=order_id)
            )

            items = []

            for item in order.items.all():
                product = item.advertised_product

                items.append({
                    "product_id": product.product_id,
                    "description": product.description,
                    "sales_price": item.sales_price,
                })

            product_total = sum(
                item["sales_price"] for item in items
            )

            delivery_fee = order.delivery_fee or 0
            grand_total = product_total + delivery_fee

            return Response({
                "status": 1,
                "data": {
                    "order_id": order.id,

                    "customer": {
                        "name": order.customer.name,
                        "phone": order.customer.phone,
                    },

                    "status": order.status,
                    "fulfillment_method": order.fulfillment_method,

                    "delivery": {
                        "type": order.delivery_type,
                        "country": (
                            order.delivery_country.country_code
                            if order.delivery_country else None
                        ),
                        "state": (
                            order.delivery_state.name
                            if order.delivery_state else None
                        ),
                        "city": (
                            order.delivery_city.name
                            if order.delivery_city else None
                        ),
                        "location": (
                            order.delivery_location.name
                            if order.delivery_location else None
                        ),
                        "address": order.delivery_address,
                        "fee": order.delivery_fee,
                    },

                    "items": items,

                    "totals": {
                        "products": product_total,
                        "delivery": delivery_fee,
                        "grand_total": grand_total,
                    },

                    "payment": {
                        "status": (
                            order.sale.payment_status
                            if hasattr(order, "sale")
                            else None
                        ),
                        "method": (
                            order.sale.payment_method
                            if hasattr(order, "sale")
                            else None
                        ),
                    },
                },
                "message": "success",
            })

        except SMTBOrder.DoesNotExist:
            return Response({
                "status": 0,
                "message": "Order not found.",
            }, status=404)

