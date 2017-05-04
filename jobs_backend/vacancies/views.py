from django.db.models import Q
from rest_framework import mixins, permissions, viewsets, generics, status
from rest_framework.response import Response

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
        search_param = self.search_serializer(data=self.request.query_params)
        search_param.is_valid(raise_exception=True)
        queryset = queryset.filter(search_param.save())
        return queryset


