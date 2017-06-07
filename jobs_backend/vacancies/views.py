from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import status

from .models import Tag, Category, Vacancy
from .serializers import (
    TagSerializer, CategorySerializer, VacancySerializer)


class TagViewSet(mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """
    Tag ViewSet
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @list_route()
    def search(self, request):
        search_title = self.request.query_params.get('title')
        if search_title is not None:
            queryset = self.get_queryset().filter(title__icontains=search_title)

        if queryset.exists():
            view = self.__class__.as_view({'get': 'list'}, queryset=queryset)
            return view(request, *self.args, **self.kwargs)

        return Response(status=status.HTTP_404_NOT_FOUND)


class CategoryViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
    Category ViewSet
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
    serializer_class = VacancySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Vacancy.objects\
        .select_related(
            'location_city', 'location_city__country', 'location_country',
            'location_city__region', 'location_city__subregion',
            'category', 'category__parent')\
        .prefetch_related(
            'location_city__alt_names', 'location_city__country__alt_names',
            'location_country__alt_names', 'keywords')\
        .all()

    @list_route()
    def search(self, request):
        search_title = self.request.query_params.get('title')
        search_tag = self.request.query_params.get('tag')
        search_category = self.request.query_params.get('category')
        queryset = self.get_queryset()

        if search_title is not None:
            queryset = queryset.filter(
                title__icontains=search_title)

        if search_tag is not None:
            queryset = queryset.filter(
                keywords__title__icontains=search_tag)

        if search_category is not None:
            queryset = queryset.filter(
                category__title__icontains=search_category)

        if queryset.exists():
            view = self.__class__.as_view(
                {'get': 'list'}, queryset=queryset)
            return view(request, *self.args, **self.kwargs)

        return Response(status=status.HTTP_404_NOT_FOUND)
