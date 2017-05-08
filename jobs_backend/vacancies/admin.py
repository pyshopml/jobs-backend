from django.contrib import admin

from .models import Tag, Category, Vacancy


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    fields = ('title', 'description', 'created_on', 'modified_on')
    readonly_fields = ('created_on', 'modified_on')
    list_display = ('id', 'title', 'description', 'created_on', 'modified_on')

