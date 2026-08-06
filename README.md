# ArchiveTube

![ArchiveTube 아이콘](frontend/public/icon.png)

ArchiveTube는 YouTube 영상과 재생목록을 개인 미디어 보관함으로 정리할 수 있는 데스크톱 애플리케이션입니다. 영상은 MP4로 저장하고, 오디오는 192kbps MP3로 추출할 수 있습니다.

Vue 3 기반 인터페이스와 Python·pywebview 백엔드를 결합했으며, 실제 미디어 처리는 `yt-dlp`와 FFmpeg가 담당합니다.

## 주요 기능

- 단일 YouTube 영상의 MP4 다운로드 및 MP3 오디오 추출
- YouTube 재생목록 전체 일괄 다운로드
- 영상과 재생목록이 함께 포함된 URL에서 전체 재생목록 또는 현재 영상 선택
- 재생목록별 폴더와 순번이 포함된 파일명 자동 생성
- 접근할 수 없는 항목을 건너뛰고 나머지 다운로드 계속 진행
- 현재 항목, 전체 진행률, 성공·실패 개수를 보여주는 실시간 상태 화면
- macOS와 Windows 데스크톱 앱 패키징 지원

## 저장 위치

다운로드 결과는 운영체제의 기본 `Downloads` 폴더에 저장됩니다.

단일 영상:

```text
Downloads/영상 제목.mp4
Downloads/영상 제목.mp3
```

재생목록:

```text
Downloads/재생목록 제목/01 - 영상 제목.mp4
Downloads/재생목록 제목/02 - 영상 제목.mp4
```

## 기술 구성

- 프런트엔드: Vue 3, Vite, SCSS
- 데스크톱 셸: Python 3, pywebview
- 미디어 처리: yt-dlp, imageio-ffmpeg
- 앱 패키징: PyInstaller

## 개발 환경 실행

### 1. Python 환경 준비

```bash
cd backend
python -m venv venv
```

macOS 또는 Linux:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

Windows:

```powershell
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 프런트엔드 실행

프로젝트 루트에서 다음 명령을 실행합니다.

```bash
cd frontend
npm install
npm run dev
```

### 3. 데스크톱 앱 실행

프런트엔드 개발 서버가 실행 중인 상태에서 별도 터미널을 열어 실행합니다.

```bash
backend/venv/bin/python backend/main.py
```

Windows에서는 `backend/venv/Scripts/python.exe backend/main.py`를 사용합니다.

## 테스트

백엔드 테스트:

```bash
python -m unittest discover -s backend/tests -v
```

프런트엔드 프로덕션 빌드 확인:

```bash
cd frontend
npm run build
```

## 데스크톱 앱 빌드

빌드 환경에는 `PyInstaller`와 `Pillow`가 추가로 필요합니다.

```bash
backend/venv/bin/python -m pip install pyinstaller Pillow
backend/venv/bin/python deploy/build.py
```

빌드 결과:

- macOS: `dist/ArchiveTube.app`
- Windows: `dist/ArchiveTube.exe`

macOS용 DMG 생성 방법은 [macOS 패키징 가이드](deploy/macOS_Packaging.md)를 참고하세요.

## 프로젝트 구조

```text
backend/             Python·pywebview 백엔드와 테스트
frontend/            Vue 3 사용자 인터페이스
deploy/              데스크톱 앱 패키징 스크립트와 문서
dist/                생성된 애플리케이션
```

## 사용 안내

ArchiveTube는 YouTube 또는 Google이 제작·승인·후원한 제품이 아닙니다. 본인이 다운로드 및 보관할 권한이 있는 콘텐츠에만 사용하고, YouTube 이용약관과 해당 지역의 저작권 관련 법률을 준수하세요.
