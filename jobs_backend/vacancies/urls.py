from rest_framework.routers import DefaultRouter

from .views import VacancyViewSet


vacancy_router = DefaultRouter()
vacancy_router.register(r'', VacancyViewSet)

urlpatterns = vacancy_router.urls
