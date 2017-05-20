from rest_framework.routers import DefaultRouter

from jobs_backend.geo import views


cities_router = DefaultRouter()
cities_router.register(r'', views.CityViewSet)

urlpatterns = cities_router.urls
