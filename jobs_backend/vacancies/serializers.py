import operator
from functools import reduce

from django.db.models import Q
from rest_framework import serializers

from .models import Tag, Category, Vacancy


class KeywordsField(serializers.StringRelatedField):
    """
    Representation `keywords` field of the vacancy model
    """

    def to_internal_value(self, data):
        tag, created = Tag.objects.get_or_create(title=data)
        return tag


class CategoryField(serializers.RelatedField):
    """
    Representation `category` field of the vacancy model
    """
    queryset = Category.objects.all()

    def to_representation(self, value):
        ret = []
        while value:
            ret.append({'id': value.id, 'title': value.title})
            value = value.parent

        return ret

    def to_internal_value(self, data):
        try:
            category = self.queryset.get(id=data)
        except Category.DoesNotExist:
            return None

        return category


class LocationField(serializers.DictField):
    """
    Representation `location` field
    """
    city = serializers.CharField(max_length=128)
    country = serializers.CharField(max_length=128)


class VacancySerializer(serializers.ModelSerializer):
    """
    Common vacancy model serializer
    """
    keywords = KeywordsField(many=True)
    category = CategoryField()
    location = LocationField(required=False)

    class Meta:
        model = Vacancy
        fields = (
            'id', 'url', 'title', 'description', 'salary_min', 'salary_max',
            'location', 'keywords', 'busyness', 'remote_work', 'category',
            'created_on', 'modified_on'
        )
        extra_kwargs = {
            'url': {'view_name': 'api:vacancies:vacancy-detail',
                    'read_only': True}
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
