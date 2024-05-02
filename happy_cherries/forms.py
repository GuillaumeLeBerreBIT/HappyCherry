from django import forms 
from .models import Movie, Review

class MovieForm(forms.ModelForm):
    class Meta():
        model = Movie
        fields = ['title', 'poster_path', 'overview', 'release_date',
                  'cast', 'genre', 'status', 'runtime', 'tagline']

class ReviewForm(forms.ModelForm):
    class Meta():
        model = Review
        fields = ['score', 'review']