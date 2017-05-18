from rest_framework import serializers

from cities.models import Country, City


class _LangAltNamesMixin(serializers.ModelSerializer):
    """
    Adds a field `alt_names` to the serializer as a list of values filtered by
    a parameter `lang`, if it is specified
    """
    alt_names = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.lang = kwargs.pop('lang')
        super().__init__(*args, **kwargs)

    def get_alt_names(self, obj):
        alt_names = obj.alt_names.all()
        if self.lang is not None:
            alt_names = obj.alt_names.filter(language_code=self.lang)

        return [alt_name.name for alt_name in alt_names]


class CountrySerializer(_LangAltNamesMixin, serializers.ModelSerializer):
    """
    Country model serializer
    """
    class Meta:
        model = Country
        fields = ('id', 'url', 'name', 'alt_names',)
        extra_kwargs = {
            'url': {'view_name': 'api:countries:country-detail',
                    'read_only': True}
        }


class CitySerializer(_LangAltNamesMixin, serializers.ModelSerializer):
    """
    City model serializer
    """
    country = serializers.StringRelatedField()
    region = serializers.StringRelatedField()
    subregion = serializers.StringRelatedField()

    class Meta:
        model = City
        fields = ('id', 'url', 'name', 'country', 'region', 'subregion',
                  'timezone', 'kind', 'alt_names',)
        extra_kwargs = {
            'url': {'view_name': 'api:cities:city-detail',
                    'read_only': True}
        }
