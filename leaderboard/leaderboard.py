from database.database import game_result_db, leaderboard_db
from datetime import datetime


async def update_game_result(player1_id: int, player2_id: int, winner_id: int):
    if player1_id == winner_id:
        game_result_db.insert(
            {
                "player_id": player1_id,
                "opponent_id": player2_id,
                "game_result": "win",
                "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ).execute()
        game_result_db.insert(
            {
                "player_id": player2_id,
                "opponent_id": player1_id,
                "game_result": "lose",
                "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ).execute()
    else:
        game_result_db.insert(
            {
                "player_id": player1_id,
                "opponent_id": player2_id,
                "game_result": "lose",
                "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ).execute()
        game_result_db.insert(
            {
                "player_id": player2_id,
                "opponent_id": player1_id,
                "game_result": "win",
                "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ).execute()


async def get_leaderboard():
    result = leaderboard_db.select("*").order("rank", desc=False).execute()
    return result.data
