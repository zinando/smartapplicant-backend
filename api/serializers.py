# api/serializers.py
from rest_framework import serializers
from .models import GeneralData, JobTitle, Responsibility, Skill

class GeneralDataSerializer(serializers.Serializer):
    class Meta:
        model = GeneralData()
        fields = '__all__'

class ResponsibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsibility
        fields = '__all__'

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class JobTitleSerializer(serializers.ModelSerializer):
    responsibilities = ResponsibilitySerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    class Meta:
        model = JobTitle
        fields = '__all__'