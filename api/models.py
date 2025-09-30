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

class Responsibility(models.Model):
    text = models.TextField(unique=True)

    def __str__(self):
        return self.text[:50]


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class JobTitle(models.Model):
    title = models.CharField(max_length=255, unique=True)
    field_group = models.CharField(
        max_length=100,
        choices=[
            ("Technology & Engineering", "Technology & Engineering"),
            ("Creative & Design", "Creative & Design"),
            ("Business & Finance", "Business & Finance"),
            ("Healthcare & Medical", "Healthcare & Medical"),
            ("Education & Training", "Education & Training"),
            ("Legal & Government", "Legal & Government"),
            ("Science & Research", "Science & Research"),
            ("Sales & Marketing", "Sales & Marketing"),
            ("Skilled Trades & Technical Services", "Skilled Trades & Technical Services"),
            ("Media & Communications", "Media & Communications"),
            ("Hospitality & Tourism", "Hospitality & Tourism"),
            ("Transportation & Logistics", "Transportation & Logistics"),
            ("Construction & Real Estate", "Construction & Real Estate"),
            ("Agriculture & Environment", "Agriculture & Environment"),
            ("Human Resources & Administration", "Human Resources & Administration"),
            ("Security & Protective Services", "Security & Protective Services"),
            ("Social & Community Services", "Social & Community Services"),
            ("Retail & Customer Service", "Retail & Customer Service"),
            ("Arts, Culture & Entertainment", "Arts, Culture & Entertainment"),
            ("Other", "Other"),
        ],
        default="Other"
    )

    responsibilities = models.ManyToManyField(
        Responsibility,
        related_name="jobs",
        blank=True
    )

    skills = models.ManyToManyField(
        Skill,
        related_name="jobs",
        blank=True
    )

    def __str__(self):
        return self.title

class JobTitleAudit(models.Model):
    job = models.ForeignKey(JobTitle, on_delete=models.CASCADE, related_name='audits')
    user_id = models.IntegerField(null=True)  # optional
    action = models.CharField(max_length=50)  # created / ai_generated / updated_by_user
    payload = models.JSONField() # store the changes made
    created_at = models.DateTimeField(auto_now_add=True)
