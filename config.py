from pydantic_settings import BaseSettings, SettingsConfigDict


# 환경 설정을 관리하는 Pydantic 모델 클래스.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',  # .env 파일의 경로를 지정.
        env_ignore_empty=True,  # .env 파일 내의 빈 환경 변수 무시.
        extra='ignore',  # 모델에 정의되지 않은 환경 변수 무시.
    )
    # .env 기본 환경 변수.
    # 0903/3-7
    NAVER_ID: str | None = None
    NAVER_PW: str | None = None


settings = Settings()  # type: ignore
