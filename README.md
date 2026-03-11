# HappyCherry

A personal media tracking web app built with Django. Track movies and TV shows you've watched, want to watch, or have in your favorites. Integrates with The Movie Database (TMDB) API to browse and add new titles.

---

## Features

- Browse and search movies and TV shows via TMDB API
- Personal library, watchlist, and favorites lists
- Quick reviews (score + text) and extended reviews (status, priority, rewatch value, etc.)
- Episode and season tracking for TV shows
- Per-item notes on TV shows
- User authentication (register, login, logout)

---

## Tech Stack

- **Backend:** Python 3, Django 5.0.4
- **Database:** SQLite (development)
- **Frontend:** Bootstrap 5, jQuery 3.3.1, django-bootstrap5
- **External API:** TMDB (The Movie Database)

---

## Getting Started

### Prerequisites

- Python 3.10+
- A TMDB API Bearer Token ([get one here](https://www.themoviedb.org/settings/api))

### Setup

```bash
# Clone the repo
git clone <repo-url>
cd HappyCherry

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (see Configuration below)
cp .env.example .env
# Edit .env with your values

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Start the dev server
python manage.py runserver
```

### Configuration

The app currently has credentials hardcoded — before running or sharing the project, these must be moved to environment variables:

| Variable | Location | Description |
|---|---|---|
| `SECRET_KEY` | `happy_cherry/settings.py` | Django secret key |
| `TMDB_BEARER_TOKEN` | `happy_cherries/TMDB_API.py` | TMDB API auth header |
| `DEBUG` | `happy_cherry/settings.py` | Set to `False` in production |

---

## Project Structure

```
HappyCherry/
├── happy_cherry/          # Django project settings & root URLs
├── happy_cherries/        # Main feature app
│   ├── models.py          # Movie, TvShow, Review, ExtendedReview, Note
│   ├── views.py           # All view logic (~1400 lines)
│   ├── urls.py            # 44 URL patterns
│   ├── forms.py           # Model forms
│   ├── TMDB_API.py        # TMDB API integration
│   ├── variables.py       # Genre ID mappings
│   ├── css/styles.css     # Custom styles
│   └── templates/         # 21 HTML templates
├── users/                 # Auth app (register + Django built-in auth)
└── db.sqlite3             # SQLite database
```

---

## Areas for Improvement

This section tracks known technical debt and planned improvements, roughly ordered by priority.

---

### Security (Fix before any deployment)

- [ ] **Move `SECRET_KEY` to environment variable** — currently hardcoded in `settings.py`
- [ ] **Move TMDB Bearer Token to environment variable** — currently hardcoded in `TMDB_API.py`
- [ ] **Set `DEBUG = False` via environment variable** — never commit `True`
- [ ] **Configure `ALLOWED_HOSTS`** — currently empty, will reject all requests in production
- [ ] **Add `.env` support** — use `python-decouple` or `django-environ`

---

### Views — Reduce Duplication (~400+ duplicate lines)

`views.py` is 1372 lines. The same patterns repeat for every movie/TV show combination.

- [ ] **Consolidate `movies()`, `movies_watchlist()`, `movies_favorites()`** — all three are identical except for a queryset filter. A single view with a `filter_type` parameter (or a shared helper) would cut ~150 lines.
- [ ] **Do the same for the TV show equivalents** — `tvshows()`, `tvshows_watchlist()`, `tvshows_favorites()`
- [ ] **Extract the review-aggregation block** — the `avg_score` calculation (iterating public reviews) is copy-pasted into every library view. Move it to a model method or a manager.
- [ ] **Remove leftover `print()` debug statements** — at least one in `index()` (line ~38) and one in `forms.py` `ExtendedMovieReviewForm.clean()`
- [ ] **Split `views.py` into multiple files** — e.g., `views/movies.py`, `views/tvshows.py`, `views/reviews.py`, `views/browse.py`. Import them back in `views/__init__.py`.

---

### Templates — Reduce from 21 to ~10

Most template pairs (movie vs TV show) are structurally identical with only field name differences.

| Can be merged into one | Current files |
|---|---|
| Single detail page (`media_detail.html`) | `movie.html` (330 lines) + `tvshow.html` (359 lines) |
| Single extended review page | `movie_extendedreview.html` + `tvshow_extendedreview.html` |
| Single search/results page | `search_movie.html` + `search_tvshow.html` + `requested_movie.html` + `requested_tvshow.html` |
| Single form page | `add_review_movie.html` + `add_review_tvshow.html` + `edit_review_movie.html` + `edit_review_tvshow.html` |
| Single note form page | `add_note_tvshow.html` + `edit_note_tvshow.html` |
| Single delete confirm page | `delete_movie.html` + `delete_show.html` + `delete_review_movie.html` + `delete_review_tvshow.html` |

Strategy: pass a `media_type` context variable (`"movie"` or `"tvshow"`) and use `{% if media_type == "movie" %}` for the handful of differing fields.

- [ ] **Merge detail pages** into `media_detail.html`
- [ ] **Merge all form pages** into one generic `form.html` (they all just render `{{ form|bootstrap5 }}`)
- [ ] **Merge all delete confirmation pages** into one `confirm_delete.html`
- [ ] **Move all inline CSS from `base.html`** (~196 lines) into `css/styles.css` — keeps the template clean

---

### JavaScript — Add Client-Side Interactivity

Currently there is almost no custom JS; everything is full page reloads.

- [ ] **Add/remove from watchlist & favorites via fetch() (AJAX)** — no need to reload the page to toggle a heart or bookmark icon. Add Django REST endpoints returning JSON.
- [ ] **Live search suggestions** — as the user types in the search box, query TMDB and show a dropdown of results without a full page reload.
- [ ] **Score input as a visual rating widget** — replace the plain number input with a star or slider component.
- [ ] **Confirm delete with a modal** — instead of a separate delete confirmation page, pop a Bootstrap modal inline. Eliminates 4 templates entirely.
- [ ] **Move datepicker activation to a JS file** — currently the datepicker library is loaded via CDN but activation logic is inconsistent.
- [ ] **Extract all inline `<script>` blocks from `base.html`** into a `static/js/app.js` file.

---

### Database / Models

- [ ] **Normalize genres** — `genre = CharField(300)` stores comma-separated strings (e.g. `"Action,Drama"`). Should be a `ManyToManyField` to a `Genre` model.
- [ ] **Normalize cast** — same issue as genres; a `Person` model with a M2M to each media item is more queryable.
- [ ] **Add database indexes** — `owner`, `date_added`, `watchlist`, `favorites` are filtered constantly but have no indexes.
- [ ] **Rename `id_movie` / `id_tvshow`** to `tmdb_id` — clearer naming.
- [ ] **Consolidate `ExtendedMovieReview` and `ExtendedTvShowReview`** using Django's `GenericForeignKey` (content types framework) — one model instead of two nearly identical ones.
- [ ] **Add pagination to library views** — currently all user items are loaded in one query; will get slow.
- [ ] **Add `unique_together` constraints** — a user should not be able to add the same TMDB title twice.

---

### URL Configuration

- [ ] **Reduce 44 URL patterns** — movie and TV show endpoints are mirrors of each other. A `media_type` path prefix (`/media/<str:media_type>/`) could halve the pattern count.
- [ ] **Consistent parameter names** — currently mixes `movie_id`, `tvshow_id`, `review_id`, and `pk`. Standardize to `pk` or `<media_type>_id`.

---

### Static Files

- [ ] **Configure Django static files properly** — set `STATIC_URL`, `STATICFILES_DIRS`, and `STATIC_ROOT` in `settings.py`. Currently CSS uses a relative path (`./css/styles.css`) which is fragile.
- [ ] **Move CSS into `static/` directory** — follow Django conventions so `{% static %}` tags work correctly.

---

### Code Quality / Dev Experience

- [ ] **Add a `requirements.txt`** — not currently in the repo
- [ ] **Add a `.env.example`** file documenting required environment variables
- [ ] **Add tests** — the `test/` directory has only `movie_request.py`. At minimum, add model tests and a few view integration tests.
- [ ] **Remove all `print()` debug statements** from production code
- [ ] **Extract TMDB API calls into a service class** — currently the raw API functions are called directly from views; wrapping them in a `TMDBService` class makes mocking and testing easier.
- [ ] **Add a `Makefile` or `justfile`** with common dev commands (`make migrate`, `make run`, `make test`)

---

### Longer-term / Nice to Have

- [ ] Switch from SQLite to PostgreSQL for production
- [ ] Add sorting and filtering (by genre, year, score, date added) to all list views
- [ ] Statistics page — total watch time, top genres, score distribution
- [ ] Bulk operations — mark multiple items as watched, export list to CSV
- [ ] Caching for TMDB API responses (avoid redundant calls for the same title)
- [ ] Dark/light mode toggle
- [ ] Responsive mobile improvements (sidebar collapses cleanly on small screens)
