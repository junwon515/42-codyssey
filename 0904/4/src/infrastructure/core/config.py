from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CSV_FILE: str = 'todo_data.csv'
    FIELDNAMES: list[str] = ['id', 'task', 'due_date', 'is_completed']
    DATABASE_URL: str = 'sqlite+aiosqlite:///./sql_app.db'
    TRUSTED_IPS: tuple[str, ...] = ('127.0.0.1', 'localhost')

    class Config:
        env_file = '../../.env'


settings = Settings()
