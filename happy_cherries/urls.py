"""Defines URL patterns for happy_cherries."""

from django.urls import path

from . import views

app_name = 'happy_cherries'
urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    # Page for showing all the movies
    path('movies/', views.movies, name='movies'),
    # Detail page for a single movie
    path('movies/<int:movie_id>/', views.movie, name='movie'),
    # Detail page for a single movie
    path('movies/<int:movie_id>/add_review', views.add_review, name='add_review'),
    # Edit a review given to a Movie
    path('movies/<int:review_id>/edit_review', views.edit_review, name='edit_review'),
    # Add a movie to the page. 
    path('movies/add_movie_manual/', views.add_movie_manual, name='add_movie_manual'),
    # Search for a specific movie
    path('movies/movie_search/', views.movie_search, name='movie_search'),
    # Add a movie to the page. 
    # Make sure the movie_id is parsed to the URL as well otherwise get an error no reverse match
    path('movies/movie_search/requested_movie/<int:movie_id>/', views.requested_movie, name='requested_movie'),
    # Page for showing all the tvshows added to your list.
    path('tvshows/', views.tvshows, name='tvshows'),
    # Adding the form to manually fill in the TV shows
    path('tvshows/add_manual_tvshow/', views.add_tvshow_manual, name='add_tvshow_manual'),
    # search for a specific TvShow.
    path('tvshows/search_tvshow/', views.search_tvshow, name='search_tvshow'),
]