from rest_framework import mixins, permissions, viewsets

from .models import Vacancy
from .serializers import VacancySerializer


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
