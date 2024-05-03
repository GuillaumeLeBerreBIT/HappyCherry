from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 

# Create your models here.
class Movie(models.Model):
    """A movie the user want to write a rating about."""
    
    title = models.CharField(max_length=150)
    date_added = models.DateTimeField(auto_now_add=True)
    
    poster_path = models.CharField(max_length=100)
    overview = models.TextField()
    release_date = models.DateField(db_comment="Date when the movie was released")
    
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
    
    title = models.CharField(max_length=150)
    date_added = models.DateTimeField(auto_now_add=True)
    
class Review(models.Model):
    """The user can leave a review about the movie he has seen."""
    
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=50, validators=[MinValueValidator(1), MaxValueValidator(100)])
    review = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """Return a string representation of the model Review."""
        
        if len(self.review) > 50: 
            return f"{self.review[:50]}..."
        else: 
            return f"{self.review}"