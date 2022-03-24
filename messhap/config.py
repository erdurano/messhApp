from pydantic import BaseSettings


class TestSettings(BaseSettings):
    db_path: str
    secret_key: str
    algorithm: str
    access_token_expire_mins: int

    class Config:
        env_file = "test.env"


settings = TestSettings()
