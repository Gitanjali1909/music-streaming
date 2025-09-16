import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT")
    )

def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="Songs Dashboard", layout="wide")
st.title("🎵 Songs Dashboard")

songs = run_query("""
SELECT title, artist, album, genre, duration, release_date
FROM Songs
LIMIT 100;
""")

kpis = run_query("""
SELECT COUNT(*) AS total_songs,
       COUNT(DISTINCT artist) AS unique_artists,
       COUNT(DISTINCT genre) AS unique_genres
FROM Songs;
""")

col1, col2, col3 = st.columns(3)
col1.metric("Total Songs", kpis["total_songs"][0])
col2.metric("Unique Artists", kpis["unique_artists"][0])
col3.metric("Genres", kpis["unique_genres"][0])

genre_df = run_query("""
SELECT genre, COUNT(*) AS total_songs
FROM Songs
GROUP BY genre
ORDER BY total_songs DESC;
""")

fig_genre = px.bar(
    genre_df,
    x="genre",
    y="total_songs",
    title="Top Genres by Song Count"
)
st.plotly_chart(fig_genre, use_container_width=True)

fig_scatter = px.scatter(
    songs,
    x="duration",
    y="release_date",
    color="genre",
    hover_data=["title", "artist"],
    title="Duration vs Release Date of Songs"
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("Songs (sample 100)")
st.dataframe(songs)
