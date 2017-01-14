from rest_framework import serializers

from .models import Vacancy


class VacancySerializer(serializers.ModelSerializer):
    """
    Common vacancy model serializer
    """
    class Meta:
        model = Vacancy
        fields = ('id', 'title', 'description', 'created_on', 'modified_on')
