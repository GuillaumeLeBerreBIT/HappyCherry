import requests, json

# MOVIES 
def fetch_movies(headers, movie_query, url_movie_search):
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
            'poster': sq['poster_path'],
            'genre_ids': sq['genre_ids'],
            'title': sq['title'],
            'release_date': sq['release_date'],
        }
        # Add each movie to a list.
        movie_list.append(requested_data)
    
    # Return the movie list.
    return movie_list

def fetch_trending_movies(headers, url_trending):
    """Get all the trending movies to show on the page when searching for a movie."""
    response = requests.get(url_trending, headers=headers).json()
    
    movie_list = []
    for sq in response['results']:
        requested_data = {
            'id': sq['id'],
                'poster': sq['poster_path'],
                'genre_ids': sq['genre_ids'],
                'title': sq['title'],
                'release_date': sq['release_date'],
        }
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
def fetch_tvshow(headers, url_tvshow, search):
    """Want to get all the results from the search query."""
    # Using the input name, will return a Dynamic search with all Shows related to the name
    response = requests.get(url_tvshow.format(search), headers=headers).json()
    
    tvshow_list = []
    for sq in response['results']:
        
        requested_data = {
            'id': sq['id'],
            'poster': sq['poster_path'],
            'genre_ids': sq['genre_ids'],
            'name': sq['name'],
            'first_air_date': sq['first_air_date'],
        }
        
        tvshow_list.append(requested_data)
    
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