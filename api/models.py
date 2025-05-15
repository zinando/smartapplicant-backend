from django.db import models

# Create your models here.
class GeneralData(models.Model):
    """This model stores genral data used for statistics purpose"""
    ats_score = models.JSONField(null=True)
    registered_users = models.IntegerField()
    premium_users = models.IntegerField()
    currently_online = models.IntegerField()

    def __str__(self):
        return f"There are currently {self.currently_online} users online."