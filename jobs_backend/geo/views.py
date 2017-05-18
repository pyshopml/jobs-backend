from rest_framework import mixins, viewsets
from cities.models import Country, City

from .serializers import CountrySerializer, CitySerializer


class _LangParamMixin:
    """
    Receives a parameter `lang` and sends it to the serializer
    """

    def filter_queryset(self, queryset):
        self.lang = self.request.query_params.get('lang')
        return super().filter_queryset(queryset)

    def get_serializer(self, *args, **kwargs):
        kwargs['lang'] = self.lang
        return super().get_serializer(*args, **kwargs)


class CountryViewSet(_LangParamMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """
    API Endpoint to get a list of countries with search and filtering
    """
    serializer_class = CountrySerializer
    queryset = Country.objects.all()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        search_param = self.request.query_params.get('search')

        if search_param is not None:
            if self.lang is not None:
                queryset = queryset.filter(
                    alt_names__language_code=self.lang,
                    alt_names__name__icontains=search_param)

            else:
                queryset = queryset.filter(name__icontains=search_param)

        return queryset.distinct()


class CityViewSet(_LangParamMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    API Endpoint to get a list of cities with search and filtering
    """
    serializer_class = CitySerializer
    queryset = City.objects.all()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        country_param = self.request.query_params.get('country')
        search_param = self.request.query_params.get('search')

        if country_param is not None:
            if self.lang is not None:
                queryset = queryset.filter(
                    country__alt_names__language_code=self.lang,
                    country__alt_names__name__icontains=country_param)
            else:
                queryset = queryset.filter(
                    country__name__icontains=country_param)

        if search_param is not None:
            if self.lang is not None:
                queryset = queryset.filter(
                    alt_names__language_code=self.lang,
                    alt_names__name__icontains=search_param)
            else:
                queryset = queryset.filter(name__icontains=search_param)

        return queryset.distinct()
