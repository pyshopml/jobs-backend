from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter

from .views import VacancyViewSet


vacancy_router = DefaultRouter()
vacancy_router.register(r'vacancy', VacancyViewSet)

urlpatterns = [
    url(r'^', include(vacancy_router.urls)),
]
