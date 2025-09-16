import os
import random
import datetime
import pandas as pd
from faker import Faker
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from tqdm import tqdm

load_dotenv()
faker = Faker()
Faker.seed(42)
random.seed(42)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


N_USERS = 200
N_PLAYLISTS = 300
N_EVENTS = 20000
BATCH_SIZE = 2000

DATASET_PATH = "data/Spotify_Youtube.csv"

def pg_connect():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def random_datetime_within_days(days=365):
    now = datetime.datetime.now()
    start = now - datetime.timedelta(days=days)
    delta_seconds = int((now - start).total_seconds())
    rand_sec = random.randint(0, delta_seconds)
    return start + datetime.timedelta(seconds=rand_sec)

def generate_users(n):
    users = []
    for _ in range(n):
        name = faker.name()
        email = faker.unique.email()
        country = faker.country()
        age = random.randint(15, 70)
        signup_date = faker.date_between(start_date='-4y', end_date='today')
        users.append((name, email, country, age, signup_date))
    return users

def load_songs_from_csv(path):
    df = pd.read_csv(path)
    songs = []
    for _, row in df.iterrows():
        title = str(row.get("Track", "Unknown"))[:300]
        artist = str(row.get("Artist", "Unknown"))[:200]
        album = str(row.get("Album", "Unknown"))[:200]
        genre = str(row.get("Album_type", "Unknown"))[:100]   
        duration = row.get("Duration_ms", None)

        if pd.isna(duration):
            duration = random.randint(120000, 420000)
        duration = int(duration) // 1000  

        release_date = faker.date_between(start_date='-10y', end_date='today')

        songs.append((title, artist, album, genre, duration, release_date))
    return songs



def insert_bulk(conn, cur, query, rows):
    execute_values(cur, query, rows)
    conn.commit()

def main():
    conn = pg_connect()
    cur = conn.cursor()

    users = generate_users(N_USERS)
    insert_bulk(conn, cur,
                "INSERT INTO Users (name, email, country, age, signup_date) VALUES %s",
                users)
    cur.execute("SELECT user_id FROM Users")
    user_ids = [r[0] for r in cur.fetchall()]

    songs = load_songs_from_csv(DATASET_PATH)
    insert_bulk(conn, cur,
        "INSERT INTO Songs (title, artist, album, genre, duration, release_date) VALUES %s",
        songs
    )
    cur.execute("SELECT song_id, duration FROM Songs")
    rows = cur.fetchall()
    song_ids = [r[0] for r in rows]
    song_durations = {r[0]: r[1] for r in rows}

    playlist_ids = []
    for i in range(N_PLAYLISTS):
        owner = random.choice(user_ids)
        name = f"{faker.word().capitalize()} Mix {i}"
        created_at = faker.date_between(start_date='-2y', end_date='today')
        cur.execute(
            "INSERT INTO Playlists (user_id, playlist_name, created_at) VALUES (%s,%s,%s) RETURNING playlist_id",
            (owner, name, created_at))
        playlist_ids.append(cur.fetchone()[0])
    conn.commit()

    playlist_song_rows = []
    for pid in playlist_ids:
        chosen = random.sample(song_ids, random.randint(5, 20))
        for sid in chosen:
            playlist_song_rows.append((pid, sid))
        if len(playlist_song_rows) > BATCH_SIZE:
            insert_bulk(conn, cur, "INSERT INTO PlaylistSongs (playlist_id, song_id) VALUES %s", playlist_song_rows)
            playlist_song_rows = []
    if playlist_song_rows:
        insert_bulk(conn, cur, "INSERT INTO PlaylistSongs (playlist_id, song_id) VALUES %s", playlist_song_rows)

    events_rows = []
    for _ in tqdm(range(N_EVENTS)):
        uid = random.choice(user_ids)
        sid = random.choice(song_ids)
        pid = random.choice(playlist_ids) if random.random() < 0.4 else None
        played_at = random_datetime_within_days(365)
        skipped = random.random() < 0.18
        duration = song_durations[sid]
        duration_played = random.randint(1, max(1, int(duration * (0.35 if skipped else 1))))
        events_rows.append((uid, sid, pid, played_at, skipped, duration_played))

        if len(events_rows) >= BATCH_SIZE:
            insert_bulk(conn, cur,
                        "INSERT INTO ListeningHistory (user_id, song_id, playlist_id, played_at, skipped, duration_played) VALUES %s",
                        events_rows)
            events_rows = []
    if events_rows:
        insert_bulk(conn, cur,
                    "INSERT INTO ListeningHistory (user_id, song_id, playlist_id, played_at, skipped, duration_played) VALUES %s",
                    events_rows)

    for table in ["Users", "Songs", "Playlists", "PlaylistSongs", "ListeningHistory"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"{table}: {cur.fetchone()[0]}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
