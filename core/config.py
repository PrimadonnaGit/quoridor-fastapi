import os

# Kakao
KAKAO_CLIENT_ID: str = os.getenv("KAKAO_CLIENT_ID", "")
REDIRECT_URI: str = os.getenv("KAKAO_REDIRECT_URI", "")
KAKAO_TOKEN_URL: str = os.getenv("KAKAO_TOKEN_URL", "")

# Database
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
