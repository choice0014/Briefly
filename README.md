# Briefly - AI Daily News Summarizer

Briefly는 다양한 RSS 뉴스 피드를 실시간으로 크롤링하고, 고성능 대형 언어 모델(LLM)을 통해 핵심 내용을 3줄의 명사형 문장으로 한국어 요약하여 직관적인 웹 대시보드로 제공하는 자동화 프로젝트입니다.

---

## 1. 프로젝트 주요 기능
* **실시간 RSS 크롤링**: IT/Tech, 정치, 국제 뉴스 등의 RSS 피드를 주기적으로 파싱하여 최신 기사를 수집합니다.
* **Groq AI 뉴스 요약**: Llama 3.3 70B 모델과 정교하게 제어된 프롬프트 하네스를 결합하여 사족이 배제된 일관적인 3줄 요약본을 생성합니다.
* **반응형 다크모드 대시보드**: 카테고리별 그리드 스타일의 깔끔한 다크 테마 UI 대시보드(`index.html`)를 자동 빌드합니다.
* **GitHub Actions 자동 배포**: 1시간 주기의 스케줄러가 작동하여 크롤링, AI 요약, Git 커밋, 그리고 GitHub Pages 호스팅 웹 서버 배포까지 완전히 자동 수행합니다.
* **자동 백업 시스템**: 새로운 `index.html`이 덮어씌워지기 전에 기존 대시보드 내역을 파일 생성 시간 기준으로 `history/` 디렉토리에 고스란히 백업합니다.

---

## 2. 프로젝트 폴더 구조
* `.github/workflows/update_news.yml` - GitHub Actions 스케줄링 및 직접 Pages 배포 워크플로우 설정
* `history/` - 기존 index.html 백업 파일 저장소
* `templates/` - 대시보드 빌드용 Jinja2 HTML 템플릿 (`dashboard.html`)
* `app.py` - 전체 시스템 제어 및 정적 웹 생성 메인 스크립트
* `crawler.py` - RSS 뉴스 수집기 (프로토콜 보안 검증 내장)
* `summarizer.py` - Groq API 연동 AI 요약 엔진 및 예외 필터 가드레일
* `push.bat` - 동적 현재 브랜치 감지 기반 GitHub 커밋/푸시 자동화 스크립트
* `gemini.md` - 대안 AI 요약 엔진으로서의 Gemini API 연동 설계서
* `requirements.txt` - 파이썬 의존성 패키지 관리 파일
* `.env` - 로컬 실행 시 환경 변수 및 RSS 뉴스 소스 관리 파일

---

## 3. Git 브랜치 전략
본 프로젝트는 개발 안정성을 강화하기 위해 이중화 브랜치 전략을 취하고 있습니다.
* **`main` 브랜치 (안정 배포 / 베타)**
  * 안정성이 보장된 운영 버전입니다. GitHub Pages의 정각 자동 스케줄링 및 웹 배포는 오직 이 브랜치를 기반으로만 트리거됩니다.
* **`develop` 브랜치 (통합 개발 / 알파)**
  * 새로운 기능 개발 및 리팩토링이 최종 통합되는 공간입니다.
* **`feature/...` 브랜치 (개별 기능 개발)**
  * 개별 작업(예: `feature/theme-color`)을 독립 격리하여 수행하고, 완료 시 `develop`에 병합합니다.

---

## 4. 로컬 개발 및 실행 방법
1. **의존성 라이브러리 설치**:
   ```bash
   pip install -r requirements.txt
   ```
2. **환경변수 파일 설정**:
   프로젝트 루트에 `.env` 파일을 만들고 아래 내용을 구성합니다.
   ```text
   TECH_FEEDS=https://techcrunch.com/feed/
   POLITICS_FEEDS=https://feeds.bbci.co.uk/news/politics/rss.xml
   INTL_FEEDS=https://feeds.bbci.co.uk/news/world/rss.xml
   GROQ_API_KEY=gsk_... (로컬 요약 수행 시 필수)
   ```
3. **로컬 크롤링 및 대시보드 빌드**:
   ```bash
   python app.py
   ```
4. **자동 코드 업로드**:
   로컬에서 `push.bat`을 실행하면 현재 속해 있는 브랜치를 감지하여 자동으로 원격 저장소에 pull rebase 후 push를 완료합니다.
