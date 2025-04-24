# SQL Agent Web Application

SQL Agent Web Application은 A2A(Agent-to-Agent) 프로토콜을 사용하여 자연어 쿼리를 SQL로 변환하고 데이터베이스에서 결과를 조회할 수 있는 웹 인터페이스를 제공합니다.

## 주요 기능

- 자연어 질문을 SQL 쿼리로 변환
- 데이터베이스 쿼리 결과 표시
- 결과 엑셀 파일 다운로드
- Docker를 통한 쉬운 배포

## 설치 및 실행 방법

### 환경 설정

1. 환경 변수 설정을 위해 `.env` 파일 생성:
   ```
   # SQL Agent Web Interface Environment Variables
   SQL_AGENT_URL=http://localhost:10000
   PORT=8000
   HOST=0.0.0.0
   GOOGLE_API_KEY=your_google_api_key_here
   FLASK_DEBUG=True
   
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_database
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```
   
2. Google API Key를 발급받아 `.env` 파일에 추가
   - [Google AI Studio](https://makersuite.google.com/app/apikey)에서 API 키 발급

### 로컬 개발 환경

1. 필요한 패키지 설치:
   ```
   pip install -r requirements.txt
   ```

2. SQL Agent 서버 실행:
   ```
   python -m api.agents.sql_agent
   ```

3. 웹 인터페이스 실행:
   ```
   python -m api.web
   ```

4. 브라우저에서 http://localhost:8000 접속

### Docker를 통한 배포

1. Docker와 Docker Compose 설치

2. Docker Compose를 통한 빌드 및 실행:
   ```
   docker-compose up -d
   ```

3. 브라우저에서 http://localhost:8000 접속

## 프로젝트 구조

- `api/agents/`: A2A 프로토콜을 구현한 SQL Agent
- `api/common/`: A2A 프로토콜 구현을 위한 공통 모듈
- `api/web/`: 웹 인터페이스 모듈
- `api/core/`: 데이터베이스 스키마 및 연결 관리
- `Dockerfile`: 웹 인터페이스용 Docker 설정
- `Dockerfile.sql_agent`: SQL Agent용 Docker 설정
- `docker-compose.yml`: Docker Compose 설정

## 환경 변수

주요 환경 변수는 다음과 같습니다:

- `SQL_AGENT_URL`: SQL Agent 서버 URL
- `PORT`: 웹 서버 포트
- `HOST`: 웹 서버 호스트
- `GOOGLE_API_KEY`: Google API 키
- `FLASK_DEBUG`: 디버그 모드 설정

### 데이터베이스 환경 변수

- `DB_HOST`: 데이터베이스 호스트 (기본값: localhost)
- `DB_PORT`: 데이터베이스 포트 (기본값: 5432)
- `DB_NAME`: 데이터베이스 이름
- `DB_USER`: 데이터베이스 사용자 이름
- `DB_PASSWORD`: 데이터베이스 비밀번호

## 사용 방법

1. 쿼리 입력 상자에 자연어 질문 또는 SQL 쿼리 입력
   예: "모든 사용자의 목록을 보여줘" 또는 "SELECT * FROM users"

2. "Submit Query" 버튼 클릭

3. 결과 테이블 확인

4. "Download Excel" 버튼을 클릭하여 결과를 엑셀 파일로 다운로드

## 문제 해결

- SQL Agent 연결 오류: SQL Agent 서버가 실행 중인지 확인
- 데이터베이스 연결 오류: 데이터베이스 설정 확인
- Docker 실행 오류: `docker-compose logs`로 로그 확인
