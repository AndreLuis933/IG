import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from supabase import create_client

# Configuração da conexão
DATABASE_URL = os.getenv("DATABASE_URL")
ENGINE = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=ENGINE)
DATABASE_TYPE = ENGINE.dialect.name
SUPABASE_CLIENT = create_client(
    os.environ["PROJECT_URL"],
    os.environ["API_KEY_SECRET"],
)
