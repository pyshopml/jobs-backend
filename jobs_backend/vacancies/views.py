from rest_framework import mixins, permissions, viewsets, generics, status

from .models import Vacancy
from .serializers import VacancySerializer, SearchSerializer, SortSerializer


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


class SortSearchVacancyView(generics.ListAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    search_serializer = SearchSerializer
    sort_serializer = SortSerializer

    def filter_queryset(self, queryset):
        """
        Filter and sort vacancy list
        :param queryset: 
        :return: 
        """
        queryset = super().filter_queryset(queryset)
        query_params = self.request.query_params
        if 'phrase' in query_params:
            search_param_ser = self.search_serializer(data=query_params)
            search_param_ser.is_valid(raise_exception=True)
            filter_query = search_param_ser.save()  # return Q object
            queryset = queryset.filter(filter_query)
        if 'sort_field' in query_params:
            sort_ser = self.sort_serializer(data=query_params)
            sort_ser.is_valid(raise_exception=True)
            sort_param = sort_ser.save()  # return sort param
            queryset = queryset.order_by(sort_param)
        return queryset


