
Want to access each review to a specific User. Since the Reviews are linked with PK can get acces to them to the attributes from the upper classes. 

for review in Review.objects.all():
...     dir(review.movie)
...
[...... 'cast', 'check', 'clean', 'clean_fields', 'date_added', 'date_error_message', 'delete', 'from_db', 'full_clean', 'genre', 'get_constraints', 'get_deferred_fields', 'get_next_by_date_added', 'get_next_by_release_date', 'get_previous_by_date_added', 'get_previous_by_release_date', 'id', 'id_movie', 'objects', 'overview', 'owner', 'owner_id', 'pk', 'poster_path', 'prepare_database_save', 'refresh_from_db', 'release_date', 'review_set', 'runtime', 'save', 'save_base', 'serializable_value', 'status', 'tagline', 'title']

Which shows can access each owner for the specific Topic. 

>>> for review in Review.objects.all():   
...     print(review.movie.owner)          
...
hc_admin
hc_admin