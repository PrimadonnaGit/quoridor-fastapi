from datetime import datetime

from core.database import Database


async def get_leaderboard(db: Database, limit: int) -> list[dict]:
    result = (
        db.client.table("leaderboard")
        .select("*")
        .order("rank", desc=False)
        .limit(limit)
        .execute()
    )
    return result.data


async def update_game_result(
    db: Database, player1_id: int, player2_id: int, winner_id: int
) -> None:
    if player1_id == player2_id:
        return

    player1_result = await game_result(player1_id, winner_id)
    player2_result = await game_result(player2_id, winner_id)

    if player1_id != 0:
        await insert_game_result(db, player1_id, player2_id, player1_result)

    if player2_id != 0:
        await insert_game_result(db, player2_id, player1_id, player2_result)


async def game_result(player_id: int, winner_id: int) -> str:
    return "win" if player_id == winner_id else "lose"


async def insert_game_result(
    db: Database, player_id: int, opponent_id: int, result: str
) -> None:
    played_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.client.table("game_results").insert(
        {
            "player_id": player_id,
            "opponent_id": opponent_id,
            "game_result": result,
            "played_at": played_at,
        }
    ).execute()
