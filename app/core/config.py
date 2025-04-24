from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "SmartConfig"  # valeur utile si .env n’existe pas
    database_url: str              # obligatoire => levée d’erreur si absente du .env
    secret_key: str                # à mettre dans .env
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

# Create an instance of the Settings class
settings = Settings()
