import os
import pickle
import json
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import streamlit as st

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", layout="wide")

movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))


def get_tmdb_api_key():
    api_key = os.getenv("TMDB_API_KEY")
    if api_key:
        return api_key.strip()

    try:
        return st.secrets["TMDB_API_KEY"].strip()
    except Exception:
        return None


def fetch_json(url):
    response = urlopen(url, timeout=10)
    return json.loads(response.read().decode("utf-8"))


@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    api_key = get_tmdb_api_key()
    if not api_key:
        return None

    try:
        data = fetch_json(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}")
        poster_path = data.get("poster_path")
        if poster_path:
            return f"{POSTER_BASE_URL}{poster_path}"
    except (HTTPError, URLError, TimeoutError, ValueError):
        return None

    return None


def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1],
    )[1:6]

    recommendations = []
    for item in movies_list:
        row = movies.iloc[item[0]]
        recommendations.append(
            {
                "id": int(row["id"]),
                "title": row["title"],
                "rating": f'{row["vote_average"]:.1f}',
                "year": str(row["release_date"])[:4],
            }
        )

    return recommendations


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Manrope:wght@400;500;700;800&display=swap');

    :root {
        --bg-panel: rgba(12, 20, 36, 0.84);
        --bg-card: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(255,255,255,0.04));
        --text-main: #f5f7fb;
        --text-soft: #aab6d3;
        --accent: #ff725e;
        --accent-2: #ffd166;
        --stroke: rgba(255,255,255,0.12);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(255, 114, 94, 0.28), transparent 28%),
            radial-gradient(circle at top right, rgba(255, 209, 102, 0.22), transparent 24%),
            linear-gradient(135deg, #060816 0%, #0b1020 46%, #111a31 100%);
        color: var(--text-main);
        font-family: 'Manrope', sans-serif;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    div[data-testid="stToolbar"] {
        right: 1rem;
    }

    div[data-testid="stDecoration"] {
        display: none;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .hero {
        background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
        border: 1px solid var(--stroke);
        border-radius: 28px;
        padding: 2.5rem;
        box-shadow: 0 24px 80px rgba(0,0,0,0.28);
        backdrop-filter: blur(16px);
        margin-bottom: 1.5rem;
    }

    .eyebrow {
        color: var(--accent-2);
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 0.18rem;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    .hero h1 {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 4.4rem;
        line-height: 0.95;
        letter-spacing: 0.04rem;
        margin: 0;
    }

    .hero p {
        color: var(--text-soft);
        font-size: 1.05rem;
        line-height: 1.8;
        max-width: 760px;
        margin-top: 1rem;
        margin-bottom: 0;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 800;
        margin: 0.6rem 0 1rem 0;
    }

    div[data-baseweb="select"] > div {
        background: rgba(9, 14, 28, 0.92) !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
        border-radius: 16px !important;
        min-height: 3.2rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--accent), #ff9a5a) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        font-weight: 800 !important;
        padding: 0.8rem 1.4rem !important;
        width: 100%;
        box-shadow: 0 14px 40px rgba(255, 114, 94, 0.28);
    }

    .result-shell {
        background: var(--bg-panel);
        border: 1px solid var(--stroke);
        border-radius: 26px;
        padding: 1.4rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    .movie-card {
        border-radius: 24px;
        padding: 1rem;
        background: var(--bg-card);
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        min-height: 100%;
    }

    .movie-rank {
        display: inline-block;
        color: var(--accent-2);
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.08rem;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    .movie-title {
        font-size: 1.08rem;
        font-weight: 800;
        line-height: 1.4;
        min-height: 60px;
        margin: 0.9rem 0 1rem 0;
        animation: titleBlink 1.3s ease-in-out infinite;
        text-shadow: 0 0 12px rgba(255, 114, 94, 0.35);
    }

    .meta-row {
        display: flex;
        justify-content: space-between;
        gap: 0.75rem;
        color: var(--text-soft);
        font-size: 0.95rem;
        padding-top: 0.9rem;
        border-top: 1px solid rgba(255,255,255,0.08);
    }

    .poster-fallback {
        height: 250px;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, rgba(255,114,94,0.22), rgba(255,209,102,0.14));
        color: white;
        font-weight: 800;
        line-height: 1.5;
    }

    @keyframes titleBlink {
        0%,
        100% {
            opacity: 1;
            color: var(--text-main);
        }
        50% {
            opacity: 0.45;
            color: var(--accent-2);
        }
    }

    @media (max-width: 900px) {
        .hero {
            padding: 1.5rem;
        }

        .hero h1 {
            font-size: 3rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">Cinema Discovery Engine</div>
        <h1>Find the next movie worth your time.</h1>
        <p>
            Pick one film you already like and get five close matches based on story-level similarity.
            Poster images are fetched from TMDB when a valid API key is available.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

controls_col, button_col = st.columns([4, 1])

with controls_col:
    st.markdown('<div class="section-title">Choose a movie</div>', unsafe_allow_html=True)
    selected_movie = st.selectbox(
        "Choose a movie",
        movies["title"].values,
        label_visibility="collapsed",
        help="Start with a movie you already enjoy.",
    )

with button_col:
    st.markdown("<div style='height: 2.35rem;'></div>", unsafe_allow_html=True)
    should_recommend = st.button("Get Recommendations", use_container_width=True)

if should_recommend:
    recommendations = recommend(selected_movie)
    st.markdown(
        f"""
        <div class="result-shell">
            <div class="section-title">Because you picked \"{selected_movie}\"</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(5)
    for index, (column, movie) in enumerate(zip(columns, recommendations), start=1):
        poster_url = fetch_poster(movie["id"])
        with column:
            st.markdown(f'<div class="movie-card"><div class="movie-rank">Match {index:02d}</div>', unsafe_allow_html=True)
            if poster_url:
                st.image(poster_url, use_container_width=True)
            else:
                st.markdown(
                    f'<div class="poster-fallback">{movie["title"]}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"""
                    <div class="movie-title">{movie["title"]}</div>
                    <div class="meta-row">
                        <span>Rating {movie["rating"]}</span>
                        <span>Year {movie["year"]}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
