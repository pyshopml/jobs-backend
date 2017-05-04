import operator
from functools import reduce

from django.db.models import Q
from rest_framework import serializers

from .models import Vacancy


class VacancySerializer(serializers.ModelSerializer):
    """
    Common vacancy model serializer
    """

    class Meta:
        model = Vacancy
        fields = (
            'id', 'url', 'title', 'description', 'created_on', 'modified_on'
        )
        extra_kwargs = {
            'url': {'view_name': 'api:vacancies:vacancy-detail', 'read_only': True}
        }


class SearchSerializer(serializers.Serializer):
    """
    Search words serializer
    """

    TITLE = 'title'
    DESCRIPTION = 'description'
    search_sections = (TITLE, DESCRIPTION)
    ANY = 'anywhere'
    search_sections_param = [
        (TITLE, 'title'),
        (DESCRIPTION, 'description'),
        (ANY, 'anywhere')
    ]

    phrase = serializers.CharField(min_length=3, max_length=50, label='Search phrase', help_text='min 3 chars, max 50')
    section = serializers.MultipleChoiceField(choices=search_sections_param, label='Search in')

    @staticmethod
    def validate_section(value):
        """
        Check on empty set in multiplechoise field.
        """
        if not value:
            raise serializers.ValidationError('Choise search section must be set!')
        return value

    @staticmethod
    def _create_query(search_text, sections):
        queries = [Q(**{'{}__icontains'.format(field): search_text}) for field in sections]
        query = reduce(operator.or_, queries)
        return query

    def create(self, validated_data):
        search_text = self.validated_data.get('phrase')
        sections = self.validated_data.get('section', set())
        sections = self.search_sections if SearchSerializer.ANY in sections or not sections else sections
        return self._create_query(search_text, sections)
