from django.contrib import admin

# Register your models here.
from .models import Movie, PublicReview, TvShow, ExtendedMovieReview, ExtendedTvShowReview, Note

# If you want to check in the Admin page need to register it to the site. 
admin.site.register(Movie)
admin.site.register(TvShow)
admin.site.register(PublicReview)
admin.site.register(ExtendedMovieReview)
admin.site.register(ExtendedTvShowReview)
admin.site.register(Note)
