import requests, json

# VARIABLES
genres_movies = [
    {'id': 28, 'name': 'Action'},
    {'id': 12, 'name': 'Adventure'},
    {'id': 16, 'name': 'Animation'},
    {'id': 35, 'name': 'Comedy'},
    {'id': 80, 'name': 'Crime'},
    {'id': 99, 'name': 'Documentary'},
    {'id': 18, 'name': 'Drama'},
    {'id': 10751, 'name': 'Family'},
    {'id': 14, 'name': 'Fantasy'},
    {'id': 36, 'name': 'History'},
    {'id': 27, 'name': 'Horror'},
    {'id': 10402, 'name': 'Music'},
    {'id': 9648, 'name': 'Mystery'},
    {'id': 10749, 'name': 'Romance'},
    {'id': 878, 'name': 'Science Fiction'},
    {'id': 10770, 'name': 'TV Movie'},
    {'id': 53, 'name': 'Thriller'},
    {'id': 10752, 'name': 'War'},
    {'id': 37, 'name': 'Western'}
    ]

genres_tvshows = [
    {
      "id": 10759,
      "name": "Action & Adventure"
    },
    {
      "id": 16,
      "name": "Animation"
    },
    {
      "id": 35,
      "name": "Komödie"
    },
    {
      "id": 80,
      "name": "Krimi"
    },
    {
      "id": 99,
      "name": "Dokumentarfilm"
    },
    {
      "id": 18,
      "name": "Drama"
    },
    {
      "id": 10751,
      "name": "Familie"
    },
    {
      "id": 10762,
      "name": "Kids"
    },
    {
      "id": 9648,
      "name": "Mystery"
    },
    {
      "id": 10763,
      "name": "News"
    },
    {
      "id": 10764,
      "name": "Reality"
    },
    {
      "id": 10765,
      "name": "Sci-Fi & Fantasy"
    },
    {
      "id": 10766,
      "name": "Soap"
    },
    {
      "id": 10767,
      "name": "Talk"
    },
    {
      "id": 10768,
      "name": "War & Politics"
    },
    {
      "id": 37,
      "name": "Western"
    }
]
def convert_ids_genre(ids, genres):
    """Need to convert the ids to representative genre"""
    
    genre_list = []
    for i in ids:
        for genre in genres:
            if i == genre['id']:
                genre_list.append(genre["name"])
    
    return genre_list

# MOVIES 
def fetch_movies(headers, movie_query, url_movie_search, url_poster):
    """Will show the movies through dynamic search on the page."""
    # Want the response to be in JSON format. 
    response = requests.get(url_movie_search.format(movie_query), headers=headers).json() 

    movie_list = []
    for sq in response['results']:
        
        # Fetch all essential information. 
        # A trick: in the HTML when wanting to parse specific information such as an id.
        # Can then make a link directly to specific item using the ID given to the object or movie.  
        requested_data = {
            'id': sq['id'],
            'poster': url_poster.format(sq['poster_path']),
            'genre_ids': sq['genre_ids'],
            'title': sq['title'],
            'release_date': sq['release_date'],
        }
        
        requested_data["genres"] = convert_ids_genre(requested_data["genre_ids"], genres_movies)
        
        # Add each movie to a list.
        movie_list.append(requested_data)
    
    # Return the movie list.
    return movie_list

def fetch_trending_rated_upcoming_popular_movies(headers, url_trending, url_poster):
    """Get all the trending movies to show on the page when searching for a movie."""
    response = requests.get(url_trending, headers=headers).json()
    
    movie_list = []
    for sq in response['results']:
        requested_data = {
                'id': sq['id'],
                'poster': url_poster.format(sq['poster_path']),
                'genre_ids': sq['genre_ids'],
                'title': sq['title'],
                'release_date': sq['release_date'],
        }
        
        requested_data["genres"] = convert_ids_genre(requested_data["genre_ids"], genres_movies)
        
        movie_list.append(requested_data)
    
    return movie_list

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


# TVSHOWS
def fetch_tvshow(headers, url_tvshow, search, url_poster):
    """Want to get all the results from the search query."""
    # Using the input name, will return a Dynamic search with all Shows related to the name
    response = requests.get(url_tvshow.format(search), headers=headers).json()
    
    tvshow_list = []
    for sq in response['results']:
        
        requested_data = {
            'id': sq['id'],
            'poster': url_poster.format(sq['poster_path']),
            'genre_ids': sq['genre_ids'],
            'name': sq['name'],
            'first_air_date': sq['first_air_date'],
        }
        
        requested_data["genres"] = convert_ids_genre(requested_data["genre_ids"], genres_tvshows)
        
        tvshow_list.append(requested_data)
    
    return tvshow_list

def fetch_trending_tvshows(headers, url_trending, url_poster):
    """Get a list of all the trending Tv Shows to show on the search page."""
    
    response = requests.get(url_trending, headers=headers).json()
    
    tvshow_list = []
    for tvshow in response['results']:
        
        tvshow = {
            "id": tvshow['id'],
            "poster": url_poster.format(tvshow['poster_path']),
            "name": tvshow['name'],
            "genre_ids": tvshow['genre_ids'],
            "first_air_date": tvshow['first_air_date']
        }
        
        tvshow["genres"] = convert_ids_genre(tvshow["genre_ids"], genres_tvshows)
        
        tvshow_list.append(tvshow)
    
    return tvshow_list
    

def fetch_detailed_tvshow(headers, tvshow_id, url_tvshow, url_cast, url_poster):
    """Get all the information of a specific Tv Show."""
    
    # API Request using the movie ID and convert JSON-format into Dictionary.
    response = requests.get(url_tvshow.format(tvshow_id), headers=headers).json()
    
    # Genre
    # Because easy to save the genres in the Model Movie as a string seperated by ','.
    genres = ""
    for genre in response['genres']:
        genres += f"{genre['name']},"
    # Remove the last ',' from the string
    genres = genres[:-1]

    # Cast -- > API Request using the movie ID and convert JSON-format into Dictionary.
    response_credits = requests.get(url_cast.format(tvshow_id), headers=headers).json()
    # Because easy to save the genres in the Model Movie as a string seperated by ','.
    actors = ""
    for c in response_credits['cast']:
        actors += f"{c['name']},"
    # Remove the last ',' from the string
    actors = actors[:-1]
    print(actors)
    # Save all the necassary information in a dictionary. 
    tvshow_info = {
        'id': response['id'],
        'name': response['name'],
        'first_air_date': response['first_air_date'],
        'last_air_date': response['last_air_date'],
        'poster_path': url_poster.format(response['poster_path']),
        'next_episode_to_air': response['next_episode_to_air'],
        'number_of_seasons': response['number_of_seasons'],
        'number_of_episodes': response['number_of_episodes'],
        'overview': response['overview'],
        'genres': genres,
        'cast': actors,
        #'seasons':response['seasons']
    }
    
    return tvshow_info