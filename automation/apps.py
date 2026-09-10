from django.apps import AppConfig
from django.core.cache import cache
import logging


class AutomationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'automation'

    def ready(self):
        # This runs once when Django starts
        # if not cache.get("startup_flag"):
        # logging.info("Setting up initial cache values on startup.")
        # cache.clear()
        self.save_admin_contacts_to_cache()
        # cache.set("startup_flag", True, timeout=None)
        # pass
    
    def save_admin_contacts_to_cache(self):
        from .models import Tenant
        tenants = Tenant.objects.all()
        for tenant in tenants:
            biz_info = tenant.business_details or {}
            if biz_info:
                admin_contacts = [
                    value for key, value in
                    biz_info.get("admin_contacts", {}).items()]
                if admin_contacts:
                    key = f"{tenant.waba_phone_number_id}_admin_contacts"
            
                    cache.set(key, list(set(admin_contacts)), timeout=None)
                    logging.info("Admin contacts saved to cache for tenant: %s", tenant.waba_phone_number_id)

    
