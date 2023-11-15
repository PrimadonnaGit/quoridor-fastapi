from core.database import Database
from core.exception import UserNotFound


async def get_user_by_user_id(db: Database, user_id: int) -> dict | None:
    user = db.client.table("users").select("*").eq("id", user_id).execute()

    if user.data:
        return user.data[0]

    return None


async def get_user_by_social_id(db: Database, social_user_id: str) -> dict | None:
    user = (
        db.client.table("users")
        .select("*")
        .eq("social_user_id", social_user_id)
        .execute()
    )

    if user.data:
        return user.data[0]

    return None


async def update_user(
    db: Database, user_id: int, nickname: str | None, profile_image: str | None
) -> bool:
    user = db.client.table("users").select("*").eq("id", user_id).execute()

    if not user.data:
        raise UserNotFound()

    if nickname is None and profile_image is None:
        return False

    update_query = {}

    if nickname:
        update_query["nickname"] = nickname

    if profile_image:
        update_query["profile_image"] = profile_image

    if user.data:
        db.client.table("users").update(update_query).eq("id", user_id).execute()

    return True
