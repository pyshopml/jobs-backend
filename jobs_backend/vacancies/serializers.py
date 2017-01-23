from rest_framework import serializers

from .models import Vacancy


class VacancySerializer(serializers.HyperlinkedModelSerializer):
    """
    Common vacancy model serializer
    """
    class Meta:
        model = Vacancy
        fields = (
            'id', 'url', 'title', 'description', 'created_on', 'modified_on'
        )
        extra_kwargs = {
            'url': {'view_name': 'vacancies:vacancy-detail', 'read_only': True}
        }
