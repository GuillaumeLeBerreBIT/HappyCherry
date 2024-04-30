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
    # Add a movie to the page. 
    path('movies/add_movie_manual/', views.add_movie_manual, name='add_movie_manual'),
    # Add a movie to the page. 
    path('movies/movie_search/', views.movie_search, name='movie_search'),
    # Add a movie to the page. 
    # Make sure the movie_id is parsed to the URL as well otherwise get an error no reverse match
    path('movies/movie_search/requested_movie/<int:movie_id>/', views.requested_movie, name='requested_movie'),
]