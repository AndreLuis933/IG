import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from supabase import create_client

#load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    msg = "DATABASE_URL não está definida. Defina a variável de ambiente DATABASE_URL"
    raise RuntimeError(msg)
ENGINE = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=ENGINE)
DATABASE_TYPE = ENGINE.dialect.name
LOCAL = os.getenv("LOCAL", "false").lower() == "true"
SUPABASE_CLIENT = create_client(os.environ["PROJECT_URL"], os.environ["API_KEY_SECRET"]) if not LOCAL else None
