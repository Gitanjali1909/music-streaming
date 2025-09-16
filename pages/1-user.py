import streamlit as st
import pandas as pd
import psycopg2
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

st.set_page_config(page_title="Users Dashboard", layout="wide")
st.title("👤 Users Dashboard")

kpis = run_query("""
    SELECT 
        COUNT(*) AS total_users,
        AVG(age)::numeric(10,1) AS avg_age,
        COUNT(DISTINCT country) AS unique_countries
    FROM Users;
""")

col1, col2, col3 = st.columns(3)
col1.metric("Total Users", kpis["total_users"][0])
col2.metric("Avg Age", kpis["avg_age"][0])
col3.metric("Countries", kpis["unique_countries"][0])

users = run_query("SELECT * FROM Users LIMIT 50;")
st.subheader("Users (sample 50)")
st.dataframe(users)

age_df = run_query("SELECT age, COUNT(*) AS count FROM Users GROUP BY age ORDER BY age;")
st.subheader("Age Distribution")
st.bar_chart(age_df.set_index("age"))

country_df = run_query("SELECT country, COUNT(*) AS user_count FROM Users GROUP BY country ORDER BY user_count DESC LIMIT 10;")
st.subheader("Top 10 Countries by Users")
st.bar_chart(country_df.set_index("country"))
