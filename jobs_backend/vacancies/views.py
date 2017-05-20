from rest_framework import mixins, permissions, viewsets, generics

from .models import Tag, Category, Vacancy
from .serializers import (
    TagSerializer, CategorySerializer, VacancySerializer, SearchSerializer)


class TagView(generics.ListAPIView):
    """
    Tag View
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CategoryView(generics.ListAPIView):
    """
    Category View
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


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
        search_param_ser = self.search_serializer(data=self.request.query_params)
        search_param_ser.is_valid(raise_exception=True)
        queryset = queryset.filter(search_param_ser.save())
        return queryset
