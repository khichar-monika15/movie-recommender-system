import os
import pickle
import requests
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity

TMDB_KEY = "8265bd1679663a7ea12ac168da84d2e8"
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")


@st.cache_resource
def load_models():
    movies  = pickle.load(open(os.path.join(MODEL_DIR, "movie_list.pkl"),  "rb"))
    sim     = pickle.load(open(os.path.join(MODEL_DIR, "similarity.pkl"),  "rb"))
    vec     = pickle.load(open(os.path.join(MODEL_DIR, "vectorizer.pkl"),  "rb"))
    vectors = pickle.load(open(os.path.join(MODEL_DIR, "vectors.pkl"),     "rb"))
    return movies, sim, vec, vectors


def fetch_poster(movie_id):
    try:
        data = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_KEY}&language=en-US",
            timeout=5,
        ).json()
        path = data.get("poster_path", "")
        return f"https://image.tmdb.org/t/p/w500{path}" if path else "https://placehold.co/500x750?text=No+Poster"
    except Exception:
        return "https://placehold.co/500x750?text=No+Poster"


def recommend_static(movie, movies, similarity):
    idx = movies[movies["title"] == movie].index[0]
    distances = sorted(enumerate(similarity[idx]), reverse=True, key=lambda x: x[1])
    names, posters = [], []
    for i, _ in distances[1:6]:
        names.append(movies.iloc[i].title)
        posters.append(fetch_poster(movies.iloc[i].movie_id))
    return names, posters


def fetch_tmdb_tags(title):
    try:
        results = requests.get(
            f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={title}",
            timeout=5,
        ).json().get("results", [])
        if not results:
            return None, None, None
        movie    = results[0]
        mid      = movie["id"]
        details  = requests.get(f"https://api.themoviedb.org/3/movie/{mid}?api_key={TMDB_KEY}", timeout=5).json()
        credits  = requests.get(f"https://api.themoviedb.org/3/movie/{mid}/credits?api_key={TMDB_KEY}", timeout=5).json()
        keywords = requests.get(f"https://api.themoviedb.org/3/movie/{mid}/keywords?api_key={TMDB_KEY}", timeout=5).json()
        genres   = [g["name"].replace(" ", "") for g in details.get("genres", [])]
        cast     = [c["name"].replace(" ", "") for c in credits.get("cast", [])[:3]]
        crew     = [c["name"].replace(" ", "") for c in credits.get("crew", []) if c["job"] == "Director"]
        kws      = [k["name"].replace(" ", "") for k in keywords.get("keywords", [])[:5]]
        overview = details.get("overview", "").split()[:20]
        tags     = " ".join(genres + cast + crew + kws + overview).lower()
        poster   = (
            f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}"
            if movie.get("poster_path") else None
        )
        return tags, movie.get("title", title), poster
    except Exception:
        return None, None, None


def recommend_live(title, movies, vectorizer, vectors):
    tags, canonical, _ = fetch_tmdb_tags(title)
    if tags is None:
        return None, None, None
    new_vec    = vectorizer.transform([tags]).toarray()
    sim_scores = cosine_similarity(new_vec, vectors)[0]
    top        = sorted(enumerate(sim_scores), reverse=True, key=lambda x: x[1])[:5]
    names, posters = [], []
    for idx, _ in top:
        m = movies.iloc[idx]
        names.append(m["title"])
        posters.append(fetch_poster(m["movie_id"]))
    return names, posters, canonical


# ── UI ────────────────────────────────────────────────────────────────────────
st.title("Movie Recommender System")
st.caption("Content-based recommendations · Static dataset + Live TMDB API for recent films")

movies, similarity, vectorizer, vectors = load_models()
movie_list = movies["title"].values

search_query   = st.text_input(
    "Search any movie (including recent releases):",
    placeholder="e.g. Dhurandhar 2",
)
selected_movie = st.selectbox("Or select from the training dataset:", movie_list)

if st.button("Show Recommendations"):
    query = search_query.strip() if search_query.strip() else selected_movie

    if query in movie_list:
        names, posters = recommend_static(query, movies, similarity)
        st.subheader(f"Movies similar to: {query}")
    else:
        with st.spinner(f"'{query}' not in training data — fetching from TMDB Live API..."):
            result = recommend_live(query, movies, vectorizer, vectors)
        if result[0] is None:
            st.error(f"Could not find '{query}' on TMDB. Check the spelling.")
            st.stop()
        names, posters, canonical = result
        st.subheader(f"Movies similar to: {canonical}")
        st.info("Sourced via TMDB Live API — this film was released after the training dataset was compiled.")

    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            st.image(poster)
