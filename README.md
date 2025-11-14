# 42-Codyssey 학습 저장소

<img width="1200" height="390" alt="codyssey_logo" src="https://github.com/user-attachments/assets/57e8dfa8-7b80-48dc-a040-b0a04d0ed8bc" />

안녕하세요! 이 저장소는 42 서울의 교육 과정(Codyssey)을 진행하며 학습하고 고민한 내용들을 정리하는 공간입니다. 다양한 과제와 프로젝트를 통해 배운 점들을 기록하고 있습니다.

---

## 📚 전체 학습 모듈

### 0304: Python 기초 및 데이터 처리

* `1-1`: 로그 파일 처리 및 분석
* `1-3`: CSV/Binary 파일 처리
* `1-4`: Numpy 데이터 처리
* `1-6`: 멀티프로세싱/스레딩
* `2-1`: ZIP 파일 암호 해제
* `2-2`: 시저 암호 해독
* `2-3`: PyQt5 계산기 GUI
* `2-7`: 음성 인식(STT)
* `3-5`: 데이터베이스 연동 및 시각화

### 0904: 웹 및 네트워크 프로그래밍

* `3-1`: SMTP 이메일 발송
* `3-2`: 소켓 통신 채팅 서버
* `3-4`: HTTP 서버 및 IP 위치 추적
* `3-7`: 웹 크롤링(정적/동적)
* **`4`**: **FastAPI 기반 웹 애플리케이션**
  * **[➡️ [0904/4] 상세 README 보러 가기](./0904/4/README.md)**

---

## 🛠️ 환경 설정

이 저장소는 Python 프로젝트 관리를 위해 **`uv`** 를 사용합니다. `uv`는 `pip`과 `venv`를 대체하는 매우 빠른 Python 패키지 설치 및 관리 도구입니다.

### 1\. `uv` 설치하기

`uv`가 설치되어 있지 않다면, 먼저 `uv`를 설치합니다.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 또는 pip를 통해 설치
pip install uv
```

### 2\. 가상 환경 생성 및 의존성 설치

저장소 루트 디렉터리(`42-codyssey/`)에서 다음 명령어를 실행하세요.

```bash
# 가상 환경 생성 및 의존성 설치 (uv.lock 파일 기준)
# pyproject.toml이 아닌 uv.lock을 기준으로 정확히 설치합니다.
uv sync
```

### 3\. [0904/4] FastAPI 프로젝트 실행

환경 설정이 완료되면, 메인 프로젝트(`0904/4`)를 실행할 수 있습니다.

```bash
# 1. .env 파일 설정
# .env.example 파일을 복사하여 .env 파일을 생성하고,
# 내부의 DATABASE_URL 등을 실제 환경에 맞게 수정해야 합니다.
cp ../.env.example .env

# 2. 메인 프로젝트 디렉터리로 이동
cd 0904/4

# 3. 데이터베이스 마이그레이션 적용 (Alembic)
uv run alembic upgrade head

# 4. FastAPI 서버 실행
# main.py의 app 객체를 Uvicorn으로 실행합니다.
uv run uvicorn main:app --host 0.0.0.0 --reload
```
