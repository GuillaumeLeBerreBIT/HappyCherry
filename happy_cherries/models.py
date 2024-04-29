from django.db import models

class CastMember(models.Model):
    """To enter a Casting member of movie(s)"""
    actor = models.CharField(max_length=100)
    
    def __str__(self):
        """Return the actor name"""
        return self.actor
    
class Genre(models.Model):
    """To give the genre of a moveie"""
    genre = models.CharField(max_length=100)
    
    def __str__(self):
        """Return the genre"""
        return self.genre

# Create your models here.
class Movie(models.Model):
    """A movie the user want to write a rating about."""
    
    title = models.CharField(max_length=150)
    date_added = models.DateTimeField(auto_now_add=True)
    
    poster_path = models.CharField(max_length=100)
    overview = models.TextField()
    release_date = models.DateField(db_comment="Date when the movie was released")
    
    #A movie can have multiple genres, but a genre can be linked to multiple movies.
    cast = models.ManyToManyField(CastMember)
    # A movie can have multiple actors but an actor can be casted in multiple movies. 
    genres = models.ManyToManyField(Genre)
    
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