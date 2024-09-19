from django import forms 
from .models import Movie, PublicReview, TvShow, Note, ExtendedMovieReview, ExtendedTvShowReview

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
        
class ExtendedMovieReviewForm(forms.ModelForm):
    class Meta():
        model = ExtendedMovieReview
        fields = ['status', 'first_time_watched', 'last_time_watched', 'your_score', 
                  'finish_date', 'finish_date_unknown', 'priority', 'total_times_rewatched',
                  'rewatch_value', 'comment']

class ExtendedTvShowReviewForm(forms.ModelForm):
    class Meta():
        model = ExtendedTvShowReview
        fields = ['status', 'episodes_watched', 'your_score', 'start_date',
                  'start_date_unknown', 'finish_date', 'finish_date_unknown', 'priority',
                  'rewatch_value', 'total_times_rewatched', 'comment']
        
class NoteForm(forms.ModelForm):
    class Meta: 
        model = Note
        fields = ['note']
        