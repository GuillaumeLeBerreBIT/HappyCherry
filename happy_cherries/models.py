from django.db import models

# Create your models here.
class Movie(models.Model):
    """A movie the user want to write a rating about."""
    
    title = models.CharField(max_length=150)
    date_added = models.DateTimeField(auto_now_add=True)
    
    poster_image = models.ImageField((""), upload_to=None, height_field=None, width_field=None)
    genres = models.CharField()
    cast = models.CharField()
    overview = models.TextField()
    release_date = models.DateField(db_comment="Date when the movie was released")
    
    def __str__(self):
        """Return a string representation of the model"""
        return self.title