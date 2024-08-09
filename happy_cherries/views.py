from django.shortcuts import render, redirect, get_object_or_404
# This will restricts the user to access certain data. 
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Movie, Review, TvShow, Note
from .forms import MovieForm, ReviewForm, TvShowForm, NoteForm
from .tmdb import fetch_movies, fetch_movies_list, fetch_detailed_movie, fetch_tvshow, fetch_detailed_tvshow, fetch_tvshows_list

import json, requests # This is to send a request to the URLs defined (Not a Django request)

def check_user(request, film):
    """Check if the logged in user is linked to the saved movie"""
    if request.user != film.owner:
        raise Http404

# The welcome page. 
def index(request):
    """Show the Home page for Happy Cherry."""
    # API_KEY
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
    }
    
    url_now_playing = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=1"
    
    url_airing = "https://api.themoviedb.org/3/tv/airing_today?language=en-US&page=1"

    url_poster = "https://image.tmdb.org/t/p/w500/{}"
    
    # Return all the movies currently in the cinema
    now_playing = fetch_movies_list(headers, url_now_playing, url_poster)[:5]
    now_airing = fetch_tvshows_list(headers, url_airing, url_poster)[:5]
    
    context = {'now_playing': now_playing,
               'now_airing': now_airing}
    return render(request, 'happy_cherries/index.html', context)

# MOVIES
# Show all the movies that you have saved. 
# Check if the user is logged in or not. 
@login_required
def movies(request):
    """
    List all the movies that have been added.
    The user can select a movie to leave a review behind. 
    """
    # Retrieve only the objects from database whose owner attribute matches the current user.
    movies = Movie.objects.filter(owner=request.user).order_by('date_added')
    
    # This will take all the movies for each specific owner. 
    for movie in movies:
        # Gets all the reviews per movie
        # The problem is it each movie is saved as a seperate ID. Even if the same movie is added. 
        # But the all movies that are the same have the same "id_movie" --> Can iterate over to get all the Reviews of that specific movie. 
        identical_movies = Movie.objects.filter(id_movie=movie.id_movie)
        # Can now get all the reviews for those movies. 
        all_reviews = []
        for iden_movie in identical_movies:
            # This line aggregates all reviews related to the identical movies into a single list. It does not add a list as a single item (append would not work).
            all_reviews.extend(iden_movie.review_set.all())
        
        #reviews = movie.review_set.all()
        # If there are existing reviews for a movie.
        if all_reviews:
            # Iterate over the reviews per movie and calculate the total score
            total_sum = sum(review.score for review in all_reviews)
            # Directly assign the value to the saved model in the dictionary.
            movie.avg_score = round(total_sum / len(all_reviews), None)
        
        # Convert the text to a list.
        movie.genres = movie.genre.split(',')
        movie.genres.sort()
    
    context = {'movies': movies}
    
    return render(request, 'happy_cherries/movies.html', context)

@login_required
def movie(request, movie_id):
    """
    Display a overview of the movie genre, actors, duration, ... 
    Shows the score and a review left by one or multiple persons.
    """
    # Get the requested movie.   
    movie = Movie.objects.get(id=movie_id)
    
    # Make sure the saved movie belongs to the user
    if movie.owner != request.user:
        raise Http404   # Returning the standard error.
    
    # Split the saved lists and parse them in the context dictionary
    movie.cast_spl, movie.genre_spl = movie.cast.split(','), movie.genre.split(',')
    
    # Only show the first 6 six actors if it exceeds limits
    # Because want to acces an object use a dot hore to get acces to the attribute. 
    if len(movie.cast_spl) > 6:
        movie.cast_spl = movie.cast_spl[0:6]
        movie.cast_spl.append('...')
    
    # Get the reviews linked to specific movie. 
    # This is the model object, iterate to get all the reviews which then can access the score attr
    identical_movies = Movie.objects.filter(id_movie=movie.id_movie)
    # Can now get all the reviews for those movies. 
    all_reviews = []
    for iden_movie in identical_movies:
        # This line aggregates all reviews related to the identical movies into a single list. It does not add a list as a single item (append would not work).
        all_reviews.extend(iden_movie.review_set.all())

    # If there are existing reviews for a movie.
    if all_reviews:
        # Iterate over the reviews per movie and calculate the total score
        total_sum = sum(review.score for review in all_reviews)
        # Direclty assign the value to the saved model in the dictionary.
        movie.avg_score = round(total_sum / len(all_reviews), None)
    
    context = {'movie': movie, 
               'reviews': all_reviews}
    
    return render(request, 'happy_cherries/movie.html', context)

@login_required
def delete_post_movie(request, movie_id):
    """Deleting a saved Movie from the list."""
    # Get the requested movie to delete.
    movie = get_object_or_404(Movie, id = movie_id)
    
    # Check if the current user is linked to the movie. 
    check_user(request, movie)
    
    # Pass the movie object to the HTML page. 
    context = {'movie': movie}
    
    # Create a view to make sure the user wants to delete the post. 
    if request.method != "POST":
        return render(request, "happy_cherries/delete_post.html", context)
    
    # If the method is a POST
    elif request.method == "POST":
        # Delete the movie object.
        movie.delete()
        # Send the user back to the movie page
        return redirect('happy_cherries:movies')

def movie_search(request):
    """
    The user can search for a movie based on dynamic search term. 
    All relevant movies then are shown. 
    When clicked on a movie of interest then detailed information is shown.  
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
        movie_list = fetch_movies_list(headers, url_trending, url_poster)
        
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
    
    is_owner = False 
    if request.user.is_authenticated:
        is_owner = True
    
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
        
        # When logged in. 
        if is_owner:
            # Get all the saved Movie objects from the authenticated user
            saved_movies = Movie.objects.filter(owner=request.user)
            
            # Saved all the titles in a list 
            titles = []
            for saved in saved_movies:
                titles.append(saved.title)
            # Then pass the variable to tell wether the movie is saved or not. 
            if movie['title'] in titles: saved = "Saved"
            else: saved  = "Unsaved"
            
        # When nog logged in it is not saved and can't be saved.    
        else: saved = "Unsaved"
        
        context = {
            'movie': movie,
            'saved': saved,
            'is_owner': is_owner
            }
        return render(request, 'happy_cherries/requested_movie.html', context)

    else: 
        
        # Need to check of the current use is the owner or not.        
        movie = fetch_detailed_movie(headers=headers, 
                                     url_movie=url_det_movie, 
                                     url_cast=url_credits_movie, 
                                     url_poster=url_poster, 
                                     movie_id=movie_id)
        
        # Create an instance of the model to save all the information directly into the database. 
        # No need to create Form since have the values predefined
        m = Movie(title=movie['title'],
                owner=request.user,
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
    movie_list = fetch_movies_list(headers, url_top_rated, url_poster)
    
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
    movie_list = fetch_movies_list(headers, url_upcoming, url_poster)
    
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
    movie_list = fetch_movies_list(headers, url_playing, url_poster)
    
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
    movie_list = fetch_movies_list(headers, url_popular, url_poster)
    
    context = {
        'movie_list': movie_list,
        'title':'Popular Movies'
    }
    return render(request, 'happy_cherries/movies_list.html', context)
    
    
# TV SHOWS
@login_required
def tvshows(request):
    """
    Want to shows all the TV shows that you have added to your list.
    User can select a Tv Show that has been added to your list.
    """
    # Filter the movie by User set. 
    tv_shows = TvShow.objects.filter(owner=request.user).order_by('date_added')
    # Note is linked to the user so do not need to filter the note by user. 
    
    for tv_show in tv_shows:
        reviews = tv_show.review_set.all()
        # Firstly check if there are any reviews left behind. 
        if reviews:
            total_sum = sum(review.score for review in reviews)
            tv_show.avg_score = round(total_sum / len(reviews), None)
        
        #print(dir(tv_show))
        #print(tv_show.id, tv_show.id_tvshow)
        # Take the last note that has been left 
        note = tv_show.note_set.first()
        # If there is a note set then. 
        if note:
            tv_show.note = note
        
        # Convert the text to a list.
        tv_show.genres = tv_show.genre.split(',')
        tv_show.genres.sort()
    
    context = {'tv_shows': tv_shows}
    return render(request, 'happy_cherries/tvshows.html', context)

@login_required
def tvshow(request, tvshow_id):
    """
    Want to be able to get the detailed information of a TvShow.
    The user can leave a review as well as a score behind.
    Can also leave a note saying an what episode he currently is on.    
    """
    # Use the TvShow Primary key to get acces. 
    tvshow = TvShow.objects.get(id=tvshow_id)
    
    # Make sure the saved movie belongs to the user
    if tvshow.owner != request.user:
        raise Http404   # Returning the standard error.
    
    # Get the note linked to a specific Movie
    note = tvshow.note_set.first() # Get the latest note added
    
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
        tvshow.avg_score = round(total_sum/len(reviews), None)    
    
    context = {'tvshow': tvshow, 
               'reviews': reviews, 
               'note': note}
    
    return render(request, 'happy_cherries/tvshow.html', context)

@login_required
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

@login_required
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
    
    is_owner = False 
    if request.user.is_authenticated:
        is_owner = True
    
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
            
        # When logged in. 
        if is_owner:
            # Get all the saved Movie objects from the authenticated user
            saved_tvshows = TvShow.objects.filter(owner=request.user)
            
            # Saved all the titles in a list 
            names = []
            for saved_show in saved_tvshows:
                names.append(saved_show.name)
            
            # Then pass the variable to tell wether the movie is saved or not. 
            if tvshow['name'] in names: saved = True
            else: saved  = False
            
        # When nog logged in it is not saved and can't be saved.    
        else: saved = False
        
        context = {'tvshow': tvshow,
                   'saved': saved,
                   'is_owner': is_owner}
        return render(request, 'happy_cherries/requested_tvshow.html', context)
    # POST request -- > Save the Tv Show into a model which then redirected to tvshow homepage.    
    else:
        
        tvshow = fetch_detailed_tvshow(headers, tvshow_id, url_det_tvshow, url_credits_tvshow, url_poster)
            
        # Create an instance of the model to save all the information directly into the database. 
        # No need to create Form since have the values predefined
        s = TvShow(name=tvshow['name'],
                   owner=request.user,
                   id_tvshow=tvshow['id'],
                   poster_path=tvshow['poster_path'],
                   overview=tvshow['overview'],
                   first_air_date=tvshow['first_air_date'],
                   last_air_date=tvshow['last_air_date'],
                   next_episode_to_air=tvshow['next_episode_to_air']['air_date'],
                   number_of_episodes=tvshow['number_of_episodes'],
                   number_of_seasons=tvshow['number_of_seasons'],
                   cast=tvshow['cast'],
                   genre=tvshow['genres']
                   )
        
        s.save()
        
        return redirect('happy_cherries:tvshows')

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

# REVIEW - MOVIES
@login_required
def add_review_movie(request, movie_id):
    """The user can leave a review about the movie as well as a score to view the movie as."""
    movie = get_object_or_404(Movie, id=movie_id)
    # Check if the owner of the saved movie is the one wanting to add a comment 
    check_user(request, movie)
    
    if request.method != 'POST':
        # Creating a blank form
        form = ReviewForm()
    
    else:
        form = ReviewForm(data=request.POST)
        
        if form.is_valid():
            new_review = form.save(commit=False)
            # Save the review under the PK linked to specific movie
            new_review.movie = movie
            new_review.owner = request.user
            new_review.save()
            
            return redirect('happy_cherries:movie', movie_id=movie_id)
    
    context = {'form': form, 'movie': movie}
    return render(request, 'happy_cherries/add_review_movie.html', context)

@login_required
def edit_review_movie(request, review_id):
    """Want the user to be able to edit the score or review."""
    review = Review.objects.get(id=review_id)
    movie = review.movie
    
    # Check if the owner of the movie is the one wanting to edit the comment. 
    check_user(request, movie)
    
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
@login_required
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
            new_review.owner = request.user
            new_review.save()
            
            return redirect('happy_cherries:tvshow', tvshow_id=tvshow_id)
    
    context = {'form': form, 'tvshow': tvshow}
    return render(request, 'happy_cherries/add_review_tvshow.html', context)

@login_required
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