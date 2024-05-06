from django.contrib import admin

# Register your models here.
from .models import Movie, Review, TvShow

admin.site.register(Movie)
admin.site.register(Review)
admin.site.register(TvShow)