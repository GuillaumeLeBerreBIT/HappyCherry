from django.shortcuts import render, redirect, get_object_or_404
# This will restricts the user to access certain data. 
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.forms.models import model_to_dict

from .models import Movie, PublicReview, TvShow, ExtendedTvShowReview, ExtendedMovieReview
from .forms import ReviewForm, ExtendedMovieReviewForm, ExtendedTvShowReviewForm

from .TMDB_API import MovieDatabase
from django.utils import timezone

from datetime import datetime

def convert_date(time_str):
    """Convert the time string to time object"""
    if time_str:
        time_obj = datetime.strptime(time_str, '%Y-%m-%d')
        return datetime.strftime(time_obj, '%d %b, %Y')
    else: 
        return ''

def check_user(request, media):
    """Check if the logged in user is linked to the saved movie/show"""
    if request.user != media.owner:
        raise Http404

# The welcome page. 
def index(request):
    """Show the Home page for Happy Cherry."""
    movie_api = MovieDatabase()
    
    # Return all the movies currently in the cinema
    now_playing = movie_api.fetch_movies_list('NOW_PLAYING')[:5]
    now_airing = movie_api.fetch_tvshows_list('NOW_AIRING')[:5]
    
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
            all_reviews.extend(iden_movie.publicreview_set.all())
        
        #reviews = movie.publicreview_set.all()
        # If there are existing reviews for a movie.
        if all_reviews:
            # Iterate over the reviews per movie and calculate the total score
            total_sum = sum(review.score for review in all_reviews)
            # Directly assign the value to the saved model in the dictionary.
            movie.avg_score = round(total_sum / len(all_reviews), None)
        
        # Convert the text to a list.
        movie.genres = movie.genre.split(',')
        movie.genres.sort()
        
    # Initialize is_delete based on session data
    is_delete = request.session.get('is_delete', False)
        
    if request.method == 'POST':
        if request.POST.get('action') == 'delete_movies':
            # Toggle is_delete in the session
            request.session['is_delete'] = True
            return redirect('happy_cherries:movies')
        
        if request.POST.get('action') == 'save_movies':
            # Toggle is_delete in the session
            request.session['is_delete'] = False
            return redirect('happy_cherries:movies')
        
    
    context = {
        'movies': movies, 
        'title': 'Library Movies',
        'is_delete': is_delete
        }
    
    return render(request, 'happy_cherries/movies.html', context)

@login_required
def movies_watchlist(request):
    """Show all the movies added to your watchlist."""
    
    movies = Movie.objects.filter(owner=request.user, watchlist=True).order_by('date_added')
    
    for movie in movies:
        
        identical_movies = Movie.objects.filter(id_movie=movie.id_movie)    # Get all the movies with the same ID. 
        
        all_reviews = []
        for iden_movie in identical_movies:
            
            all_reviews.extend(iden_movie.publicreview_set.all())
        
        if all_reviews:
            
            total_sum = sum(review.score for review in all_reviews)
            movie.avg_score = round(total_sum / len(all_reviews), None)
        
        movie.genres = movie.genre.split(',')
        movie.genres.sort()
    
    context = {'movies': movies, 'title': 'Watchlist Movies'}
    return render(request, 'happy_cherries/movies.html', context)
 
@login_required
def movies_favorites(request):
    """Show all the movies add to your favorites list."""
    
    movies = Movie.objects.filter(owner= request.user, favorites=True).order_by('date_added')
    
    for movie in movies:
        
        identical_movies = Movie.objects.filter(id_movie=movie.id_movie)
        
        all_reviews = []
        for iden_movie in identical_movies:
            
            all_reviews.extend(iden_movie.publicreview_set.all())
            
            if all_reviews:
                
                total_sum = sum(review.score for review in all_reviews)
                movie.avg_score = round(total_sum / len(all_reviews), None)
        
        movie.genres = movie.genre.split(',')
        movie.genres.sort()
    
    context = {'movies': movies, 'title': 'Favorite Movies'}
    return render(request, 'happy_cherries/movies.html', context)

@login_required
def movie(request, movie_id):
    """
    Display a overview of the movie genre, actors, duration, ... 
    Shows the score and a review left by one or multiple persons.
    """
    # Get the requested movie.   
    movie = get_object_or_404(Movie, id=movie_id)
    
    ext_review = movie.extendedmoviereview_set.first()
    
    # Make sure the saved movie belongs to the user
    check_user(request, movie)
    
    is_owner = False
    if request.user.is_authenticated:
        is_owner = True
    
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
    all_extended_reviews = []
    for iden_movie in identical_movies:
        # This line aggregates all reviews related to the identical movies into a single list. It does not add a list as a single item (append would not work).
        all_reviews.extend(iden_movie.publicreview_set.all())
        all_extended_reviews.extend(iden_movie.extendedmoviereview_set.all())

    # If there are existing reviews for a movie.
    if all_reviews:
        # Iterate over the reviews per movie and calculate the total score
        total_sum = sum(review.score for review in all_reviews)
        # Direclty assign the value to the saved model in the dictionary.
        movie.avg_score = round(total_sum / len(all_reviews), None)
    
    if request.method == 'POST':
        
        action = request.POST.get('action')
        
        if action == "remove_movie":
            movie.delete()
            # Refresh teh page directly. 
            return redirect('happy_cherries:movies')
        
        elif action == 'save_watchlist': 
            movie.watchlist = True
            movie.save()
            # Refresh teh page directly. 
            return redirect('happy_cherries:movie', movie_id=movie.id)
    
        elif action == 'save_favorite': 
            movie.favorites = True
            movie.save()
            # Refresh teh page directly. 
            return redirect('happy_cherries:movie', movie_id=movie.id)
        
        elif action == 'remove_favorite':
            movie.favorites = False
            movie.save()
            return redirect('happy_cherries:movie', movie_id=movie.id)
        
        elif action == 'remove_watchlist':
            movie.watchlist = False
            movie.save()
            return redirect('happy_cherries:movie', movie_id=movie.id)

        elif action == 'remove_review_movie':
            # Get the review ID from the form
            review_id = request.POST.get('review_id')
            print(request.POST)
            if review_id:
                review = get_object_or_404(PublicReview, id=review_id)
                review.delete()
                
                return redirect('happy_cherries:movie', movie_id=movie.id)
            
    
    context = {
        'movie': movie, 
        'is_owner': is_owner,
        'reviews': all_reviews,
        'extended_review': ext_review,
        'in_watchlist': movie.watchlist,
        'in_favorite': movie.favorites
        }
    
    return render(request, 'happy_cherries/movie.html', context)

@login_required
def delete_movie(request, movie_id):
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
    movie_api = MovieDatabase()
    
    # If searching for a movie then get the name and view all movies related to search. 
    if request.method == 'POST':
        
        requested_page = int(request.POST.get('page', 1))
        movie_search = request.POST.get('movie_query')
        
        # Get all the movies through Dynamic search. 
        movie_list, pagination = movie_api.fetch_movies(movie_search, requested_page)
        
        for movie in movie_list:
            movie['release_date'] = convert_date(movie["release_date"])
            
        context = {
            'movie_list': movie_list,
            'pagination': pagination,
            'search_query': request.POST.get('movie_query', '')
        }

    # IF it is a GET request just loading page. 
    else: 
        # Get all the trending movies so the home page does not look empty. 
        movie_list = movie_api.fetch_movies_list("TRENDING")
        
        for movie in movie_list:
            movie['release_date'] = convert_date(movie["release_date"])
        
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
    movie_api = MovieDatabase()
    
    is_owner = False 
    if request.user.is_authenticated:
        is_owner = True
    
    if request.method != "POST":
        
        # Using the Movie ID which has been saved from teh request response and parsed to the URL. 
        # Can use it to get the detailed information of a Tv Show
        movie = movie_api.fetch_detailed_movie(movie_id=movie_id)
        # Because the Cast and Genres are saved in a long string splitted by ',' to save easily in the model direclty.
        # We split the string to then iterate over a list in the HTML file.  
        movie['cast'], movie['genres_spl'] = movie['cast'].split(','), movie['genres'].split(',')
        # Only show the first 6 six actors if it exceeds limits
        if len(movie['cast']) > 6:
            movie["cast_spl"] = movie["cast"][0:6]
            movie["cast_spl"].append('...')
        
        # Convert date
        movie['release_date'] = convert_date(movie['release_date'])
        
        # When logged in. 
        if is_owner:
            # Get all the saved Movie objects from the authenticated user
            saved_movie = Movie.objects.filter(owner=request.user, title=movie['title']).first()
            
            # Then pass the variable to tell wether the movie is saved or not. 
            if saved_movie: 
                saved = "Saved"
                in_watchlist = saved_movie.watchlist
                is_favorite = saved_movie.favorites
                
            else: 
                saved  = "Unsaved"
                in_watchlist = is_favorite = False
            
        # When nog logged in it is not saved and can't be saved.    
        else: 
            saved  = "Unsaved"
            in_watchlist = is_favorite = False
        
        context = {
            'movie': movie,
            'saved': saved,
            'is_owner': is_owner,
            'in_watchlist': in_watchlist,
            'is_favorite': is_favorite
            }
        
        return render(request, 'happy_cherries/requested_movie.html', context)

    elif request.method == 'POST': 
        
        # Get the current action given by entered Form
        action = request.POST.get('action')
        
        # Need to check of the current use is the owner or not.        
        movie = movie_api.fetch_detailed_movie(movie_id=movie_id)
        
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
        
        if action == "save_movie":
            
            m.watchlist = m.favorites = False
            m.save()
        
            # Redirect to the movies page after saving
            return redirect('happy_cherries:movies')
    
        elif action == 'save_watchlist': 
        
            m.watchlist = True
            m.favorites = False
                
            m.save()
        
            # Redirect to the movies page after saving
            return redirect('happy_cherries:movies_watchlist')
    
        elif action == 'save_favorite': 
            
            m.watchlist = False
            m.favorites = True
                
            m.save()
            
            # Redirect to the movies page after saving
            return redirect('happy_cherries:movies_favorites')
    
def top_rated_movies(request):
    """
    Get a list of all the trending movies
    """
    movie_api = MovieDatabase()
    
    if request.method == 'POST':
        requested_page = int(request.POST.get('page', 1))
    else:
        requested_page = 1
    # Get all the trending movies so the home page does not look empty. 
    movie_list, pagination = movie_api.fetch_movies_list('TOP_RATED', requested_page)
    
    for movie in movie_list:
        movie['release_date'] = convert_date(movie["release_date"])
        
    context = {
        'movie_list': movie_list,
        'title': "Top Rated Movies",
        'pagination': pagination,
    }
    return render(request, 'happy_cherries/movies_list.html', context)

def upcoming_movies(request):
    """
    Get a list of all the trending movies
    """
    movie_api = MovieDatabase()
    
    if request.method == 'POST':
        requested_page = int(request.POST.get('page', 1))
    else:
        requested_page = 1
    
    # Get all the trending movies so the home page does not look empty. 
    movie_list, pagination = movie_api.fetch_movies_list('UPCOMING', requested_page)
    
    for movie in movie_list:
        movie['release_date'] = convert_date(movie["release_date"])
    
    context = {
        'movie_list': movie_list,
        'title': "Upcoming Movies",
        'pagination': pagination,
    }
    return render(request, 'happy_cherries/movies_list.html', context)

def now_playing_movies(request):
    """
    Get a list of all the now playing movies
    """
    movie_api = MovieDatabase()
    
    if request.method == 'POST':
        requested_page = int(request.POST.get('page', 1))
    else:
        requested_page = 1
    
    # Get all the trending movies so the home page does not look empty. 
    movie_list, pagination = movie_api.fetch_movies_list('NOW_PLAYING', requested_page)
    
    for movie in movie_list:
        movie['release_date'] = convert_date(movie["release_date"])
        
    context = {
        'movie_list': movie_list,
        'title':'Now Playing Movies',
        'pagination': pagination
    }
    return render(request, 'happy_cherries/movies_list.html', context)

def popular_movies(request):
    """List of all the popular movies"""
    movie_api = MovieDatabase()
    
    if request.method == 'POST':
        requested_page = int(request.POST.get('page', 1))
    else:
        requested_page = 1
    
    # Get all the trending movies so the home page does not look empty. 
    movie_list, pagination = movie_api.fetch_movies_list('POPULAR', requested_page)
    
    for movie in movie_list:
        movie['release_date'] = convert_date(movie["release_date"])
        
    context = {
        'movie_list': movie_list,
        'title':'Popular Movies',
        'pagination': pagination
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
        
        identical_tv_shows = TvShow.objects.filter(id_tvshow=tv_show.id_tvshow)    # Get all the movies with the same ID. 
        
        all_reviews = []
        for iden_tv_show in identical_tv_shows:
            
            all_reviews.extend(iden_tv_show.publicreview_set.all())
        
        if all_reviews:
            
            total_sum = sum(review.score for review in all_reviews)
            tv_show.avg_score = round(total_sum / len(all_reviews), None)
        
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
    
    # Initialize is_delete based on session data
    is_delete = request.session.get('is_delete', False)
        
    if request.method == 'POST':
        if request.POST.get('action') == 'delete_tvshows':
            # Toggle is_delete in the session
            request.session['is_delete'] = True
            return redirect('happy_cherries:tvshows')
        
        if request.POST.get('action') == 'save_tvshows':
            # Toggle is_delete in the session
            request.session['is_delete'] = False
            return redirect('happy_cherries:tvshows')
    
    context = {'tv_shows': tv_shows, 
               'title': 'Library Tv Shows',
               'is_delete': is_delete
               }
    
    return render(request, 'happy_cherries/tvshows.html', context)

@login_required
def tvshows_watchlist(request):
    """Show all the movies added to your watchlist."""
    
    tv_shows = TvShow.objects.filter(owner=request.user, watchlist=True).order_by('date_added')
    
    for tv_show in tv_shows:
        
        identical_tv_shows = TvShow.objects.filter(id_tvshow=tv_show.id_tvshow)    # Get all the movies with the same ID. 
        
        all_reviews = []
        for iden_tv_show in identical_tv_shows:
            
            all_reviews.extend(iden_tv_show.publicreview_set.all())
        
        if all_reviews:
            
            total_sum = sum(review.score for review in all_reviews)
            tv_show.avg_score = round(total_sum / len(all_reviews), None)
        
        note = tv_show.note_set.first()
        # If there is a note set then. 
        if note:
            tv_show.note = note
        
        tv_show.genres = tv_show.genre.split(',')
        tv_show.genres.sort()
    
    context = {'tv_shows': tv_shows, 'title': 'Watchlist Tv Shows'}
    return render(request, 'happy_cherries/tvshows.html', context)
 
@login_required
def tvshows_favorites(request):
    """Show all the movies add to your favorites list."""
    
    tv_shows = TvShow.objects.filter(owner=request.user, favorites=True).order_by('date_added')
    
    for tv_show in tv_shows:
        
        identical_tv_shows = TvShow.objects.filter(id_tvshow=tv_show.id_tvshow)    # Get all the movies with the same ID. 
        
        all_reviews = []
        for iden_tv_show in identical_tv_shows:
            
            all_reviews.extend(iden_tv_show.publicreview_set.all())
        
        if all_reviews:
            
            total_sum = sum(review.score for review in all_reviews)
            tv_show.avg_score = round(total_sum / len(all_reviews), None)
        
        note = tv_show.note_set.first()
        # If there is a note set then. 
        if note:
            tv_show.note = note
        
        tv_show.genres = tv_show.genre.split(',')
        tv_show.genres.sort()
    
    context = {
        'tv_shows': tv_shows, 
        'title': 'Favorite Tv Shows'
        }
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
    
    ext_review = tvshow.extendedtvshowreview_set.first()
    
    check_user(request, tvshow)
    
    is_owner = False
    if request.user.is_authenticated:
        is_owner = True
        
    # Get the note linked to a specific Movie
    note = tvshow.note_set.first() # Get the latest note added
    
    tvshow.cast_spl, tvshow.genres_spl = tvshow.cast.split(','), tvshow.genre.split(',')
    
    # Only show the first 6 six actors if it exceeds limits
    # Because want to acces an object use a dot hore to get acces to the attribute. 
    if len(tvshow.cast_spl) > 6:
        tvshow.cast_spl = tvshow.cast_spl[0:6]
        tvshow.cast_spl.append('...')
    
    # Get the reviews linked to specific movie. 
    # This is the model object, iterate to get all the reviews which then can access the score attr
    identical_tvshows = TvShow.objects.filter(id_tvshow=tvshow.id_tvshow)
    
    all_reviews = []
    all_extended_reviews = []
    for iden_tvshow in identical_tvshows:
        # This line aggregates all reviews related to the identical movies into a single list. It does not add a list as a single item (append would not work).
        all_reviews.extend(iden_tvshow.publicreview_set.all())
        all_extended_reviews.extend(iden_tvshow.extendedtvshowreview_set.all())

    if all_reviews:
        total_sum = sum(review.score for review in all_reviews)
        tvshow.avg_score = round(total_sum/len(all_reviews), None)  
        
    if request.method == 'POST':
        
        action = request.POST.get('action')
        
        if action == "remove_tvshow":
            tvshow.delete()
            # Refresh teh page directly. 
            return redirect('happy_cherries:tvshows')
        
        elif action == 'save_watchlist': 
            tvshow.watchlist = True
            tvshow.save()
            # Refresh teh page directly. 
            return redirect('happy_cherries:tvshow', tvshow_id=tvshow.id)
    
        elif action == 'save_favorite': 
            tvshow.favorites = True
            tvshow.save()
            # Refresh teh page directly. 
            return redirect('happy_cherries:tvshow', tvshow_id=tvshow.id)
        
        elif action == 'remove_favorite':
            tvshow.favorites = False
            tvshow.save()
            return redirect('happy_cherries:tvshow', tvshow_id=tvshow.id)
        
        elif action == 'remove_watchlist':
            tvshow.watchlist = False
            tvshow.save()
            return redirect('happy_cherries:tvshow', tvshow_id=tvshow.id)
        
    context = {
        'tvshow': tvshow, 
        'is_owner': is_owner,
        'reviews': all_reviews,
        'extended_review': ext_review,
        'in_watchlist': tvshow.watchlist,
        'in_favorite': tvshow.favorites, 
        'note': note
        }
    
    return render(request, 'happy_cherries/tvshow.html', context)

@login_required
def delete_tvshow(request, tvshow_id):
    """Makes it so can delete the TvShow from your list."""
    tvshow = get_object_or_404(TvShow, id = tvshow_id)  #Get the TvShow based on the ID parsed in the URL
    
    check_user(request, tvshow) #Check user
    
    context = {'tvshow': tvshow}
    
    if request.method != 'POST':    # If it isnt POST render delete show page
        
        return render(request, 'happy_cherries/delete_show.html', context)
    
    elif request.method == 'POST':  #If a POST then delete the show
        
        tvshow.delete()
        
        return redirect('happy_cherries:tvshows')

def tvshow_search(request):
    """
    Want to show all the results from the search query.
    Show a list with all the movies matching the search query. 
    """
    
    movie_api = MovieDatabase()
    
    if request.method == 'POST':
        
        tvshow_search = request.POST['tvshow_query']
        
        tvshow_list = movie_api.fetch_tvshow(tvshow_search)
        
        for show in tvshow_list:
            show['first_air_date'] = convert_date(show["first_air_date"])
        
        context = {'tvshow_list': tvshow_list}
        
        return render(request, 'happy_cherries/search_tvshow.html', context)
        
    else: # GET request
        
        tvshow_list = movie_api.fetch_tvshows_list('POPULAR')
        
        for show in tvshow_list:
            show['first_air_date'] = convert_date(show["first_air_date"])
        
        context = {'tvshow_list': tvshow_list,}
        
        return render(request, 'happy_cherries/search_tvshow.html', context)
        
def requested_tvshow(request, tvshow_id):
    """
    Want to show a detailed information of all the TvShow.
    This also having the user the option to save the information to his list.
    """
    movie_api = MovieDatabase()
    
    is_owner = False 
    if request.user.is_authenticated:
        is_owner = True
    
    # GET request -- > Show all the detailed information of Tv Show
    if request.method != 'POST':
        # Want to get all the detailed information of a movie. 
        
        tvshow = movie_api.fetch_detailed_tvshow(tvshow_id)
        
        # Because the Cast and Genres are saved in a long string splitted by ',' to save easily in the model direclty.
        # We split the string to then iterate over a list in the HTML file.  
        tvshow['cast'], tvshow['genres'] = tvshow['cast'].split(','), tvshow['genres'].split(',')
        
        # Only show the first 6 six actors if it exceeds limits
        if len(tvshow['cast']) > 6:
            tvshow["cast"] = tvshow["cast"][0:6]
            tvshow["cast"].append('...')
            
        # When logged in. 
        # When logged in. 
        if is_owner:
            # Get all the saved Movie objects from the authenticated user
            saved_tvshow = TvShow.objects.filter(owner=request.user, title=tvshow['title']).first()
            
            # Then pass the variable to tell wether the movie is saved or not. 
            if saved_tvshow: 
                saved = "Saved"
                in_watchlist = saved_tvshow.watchlist
                is_favorite = saved_tvshow.favorites
                
            else: 
                saved  = "Unsaved"
                in_watchlist = is_favorite = False
            
        # When nog logged in it is not saved and can't be saved.    
        else: 
            saved  = "Unsaved"
            in_watchlist = is_favorite = False
        
        context = {'tvshow': tvshow,
                   'saved': saved,
                   'is_owner': is_owner,
                   'in_watchlist': in_watchlist,
                   'is_favorite': is_favorite,
                   }
        
        return render(request, 'happy_cherries/requested_tvshow.html', context)
    
    # POST request -- > Save the Tv Show into a model which then redirected to tvshow homepage.    
    elif request.method == 'POST': 
        
        # Get the current action given by entered Form
        action = request.POST.get('action')
        
        tvshow = movie_api.fetch_detailed_tvshow(tvshow_id)
            
        # Create an instance of the model to save all the information directly into the database. 
        # No need to create Form since have the values predefined
        s = TvShow(title=tvshow['title'],
                   owner=request.user,
                   id_tvshow=tvshow['id'],
                   poster_path=tvshow['poster_path'],
                   overview=tvshow['overview'],
                   first_air_date=tvshow['first_air_date'],
                   last_air_date=tvshow['last_air_date'],
                   next_episode_to_air=tvshow['next_episode_to_air'],
                   number_of_episodes=tvshow['number_of_episodes'],
                   number_of_seasons=tvshow['number_of_seasons'],
                   cast=tvshow['cast'],
                   genre=tvshow['genres'],
                   tagline=tvshow['tagline']
                   )
        
        if action == "save_tvshow":
            
            s.watchlist = s.favorites = False
            s.save()
        
            # Redirect to the movies page after saving
            return redirect('happy_cherries:tvshows')
    
        elif action == 'save_watchlist': 
        
            s.watchlist = True
            s.favorites = False
                
            s.save()
        
            # Redirect to the movies page after saving
            return redirect('happy_cherries:tvshows_watchlist')
    
        elif action == 'save_favorite': 
            
            s.watchlist = False
            s.favorites = True
                
            s.save()
            
            # Redirect to the movies page after saving
            return redirect('happy_cherries:tvshows_favorites')

def top_rated_tvshows(request):
    """
    Get a list of all the trending tvshows
    """
    movie_api = MovieDatabase()
    
    tvshow_list = movie_api.fetch_tvshows_list('TOP_RATED')
    
    for show in tvshow_list:
        show['first_air_date'] = convert_date(show["first_air_date"])
    
    context = {
        'tvshow_list': tvshow_list,
        'title': "Top Rated TV Shows"
    }
    return render(request, 'happy_cherries/tvshows_list.html', context)

def upcoming_tvshows(request):
    """
    Get a list of all the tvshows airing in the next seven days
    """
    movie_api = MovieDatabase()
    
    tvshow_list = movie_api.fetch_tvshows_list('UPCOMING')
    
    for show in tvshow_list:
        show['first_air_date'] = convert_date(show["first_air_date"])
        
    context = {
        'tvshow_list': tvshow_list,
        'title': "On The Air TV Shows"
    }
    return render(request, 'happy_cherries/tvshows_list.html', context)

def now_airing_tvshows(request):
    """
    Get a list of all the tvshows airing today
    """
    movie_api = MovieDatabase()
    
    tvshow_list = movie_api.fetch_tvshows_list('NOW_AIRING')
    
    for show in tvshow_list:
        show['first_air_date'] = convert_date(show["first_air_date"])
        
    context = {
        'tvshow_list': tvshow_list,
        'title': "TV Shows Airing Today"
    }
    return render(request, 'happy_cherries/tvshows_list.html', context)

def popular_tvshows(request):
    """
    Get a list of all the tvshows airing today
    """
    movie_api = MovieDatabase()
    
    tvshow_list = movie_api.fetch_tvshows_list('POPULAR')
    
    for show in tvshow_list:
        show['first_air_date'] = convert_date(show["first_air_date"])
    
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
    review = PublicReview.objects.get(id=review_id)
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

@login_required
def delete_review_movie(request, review_id):
    """Delete the review of a Movie."""
    
    review = get_object_or_404(PublicReview, id=review_id)
    # Get the movie object linked to it. 
    movie = review.movie
    
    context = {'review': review, 'media': movie}
    
    if request.method != 'POST':
        
        return render(request, 'happy_cherries/delete_review_movie.html', context)
    
    elif request.method == 'POST':
        
        review.delete()
        
        return redirect('happy_cherries:movie', movie_id=movie.id)
    

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
def delete_review_tvshow(request, review_id):
    """Delete the review for that specific movie."""
    review = get_object_or_404(PublicReview, id=review_id)
    tvshow = review.tvshow
    
    context = {'review': review, 'tvshow': tvshow}
    
    if request.method != 'POST':
        
        return render(request, 'happy_cherries/delete_review_tvshow.html', context)
        
    elif request.method == 'POST':
        
        review.delete()
        
        return redirect('happy_cherries:tvshow', tvshow_id=tvshow.id)

@login_required
def edit_review_tvshow(request, review_id):
    """Want the user to be able to edit the score or review."""
    review = PublicReview.objects.get(id=review_id)
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

@login_required
def create_extended_review_movie(request, movie_id):
    """
    Create an extended review for bounded specifically to the user itself.
    """

    movie = get_object_or_404(Movie, id=movie_id)
    
    # Check if the owner of the saved movie is the one wanting to add a comment 
    check_user(request, movie)
    
    # Split the saved lists and parse them in the context dictionary
    movie.cast_spl, movie.genre_spl = movie.cast.split(','), movie.genre.split(',')
    
    # Only show the first 6 six actors if it exceeds limits
    # Because want to acces an object use a dot hore to get acces to the attribute. 
    if len(movie.cast_spl) > 6:
        movie.cast_spl = movie.cast_spl[0:6]
        movie.cast_spl.append('...')
    
    ext_review = movie.extendedmoviereview_set.filter(owner=request.user).first()
    
    if request.method != 'POST':
        # A blank form
        if ext_review:
            
            ext_review.first_time_watched= ext_review.first_time_watched.strftime('%m/%d/%Y') if ext_review.first_time_watched else ''
            ext_review.last_time_watched= ext_review.last_time_watched.strftime('%m/%d/%Y') if ext_review.last_time_watched else ''
            ext_review.finish_date= ext_review.finish_date.strftime('%m/%d/%Y') if ext_review.finish_date else ''
            
            form = ExtendedMovieReviewForm(instance=ext_review)
        else: 
            form = ExtendedMovieReviewForm()
        
    else: 
        
        form = ExtendedMovieReviewForm(data=request.POST)
        
        if form.is_valid():
            # Do not save it directly
            extended_review = form.save(commit=False)
            # Link the owner and user to the movie
            extended_review.movie = movie
            extended_review.owner = request.user
            extended_review.date_added = timezone.now()
            
            if ext_review:
                extended_review.id = ext_review.id
            
            # Save the extended review
            extended_review.save()
            
            return redirect('happy_cherries:movie', movie_id=movie.id)
    
    # Reformat the dates from "Nov. 4, 2024" to "11/04/2024"
    
    context = {'form': form,'movie': movie}
    return render(request, 'happy_cherries/movie_extendedreview.html', context)

@login_required
def create_extended_review_tvshow(request, tvshow_id):
    
    tvshow = get_object_or_404(TvShow, id=tvshow_id)
    
    check_user(request, tvshow)
    
    tvshow.cast_spl, tvshow.genres_spl = tvshow.cast.split(','), tvshow.genre.split(',')
    
    # Only show the first 6 six actors if it exceeds limits
    # Because want to acces an object use a dot hore to get acces to the attribute. 
    if len(tvshow.cast_spl) > 6:
        tvshow.cast_spl = tvshow.cast_spl[0:6]
        tvshow.cast_spl.append('...')
    
    ext_review = tvshow.extendedtvshowreview_set.filter(owner=request.user).first()
    
    if request.method != 'POST':
        
        # A blank form
        if ext_review:
            
            ext_review.start_date= ext_review.start_date.strftime('%m/%d/%Y') if ext_review.start_date else ''
            ext_review.finish_date= ext_review.finish_date.strftime('%m/%d/%Y') if ext_review.finish_date else ''

            form = ExtendedTvShowReviewForm(instance=ext_review)
        else:
                  
            form = ExtendedTvShowReviewForm()
        
    elif request.method == 'POST':
        
        form = ExtendedTvShowReviewForm(data=request.POST)
        
        if form.is_valid():
            
            extended_review = form.save(commit=False)
            # Set the Movie as User to the object
            extended_review.tvshow = tvshow
            extended_review.owner = request.user
            extended_review.date_added= timezone.now()
            
            if ext_review:
                extended_review.id = ext_review.id
            
            extended_review.save()
            
            return redirect('happy_cherries:tvshow', tvshow_id=tvshow.id)
    
    context = {'form': form, 'tvshow': tvshow}
    return render(request, 'happy_cherries/tvshow_extendedreview.html', context)