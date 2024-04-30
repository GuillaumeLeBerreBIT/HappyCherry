from django.shortcuts import render, redirect

from .models import Movie, Review
from .forms import MovieForm
import json, requests # This is to send a request to the URLs defined (Not a Django request)

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
    # Split the saved lists and parse them in the context dictionary
    cast_spl = movie.cast.split(',')
    genre_spl = movie.genre.split(',')
    
    reviews = Review.objects.order_by('date_added')
    context = {'movie': movie, 
               'reviews': reviews, 
               'cast_spl': cast_spl,
               'genre_spl': genre_spl}
    
    return render(request, 'happy_cherries/movie.html', context)

def add_movie_manual(request):
    """
    The user can add a new movie to the page. 
    Can manually fill in all the information for the Movie to be added
    When the correct movie found can add to the home page to leave a review behind. 
    """
    if request.method != 'POST':
        # Create a blank form.
        form = MovieForm()
    else: 
        form = MovieForm(date=request.POST)
        if form.is_valid():
            form.save()
            return redirect('happy_cherries:movies')
    
    context = {'form': form}
    return render(request, 'happy_cherries/add_movie.html', context)


def movie_search(request):
    """
    The user can search for a movie based on dynamic search term. 
    All relevant movies then are shown. 
    When clicked on the relevant movie will be added to the list.  
    """
    # API_KEY
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
    }
    # Query results for a movie search
    url_movie_search = "https://api.themoviedb.org/3/search/movie?query={}&include_adult=false&language=en-US&page=1"
    # Fetch the poster image of the movie
    url_poster_image = "https://image.tmdb.org/t/p/w500/{}"
    # Fetch the cast members of the movie
    url_credits_movie = "https://api.themoviedb.org/3/movie/{}/credits?language=en-US"
    
    if request.method == 'POST':
        
        movie_search = request.POST['movie_query']
        # Get all the movies through Dynamic search. 
        movie_list = fetch_movies(headers, movie_search, url_movie_search)
        
        context = {
            'movie_list': movie_list
        }

        return render (request, 'happy_cherries/search_movie.html', context)
    # IF it is a GET request
    else: 
        return render(request, 'happy_cherries/search_movie.html')
    

def fetch_movies(headers, movie_query, url_movie_search):
    # Want the response to be in JSON format. 
    response = requests.get(url_movie_search.format(movie_query), headers=headers).json() 

    movie_list = []
    for sq in response['results']:
        
        # Fetch all essential information. 
        # A trick: in the HTML when wanting to parse specific information such as an id.
        # Can then make a link directly to specific item using the ID given to the object or movie.  
        requested_data = {
            'id': sq['id'],
            'poster': sq['poster_path'],
            'genre_ids': sq['genre_ids'],
            'original_title': sq['original_title'],
            'release_date': sq['release_date'],
        }
        # Add each movie to a list.
        movie_list.append(requested_data)
    
    # Return the movie list.
    return movie_list

def requested_movie(request, movie_id):
    """
    When the user has found the movie he has been interested in. 
    Will be able to view the details about the movie.
    Finally will also be able to add to the database/Movie page. 
    """
    # Now I need to get access to the contents of the dictionary from movie_list based on the clicked movie
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
    }
    # Get the detailed information of the movie
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US", 
                         headers=headers).json()
    
    genre_name = []
    #This will return multiple dictionarys
    for genre in response['genres']:
        
        genre_name.append(genre['name'])
    
    movie = {
        'id': response['id'],
        'poster': f"https://image.tmdb.org/t/p/w500/{response['poster_path']}",
        'overview': response['overview'],
        'genres': genre_name,
        'original_title': response['original_title'],
        'release_date': response['release_date'],
    }
    
    context = {'movie': movie}
    return render(request, 'happy_cherries/requested_movie.html', context)

    