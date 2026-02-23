import webview
import yt_dlp
import threading
import sys
import os
import imageio_ffmpeg
import platform

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    return os.path.join(base_path, relative_path)

def get_ffmpeg_path():
    """
    Get the path to the ffmpeg executable.
    In PyInstaller bundle, we expect it in the 'bin' directory.
    """
    try:
        base_path = sys._MEIPASS
        # We will copy imageio_ffmpeg's binary to our bundled 'bin' folder
        exe_name = 'ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg'
        return os.path.join(base_path, 'bin', exe_name)
    except Exception:
        # Not bundled, use imageio_ffmpeg directly
        return imageio_ffmpeg.get_ffmpeg_exe()


class BackendApi:
    def __init__(self):
        pass

    # 1. 영상 정보 가져오기 (JS -> Python 호출)
    def get_info(self, url):
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'ffmpeg_location': get_ffmpeg_path(),
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'success': True,
                    'title': info.get('title'),
                    'thumbnail': info.get('thumbnail'),
                    'duration': info.get('duration')
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # 2. 다운로드 시작 (백그라운드 스레드 실행)
    def download(self, url, format_type='video'):
        # 메인 UI가 멈추지 않도록 스레드로 실행
        thread = threading.Thread(target=self._download_thread, args=(url, format_type))
        thread.start()
        return {'success': True}

    # 3. 실제 다운로드와 FFmpeg 설정 (yt-dlp 로직)
    def _download_thread(self, url, format_type):
        def progress_hook(d):
            if d['status'] == 'downloading':
                # 진행률 계산
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                if total:
                    percent = (downloaded / total) * 100
                    # Python -> JS로 진행률 전송 (JS의 글로벌 함수 호출)
                    if webview.windows:
                        webview.windows[0].evaluate_js(f"window.updateProgress({percent})")
            elif d['status'] == 'finished':
                if webview.windows:
                    webview.windows[0].evaluate_js(f"window.updateStatus('처리 중...')")

        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        ydl_opts = {
            'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'), # 다운로드 파일명 형식
            'progress_hooks': [progress_hook],
            'ffmpeg_location': get_ffmpeg_path(),
        }

        # 🎯 yt-dlp 포맷/옵션 설정
        if format_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192', # 192kbps 고음질
                }],
            })
        else: # 비디오 (최고화질 영상 + 오디오 병합)
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            if webview.windows:
                webview.windows[0].evaluate_js("window.downloadComplete(true, '다운로드 완료! (다운로드 폴더를 확인하세요)')")
        except Exception as e:
            if webview.windows:
                webview.windows[0].evaluate_js(f"window.downloadComplete(false, '오류 발생: {str(e)}')")

def main():
    api = BackendApi()
    
    # 개발 모드일 경우 Vite 구동 주소인 localhost:5173 사용
    url = 'http://localhost:5173'
    
    # sys.frozen은 PyInstaller로 패키징되었을 때 True가 됩니다.
    if getattr(sys, 'frozen', False) or (len(sys.argv) > 1 and sys.argv[1] == '--prod'):
        # 빌드 후 배포 시에는 PyInstaller MEIPASS 또는 상위 폴더 기준의 경로 사용
        url = get_resource_path(os.path.join('frontend', 'dist', 'index.html'))

    window = webview.create_window(
        title='PyVue-Tube 🎵', 
        url=url, 
        js_api=api, 
        width=900, 
        height=700,
        background_color='#111827' # 다크모드 배경색 매칭 (gray-900)
    )
    api.window = window
    is_prod = getattr(sys, 'frozen', False) or (len(sys.argv) > 1 and sys.argv[1] == '--prod')
    webview.start(debug=not is_prod)

if __name__ == '__main__':
    main()
