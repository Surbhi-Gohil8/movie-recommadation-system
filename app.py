import streamlit as st
import pickle
import pandas as pd
import requests
import time
from streamlit_lottie import st_lottie
import json
from functools import lru_cache
import concurrent.futures

# Set page configuration
st.set_page_config(
    page_title="CineMatch - Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Lottie animation
def load_lottie_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Custom CSS for styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Call the function to apply custom CSS
local_css("style.css")

def set_bg_hack_url():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set background
set_bg_hack_url()

def fetch_posture(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=1498cf04185c1912386f3fbd3278b016&language=en-US'.format(movie_id)
    )
    data = response.json()
    print(data)
    if 'poster_path' in data and data['poster_path']:
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    else:
        return "https://via.placeholder.com/500x750?text=No+Poster"

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommend_movies = []
    recommend_movies_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id   # ✅ fixed: use actual movie_id column
        recommend_movies.append(movies.iloc[i[0]].title)
        recommend_movies_posters.append(fetch_posture(movie_id))
    return recommend_movies, recommend_movies_posters   # ✅ fixed: return both

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# Custom CSS for cards
st.markdown("""
    <style>
    .movie-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .movie-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
    }
    .movie-poster {
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 10px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    .movie-title {
        color: white;
        font-weight: 600;
        font-size: 1rem;
        text-align: center;
        margin-top: auto;
        padding: 5px;
    }
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        border-radius: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(45deg, #6366F1, #8B5CF6);
        color: white;
        font-weight: 600;
        border: none;
        padding: 12px 24px;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 14px rgba(99, 102, 241, 0.25);
        background: linear-gradient(45deg, #4F46E5, #7C3AED);
    }
    
    /* Modern card design */
    .movie-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        display: flex;
        flex-direction: column;
        border: 1px solid rgba(255, 255, 255, 0.08);
        overflow: hidden;
    }
    
    .movie-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .movie-poster {
        border-radius: 0;
        overflow: hidden;
        margin-bottom: 0;
        position: relative;
        padding-top: 150%;
    }
    
    .movie-poster img {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
    }
    
    .movie-card:hover .movie-poster img {
        transform: scale(1.05);
    }
    
    .movie-title {
        color: white;
        font-weight: 600;
        font-size: 0.95rem;
        text-align: center;
        padding: 16px 12px;
        margin: 0;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(8px);
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        transform: translateY(100%);
        transition: transform 0.3s ease;
    }
    
    .movie-card:hover .movie-title {
        transform: translateY(0);
    }
    
    /* Loading animation */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem 0;
    }
    
    .loading-text {
        color: white;
        margin-top: 1rem;
        font-size: 1.2rem;
        font-weight: 500;
        text-align: center;
    }
    
    .dot-pulse {
        position: relative;
        left: -9999px;
        width: 10px;
        height: 10px;
        border-radius: 5px;
        background-color: #6366F1;
        color: #6366F1;
        box-shadow: 9999px 0 0 -5px #6366F1;
        animation: dotPulse 1.5s infinite linear;
        animation-delay: .25s;
        margin: 20px auto;
    }
    
    .dot-pulse::before, .dot-pulse::after {
        content: '';
        display: inline-block;
        position: absolute;
        top: 0;
        width: 10px;
        height: 10px;
        border-radius: 5px;
        background-color: #6366F1;
        color: #6366F1;
    }
    
    .dot-pulse::before {
        box-shadow: 9974px 0 0 -5px #6366F1;
        animation: dotPulseBefore 1.5s infinite linear;
        animation-delay: 0s;
    }
    
    .dot-pulse::after {
        box-shadow: 10024px 0 0 -5px #6366F1;
        animation: dotPulseAfter 1.5s infinite linear;
        animation-delay: .5s;
    }
    
    @keyframes dotPulseBefore {
        0% { box-shadow: 9974px 0 0 -5px #6366F1; }
        30% { box-shadow: 9974px 0 0 2px #6366F1; }
        60%, 100% { box-shadow: 9974px 0 0 -5px #6366F1; }
    }
    
    @keyframes dotPulse {
        0% { box-shadow: 9999px 0 0 -5px #6366F1; }
        30% { box-shadow: 9999px 0 0 2px #6366F1; }
        60%, 100% { box-shadow: 9999px 0 0 -5px #6366F1; }
    }
    
    @keyframes dotPulseAfter {
        0% { box-shadow: 10024px 0 0 -5px #6366F1; }
        30% { box-shadow: 10024px 0 0 2px #6366F1; }
        60%, 100% { box-shadow: 10024px 0 0 -5px #6366F1; }
    }
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(45deg, #FF4B4B, #FF9A5A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: rgba(255, 255, 255, 0.8);
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Main content with modern layout
st.markdown('<h1 class="main-title">CineMatch</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover your next favorite movie</p>', unsafe_allow_html=True)

# Center the selectbox and button
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    selected_movie_name = st.selectbox(
        "Select a movie you like:",
        movies['title'].values,
        key="movie_selector",
        help="Choose a movie to get personalized recommendations"
    )
    
    if st.button("🎬 Get Movie Recommendations"):
        # Show loading animation
        with st.spinner(''):
            loading_placeholder = st.empty()
            with loading_placeholder.container():
                st.markdown("""
                <div class="loading-container">
                    <div class="dot-pulse"></div>
                    <div class="loading-text">Finding the perfect matches for you...</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Simulate a small delay to show the loading animation
            time.sleep(0.5)
            
            # Get recommendations
            names, posters = recommend(selected_movie_name)
            
            # Clear the loading animation
            loading_placeholder.empty()
            
            # Display recommendations in a grid with modern design
            st.markdown("""
            <div style="margin: 3rem 0 1rem 0;">
                <h2 style="text-align: center; color: white; margin-bottom: 2rem; font-size: 2rem; font-weight: 700; letter-spacing: -0.5px;">
                    Recommended For You
                </h2>
                <div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); margin: 0 auto; width: 80%;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Create 5 columns for the movie cards with responsive design
            cols = st.columns(5)
            
            for i in range(5):
                with cols[i]:
                    # Generate a streaming link
                    search_query = names[i].replace(' ', '+') + '+movie+watch+online'
                    watch_link = f"https://www.google.com/search?q={search_query}"
                    
                    # Create a container for the movie card
                    with st.container():
                        # Display the movie poster
                        st.markdown(
                            f"""
                            <div class="movie-card">
                                <div class="movie-poster">
                                    <img src="{posters[i]}" alt="{names[i]}" onerror="this.onerror=null; this.src='https://via.placeholder.com/500x750?text=No+Poster';">
                                </div>
                                <div class="movie-title">{names[i]}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Add the watch button using st.link_button
                        st.link_button("Watch Movie", watch_link, use_container_width=True, 
                                     help=f"Watch {names[i]} online")
            
            # Add some spacing at the bottom
            st.markdown("<div style='margin-bottom: 3rem;'></div>", unsafe_allow_html=True)
