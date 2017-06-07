from django.db.models import Prefetch

from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import list_route
from cities.models import Country, City, AlternativeName

from .serializers import CountrySerializer, CitySerializer


class _LangParamMixin:
    """
    Receives a parameter `lang` and sends it to the serializer
    """

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.lang = self.request.query_params.get('lang')

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        # query optimization with prefetch_related
        alt_names_queryset = AlternativeName.objects.all()
        if self.lang is not None:
            alt_names_queryset = alt_names_queryset.filter(
                language_code=self.lang)
        queryset = queryset.prefetch_related(Prefetch(
            'alt_names', queryset=alt_names_queryset,
            to_attr='alt_names_lang'))

        return queryset

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

    @list_route()
    def search(self, request):
        search_name = self.request.query_params.get('name')
        queryset = self.get_queryset()

        if search_name is not None:
            if self.lang is not None:
                queryset = queryset.filter(
                    alt_names__language_code=self.lang,
                    alt_names__name__icontains=search_name)
            else:
                queryset = queryset.filter(name__icontains=search_name)

        if queryset.exists():
            queryset = queryset.distinct()
            view = self.__class__.as_view({'get': 'list'}, queryset=queryset)
            return view(request, *self.args, **self.kwargs)

        return Response(status=status.HTTP_404_NOT_FOUND)


class CityViewSet(_LangParamMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    API Endpoint to get a list of cities with search and filtering
    """
    serializer_class = CitySerializer
    queryset = City.objects.all().select_related(
        'country', 'region', 'subregion')

    @list_route()
    def search(self, request):
        search_name = self.request.query_params.get('name')
        search_country = self.request.query_params.get('country')
        queryset = self.get_queryset()

        if search_country is not None:
            if self.lang is not None:
                queryset = queryset.filter(
                    country__alt_names__language_code=self.lang,
                    country__alt_names__name__icontains=search_country)
            else:
                queryset = queryset.filter(
                    country__name__icontains=search_country)

        if search_name is not None:
            if self.lang is not None:
                queryset = queryset.filter(
                    alt_names__language_code=self.lang,
                    alt_names__name__icontains=search_name)
            else:
                queryset = queryset.filter(name__icontains=search_name)

        if queryset.distinct():
            queryset = queryset.distinct()
            view = self.__class__.as_view({'get': 'list'}, queryset=queryset)
            return view(request, *self.args, **self.kwargs)

        return Response(status=status.HTTP_404_NOT_FOUND)
