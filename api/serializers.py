# api/serializers.py
from rest_framework import serializers
from .models import GeneralData

class GeneralDataSerializer(serializers.Serializer):
    class Meta:
        model = GeneralData()
        fields = '__all__'