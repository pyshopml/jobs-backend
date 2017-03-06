from django.conf.urls import url

from jobs_backend.users import views


urlpatterns = [
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),

    url(r'^activate/$', views.ActivationView.as_view(), name='activation'),

    url(r'^password/$',
        views.PasswordChangeView.as_view(),
        name='password_change'),
    url(r'^password/reset/$',
        views.PasswordResetView.as_view(),
        name='password_reset'),
    url(r'^password/reset/confirm/$',
        views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    url(r'^authtoken/validate/$',
        views.AuthTokenValidationView.as_view(),
        name='authtoken_validate')
]
