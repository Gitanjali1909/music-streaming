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

st.set_page_config(page_title="Music Streaming Analytics", layout="wide")

st.title("🎵 Music Streaming Dashboard")
st.markdown("Welcome! Use the sidebar to navigate between **Users, Songs, Playlists, and Analytics**.")

kpis = run_query("""
SELECT 
    (SELECT COUNT(*) FROM Users) AS total_users,
    (SELECT COUNT(*) FROM Songs) AS total_songs,
    (SELECT COUNT(*) FROM ListeningHistory) AS total_plays,
    ROUND(
        100.0 * (SELECT COUNT(*) FROM ListeningHistory WHERE skipped = TRUE) 
        / NULLIF((SELECT COUNT(*) FROM ListeningHistory), 0), 2
    ) AS skip_rate
""")

col1, col2, col3, col4 = st.columns(4)
col1.metric("👤 Total Users", kpis["total_users"][0])
col2.metric("🎶 Total Songs", kpis["total_songs"][0])
col3.metric("▶️ Total Plays", kpis["total_plays"][0])
col4.metric("⏩ Skip Rate (%)", kpis["skip_rate"][0])

st.subheader("📀 Songs Overview")

songs_df = run_query("""
SELECT song_id, title, artist, album, genre, duration, release_date
FROM Songs
LIMIT 50
""")

st.dataframe(songs_df)

if not songs_df.empty:
    fig = px.scatter(
        songs_df,
        x="duration",
        y="release_date",
        hover_data=["title", "artist"]
    )
    st.plotly_chart(fig, use_container_width=True)
