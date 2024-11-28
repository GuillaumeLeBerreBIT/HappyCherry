import requests, json
from .variables import GENRES_MOVIES, GENRES_TVSHOWS

class MovieDatabase():
    
    def __init__(self):
        
        self.base_url = ""
        
        self.headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
        }
        # Query results for a movie search
        self.base_url = "https://api.themoviedb.org/3/"
        self.url_poster = "https://image.tmdb.org/t/p/w500/{}"
        
        self.search_movie_url = "search/movie?query={}&include_adult=false&language=en-US&page=1"
        self.det_movie_url = "movie/{}?language=en-US"
        self.credits_movie_url = "movie/{}/credits?language=en-US"
        
        self.search_tvshow_url = "search/tv?query={}&include_adult=false&language=en-US&page=1"
        self.url_det_tvshow = "tv/{}?language=en-US"
        self.url_credits_tvshow = "tv/{}/credits?language=en-US"
        
        self.GENRES_MOVIES = GENRES_MOVIES
        self.GENRES_TVSHOWS = GENRES_TVSHOWS
    
    def get_url_path(self, endpoint, media):
        """Configure the correct URL endpoint."""
        
        if endpoint.upper() == "TRENDING":
            url = "trending/movie/day?language=en-US"
            
        elif endpoint.upper() == "TOP_RATED": 
            url = f"{media}/top_rated?language=en-US&page=1"
        
        elif endpoint.upper() == "UPCOMING": 
            if media == 'movie':
                url = "movie/upcoming?language=en-US&page=1"
            else: 
                url = "tv/on_the_air?language=en-US&page=1"
        
        elif endpoint.upper() == "NOW_PLAYING": 
            url = "movie/now_playing?language=en-US&page=1"
            
        elif endpoint.upper() == "NOW_AIRING":
            url = "tv/airing_today?language=en-US&page=1"
        
        elif endpoint.upper() == "POPULAR": 
            if media == 'movie':
                url = f"{media}/popular?language=en-US&page=1"
            else: 
                url = f"{media}/popular?language=en-US&page=1"
                    
        return url
    
    def convert_ids_genre(self, ids, genres):
        """Need to convert the ids to representative genre"""
        
        genre_list = []
        for i in ids:
            for genre in genres:
                if i == genre['id']:
                    genre_list.append(genre["name"])
        
        return genre_list

    def fetch_movies(self, movie_query):
        """
        Will show the movies through dynamic search on the page.
        """
        # Want the response to be in JSON format. 
        response = requests.get(self.base_url + self.search_movie_url.format(movie_query), headers=self.headers).json() 

        movie_list = []
        for sq in response['results']:
            
            # Fetch all essential information. 
            # A trick: in the HTML when wanting to parse specific information such as an id.
            # Can then make a link directly to specific item using the ID given to the object or movie.  
            requested_data = {
                'id': sq['id'],
                'poster': self.url_poster.format(sq['poster_path']),
                'genre_ids': sq['genre_ids'],
                'title': sq['title'],
                'release_date': sq['release_date'],
            }
            
            requested_data["genres"] = self.convert_ids_genre(requested_data["genre_ids"], self.GENRES_MOVIES)
            
            # Add each movie to a list.
            movie_list.append(requested_data)
        
        # Return the movie list.
        return movie_list
    
    def fetch_movies_list(self, endpoint_type):
        """Get all the trending/upcoming/popular movies to show on the page when searching for a movie."""
        
        url = self.get_url_path(endpoint_type, 'movie')
        response = requests.get(self.base_url + url , headers=self.headers).json()
        
        movie_list = []
        for sq in response['results']:
            
            requested_data = {
                'id': sq['id'],
                'poster': self.url_poster.format(sq['poster_path']),
                'genre_ids': sq['genre_ids'],
                'title': sq['title'],
                'release_date': sq['release_date'],
            }
            
            requested_data["genres"] = self.convert_ids_genre(requested_data["genre_ids"], self.GENRES_MOVIES)
            
            movie_list.append(requested_data)
        
        return movie_list 
    
    def fetch_detailed_movie(self, movie_id):
        """
        This function will manage to get all the essential information of a specific movie. 
        """
        # API Request using the movie ID and convert JSON-format into Dictionary.
        response = requests.get(self.base_url + self.det_movie_url.format(movie_id), headers=self.headers).json()
        
        # Genre
        # Because easy to save the genres in the Model Movie as a string seperated by ','.
        genres = ""
        for genre in response['genres']:
            genres += f"{genre['name']},"
        # Remove the last ',' from the string
        genres = genres[:-1]

        # Cast -- > API Request using the movie ID and convert JSON-format into Dictionary.
        response_credits = requests.get(self.base_url + self.credits_movie_url.format(movie_id), headers=self.headers).json()
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
            'poster': self.url_poster.format(response['poster_path']),
            'runtime': response['runtime'],
            'status': response['status'],
            'tagline': response['tagline'],
            'overview': response['overview'],
            'genres': genres,
            'cast': actors,
        }
        
        return movie_info
    
    def fetch_tvshow(self, search):
        """Want to get all the results from the search query."""
        # Using the input name, will return a Dynamic search with all Shows related to the name
        response = requests.get(self.base_url + self.search_tvshow_url.format(search), headers=self.headers).json()
        
        tvshow_list = []
        for sq in response['results']:
            
            requested_data = {
                'id': sq['id'],
                'poster': self.url_poster.format(sq['poster_path']),
                'genre_ids': sq['genre_ids'],
                'title': sq['name'],
                'first_air_date': sq['first_air_date'],
            }
            
            requested_data["genres"] = self.convert_ids_genre(requested_data["genre_ids"], self.GENRES_TVSHOWS)
            
            tvshow_list.append(requested_data)
        
        return tvshow_list

    def fetch_tvshows_list(self, endpoint_type):
        """Get a list of all the trending Tv Shows to show on the search page."""
        
        url = self.get_url_path(endpoint_type, 'tv')
        response = requests.get(self.base_url + url, headers=self.headers).json()
        
        tvshow_list = []
        for tvshow in response['results']:
            
            tvshow = {
                "id": tvshow['id'],
                "poster": self.url_poster.format(tvshow['poster_path']),
                "title": tvshow['name'],
                "genre_ids": tvshow['genre_ids'],
                "first_air_date": tvshow['first_air_date']
            }
            
            tvshow["genres"] = self.convert_ids_genre(tvshow["genre_ids"], self.GENRES_TVSHOWS)
            
            tvshow_list.append(tvshow)
        
        return tvshow_list
        

    def fetch_detailed_tvshow(self, tvshow_id):
        """Get all the information of a specific Tv Show."""
        
        # API Request using the movie ID and convert JSON-format into Dictionary.
        response = requests.get( self.base_url + self.url_det_tvshow.format(tvshow_id), headers=self.headers).json()
        
        # Genre
        # Because easy to save the genres in the Model Movie as a string seperated by ','.
        genres = ""
        for genre in response['genres']:
            genres += f"{genre['name']},"
        # Remove the last ',' from the string
        genres = genres[:-1]

        # Cast -- > API Request using the movie ID and convert JSON-format into Dictionary.
        response_credits = requests.get(self.base_url + self.url_credits_tvshow.format(tvshow_id), headers=self.headers).json()
        # Because easy to save the genres in the Model Movie as a string seperated by ','.
        actors = ""
        for c in response_credits['cast']:
            actors += f"{c['name']},"
        # Remove the last ',' from the string
        actors = actors[:-1]
        
        # Save all the necassary information in a dictionary. 
        tvshow_info = {
            'id': response['id'],
            'title': response['name'],
            'first_air_date':response['first_air_date'],
            'last_air_date': response['last_air_date'],
            'poster_path': self.url_poster.format(response['poster_path']),
            'number_of_seasons': response['number_of_seasons'],
            'number_of_episodes': response['number_of_episodes'],
            'overview': response['overview'],
            'genres': genres,
            'cast': actors,
            'tagline': response['tagline'],
            #'seasons':response['seasons']
        }
        
        if response['next_episode_to_air']:
            tvshow_info['next_episode_to_air'] = response['next_episode_to_air']['air_date']
        else:
            tvshow_info['next_episode_to_air'] = None
        
        return tvshow_info