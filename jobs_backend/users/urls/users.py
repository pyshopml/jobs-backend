from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter

from jobs_backend.users import views


users_router = DefaultRouter()
users_router.register(r'users', views.UserViewSet)

urlpatterns = [
    url(r'^', include(users_router.urls)),
]
