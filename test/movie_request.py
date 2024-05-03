import requests, json

# GET THE MOVIE ID
url = "https://api.themoviedb.org/3/search/movie?query=Civil%20War&include_adult=false&language=en-US&page=1"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTEwZTMzYzBiNzM5NWJhYWI2Nzg4MDJlOTkzMTJlYiIsInN1YiI6IjY2MjkxM2I5ZTI5NWI0MDE4NzllMTBiYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IwgWzjezREKj75fLbuLlK-Kp03z_yRyRcQaUJai68l0"
}

#response = requests.get(url, headers=headers).json()

#print(response['results'][0:10])
"""
movie_list = []
for sq in response['results']:
    
    form_data = {
        'id': sq['id'],
        'poster': sq['poster_path'],
        'genre_ids': sq['genre_ids'],
        'original_title': sq['original_title'],
        'overview': sq['overview'],
        'release_date': sq['release_date'],
    }
    movie_list.append(form_data)
#print(movie_list)
"""
url = "https://api.themoviedb.org/3/movie/929590?language=en-US"

url = "https://api.themoviedb.org/3/trending/movie/week?language=en-US"

response = requests.get(url, headers=headers).json()
print(response)



#genres = ""
#for genre in response['genres']:
#    genres += f"{genre['name']},"
#genres = genres[:-1]
#print(genres)

#response = requests.get(f"https://api.themoviedb.org/3/movie/929590/credits?language=en-US", 
#                            headers=headers).json()
#print(response)

#for actor in response['cast']:
    #print(actor['name'])


"""
form_data = {
    'id': movie['results'][0]['id'],
    'genre_ids': movie['results'][0]['genre_ids'],
    'original_title': movie['results'][0]['original_title'],
    'overview': movie['results'][0]['overview'],
    'release_date': movie['results'][0]['release_date'],
}

# GET THE POSTER TO DISPLAY THE PICTURE
# Can use the Poster path to show the Image. 
form_data['poster_path'] = f"https://image.tmdb.org/t/p/w500/{movie['results'][0]['poster_path']}"

# GET THE CREDITS OF THE MOVIE. 
url = f"https://api.themoviedb.org/3/movie/{movie['results'][0]['id']}/credits?language=en-US"

response = requests.get(url, headers=headers)

credits_dict = response.json()

# GET THE MOST IMPORTANT CAST MEMBERS
#print(credits_dict) # The keys returned will be -- > id, cast, crew
cast = []

for castmember in credits_dict['cast'][0:6]:
    
    cast.append(castmember['name'])
    
form_data['cast'] = cast

# GENRES >> Need to convert 
url = "https://api.themoviedb.org/3/genre/movie/list?language=en"

response = requests.get(url, headers=headers)

movie_genres = []

genres = response.json()
for genre in genres['genres']:
    
    if genre['id'] in movie['results'][0]['genre_ids']:
        movie_genres.append(genre['name'])

form_data['genres'] = movie_genres
"""
#print(form_data)