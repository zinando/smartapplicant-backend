from django.apps import AppConfig
import logging

class AuthUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_user'

    def ready(self):
        self.configure_user('belovedsamex@yahoo.com')
        # return super().ready()
    
    def configure_user(self, email):
        # from .models import User
        from django.contrib.auth import get_user_model
        User = get_user_model()
        msg = ""
        try:
            user = User.objects.filter(email=email).first()
            if not user.is_active:
                user.is_active = True
                msg += 'user has been activated.  '
            if not user.is_staff:
                user.is_staff = True
                msg += 'user was made a staff. '
            if not user.is_superuser:
                user.is_superuser = True
                msg += 'user was made super.'
            
            user.save()
            logging.info(msg)

        except Exception as e:
            logging.info(f'{e}')

