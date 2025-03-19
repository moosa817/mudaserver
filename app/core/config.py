from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MudaServer"
    admin_email: str
    custom_battery : bool = False #Leave it to be False if you are not using linux & have upower

    class Config:
        env_file = ".env"


config = Settings()