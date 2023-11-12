import os

from supabase import create_client, Client

url: str = os.getenv("SUPABASE_URL", "")
key: str = os.getenv("SUPABASE_KEY", "")

supabase: Client = create_client(url, key)

user_db = supabase.table("users")
game_result_db = supabase.table("game_results")
leaderboard_db = supabase.table("leaderboard")
