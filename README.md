# Movie Recommender System

A content-based movie recommendation engine deployed on Streamlit Community Cloud. Recommends similar films using TF-IDF vectors and cosine similarity — and handles movies released after the training data using a **live TMDB API fallback**.

---

## Features

- Recommend 5 similar movies for any title from the TMDB 5000 dataset (4806 movies)
- **Live API fallback for recent releases** — if a movie isn't in the training data (e.g. *Dhurandhar 2*, released March 2026), the app fetches its metadata from TMDB's API at runtime, builds the same feature vector as the training pipeline, and computes similarity on the fly. No retraining needed.
- Movie posters fetched live from TMDB
- Info banner shown when results come from the live API path vs. the static dataset

## How It Works

**Static path (training dataset):**
- Each movie has a tag string combining genres, top 3 cast, director, keywords, and overview
- CountVectorizer (5000 features, English stop words removed) converts tags to vectors
- Cosine similarity is precomputed across all 4806 movies and saved to disk
- Recommendations = index lookup + sort on the precomputed matrix

**Live API path (movies not in dataset):**
1. Calls TMDB Search API to find the movie
2. Fetches genres, top cast, director, keywords, and overview
3. Builds the **same tag string** format as the training pipeline
4. Transforms using the **saved CountVectorizer** (same feature space, no refit)
5. Computes cosine similarity against all training vectors at runtime

The key design decision: saving the fitted CountVectorizer alongside the similarity matrix means new movies can be vectorized in the exact same feature space as the training data and compared directly.

## Tech Stack

| Layer | Technology |
|---|---|
| App framework | Streamlit |
| ML | scikit-learn (CountVectorizer, cosine similarity) |
| Dataset | TMDB 5000 Movies (Kaggle) |
| Live data | TMDB API |
| Model storage | Git LFS (large pkl files) |
| Deployment | Streamlit Community Cloud |

## Local Setup

**Prerequisites:** Python 3.8+

```bash
git clone https://github.com/khichar-monika15/movie-recommender-system.git
cd movie-recommender-system

# Pull LFS files (similarity.pkl, vectors.pkl)
git lfs pull

pip install -r requirements.txt
streamlit run app.py
# Opens at http://localhost:8501
```

## Deployment (Streamlit Community Cloud)

1. Push repo to GitHub (model pkl files tracked via Git LFS)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Connect repo, set main file = `app.py`
4. Deploy — public URL ready in minutes, zero server management

## Model Files

| File | Size | Description |
|---|---|---|
| `model/movie_list.pkl` | 2.3 MB | Movie metadata (title, tags) |
| `model/similarity.pkl` | 177 MB | Precomputed cosine similarity matrix (Git LFS) |
| `model/vectorizer.pkl` | 0.1 MB | Fitted CountVectorizer |
| `model/vectors.pkl` | 184 MB | Full TF-IDF vectors matrix (Git LFS) |

## Next Steps

- Move vectors to Pinecone for approximate nearest-neighbor search at scale
- Add collaborative filtering layer using user interaction data
