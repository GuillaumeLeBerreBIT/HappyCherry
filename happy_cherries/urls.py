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
    # When parsing an id with the url, need to save it into the HTTP path.
    path('movies/<int:movie_id>/', views.movie, name='movie'),
    # Add a review to a movie. 
    path('movies/<int:movie_id>/add_review/', views.add_review_movie, name='add_review_movie'),
    # To delete a movie from the user list. 
    path('movies/<int:movie_id>/delete_movie/', views.delete_movie, name='delete_movie'),
    # Edit a review given to a Movie
    path('movies/<int:review_id>/edit_review/', views.edit_review_movie, name='edit_review_movie'),
    # Delete a review of a movie. 
    path('movies/<int:review_id>/delete_review/', views.delete_review_movie, name='delete_review_movie'),
    # Let the user create an extended review. 
    path('movies/<int:movie_id>/add_extended_review/', views.create_extended_review_movie, name='create_extended_review_movie'),
    # Search for a specific movie
    path('movies/movie_search/', views.movie_search, name='movie_search'),
    # View all the Top rated movies
    path('movies/top_rated/', views.top_rated_movies, name='top_rated_movies'),
    # Show all upcoming movies
    path('movies/upcoming/', views.upcoming_movies, name='upcoming_movies'),
    # Show all movies now playing.
    path('movies/now_playing/', views.now_playing_movies, name='now_playing_movies'),
    # Show all movies now playing.
    path('movies/popular/', views.popular_movies, name='popular_movies'),
    # Add a movie to the page. 
    # Make sure the movie_id is parsed to the URL as well otherwise get an error no reverse match
    path('movies/movie_search/requested_movie/<int:movie_id>/', views.requested_movie, name='requested_movie'),
    # Page for showing all the tvshows added to your list.
    path('tvshows/', views.tvshows, name='tvshows'),
    # Page for showing all the tvshows added to your list.
    path('tvshows/<int:tvshow_id>/', views.tvshow, name='tvshow'),
    
    path('tvshows/<int:tvshow_id>/delete_tvshow/', views.delete_tvshow, name='delete_tvshow'),
    # Page for showing all the tvshows added to your list.
    path('tvshows/<int:tvshow_id>/add_note_tvshow/', views.add_note_tvshow, name='add_note_tvshow'),
    # Page for showing all the tvshows added to your list.
    path('tvshows/<int:note_id>/edit_note_tvshow/', views.edit_note_tvshow, name='edit_note_tvshow'),
    # search for a specific TvShow.
    path('tvshows/search_tvshow/', views.tvshow_search, name='tvshow_search'),
    # Get the detailed information of a TV Show.
    path('tvshows/search_tvshow/requested_tvshow/<int:tvshow_id>/', views.requested_tvshow, name='requested_tvshow'),
    # Add a review to a TvShow
    path('tvshows/<int:tvshow_id>/add_review/', views.add_review_tvshow, name='add_review_tvshow'),
    # Edit a review given to a TvShow
    path('tvshows/<int:review_id>/edit_review/', views.edit_review_tvshow, name='edit_review_tvshow'),
    # Let the user create an extended review. 
    path('tvshows/<int:tvshow_id>/add_extended_review/', views.create_extended_review_tvshow, name='create_extended_review_tvshow'),
    # View all the Top rated movies
    path('tvshows/top_rated/', views.top_rated_tvshows, name='top_rated_tvshows'),
    # Show all upcoming movies
    path('tvshows/upcoming/', views.upcoming_tvshows, name='upcoming_tvshows'),
    # Show all movies now playing.
    path('tvshows/now_airing_tvshows/', views.now_airing_tvshows, name='now_airing_tvshows'),
    # Show all movies now playing.
    path('tvshows/popular/', views.popular_tvshows, name='popular_tvshows'),
]