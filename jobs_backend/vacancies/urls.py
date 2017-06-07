from rest_framework.routers import DefaultRouter

from .views import TagViewSet, CategoryViewSet, VacancyViewSet

vacancy_router = DefaultRouter()
vacancy_router.register(r'tags', TagViewSet)
vacancy_router.register(r'categories', CategoryViewSet)
vacancy_router.register(r'', VacancyViewSet)

urlpatterns = vacancy_router.urls
