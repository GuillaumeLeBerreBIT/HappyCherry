from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 

# Create your models here.
class Movie(models.Model):
    """A movie the user want to write a rating about."""
    
    title = models.CharField(max_length=150)
    id_movie = models.IntegerField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    poster_path = models.CharField(blank=True, max_length=100)
    overview = models.TextField()
    release_date = models.DateField()
    
    genre = models.CharField(max_length=500) 
    cast = models.TextField()
    
    runtime = models.IntegerField(default=0)
    status = models.CharField(max_length=50, blank=True)
    tagline = models.CharField(max_length=300, blank=True)
    
    def __str__(self):
        """Return a string representation of the model"""
        return self.title
    
class TvShow(models.Model):
    """The repersenation of all the details of a TvSow"""
    
    name = models.CharField(max_length=150)
    id_tvshow = models.IntegerField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    poster_path = models.CharField(max_length=100, blank=True)
    overview = models.TextField(blank=True)
    first_air_date = models.DateField(null=True)
    last_air_date = models.DateField(null=True)
    next_episode_to_air = models.DateField(null=True)
    
    number_of_episodes = models.IntegerField()
    number_of_seasons = models.IntegerField()
    
    genre = models.CharField(blank=True, max_length=500) 
    cast = models.TextField(blank=True)
    
    def __str__(self):
        """String representation of model"""
        return self.name
    
class Review(models.Model):
    """The user can leave a review about the movie/TvShow he has seen."""
    
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, blank=True, null=True)  # Can have the option to have it blank so can choose between Tvshow or Movie
    tvshow = models.ForeignKey(TvShow, on_delete=models.CASCADE, blank=True, null=True)
    score = models.PositiveIntegerField(default=50, validators=[MinValueValidator(1), MaxValueValidator(100)])
    review = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """Return a string representation of the model Review."""
        
        if len(self.review) > 50: 
            return f"{self.review[:50]}..."
        else: 
            return f"{self.review}"
        
class Note(models.Model):
    """The user can leave a Note on what episode he is currently is stuck watching."""
    
    tvshow = models.ForeignKey(TvShow, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    note = models.CharField(max_length=100)
    
    def __str__(self):
        
        if len(self.note) > 50:
            return f"{self.note[:50]}"
        else:
            return f"{self.note}"
