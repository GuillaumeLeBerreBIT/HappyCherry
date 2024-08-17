from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator 

class BaseModel(models.Model):
    """The main model for the shared fields."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """
        This model will then not be used to create any database table. Instead, 
        when it is used as a base class for other models, its fields will be added to those of the child class.
        Any model that inherits from this abstract class will automatically inherit all its fields, methods, and other properties.
        """
        abstract = True 
        
class CommonContent(BaseModel):
    """Common content between TvShow & Movies."""
    
    title = models.CharField(max_length=150)
    poster_path = models.CharField(max_length=150)
    overview = models.TextField()
    cast = models.TextField()
    genre = models.CharField(max_length=300)
    
    def __str__(self):
        """Return a string representation of the model"""
        return self.title
    
    class Meta:
        """Fields will be inhireted by child classes without this creating a seperate table."""
        abstract = True

# Create your models here.
class Movie(CommonContent):
    """A movie the user want to write a rating about."""
    
    id_movie = models.IntegerField()
    release_date = models.DateField()
    runtime = models.IntegerField(default=0)
    status = models.CharField(max_length=50)
    tagline = models.CharField(max_length=300)
    
class TvShow(CommonContent):
    """The repersenation of all the details of a TvSow"""
    
    id_tvshow = models.IntegerField()
    first_air_date = models.DateField(null=True)
    last_air_date = models.DateField(null=True)
    next_episode_to_air = models.DateField(null=True)
    number_of_episodes = models.IntegerField()
    number_of_seasons = models.IntegerField()
    
class PublicReview(BaseModel):
    """The user can leave a review about the movie/TvShow he has seen."""
    # One of the 2 will always be blank/empty
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, blank=True, null=True)  # Can have the option to have it blank so can choose between Tvshow or Movie
    tvshow = models.ForeignKey(TvShow, on_delete=models.CASCADE, blank=True, null=True)
    score = models.PositiveIntegerField(default=50, validators=[MinValueValidator(1), MaxValueValidator(100)])
    review = models.TextField()
    
    def __str__(self):
        """Return a string representation of the model Review."""
        
        return f"{self.review[:50]} ..." if self.review > 50 else self.review
        
class Note(BaseModel):
    """The user can leave a Note on what episode he is currently is stuck watching."""
    
    tvshow = models.ForeignKey(TvShow, on_delete=models.CASCADE)
    note = models.CharField(max_length=100)
    
    def __str__(self):
        
        return f"{self.note[:50]} ..." if self.note > 50 else self.note
    
