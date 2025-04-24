from . import Base, engine
from app.models import * # Import all models here to ensure they are registered with SQLAlchemy

def init_db():
    Base.metadata.create_all(bind=engine)
