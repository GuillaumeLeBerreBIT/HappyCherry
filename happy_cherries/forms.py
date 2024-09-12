from django import forms 
from .models import Movie, PublicReview, TvShow, Note, ExtendedReview

class MovieForm(forms.ModelForm):
    class Meta():
        model = Movie
        fields = ['title', 'poster_path', 'overview', 'release_date',
                  'cast', 'genre', 'status', 'runtime', 'tagline']
        #labels = {'title': ''}
        widgets = {'overview': forms.Textarea(attrs={'cols': 80})}
        
class TvShowForm(forms.ModelForm):
    class Meta():
        model = TvShow
        fields = ['title', 'poster_path', 'overview', 'first_air_date',
                  'last_air_date', 'next_episode_to_air', 'number_of_episodes', 
                  'number_of_seasons', 'cast', 'genre']

class ReviewForm(forms.ModelForm):
    class Meta():
        model = PublicReview
        fields = ['score', 'review']
        
class ExtendedReviewForm(forms.ModelForm):
    class Meta():
        model = ExtendedReview
        fields = ['status', 'episodes_watched', 'your_score', 'start_date', 
                  'start_date_unknown', 'finish_date', 'priority', 'total_times_rewatched',
                  'rewatch_value', 'comment']
        
class NoteForm(forms.ModelForm):
    class Meta: 
        model = Note
        fields = ['note']
        