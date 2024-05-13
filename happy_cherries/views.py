from django.shortcuts import render, redirect

from .models import Movie, Review, TvShow
from .forms import MovieForm, ReviewForm, TvShowForm
from .tmdb import fetch_movies, fetch_trending_movies, fetch_detailed_movie, fetch_tvshow, fetch_detailed_tvshow

import json, requests # This is to send a request to the URLs defined (Not a Django request)

# Create your views here.
def index(request):
    """Show the Home page for Happy Cherry."""
    return render(request, 'happy_cherries/index.html')

# MOVIES
# Show all the movies that you ahve saved. 
def movies(request):
    """
    List all the movies that have been added.
    The user can select a movie to leave a review behind. 
    """
    
    movies = Movie.objects.order_by('date_added')
    
    for movie in movies:
        # Gets all the reviews per movie
        reviews = movie.review_set.all()
        # If there are existing reviews for a movie.
        if reviews:
            # Iterate over the reviews per movie and calculate the total score
            total_sum = sum(review.score for review in reviews)
            # Direclty assign the value to the saved model in the dictionary.
            movie.avg_score = round(total_sum / len(reviews), None)
            #print(dir(movie))
    
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
    
    # Get the reviews linked to specific movie. 
    # This is the model object, iterate to get all the reviews which then can access the score attr
    reviews = movie.review_set.order_by('-date_added')

    # If there are existing reviews for a movie.
    if reviews:
        # Iterate over the reviews per movie and calculate the total score
        total_sum = sum(review.score for review in reviews)
        # Direclty assign the value to the saved model in the dictionary.
        movie.avg_score = round(total_sum / len(reviews), None)
    
    
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
    
    url_trending = "https://api.themoviedb.org/3/trending/movie/week?language=en-US"
    
    # If searching for a movie then get the name and view all movies related to search. 
    if request.method == 'POST':
        
        movie_search = request.POST['movie_query']
        # Get all the movies through Dynamic search. 
        movie_list = fetch_movies(headers, movie_search, url_movie_search)
        
        context = {
            'movie_list': movie_list
        }

        return render(request, 'happy_cherries/search_movie.html', context)
    # IF it is a GET request just loading page. 
    else: 
        # Get all the trending movies so the home page does not look empty. 
        movie_list = fetch_trending_movies(headers, url_trending)
        
        context = {
            'movie_list': movie_list
        }
        return render(request, 'happy_cherries/search_movie.html', context)

def requested_movie(request, movie_id):
    """
    When the user has found the movie he has been interested in. 
    Will be able to view the details about the movie.
    Finally will also be able to add to the database/Movie page. 
    This does not show the reviews and a score yet!
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
        # Using the Movie ID which has been saved from teh request response and parsed to the URL. 
        # Can use it to get the detailed information of a Tv Show
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
        # No need to create Form since have the values predefined
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

# TV SHOWS
def tvshows(request):
    """
    Want to shows all the TV shows that you have added to your list.
    User can select a Tv Show that has been added to your list.
    """
        
    tv_shows = TvShow.objects.order_by('date_added')
    
    for tv_show in tv_shows:
        reviews = tv_show.review_set.all()
        # Firstly check if there are any reviews left behind. 
        if reviews:
            total_sum = sum(review.score for review in reviews)
            tv_show.avg_score = round(total_sum / len(reviews), None)
    
    context = {'tv_shows': tv_shows}
    return render(request, 'happy_cherries/tvshows.html', context)

def tvshow(request, tvshow_id):
    """
    Want to be able to get the detailed information of a specific TvShow.
    The user can leave a review as well as a score behond.
    Can also leave a note saying an what episode currently he is.    
    """
    
    tvshow = TvShow.objects.get(id=tvshow_id)
    
    # Get the reviews linked to specific Tv Show. 
    # This is the model object, iterate to get all the reviews which then can access the score attr
    reviews = tvshow.review_set.order_by('date_added')
    
    cast_spl, genres_spl = tvshow.cast.split(','), tvshow.genre.split(',')
    
    # Check if there are any reviews. 
    if reviews:
        # Iterate over all reviews
        total_sum = sum(review.score for review in reviews)
        avg_score = round(total_sum/len(reviews), None)    
    else: 
        avg_score = 0
    
    context = {'tvshow': tvshow, 'cast_spl': cast_spl, 'genres_spl': genres_spl, 'reviews': reviews, 'avg_score': avg_score}
    
    return render(request, 'happy_cherries/tvshow.html', context)

def add_tvshow_manual(request):
    """The user will be able to manually fill in a TvShow"""
    if request.method != 'POST':
        
        form = TvShowForm()
    
    else:
        
        form = TvShowForm(data=request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('happy_cherries:tvshows')
    
    context = {'form': form}
    return render(request, 'happy_cherries/add_tvshow.html', context)


def tvshow_search(request):
    """
    Want to show all the results from the search query.
    Show a list with all the movies matching the search query. 
    """
    
    # Now I need to get access to the contents of the dictionary from movie_list based on the clicked movie
    headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
        }
    
    url_tvshow = "https://api.themoviedb.org/3/search/tv?query={}&include_adult=false&language=en-US&page=1"
    
    if request.method == 'POST':
        
        tvshow_search = request.POST['tvshow_query']
        
        tvshow_list = fetch_tvshow(headers, url_tvshow, tvshow_search)
        
        context = {'tvshow_list': tvshow_list}
        
        return render(request, 'happy_cherries/search_tvshow.html', context)
        
    else: # GET request
    
        return render(request, 'happy_cherries/search_tvshow.html')
        
def requested_tvshow(request, tvshow_id):
    """
    Want to show a detailed information of all the TvShow.
    This also having the user the option to save the information to his list.
    """
    # Now I need to get access to the contents of the dictionary from movie_list based on the clicked movie
    headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
        }
    # URLs
    url_det_tvshow = "https://api.themoviedb.org/3/tv/{}?language=en-US"
    url_credits_tvshow = "https://api.themoviedb.org/3/tv/{}/credits?language=en-US"
    url_poster = "https://image.tmdb.org/t/p/w500/{}"
    
    # GET request -- > Show all the detailed information of Tv Show
    if request.method != 'POST':
        # Want to get all the detailed information of a movie. 
        
        tvshow = fetch_detailed_tvshow(headers, tvshow_id, url_det_tvshow, url_credits_tvshow, url_poster)
        
        # Because the Cast and Genres are saved in a long string splitted by ',' to save easily in the model direclty.
        # We split the string to then iterate over a list in the HTML file.  
        tvshow['cast'], tvshow['genres'] = tvshow['cast'].split(','), tvshow['genres'].split(',')
        
        context = {'tvshow': tvshow}
        return render(request, 'happy_cherries/requested_tvshow.html', context)
    # POST request -- > Save the Tv Show into a model which then redirected to tvshow homepage.    
    else:
        
        tvshow = fetch_detailed_tvshow(headers, tvshow_id, url_det_tvshow, url_credits_tvshow, url_poster)
            
        # Create an instance of the model to save all the information directly into the database. 
        # No need to create Form since have the values predefined
        s = TvShow(name=tvshow['name'],
                   id_tvshow=tvshow['id'],
                   poster_path=tvshow['poster_path'],
                   overview=tvshow['overview'],
                   first_air_date=tvshow['first_air_date'],
                   last_air_date=tvshow['last_air_date'],
                   next_episode_to_air=tvshow['next_episode_to_air'],
                   number_of_episodes=tvshow['number_of_episodes'],
                   number_of_seasons=tvshow['number_of_seasons'],
                   cast=tvshow['cast'],
                   genre=tvshow['genres']
                   )
        
        s.save()
        
        return redirect('happy_cherries:tvshows')



# REVIEW - MOVIES
def add_review_movie(request, movie_id):
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
    return render(request, 'happy_cherries/add_review_movie.html', context)

def edit_review_movie(request, review_id):
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
    return render(request, 'happy_cherries/edit_review_movie.html', context)

# REVIEW - TVSHOW
def add_review_tvshow(request, tvshow_id):
    """The user can leave a review about the movie as well as a score to view the movie as."""
    tvshow = TvShow.objects.get(id=tvshow_id)
    
    if request.method != 'POST':
        # Creating a blank form
        form = ReviewForm()
    
    else:
        form = ReviewForm(data=request.POST)
        
        if form.is_valid():
            new_review = form.save(commit=False)
            # Save the review under the PK linked to specific movie
            new_review.tvshow = tvshow
            new_review.save()
            
            return redirect('happy_cherries:tvshow', tvshow_id=tvshow_id)
    
    context = {'form': form, 'tvshow': tvshow}
    return render(request, 'happy_cherries/add_review_tvshow.html', context)

def edit_review_tvshow(request, review_id):
    """Want the user to be able to edit the score or review."""
    review = Review.objects.get(id=review_id)
    tvshow = review.tvshow
    
    if request.method != 'POST':
        
        form = ReviewForm(instance=review)
    else:
        
        form = ReviewForm(instance=review, data=request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('happy_cherries:tvshow', tvshow_id=tvshow.id)
    
    context = {'form': form, 'tvshow': tvshow, 'review': review}
    return render(request, 'happy_cherries/edit_review_tvshow.html', context)