from src.configurator import Configurator
from pathlib import Path


conf = Configurator(env_path=str(
    Path(__file__).resolve().parent / "example.env"))


@conf.env_model()
class DbConf:
    DB_SCHEMA: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int = 55432
    DB_NAME: str = "test"

    def uri(self):
        return f"{self.DB_SCHEMA}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


db = DbConf()

print(db.uri())
