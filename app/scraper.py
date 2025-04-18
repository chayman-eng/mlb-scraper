import statsapi
import psycopg2
import datetime
import json
import os
import urllib.parse as up

# Parse Railway DATABASE_URL
up.uses_netloc.append("postgres")
db_url = os.environ["DATABASE_URL"]
db_info = up.urlparse(db_url)

# Connect to Postgres
conn = psycopg2.connect(
    dbname=db_info.path[1:],
    user=db_info.username,
    password=db_info.password,
    host=db_info.hostname,
    port=db_info.port
)
cur = conn.cursor()

# Ensure table exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS mlb_boxscores (
        id SERIAL PRIMARY KEY,
        game_id TEXT UNIQUE,
        game_date DATE,
        json_data JSONB
    );
""")
conn.commit()

# Get last 7 days
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=7)
games = statsapi.schedule(start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))

# Fetch and insert each game's box score
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
        print(f"✅ Saved: {game_id} ({game['away_name']} at {game['home_name']})")
    except Exception as e:
        print(f"❌ Error for game {game_id}: {e}")

conn.commit()
cur.close()
conn.close()
