from rest_framework.routers import DefaultRouter

from jobs_backend.geo import views


countries_router = DefaultRouter()
countries_router.register(r'', views.CountryViewSet)

urlpatterns = countries_router.urls
