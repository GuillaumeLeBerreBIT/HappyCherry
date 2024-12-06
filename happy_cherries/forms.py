from django import forms 
from django.forms.widgets import SelectDateWidget
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
                  'finish_date', 'priority', 'total_times_rewatched',
                  'rewatch_value', 'comment']
        
        def clean(self):
            cleaned_data = super().clean()
            # Normalize empty or "None" values for date fields
            for field in ['first_time_watched', 'last_time_watched', 'finish_date']:
                value = cleaned_data.get(field)
                if value in ["", "None"]:
                    cleaned_data[field] = None
            # Normalize the comment field
            if cleaned_data.get('comment') == "None":
                cleaned_data['comment'] = None
            print(cleaned_data)
            return cleaned_data
        
        # widgets = {
        #     'first_time_watched': SelectDateWidget(years=range(1980, 2030)),  # Example year range
        #     'last_time_watched': SelectDateWidget(years=range(1980, 2030)),
        #     'finish_date': SelectDateWidget(years=range(1980, 2030)),
        # }

class ExtendedTvShowReviewForm(forms.ModelForm):
    class Meta:
        model = ExtendedTvShowReview
        fields = ['status', 'episodes_watched', 'your_score', 'start_date',
                   'finish_date', 'priority','rewatch_value', 'total_times_rewatched', 'comment']
        
        
class NoteForm(forms.ModelForm):
    class Meta: 
        model = Note
        fields = ['note']
        