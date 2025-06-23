from datetime import datetime, timedelta
from django.utils import timezone
from typing import List, Dict
from auth_user.models import Order, Subscription, SubscriptionType
from django.db.models import Sum, Count, Q
from django.db.models import Min
from django.contrib.auth import get_user_model

User = get_user_model()

class RevenueAnalytics:
    def __init__(self, duration_days: int = 30):
        """
        Initialize RevenueAnalytics with flexible duration:
        - 0: from start of year
        - 1: all-time
        - X: last X days
        """
        self.duration_days = duration_days
        self.end_date = timezone.now()

        if self.duration_days == 0:
            self.start_date = self.end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif self.duration_days == 1:
            # Use safe "early" aware datetime
            self.start_date = timezone.make_aware(datetime(2000, 1, 1))
        else:
            self.start_date = self.end_date - timedelta(days=duration_days)
    
    def _get_orders_queryset(self):
        """Get filtered orders queryset for the analysis period."""
        return Order.objects.filter(
            created_at__gte=self.start_date,
            created_at__lte=self.end_date,
            delete_flag=False
        )
    
    def get_total_revenue(self) -> float:
        """Calculate total revenue from paid orders."""
        return self._get_orders_queryset().filter(
            payment_status=Order.PaymentStatus.PAID
        ).aggregate(total=Sum('total'))['total'] or 0
    
    def get_revenue_by_type(self) -> Dict[str, float]:
        """Calculate revenue by order type (credit vs subscription)."""
        result = self._get_orders_queryset().filter(
            payment_status=Order.PaymentStatus.PAID
        ).values('order_type').annotate(
            total=Sum('total')
        )
        return {item['order_type']: item['total'] for item in result}
    
    def get_credit_purchase_stats(self) -> Dict:
        """Get statistics for credit purchases."""
        credit_orders = self._get_orders_queryset().filter(
            order_type=Order.OrderType.CREDIT,
            payment_status=Order.PaymentStatus.PAID
        )
        
        total_revenue = credit_orders.aggregate(total=Sum('total'))['total'] or 0
        total_credits = credit_orders.aggregate(total=Sum('quantity'))['total'] or 0
        avg_price_per_credit = total_revenue / total_credits if total_credits else 0
        
        return {
            'total_revenue': total_revenue,
            'total_credits': total_credits,
            'avg_price_per_credit': avg_price_per_credit,
            'order_count': credit_orders.count()
        }
    
    def get_subscription_stats(self) -> Dict:
        """Get statistics for subscriptions."""
        sub_orders = self._get_orders_queryset().filter(
            # order_type=Order.OrderType.SUBSCRIPTION,
            payment_status=Order.PaymentStatus.PAID
        )
        
        total_revenue = sub_orders.aggregate(total=Sum('total'))['total'] or 0

        # Group by plan and sum revenue
        sub_plan_revenue = sub_orders.values('subscription__subscription_type__name').annotate(
            total=Sum('total')
        )
        by_plan = {item['subscription__subscription_type__name'] or 'resum_credit': item['total'] for item in sub_plan_revenue}

        # Sort by revenue descending
        by_plan = dict(sorted(by_plan.items(), key=lambda item: item[1], reverse=True))

        # Calculate percentage share
        total_plan_revenue = sum(by_plan.values())
        by_plan = {
            plan: {
                'revenue': revenue,
                'percentage': (revenue / total_plan_revenue * 100) if total_plan_revenue else 0
            }
            for plan, revenue in by_plan.items()
        }

        # get 

        order_count = sub_orders.count()

        return {
            "total_revenue": total_revenue,
            "order_count": order_count,
            "avg_order_value": total_revenue / order_count if order_count else 0,
            "by_plan": by_plan
        }

    def get_total_users(self) -> int:
        """Get all registered users that are active."""
        return User.objects.filter(is_active=True).count()
    
    def get_payment_method_distribution(self) -> Dict[str, float]:
        """Get revenue distribution by payment method."""
        result = self._get_orders_queryset().filter(
            payment_status=Order.PaymentStatus.PAID
        ).values('payment_method').annotate(
            total=Sum('total'),
            count=Count('id')
        )
        
        return {
            'revenue': {item['payment_method']: item['total'] for item in result},
            'count': {item['payment_method']: item['count'] for item in result}
        }
    
    def get_active_users(self) -> int:
        """Count unique users with paid orders."""
        return self._get_orders_queryset().filter(
            payment_status=Order.PaymentStatus.PAID
        ).values('user').distinct().count()
    
    def get_conversion_rate(self) -> float:
        """Calculate conversion rate (paid orders / total orders)."""
        total_orders = self._get_orders_queryset().count()
        paid_orders = self._get_orders_queryset().filter(
            payment_status=Order.PaymentStatus.PAID
        ).count()
        
        return (paid_orders / total_orders) * 100 if total_orders else 0
    
    def get_recent_orders(self, limit: int = 10) -> List[Dict]:
        """Get most recent paid orders with relevant details."""
        return list(
            self._get_orders_queryset().filter(
                payment_status=Order.PaymentStatus.PAID
            ).select_related('user').order_by('-created_at')[:limit].values(
                'order_number',
                'created_at',
                'total',
                'order_type',
                'payment_method',
                'user__email',
                'payment_status',
                'user__first_name',
                'quantity',
                'subscription__subscription_type__name',
                'user__last_name'
            )
        )
    
    def get_growth_rates(self, previous_period_days: int = 30) -> Dict[str, float]:
        """
        Calculate growth rates compared to previous period.
        
        Args:
            previous_period_days: Number of days in the comparison period (default 30)
        """
        current_data = self.get_dashboard_data()
        
        # Get previous period data
        previous_end = self.start_date
        previous_start = previous_end - timedelta(days=previous_period_days)
        
        previous_orders = Order.objects.filter(
            created_at__gte=previous_start,
            created_at__lte=previous_end,
            delete_flag=False,
            payment_status=Order.PaymentStatus.PAID
        )
        
        previous_total = previous_orders.aggregate(total=Sum('total'))['total'] or 0
        previous_credit = previous_orders.filter(
            order_type=Order.OrderType.CREDIT
        ).aggregate(total=Sum('total'))['total'] or 0
        previous_sub = previous_orders.filter(
            order_type=Order.OrderType.SUBSCRIPTION
        ).aggregate(total=Sum('total'))['total'] or 0
        previous_users = previous_orders.values('user').distinct().count()
        
        def calc_growth(current, previous):
            return ((current - previous) / previous * 100) if previous else 0
        
        return {
            'total_revenue': calc_growth(current_data['total_revenue'], previous_total),
            'credit_purchases': calc_growth(current_data['credit_purchases']['total_revenue'], previous_credit),
            'subscriptions': calc_growth(current_data['subscriptions']['total_revenue'], previous_sub),
            'active_users': calc_growth(current_data['active_users'], previous_users)
        }
    
    def get_growth_rates_from_values(self, total_revenue, credit_stats, sub_stats, active_users) -> Dict[str, float]:
        """
        Calculate growth rates using already-computed current values.
        """
        previous_end = self.start_date
        previous_start = previous_end - timedelta(days=self.duration_days)

        previous_orders = Order.objects.filter(
            created_at__gte=previous_start,
            created_at__lte=previous_end,
            delete_flag=False,
            payment_status=Order.PaymentStatus.PAID
        )

        previous_total = previous_orders.aggregate(total=Sum('total'))['total'] or 0
        previous_credit = previous_orders.filter(
            order_type=Order.OrderType.CREDIT
        ).aggregate(total=Sum('total'))['total'] or 0
        previous_sub = previous_orders.filter(
            order_type=Order.OrderType.SUBSCRIPTION
        ).aggregate(total=Sum('total'))['total'] or 0
        previous_users = previous_orders.values('user').distinct().count()

        def calc_growth(current, previous):
            return ((current - previous) / previous * 100) if previous else 0

        return {
            'total_revenue': calc_growth(total_revenue, previous_total),
            'credit_purchases': calc_growth(credit_stats['total_revenue'], previous_credit),
            'subscriptions': calc_growth(sub_stats['total_revenue'], previous_sub),
            'active_users': calc_growth(active_users, previous_users)
        }
    
    def get_mrr_breakdown(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate MRR breakdown for new, expansion, and churned subscriptions.
        Returns a dictionary with amount and percent change over the previous period.
        Also includes total MRR and optional breakdown by month.
        """

        today = timezone.now().date()
        first_day_this_month = today.replace(day=1)
        first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)

        # Subscriptions active before this month
        current_subs = Subscription.objects.filter(
            start_date__lt=first_day_this_month,
            expiry_date__isnull=True  # active
        ).select_related('subscription_type')

        previous_subs = Subscription.objects.filter(
            start_date__lt=first_day_last_month + timedelta(days=31),
            expiry_date__isnull=True
        ).select_related('subscription_type')

        # user_id → price
        current_mrr_map = {
            sub.user_id: sub.subscription_type.price for sub in current_subs
        }

        previous_mrr_map = {
            sub.user_id: sub.subscription_type.price for sub in previous_subs
        }

        # New MRR
        new_mrr = sum(
            price for user_id, price in current_mrr_map.items() if user_id not in previous_mrr_map
        )

        # Expansion MRR
        expansion_mrr = sum(
            current_mrr_map[user_id] - previous_mrr_map[user_id]
            for user_id in current_mrr_map
            if user_id in previous_mrr_map and current_mrr_map[user_id] > previous_mrr_map[user_id]
        )

        # Churned MRR
        churned_mrr = sum(
            price for user_id, price in previous_mrr_map.items() if user_id not in current_mrr_map
        )

        previous_total_mrr = sum(previous_mrr_map.values())

        def percent_change(amount):
            return (amount / previous_total_mrr * 100) if previous_total_mrr else 0

        total_mrr = sum(current_mrr_map.values())

        result = {
            "new": {
                "amount": float(new_mrr),
                "percent": round(percent_change(new_mrr), 2)
            },
            "expansion": {
                "amount": float(expansion_mrr),
                "percent": round(percent_change(expansion_mrr), 2)
            },
            "churned": {
                "amount": float(churned_mrr),
                "percent": round(-percent_change(churned_mrr), 2)
            },
            "total_mrr": float(total_mrr),
        }

        # ─────────────────────────────────────────────────────────────
        # Dynamic breakdown by time period
        if self.duration_days <= 30:
            # Only current month data
            result["months"] = [first_day_this_month.strftime('%b')]
            result["new_mrr_data"] = [float(new_mrr)]
        else:
            # Multi-month breakdown
            start_date = self.start_date.replace(day=1)
            months = []
            monthly_mrr = []

            date_cursor = start_date
            while date_cursor <= self.end_date:
                next_month = (date_cursor + timedelta(days=32)).replace(day=1)
                subs_in_month = Subscription.objects.filter(
                    start_date__gte=date_cursor,
                    start_date__lt=next_month,
                    subscription_type__isnull=False
                ).select_related('subscription_type')

                month_name = date_cursor.strftime('%b')
                months.append(month_name)
                monthly_mrr.append(float(sum(sub.subscription_type.price for sub in subs_in_month)))

                date_cursor = next_month

            result["months"] = months
            result["new_mrr_data"] = monthly_mrr

        return result

    def get_customer_acquisition(self, marketing_spend: float = 0.0) -> Dict[str, float]:
        """
        Calculate customer acquisition metrics:
        - Number of new paying customers during the analysis period
        - CAC = total marketing spend / new customers
        """
        # Get first order per user
        first_orders = (
            Order.objects.filter(
                payment_status=Order.PaymentStatus.PAID,
                delete_flag=False
            )
            .values('user')
            .annotate(first_order_date=Min('created_at'))
            .filter(first_order_date__gte=self.start_date, first_order_date__lte=self.end_date)
        )

        new_customers = len(first_orders)

        # group users by marketing channels
        market_channel_distribution_data = User.objects.filter(
            id__in=[x['user'] for x in first_orders]
        ).values('how_you_heard').annotate(count=Count('id'))

        # market_channel_distribution_data = User.objects.values('how_you_heard').annotate(count=Count('id'))


        market_channel_distribution = {
            x['how_you_heard'].lower(): x['count']
            for x in market_channel_distribution_data
        }

        cac = marketing_spend / new_customers if new_customers else 0

        return {
            "new_customers": new_customers,
            "cac": round(cac, 2),
            'channels': market_channel_distribution
        }

    def get_plan_performance(self) -> List[Dict[str, any]]:
        """
        Returns performance metrics per subscription plan.
        """
        # fetch all subscription types except 'resume_credits'
        plans = SubscriptionType.objects.exclude(name='resume_credit').all()
        results = []

        for plan in plans:
            print(f"Analyzing plan: {plan.name} (ID: {plan.id})")
            plan_subs = Subscription.objects.filter(
                subscription_type=plan
            ).select_related('user')

            active_subs = [plan_sub for plan_sub in plan_subs if plan_sub.is_active] #plan_subs.filter(is_active=True)
            total_subs = plan_subs.count()
            price = plan.price

            # MRR = price * active subscribers
            mrr = price * len(active_subs)

            # Average lifetime in months (for ended subscriptions)
            ended_subs = plan_subs.filter(expiry_date__isnull=False)
            lifetimes = [
                ((sub.expiry_date - sub.start_date).days / 30)
                for sub in ended_subs
            ]
            avg_lifetime = round(sum(lifetimes) / len(lifetimes), 2) if lifetimes else 0

            # Churn = % of subs that ended and did NOT renew
            churned = ended_subs.filter(is_renewed=False).count()
            churn_rate = round((churned / total_subs * 100), 2) if total_subs else 0

            # Renewal rate = % that did renew
            renewed = plan_subs.filter(is_renewed=True).count()
            renewal_rate = round((renewed / total_subs * 100), 2) if total_subs else 0

            # Optional: conversion = % of users who subscribed to this plan
            total_users = User.objects.count()
            converted_users = plan_subs.values('user').distinct().count()
            conversion_rate = round((converted_users / total_users * 100), 2) if total_users else 0

            results.append({
                "plan": plan.name,
                "subscribers": len(active_subs),
                "mrr": float(mrr),
                "avg_lifetime": avg_lifetime,
                "churn_rate": churn_rate,
                "conversion_rate": conversion_rate,
                "renewal_rate": renewal_rate
            })

        return results
    
    def get_dashboard_data(self) -> Dict:
        """Generate all data needed for the analytics dashboard."""
        total_revenue = self.get_total_revenue()
        credit_stats = self.get_credit_purchase_stats()
        sub_stats = self.get_subscription_stats()
        active_users = self.get_active_users()
        mmr_breakdown = self.get_mrr_breakdown()
        customer_acquisition = self.get_customer_acquisition()
        plan_performance = self.get_plan_performance()
        total_users = self.get_total_users()
        # conversion_rate = self.get_conversion_rate()
        # payment_methods = self.get_payment_method_distribution()
        recent_orders = self.get_recent_orders()
        
        # Now that we have current values, pass them to growth_rates
        growth_rates = self.get_growth_rates_from_values(
            total_revenue, credit_stats, sub_stats, active_users
        )

        return {
                "total_revenue": total_revenue,
                "credit_purchases": credit_stats,
                "subscriptions": sub_stats,
                "active_users": active_users,
                "total_users": total_users,
                "growth_rates": growth_rates,
                "recent_orders": recent_orders,
                "mrr_breakdown": mmr_breakdown,
                "customer_acquisition": customer_acquisition,
                "plan_performance": plan_performance,
                "currency": {"symbol": "₦", "code": "NGN"}
                }

