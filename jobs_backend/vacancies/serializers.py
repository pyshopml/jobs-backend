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
    DESC = 'description'
    search_sections = (TITLE, DESC)
    ANY = 'any'
    search_sections_param = [
        (TITLE, 'title'),
        (DESC, 'description'),
        (ANY, 'anywhere')
    ]

    phrase = serializers.CharField(min_length=3, max_length=50, label='Search phrase', help_text='min 3 chars, max 50')
    section = serializers.ChoiceField(choices=search_sections_param, label='Search in')

    # def create(self, validated_data):
    #     if SearchSerializer.ANY in validated_data.section:
    #
    #         return set(self.search_sections)
    #     else:
    #         return