from django.shortcuts import render

from .models import Movie, Review

# Create your views here.
def index(request):
    """Show the Home page for Happy Cherry."""
    return render(request, 'happy_cherries/index.html')

def movies(request):
    """
    List all the movies that have been added.
    The user can select a movie to leave a review behind. 
    """
    
    movies = Movie.objects.order_by('date_added')
    
    context = {'movies': movies}
    
    return render(request, 'happy_cherries/movies.html', context)

def movie(request, movie_id):
    """
    Display the most important parts of a movie. 
    Shows the score and a review left by one or multiple persons.
    """
        
    movie = Movie.objects.get(id=movie_id)
    
    genres = movie.genres.all()
    cast = movie.cast.all()
    
    reviews = Review.objects.order_by('date_added')
    context = {'movie': movie, 'reviews': reviews, 'cast': cast, 'genres': genres}
    
    return render(request, 'happy_cherries/movie.html', context)
    
    