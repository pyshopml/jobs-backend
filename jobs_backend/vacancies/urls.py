from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from .views import TagView, CategoryView, VacancyViewSet, SearchVacancyView

vacancy_router = DefaultRouter()
vacancy_router.register(r'', VacancyViewSet)

urlpatterns = [
    url(r'^actions/search/$', SearchVacancyView.as_view(), name='search'),
    url(r'^tags/$', TagView.as_view(), name='tags'),
    url(r'^categories/$', CategoryView.as_view(), name='categories'),
]

urlpatterns += vacancy_router.urls
