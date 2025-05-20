"""Defines URL patterns for happy_cherries."""

from django.urls import path

from . import views

app_name = 'happy_cherries'
urlpatterns = [
    path('', views.index, name='index'),
    path('movies/', views.movies, name='movies'),
    # Detail page for a single movie
    # When parsing an id with the url, need to save it into the HTTP path.
    path('movies/<int:movie_id>/', views.movie, name='movie'),
    path('movies/<int:movie_id>/add_review/', views.add_review_movie, name='add_review_movie'),
    path('movies/<int:movie_id>/delete_movie/', views.delete_movie, name='delete_movie'),
    path('movies/<int:review_id>/edit_review/', views.edit_review_movie, name='edit_review_movie'),
    path('movies/<int:review_id>/delete_review_movie/', views.delete_review_movie, name='delete_review_movie'),
    path('movies/<int:movie_id>/add_extended_review/', views.create_extended_review_movie, name='create_extended_review_movie'),
    path('movies/movie_search/', views.movie_search, name='movie_search'),
    path('movies/top_rated/', views.top_rated_movies, name='top_rated_movies'),
    path('movies/upcoming/', views.upcoming_movies, name='upcoming_movies'),
    path('movies/now_playing/', views.now_playing_movies, name='now_playing_movies'),
    path('movies/popular/', views.popular_movies, name='popular_movies'),
    path('movies/watchlist/', views.movies_watchlist, name='movies_watchlist'),    
    path('movies/favorites/', views.movies_favorites, name='movies_favorites'),
    # Make sure the movie_id is parsed to the URL as well otherwise get an error no reverse match
    path('movies/movie_search/requested_movie/<int:movie_id>/', views.requested_movie, name='requested_movie'),
    path('tvshows/', views.tvshows, name='tvshows'),
    path('tvshows/<int:tvshow_id>/', views.tvshow, name='tvshow'),
    path('tvshows/<int:tvshow_id>/delete_tvshow/', views.delete_tvshow, name='delete_tvshow'),
    path('tvshows/<int:review_id>/delete_review_tvshow/', views.delete_review_tvshow, name='delete_review_tvshow'),
    path('tvshows/search_tvshow/', views.tvshow_search, name='tvshow_search'),
    # Get the detailed information of a TV Show.
    path('tvshows/search_tvshow/requested_tvshow/<int:tvshow_id>/', views.requested_tvshow, name='requested_tvshow'),
    path('tvshows/<int:tvshow_id>/add_review/', views.add_review_tvshow, name='add_review_tvshow'),
    path('tvshows/<int:review_id>/edit_review/', views.edit_review_tvshow, name='edit_review_tvshow'),
    path('tvshows/<int:tvshow_id>/add_extended_review/', views.create_extended_review_tvshow, name='create_extended_review_tvshow'),
    path('tvshows/top_rated/', views.top_rated_tvshows, name='top_rated_tvshows'),
    path('tvshows/upcoming/', views.upcoming_tvshows, name='upcoming_tvshows'),
    path('tvshows/now_airing_tvshows/', views.now_airing_tvshows, name='now_airing_tvshows'),
    path('tvshows/popular/', views.popular_tvshows, name='popular_tvshows'),
    path('tvshows/watchlist/', views.tvshows_watchlist, name='tvshows_watchlist'),    
    path('tvshows/favorites/', views.tvshows_favorites, name='tvshows_favorites'),
]