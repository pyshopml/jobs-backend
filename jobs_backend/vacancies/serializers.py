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

    def _create_query(self, validated_data):
        search_text = validated_data.get('phrase')
        sections = validated_data.get('section', set())
        if SearchSerializer.ANY in sections or not sections:
            sections = self.search_sections
        queries = [Q(**{'{}__icontains'.format(field): search_text}) for field in sections]
        query = reduce(operator.or_, queries)
        return query

    def create(self, validated_data):
        return self._create_query(validated_data)


class SortSerializer(serializers.Serializer):
    """
    Sort vacancy queryset serializer
    """
    UPDATE = 'modified_on'
    SALARY_MIN = 'salary_min'
    SALARY_MAX = 'salary_max'
    DISTANCE = 'distance'
    sort_fields = [
        (UPDATE, 'last update'),
        (SALARY_MIN, 'salary from'),
        (SALARY_MAX, 'salary to'),
    ]

    ASC = 'asc'
    DESC = 'desc'
    ordering_direction = [
        (ASC, 'asc'),
        (DESC, 'desc')
    ]
    order = serializers.ChoiceField(choices=ordering_direction, label='sort order',
                                    help_text='increase decrease', default=ASC)
    sort_field = serializers.ChoiceField(choices=sort_fields, label='Sort by')

    def _create_sort_param(self, validated_data):
        order = validated_data.get('order')
        sort_field = validated_data.get('sort_field')
        if order == self.DESC:
            sort_field = '-{}'.format(sort_field)
        return sort_field

    def create(self, validated_data):
        return self._create_sort_param(validated_data)
