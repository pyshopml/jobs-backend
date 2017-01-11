from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from jobs_backend.users import views


router = DefaultRouter()
router.register(r'users', views.UserViewSet)


urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),
    # Your stuff: custom urls includes go here
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(router.urls)),

    url(r'^api/auth/login/$', views.LoginView.as_view(), name='login'),
    url(r'^api/auth/logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^api/account/activate/$',
        views.ActivationView.as_view(),
        name='activation'),
    url(r'^api/account/password/reset/$',
        views.PasswordResetView.as_view(),
        name='password_reset'),
    url(r'^api/account/password/reset/confirm/$',
        views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    url(r'^api/account/password/change/$',
        views.PasswordChangeView.as_view(),
        name='password_change'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
