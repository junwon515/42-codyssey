from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CSV_FILE: str = 'todo_data.csv'
    FIELDNAMES: list[str] = ['id', 'task', 'due_date', 'is_completed']
    DATABASE_URL: str = 'sqlite+aiosqlite:///./sql_app.db'

    class Config:
        env_file = '../../.env'


settings = Settings()
