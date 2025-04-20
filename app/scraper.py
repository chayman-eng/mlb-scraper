import statsapi
import psycopg2
import datetime
import json
import os
import urllib.parse as up
import sys

# --------- Parse DATABASE_URL from Environment ---------
try:
    up.uses_netloc.append("postgres")
    db_url = os.environ["DATABASE_URL"]
    db_info = up.urlparse(db_url)
except Exception as e:
    print(f"❌ DATABASE_URL not set or invalid: {e}")
    sys.exit(1)

# --------- Connect to PostgreSQL ---------
try:
    conn = psycopg2.connect(
        dbname=db_info.path[1:],
        user=db_info.username,
        password=db_info.password,
        host=db_info.hostname,
        port=db_info.port
    )
    cur = conn.cursor()
except Exception as e:
    print(f"❌ Failed to connect to database: {e}")
    sys.exit(1)

# --------- Create Table if Not Exists ---------
cur.execute("""
    CREATE TABLE IF NOT EXISTS mlb_boxscores (
        id SERIAL PRIMARY KEY,
        game_id TEXT UNIQUE,
        game_date DATE,
        json_data JSONB
    );
""")
conn.commit()

# --------- Scrape Yesterday’s Games ---------
target_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
print(f"📅 Fetching games for {target_date}")
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
        print(f"✅ Saved game_id: {game_id}")
    except Exception as e:
        print(f"❌ Failed to save {game_id}: {e}")

conn.commit()
cur.close()
conn.close()

# --------- Clean Exit ---------
print("🎯 Scraper finished successfully.")
sys.exit(0)
