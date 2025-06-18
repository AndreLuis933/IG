import os

from supabase import create_client

SUPABASE_CLIENT = create_client(
    os.environ["PROJECT_URL"],
    os.environ["API_KEY_PUBLIC"],
)
