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

st.set_page_config(page_title="Analytics Dashboard", layout="wide")
st.title("📊 Advanced Analytics")

# Top Skipped Songs
skipped = run_query("""
SELECT s.title, s.artist, COUNT(*) AS skips
FROM ListeningHistory lh
JOIN Songs s ON lh.song_id = s.song_id
WHERE lh.skipped = TRUE
GROUP BY s.title, s.artist
ORDER BY skips DESC
LIMIT 10;
""")
fig1 = px.bar(skipped, x="title", y="skips", color="artist", title="Top 10 Skipped Songs")
st.plotly_chart(fig1, use_container_width=True)

# Weekly Viral Growth
viral = run_query("""
SELECT s.title, DATE_TRUNC('week', lh.played_at) AS week, COUNT(*) AS plays
FROM ListeningHistory lh
JOIN Songs s ON lh.song_id = s.song_id
WHERE lh.skipped = FALSE
GROUP BY s.title, week
HAVING COUNT(*) > 20
ORDER BY week, plays DESC;
""")
fig2 = px.line(viral, x="week", y="plays", color="title", title="Weekly Viral Growth of Songs")
st.plotly_chart(fig2, use_container_width=True)

# Listening Activity Heatmap
heatmap_df = run_query("""
SELECT EXTRACT(DOW FROM played_at) AS day,
       EXTRACT(HOUR FROM played_at) AS hour,
       COUNT(*) AS plays
FROM ListeningHistory
GROUP BY day, hour
ORDER BY day, hour;
""")
heatmap_df["day"] = heatmap_df["day"].map({0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"})
fig3 = px.density_heatmap(
    heatmap_df,
    x="hour",
    y="day",
    z="plays",
    color_continuous_scale="Blues",
    title="Listening Activity by Day & Hour"
)
st.plotly_chart(fig3, use_container_width=True)

# Power Users
power_users = run_query("""
SELECT u.name AS user_name, COUNT(*) AS total_plays
FROM ListeningHistory lh
JOIN Users u ON lh.user_id = u.user_id
GROUP BY u.name
ORDER BY total_plays DESC
LIMIT 10;
""")
fig4 = px.bar(
    power_users,
    x="user_name",
    y="total_plays",
    title="Top 10 Most Active Listeners",
    labels={"user_name": "User", "total_plays": "Plays"}
)
st.plotly_chart(fig4, use_container_width=True)
