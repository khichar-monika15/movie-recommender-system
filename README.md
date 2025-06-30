# movie-suggestion-engine

A content-based movie recommendation engine leveraging movie metadata and cosine similarity to deliver personalized suggestions.

## Tech Stack

- Language: Python
- Libraries: Pandas, Numpy, Scikit-learn
- Recommendation Techniques: TF-IDF, CountVectorizer, Cosine Similarity
- Frontend: Streamlit
- Dataset: TMDB Movie Metadata
- API Integration: TMDB API for posters and movie details

## Key Features

- Developed a movie recommendation system based on movie metadata such as genres, overview, cast, and crew
- Applied data pre-processing and feature engineering by converting relevant movie information into “tags”
- Utilized TF-IDF and CountVectorizer to create feature vectors
- Implemented Cosine Similarity to suggest movies based on content relevance
- Designed an interactive frontend with Streamlit for easy access
- Integrated TMDB API to display movie posters and enhance user experience

## How to Run Locally

1. Clone the repository and install dependencies:
   ```bash
   pip install -r requirements.txt
