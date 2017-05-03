from django.db.models import Q
from rest_framework import mixins, permissions, viewsets, generics

from .models import Vacancy
from .serializers import VacancySerializer, SearchSerializer


class VacancyViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """
    Vacancy ViewSet
    """
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class SearchVacancyView(generics.ListAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    search_serializer = SearchSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        search_param_from_response = self.search_serializer(data=self.request.query_params)
        search_param_from_response.is_valid(raise_exception=True)
        search_text = search_param_from_response.validated_data.get('phrase')
        section = search_param_from_response.validated_data.get('section', set())
        if SearchSerializer.ANY in section:
            queryset = queryset.filter(
                Q(title__icontains=search_text) |
                Q(description__icontains=search_text)
            )
            return queryset
        elif SearchSerializer.TITLE in section:
            queryset = queryset.filter(
                Q(title__icontains=search_text)
            )
        elif SearchSerializer.DESC in section:
            queryset = queryset.filter(
                Q(description__icontains=search_text)
            )
        return queryset

