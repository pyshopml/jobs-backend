from rest_framework.routers import DefaultRouter

from jobs_backend.users import views


users_router = DefaultRouter()
users_router.register(r'', views.UserViewSet)

urlpatterns = users_router.urls
