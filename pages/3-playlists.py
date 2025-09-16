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

st.set_page_config(page_title="Playlists Dashboard", layout="wide")
st.title("📂 Playlists Dashboard")

playlists = run_query("""
SELECT 
    p.playlist_id, 
    p.playlist_name, 
    u.name AS user_name, 
    COUNT(ps.song_id) AS total_songs
FROM Playlists p
JOIN Users u ON p.user_id = u.user_id
LEFT JOIN PlaylistSongs ps ON p.playlist_id = ps.playlist_id
GROUP BY p.playlist_id, p.playlist_name, u.name
ORDER BY total_songs DESC;
""")

col1, col2 = st.columns(2)
col1.metric("Total Playlists", len(playlists))
col2.metric("Avg Songs/Playlist", round(playlists["total_songs"].mean(), 1))

st.subheader("All Playlists")
st.dataframe(playlists)

fig = px.bar(
    playlists.head(15),
    x="playlist_name",
    y="total_songs",
    color="user_name",
    text="total_songs",
    title="Top 15 Playlists by Song Count"
)
st.plotly_chart(fig, use_container_width=True)

playlist_names = playlists["playlist_name"].tolist()
selected_playlist = st.selectbox("🔎 Select a playlist to see its songs", playlist_names)

playlist_songs = run_query(f"""
SELECT s.title, s.artist, s.genre
FROM PlaylistSongs ps
JOIN Songs s ON ps.song_id = s.song_id
JOIN Playlists p ON ps.playlist_id = p.playlist_id
WHERE p.playlist_name = '{selected_playlist}';
""")

st.subheader(f"Songs in Playlist: {selected_playlist}")
st.dataframe(playlist_songs)
