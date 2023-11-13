import logging

from supabase import Client, create_client

from core.config import SUPABASE_KEY, SUPABASE_URL


class Database:
    client: Client


db = Database()


async def create_supabase_client():
    logging.info("Connecting to Supabase")
    db.client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def get_database():
    return db
