from django.db import models

# Create your models here.

class SuggestionBase(models.Model):
    """Abstract base class for all suggestion models"""
    validated = models.BooleanField(default=False)
    validated_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=20, choices=[
        ('user', 'User'),
        ('ai', 'AI'),
        ('system', 'System'),
        ('seed', 'Seed Data'),
    ], default='user')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

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

class Skill(SuggestionBase):
    SKILL_CATEGORIES = [
        ('technical', 'Technical'),
        ('soft', 'Soft'),
        ('language', 'Language'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES, default='other')

    def __str__(self):
        return self.name

class JobTitle(SuggestionBase):
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
    responsibilities = models.ManyToManyField(Responsibility, related_name="jobs", blank=True)
    skills = models.ManyToManyField(Skill, related_name="jobs", blank=True)

    def __str__(self):
        return self.title

class Country(SuggestionBase):
    name = models.CharField(max_length=100)
    capital = models.CharField(max_length=100, null=True, blank=True)
    country_code = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.name

class State(SuggestionBase):
    name = models.CharField(max_length=100)
    capital = models.CharField(max_length=100, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')

    def __str__(self):
        return f"{self.name}, {self.country.name}."

class City(SuggestionBase):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return f"{self.name} {self.state}"
   
class Institution(SuggestionBase):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='institutions')

    def __str__(self):
        return f"{self.name}, {self.country}"
    
class Certification(SuggestionBase):
    name = models.CharField(max_length=100)
    issuer = models.CharField(max_length=100, blank=True)  # Issuing organization
    job_titles = models.ManyToManyField(JobTitle, related_name='certifications')

    def __str__(self):
        return self.name

class FieldOfStudy(SuggestionBase):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title
class Degree(SuggestionBase):
    title = models.CharField(max_length=120)
    abbr = models.CharField(max_length=20, blank=True, null=True)  # std abbreviation
    fields_of_study = models.ManyToManyField(FieldOfStudy, related_name='degrees')

    def __str__(self):
        return self.title

class ExperienceDescription(SuggestionBase):
    description = models.TextField()
    job_titles = models.ManyToManyField(JobTitle, related_name='experience_descriptions')

    def __str__(self):
        return self.description

class ExperienceAchievement(SuggestionBase):
    achievement = models.TextField()
    description = models.ForeignKey(ExperienceDescription, related_name='achievements', on_delete=models.CASCADE)
    job_title = models.ForeignKey(JobTitle, related_name='achievements', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.achievement

class Industry(SuggestionBase):
    title = models.CharField(max_length=100)
    job_titles = models.ManyToManyField(JobTitle, related_name='industries')

    def __str__(self):
        return self.title

class Company(SuggestionBase):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='companies')
    industry = models.ManyToManyField(Industry, related_name='companies')

    def __str__(self):
        return f"{self.name}, {self.country}"

class ProfessionalRelationship(SuggestionBase):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Application(SuggestionBase):
    """Software projects using technologies as building tools"""    
    title = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

class Technology(SuggestionBase):
    """Tools used in buiding applications"""
    CATEGORY_CHOICES = [
        ('language', 'Programming Language'),
        ('framework', 'Framework'),
        ('library', 'Library'),
        ('database', 'Database'),
        ('cloud', 'Cloud Platform'),
        ('devops', 'DevOps & CI/CD'),
        ('tool', 'Tool / Utility'),
        ('platform', 'Platform'),
        ('design', 'Design Tool'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    applications = models.ManyToManyField(Application, related_name='technologies')
    related_technologies = models.ManyToManyField('self',symmetrical=True,blank=True)


    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class Location(SuggestionBase):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='locations')

    def __str__(self):
        return f"{self.name} in {self.city}"
class JobTitleAudit(models.Model):
    job = models.ForeignKey(JobTitle, on_delete=models.CASCADE, related_name='audits')
    user_id = models.IntegerField(null=True)  # optional
    action = models.CharField(max_length=50)  # created / ai_generated / updated_by_user
    payload = models.JSONField() # store the changes made
    created_at = models.DateTimeField(auto_now_add=True)
