from django import forms 
from .models import Movie, Review, TvShow

class MovieForm(forms.ModelForm):
    class Meta():
        model = Movie
        fields = ['title', 'poster_path', 'overview', 'release_date',
                  'cast', 'genre', 'status', 'runtime', 'tagline']

class ReviewForm(forms.ModelForm):
    class Meta():
        model = Review
        fields = ['score', 'review']
        
class TvShowForm(forms.ModelForm):
    class Meta():
        model = TvShow
        fields = ['name', 'poster_path', 'overview', 'first_air_date',
                  'last_air_date', 'next_episode_to_air', 'number_of_episodes', 
                  'number_of_seasons', 'cast', 'genre']