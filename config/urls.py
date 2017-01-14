from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from jobs_backend.users.urls import users, account

# All api endpoints should be included here
api_urlpatterns = [
    url(r'^', include(users)),
    url(r'^', include('jobs_backend.vacancies.urls')),
    url(r'^account/', include(account)),
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
