# Music Streaming Analytics 🎵

Stream, explore, and analyze music with a clean, interactive dashboard. Browse songs, view artist & album details, and get analytics on your music collection — all in one place.  

## About the Project
This project is a music-streaming dashboard that lets users explore songs, artists, albums, and playlists interactively. Users can view song details, filter by genre, and visualize music statistics such as top songs, popular artists, and song duration trends.  

## Dataset
A synthetic dataset was generated with realistic data:  
- **Users:** 200  
- **Songs:** 20,000+  
- **Playlists:** Multiple playlists per user  
- **Song Attributes:** Title, artist, album, genre, duration, release date, Spotify URL  
This dataset demonstrates skills in data generation, cleaning, and database integration (PostgreSQL).  

## How It Works
- **Data & Cleaning:** Data is stored in PostgreSQL tables (`Songs`, `Users`, `Playlists`, `ListeningHistory`). Cleaned and structured for easy querying.  
- **Interactive Dashboard:** Built with Streamlit; users can browse songs, filter by genre or artist, and view song details.  
- **Analytics & Visualizations:** Plotly visualizations show top songs, song duration vs release date trends, genre distributions, and playlist statistics.  
- **Database Integration:** Data is loaded from PostgreSQL dynamically using pandas for live dashboard updates.  

## Demo
Kaggle: [https://www.kaggle.com/code/gitanjalisoni/music-streaming-analytics]
- **Run Locally:**  
```bash
streamlit run dashboard.py
