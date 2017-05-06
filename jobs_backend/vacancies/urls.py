from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from .views import VacancyViewSet, SortSearchVacancyView

vacancy_router = DefaultRouter()
vacancy_router.register(r'', VacancyViewSet)

urlpatterns = vacancy_router.urls

urlpatterns += [
    url(r'^actions/search/$', SortSearchVacancyView.as_view(), name='search'),
]