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


class VacancySerializer(serializers.ModelSerializer):
    """
    Common vacancy model serializer
    """
    keywords = KeywordsField(many=True)
    category = CategoryField()

    class Meta:
        model = Vacancy
        fields = (
            'id', 'url', 'title', 'description', 'salary_min', 'salary_max',
            'keywords', 'busyness', 'remote_work', 'category', 'created_on',
            'modified_on'
        )
        extra_kwargs = {
            'url': {'view_name': 'api:vacancies:vacancy-detail',
                    'read_only': True}
        }
