from django.shortcuts import render, redirect

from .models import Movie, Review
from .forms import MovieForm, ReviewForm
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
    
    # If searching for a movie then get the name and view all movies related to search. 
    if request.method == 'POST':
        
        movie_search = request.POST['movie_query']
        # Get all the movies through Dynamic search. 
        movie_list = fetch_movies(headers, movie_search, url_movie_search)
        
        context = {
            'movie_list': movie_list
        }

        return render (request, 'happy_cherries/search_movie.html', context)
    # IF it is a GET request just loading page. 
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
            'title': sq['title'],
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
    # URLs
    url_det_movie = "https://api.themoviedb.org/3/movie/{}?language=en-US"
    url_credits_movie = "https://api.themoviedb.org/3/movie/{}/credits?language=en-US"
    url_poster = "https://image.tmdb.org/t/p/w500/{}"
    
    if request.method != "POST":
        
        movie = fetch_detailed_movie(headers=headers, 
                                     url_movie=url_det_movie, 
                                     url_cast=url_credits_movie, 
                                     url_poster=url_poster, 
                                     movie_id=movie_id)
        # Because the Cast and Genres are saved in a long string splitted by ',' to save easily in the model direclty.
        # We split the string to then iterate over a list in the HTML file.  
        movie['cast'], movie['genres'] = movie['cast'].split(','), movie['genres'].split(',')
        
        context = {'movie': movie}
        return render(request, 'happy_cherries/requested_movie.html', context)

    else: 
        
        movie = fetch_detailed_movie(headers=headers, 
                                     url_movie=url_det_movie, 
                                     url_cast=url_credits_movie, 
                                     url_poster=url_poster, 
                                     movie_id=movie_id)
        
        # Create an instance of the model to save all the information directly into the database. 
        # No need to create Form since have the values predefined.s
        m = Movie(title=movie['title'],
                  release_date=movie['release_date'],
                  poster_path=movie['poster'],
                  overview=movie['overview'],
                  runtime= movie['runtime'],
                  status= movie['status'],
                  tagline= movie['tagline'],
                  cast=movie['cast'],
                  genre=movie['genres'],
                )
        m.save()
        
        # Redirect to the movies page after saving
        return redirect('happy_cherries:movies')
    
    
def fetch_detailed_movie(headers, url_movie, url_cast, url_poster, movie_id):
    """
    This function will manage to get all the essential information of a specific movie. 
    """
    # API Request using the movie ID and convert JSON-format into Dictionary.
    response = requests.get(url_movie.format(movie_id), headers=headers).json()
    
    # Genre
    # Because easy to save the genres in the Model Movie as a string seperated by ','.
    genres = ""
    for genre in response['genres']:
        genres += f"{genre['name']},"
    # Remove the last ',' from the string
    genres = genres[:-1]

    # Cast -- > API Request using the movie ID and convert JSON-format into Dictionary.
    response_credits = requests.get(url_cast.format(movie_id), headers=headers).json()
    # Because easy to save the genres in the Model Movie as a string seperated by ','.
    actors = ""
    for c in response_credits['cast']:
        actors += f"{c['name']},"
    # Remove the last ',' from the string
    actors = actors[:-1]
    
    # Save all the necassary information in a dictionary. 
    movie_info = {
        'id': response['id'],
        'title': response['title'],
        'release_date': response['release_date'],
        'poster': url_poster.format(response['poster_path']),
        'runtime': response['runtime'],
        'status': response['status'],
        'tagline': response['tagline'],
        'overview': response['overview'],
        'genres': genres,
        'cast': actors,
    }
    
    return movie_info

def add_review(request, movie_id):
    """The user can leave a review about the movie as well as a score to view the movie as."""
    movie = Movie.objects.get(id=movie_id)
    
    if request.method != 'POST':
        # Creating a blank form
        form = ReviewForm()
    
    else:
        form = ReviewForm(data=request.POST)
        
        if form.is_valid():
            new_review = form.save(commit=False)
            # Save the review under the PK linked to specific movie
            new_review.movie = movie
            new_review.save()
            
            return redirect('happy_cherries:movie', movie_id=movie_id)
    
    context = {'form': form, 'movie': movie}
    return render(request, 'happy_cherries/add_review.html', context)

def edit_review(request, review_id):
    """Want the user to be able to edit the score or review."""
    review = Review.objects.get(id=review_id)
    movie = review.movie
    
    if request.method != 'POST':
        
        form = ReviewForm(instance=review)
    else:
        
        form = ReviewForm(instance=review, data=request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('happy_cherries:movie', movie_id=movie.id)
    
    context = {'form': form, 'movie': movie, 'review': review}
    return render(request, 'happy_cherries/edit_review.html', context)
    