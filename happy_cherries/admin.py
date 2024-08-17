from django.contrib import admin

# Register your models here.
from .models import Movie, PublicReview, TvShow

admin.site.register(Movie)
admin.site.register(TvShow)
admin.site.register(PublicReview)
