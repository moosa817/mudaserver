from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "MudaServer"
    description: str = "Home Automation Server"
    version: str = "0.1.0"
    admin_email: str
    custom_battery: bool = (
        False  # Leave it to be False if you are not using linux & have upower
    )
    debug: bool = False
    SECRET_KEY: str

    # Database
    DATABASE_URL: str

    # jwt token expiry time
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120  # 2 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 60  # 60 days

    class Config:
        env_file = ".env"


config = Settings()
