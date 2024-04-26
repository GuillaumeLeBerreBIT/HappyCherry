from django.db import models

# Create your models here.
class Movie(models.Model):
    """A movie the user want to write a rating about."""
    
    title = models.CharField(max_length=150)
    date_added = models.DateTimeField(auto_now_add=True)
    
    poster_path = models.CharField(max_length=100)
    genres = models.CharField(max_length=100)
    cast = models.CharField(max_length=200)
    overview = models.TextField()
    release_date = models.DateField(db_comment="Date when the movie was released")
    
    def __str__(self):
        """Return a string representation of the model"""
        return self.title
    
class Review(models.Model):
    """The user can leave a review about the movie he has seen."""
    
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """Return a string representation of the model Review."""
        
        if len(self.text) > 50: 
            return f"{self.text[:50]}..."
        else: 
            return f"{self.text}"