from django.shortcuts import render, redirect, get_object_or_404

from .models import Movie, Review, TvShow, Note
from .forms import MovieForm, ReviewForm, TvShowForm, NoteForm
from .tmdb import fetch_movies, fetch_trending_rated_upcoming_popular_movies, fetch_detailed_movie, fetch_tvshow, fetch_detailed_tvshow, fetch_tvshows_list

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
        # Convert the text to a list.
        movie.genres = movie.genre.split(',')
        movie.genres.sort()
    
    context = {'movies': movies}
    
    return render(request, 'happy_cherries/movies.html', context)

def movie(request, movie_id):
    """
    Display the most important parts of a movie. 
    Shows the score and a review left by one or multiple persons.
    """
        
    movie = Movie.objects.get(id=movie_id)
    # Split the saved lists and parse them in the context dictionary
    movie.cast_spl, movie.genre_spl = movie.cast.split(','), movie.genre.split(',')
    
    # Get the reviews linked to specific movie. 
    # This is the model object, iterate to get all the reviews which then can access the score attr
    reviews = movie.review_set.order_by('-date_added')
    
    # Only show the first 6 six actors if it exceeds limits
    # Because want to acces an object use a dot hore to get acces to the attribute. 
    if len(movie.cast_spl) > 6:
        movie.cast_spl = movie.cast_spl[0:6]
        movie.cast_spl.append('...')

    # If there are existing reviews for a movie.
    if reviews:
        # Iterate over the reviews per movie and calculate the total score
        total_sum = sum(review.score for review in reviews)
        # Direclty assign the value to the saved model in the dictionary.
        movie.avg_score = round(total_sum / len(reviews), None)
    
    
    context = {'movie': movie, 
               'reviews': reviews}
    
    return render(request, 'happy_cherries/movie.html', context)

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
    
    url_poster = "https://image.tmdb.org/t/p/w500/{}"
    
    # If searching for a movie then get the name and view all movies related to search. 
    if request.method == 'POST':
        
        movie_search = request.POST['movie_query']
        # Get all the movies through Dynamic search. 
        movie_list = fetch_movies(headers, movie_search, url_movie_search, url_poster)
        
        context = {
            'movie_list': movie_list
        }

        return render(request, 'happy_cherries/search_movie.html', context)
    # IF it is a GET request just loading page. 
    else: 
        # Get all the trending movies so the home page does not look empty. 
        movie_list = fetch_trending_rated_upcoming_popular_movies(headers, url_trending, url_poster)
        
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
        # Only show the first 6 six actors if it exceeds limits
        if len(movie['cast']) > 6:
            movie["cast"] = movie["cast"][0:6]
            movie["cast"].append('...')
        
        # Get all the saved Movie objects
        saved_movies = Movie.objects.all()
        # Saved all the titles in a list 
        titles = []
        for saved in saved_movies:
            titles.append(saved.title)
        # Then pass the variable to tell wether the movie is saved or not. 
        if movie['title'] in titles: saved = "Saved"
        else: saved  = "Unsaved"
        
        context = {
            'movie': movie,
            'saved': saved
            }
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
                id_movie=movie['id'],
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
    
def top_rated_movies(request):
    """
    Get a list of all the trending movies
    """
    # API_KEY
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
    }
    
    url_top_rated = "https://api.themoviedb.org/3/movie/top_rated?language=en-US&page=1"
    
    url_poster = "https://image.tmdb.org/t/p/w500/{}"
    
    # Get all the trending movies so the home page does not look empty. 
    movie_list = fetch_trending_rated_upcoming_popular_movies(headers, url_top_rated, url_poster)
    
    context = {
        'movie_list': movie_list,
        'title': "Top Rated Movies"
    }
    return render(request, 'happy_cherries/movies_list.html', context)

def upcoming_movies(request):
    """
    Get a list of all the trending movies
    """
    # API_KEY
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
    }
    
    url_upcoming = "https://api.themoviedb.org/3/movie/upcoming?language=en-US&page=1"
    
    url_poster = "https://image.tmdb.org/t/p/w500/{}"
    
    # Get all the trending movies so the home page does not look empty. 
    movie_list = fetch_trending_rated_upcoming_popular_movies(headers, url_upcoming, url_poster)
    
    context = {
        'movie_list': movie_list,
        'title': "Upcoming Movies"
    }
    return render(request, 'happy_cherries/movies_list.html', context)

def now_playing_movies(request):
    """
    Get a list of all the now playing movies
    """
    # API_KEY
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
    }
    
    url_playing = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=1"
    
    url_poster = "https://image.tmdb.org/t/p/w500/{}"
    
    # Get all the trending movies so the home page does not look empty. 
    movie_list = fetch_trending_rated_upcoming_popular_movies(headers, url_playing, url_poster)
    
    context = {
        'movie_list': movie_list,
        'title':'Now Playing Movies'
    }
    return render(request, 'happy_cherries/movies_list.html', context)

def popular_movies(request):
    """List of all the popular movies"""
    # API_KEY
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
    }
    
    url_popular = "https://api.themoviedb.org/3/movie/popular"
    
    url_poster = "https://image.tmdb.org/t/p/w500/{}"
    
    # Get all the trending movies so the home page does not look empty. 
    movie_list = fetch_trending_rated_upcoming_popular_movies(headers, url_popular, url_poster)
    
    context = {
        'movie_list': movie_list,
        'title':'Popular Movies'
    }
    return render(request, 'happy_cherries/movies_list.html', context)
    
    
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
        
        note = tv_show.note_set.first()
        
        if note:
            tv_show.note = note
        
        # Convert the text to a list.
        tv_show.genres = tv_show.genre.split(',')
        tv_show.genres.sort()
    
    context = {'tv_shows': tv_shows}
    return render(request, 'happy_cherries/tvshows.html', context)

def tvshow(request, tvshow_id):
    """
    Want to be able to get the detailed information of a specific TvShow.
    The user can leave a review as well as a score behond.
    Can also leave a note saying an what episode currently he is.    
    """
    
    tvshow = TvShow.objects.get(id=tvshow_id)
    
    # Get the note linked to a specific Movie
    note = tvshow.note_set.order_by('-date_added').first() # To get the newest note added first
    
    # Get the reviews linked to specific Tv Show. 
    # This is the model object, iterate to get all the reviews which then can access the score attr
    reviews = tvshow.review_set.order_by('date_added')
    
    tvshow.cast_spl, tvshow.genres_spl = tvshow.cast.split(','), tvshow.genre.split(',')
    
    # Only show the first 6 six actors if it exceeds limits
    # Because want to acces an object use a dot hore to get acces to the attribute. 
    if len(tvshow.cast_spl) > 6:
        tvshow.cast_spl = tvshow.cast_spl[0:6]
        tvshow.cast_spl.append('...')
    
    # Check if there are any reviews. 
    if reviews:
        # Iterate over all reviews
        total_sum = sum(review.score for review in reviews)
        avg_score = round(total_sum/len(reviews), None)    
    else: 
        avg_score = 0
    
    context = {'tvshow': tvshow, 'reviews': reviews, 'avg_score': avg_score, 'note': note}
    
    return render(request, 'happy_cherries/tvshow.html', context)

def add_note_tvshow(request, tvshow_id):
    """The user can leave a Note behind on what episode/season he is currently at."""
    tvshow = TvShow.objects.get(id=tvshow_id)
    
    if request.method != 'POST':
        form = NoteForm()
    
    else:
        form = NoteForm(data=request.POST)

        if form.is_valid():
            
            # Delete the existing note if it exists
            existing_note = tvshow.note_set.order_by('date_added').first()
            if existing_note:
                existing_note.delete()
            # Do not save it direclty ito the database
            new_note = form.save(commit=False)
            # Set the primary key of 
            new_note.tvshow = tvshow
            new_note.save()
            return redirect('happy_cherries:tvshow', tvshow_id = tvshow_id)
        
    context = {'form': form, 'tvshow': tvshow}
    return render(request, 'happy_cherries/add_note_tvshow.html', context)

def edit_note_tvshow(request, note_id):
    """Edit the note the user left behind on the page."""
    
    note = get_object_or_404(Note, id=note_id)
    tvshow = note.tvshow
    
    if request.method != 'POST':
        form = NoteForm(instance=note)
    
    else: 
        form = NoteForm(instance=note, data=request.POST)
        
        if form.is_valid():
            
            form.save()
            return redirect('happy_cherries:tvshow', tvshow_id=tvshow.id)
        
    context = {'form': form, 'note': note, 'tvshow': tvshow}
    return render(request, 'happy_cherries/edit_note_tvshow.html', context)

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
    url_trending_tvshows = "https://api.themoviedb.org/3/tv/popular?language=en-US&page=1"
    url_poster = "https://image.tmdb.org/t/p/w500/{}"
    
    if request.method == 'POST':
        
        tvshow_search = request.POST['tvshow_query']
        
        tvshow_list = fetch_tvshow(headers, url_tvshow, tvshow_search, url_poster)
        
        context = {'tvshow_list': tvshow_list}
        
        return render(request, 'happy_cherries/search_tvshow.html', context)
        
    else: # GET request
        
        tvshow_list = fetch_tvshows_list(headers, url_trending_tvshows, url_poster)
        
        context = {'tvshow_list': tvshow_list}
        
        return render(request, 'happy_cherries/search_tvshow.html', context)
        
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
        
        # Only show the first 6 six actors if it exceeds limits
        if len(tvshow['cast']) > 6:
            tvshow["cast"] = tvshow["cast"][0:6]
            tvshow["cast"].append('...')
        
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

def top_rated_tvshows(request):
    """
    Get a list of all the trending tvshows
    """
    # API_KEY
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
    }
    
    url_top_rated = "https://api.themoviedb.org/3/tv/top_rated?language=en-US&page=1"
    
    url_poster = "https://image.tmdb.org/t/p/w500/{}"
    
    tvshow_list = fetch_tvshows_list(headers, url_top_rated, url_poster)
    
    context = {
        'tvshow_list': tvshow_list,
        'title': "Top Rated TV Shows"
    }
    return render(request, 'happy_cherries/tvshows_list.html', context)

def upcoming_tvshows(request):
    """
    Get a list of all the tvshows airing in the next seven days
    """
    # API_KEY
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
    }
    
    url_on_the_air = "https://api.themoviedb.org/3/tv/on_the_air?language=en-US&page=1"
    
    url_poster = "https://image.tmdb.org/t/p/w500/{}"
    
    tvshow_list = fetch_tvshows_list(headers, url_on_the_air, url_poster)
    
    context = {
        'tvshow_list': tvshow_list,
        'title': "On The Air TV Shows"
    }
    return render(request, 'happy_cherries/tvshows_list.html', context)

def now_airing_tvshows(request):
    """
    Get a list of all the tvshows airing today
    """
    # API_KEY
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
    }
    
    url_airing = "https://api.themoviedb.org/3/tv/airing_today?language=en-US&page=1"
    
    url_poster = "https://image.tmdb.org/t/p/w500/{}"
    
    tvshow_list = fetch_tvshows_list(headers, url_airing, url_poster)
    
    context = {
        'tvshow_list': tvshow_list,
        'title': "TV Shows Airing Today"
    }
    return render(request, 'happy_cherries/tvshows_list.html', context)

def popular_tvshows(request):
    """
    Get a list of all the tvshows airing today
    """
    # API_KEY
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
    }
    
    url_popular = "https://api.themoviedb.org/3/tv/popular?language=en-US&page=1"
    
    url_poster = "https://image.tmdb.org/t/p/w500/{}"
    
    tvshow_list = fetch_tvshows_list(headers, url_popular, url_poster)
    
    context = {
        'tvshow_list': tvshow_list,
        'title': "Popular TV Shows"
    }
    return render(request, 'happy_cherries/tvshows_list.html', context)