from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core import settings

print("✅ DATABASE_URL chargée:", settings.database_url)
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

