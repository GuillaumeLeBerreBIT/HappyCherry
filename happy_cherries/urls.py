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
]