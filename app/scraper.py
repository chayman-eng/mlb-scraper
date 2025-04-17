import statsapi
import psycopg2
import datetime
import json
import os

# Yesterday’s games
target_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

# DB credentials (from environment variables)
DB_NAME = os.getenv("PGDATABASE", "mlb")
DB_USER = os.getenv("PGUSER", "postgres")
DB_PASS = os.getenv("PGPASSWORD", "1234")
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = os.getenv("PGPORT", "5432")

# Connect to DB
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# Ensure table exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS mlb_boxscores (
        id SERIAL PRIMARY KEY,
        game_id TEXT UNIQUE,
        game_date DATE,
        json_data JSONB
    )
""")

games = statsapi.schedule(start_date=target_date, end_date=target_date)

for game in games:
    game_id = game['game_id']
    game_date = game['game_date']

    try:
        box = statsapi.boxscore_data(game_id)
        cur.execute("""
            INSERT INTO mlb_boxscores (game_id, game_date, json_data)
            VALUES (%s, %s, %s)
            ON CONFLICT (game_id) DO NOTHING
        """, (game_id, game_date, json.dumps(box)))
        print(f"✅ Saved: {game_id}")
    except Exception as e:
        print(f"❌ Error with game {game_id}: {e}")

conn.commit()
cur.close()
conn.close()
