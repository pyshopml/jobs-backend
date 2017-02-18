from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from jobs_backend.views import APIRoot


api_urlpatterns = [
    # All api endpoints should be included here
    url(r'^users/',
        include('jobs_backend.users.urls.users', namespace='users')),
    url(r'^account/',
        include('jobs_backend.users.urls.account', namespace='account')),
    url(r'^vacancies/',
        include('jobs_backend.vacancies.urls', namespace='vacancies')),
]

urlpatterns = [
    *api_urlpatterns,
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
]
urlpatterns += [
    url(r'^$', APIRoot.as_view(urlpatterns=urlpatterns, app_namespace='api_v1'), name='api_root')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
