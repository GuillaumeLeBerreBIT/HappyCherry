from django.contrib import admin

# Register your models here.
from .models import Movie, Genre, CastMember, Review

admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(CastMember)
admin.site.register(Review)
