from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from jobs_backend.users.views import UserViewSet
from jobs_backend.vacancies.views import VacancyViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'vacancy', VacancyViewSet)

# All api endpoints should be included here
api_urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^account/', include('jobs_backend.users.urls.account')),
]

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    url(r'^api/', include(api_urlpatterns)),

    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
