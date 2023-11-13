from datetime import datetime

from core.database import Database


async def get_leaderboard(db: Database):
    result = (
        db.client.table("leaderboard")
        .select("*")
        .order("rank", desc=False)
        .limit(10)
        .execute()
    )
    return result.data


async def update_game_result(
    db: Database, player1_id: int, player2_id: int, winner_id: int
):
    if player1_id == winner_id:
        db.client.table("game_result").insert(
            {
                "player_id": player1_id,
                "opponent_id": player2_id,
                "game_result": "win",
                "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ).execute()

        db.client.table("game_result").insert(
            {
                "player_id": player2_id,
                "opponent_id": player1_id,
                "game_result": "lose",
                "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ).execute()
    else:
        db.client.table("game_result").insert(
            {
                "player_id": player1_id,
                "opponent_id": player2_id,
                "game_result": "lose",
                "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ).execute()

        db.client.table("game_result").insert(
            {
                "player_id": player2_id,
                "opponent_id": player1_id,
                "game_result": "win",
                "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ).execute()