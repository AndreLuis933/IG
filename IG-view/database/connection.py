import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_CLIENT = create_client(
    os.environ["PROJECT_URL"],
    os.environ["API_KEY_PUBLIC"],
)
