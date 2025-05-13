from django.contrib import admin
from .models import Movie, Tag
from django.core.exceptions import ValidationError


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'release_year', 'country', 'subscription_required', 'created_at')
    list_filter = ('genre', 'release_year', 'subscription_required')
    search_fields = ('title', 'description')
    filter_horizontal = ('tags',)




@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

