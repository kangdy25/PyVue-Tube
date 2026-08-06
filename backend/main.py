import webview
import yt_dlp
import threading
import sys
import os
import imageio_ffmpeg
import platform
import json

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
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(parsed.query)
        
        has_playlist = 'list' in query
        has_video = 'v' in query or 'youtu.be' in parsed.netloc or parsed.path.startswith('/shorts/')
        
        video_id = None
        if 'youtu.be' in parsed.netloc:
            video_id = parsed.path.strip('/')
            has_video = True
        elif 'v' in query:
            video_id = query['v'][0]
            
        playlist_id = query['list'][0] if 'list' in query else None
        
        playlist_info = None
        video_info = None
        
        try:
            # 1. 재생목록 정보 가져오기
            if has_playlist:
                playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                ydl_opts_playlist = {
                    'quiet': True,
                    'skip_download': True,
                    'extract_flat': True,
                    'ffmpeg_location': get_ffmpeg_path(),
                }
                with yt_dlp.YoutubeDL(ydl_opts_playlist) as ydl:
                    p_info = ydl.extract_info(playlist_url, download=False)
                    thumbnails = p_info.get('thumbnails') or []
                    thumbnail_url = thumbnails[-1].get('url') if thumbnails else None
                    if not thumbnail_url:
                        entries = p_info.get('entries') or []
                        if entries and entries[0].get('thumbnails'):
                            thumbnail_url = entries[0]['thumbnails'][-1].get('url')
                    playlist_info = {
                        'title': p_info.get('title'),
                        'thumbnail': thumbnail_url,
                        'video_count': len(p_info.get('entries', [])),
                        'url': playlist_url
                    }
                    
            # 2. 영상 정보 가져오기
            if has_video:
                video_url = url
                ydl_opts_video = {
                    'quiet': True,
                    'skip_download': True,
                    'noplaylist': True,
                    'ffmpeg_location': get_ffmpeg_path(),
                }
                with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                    v_info = ydl.extract_info(video_url, download=False)
                    video_info = {
                        'title': v_info.get('title'),
                        'thumbnail': v_info.get('thumbnail'),
                        'duration': v_info.get('duration'),
                        'url': video_url
                    }
                    
            # 결합된 결과 반환
            if playlist_info and video_info:
                return {
                    'success': True,
                    'is_playlist': True,
                    'title': playlist_info['title'],
                    'thumbnail': playlist_info['thumbnail'],
                    'video_count': playlist_info['video_count'],
                    'url': playlist_info['url'],
                    'video_title': video_info['title'],
                    'video_thumbnail': video_info['thumbnail'],
                    'video_duration': video_info['duration'],
                    'video_url': video_info['url']
                }
            elif playlist_info:
                return {
                    'success': True,
                    'is_playlist': True,
                    'title': playlist_info['title'],
                    'thumbnail': playlist_info['thumbnail'],
                    'video_count': playlist_info['video_count'],
                    'url': playlist_info['url']
                }
            elif video_info:
                return {
                    'success': True,
                    'title': video_info['title'],
                    'thumbnail': video_info['thumbnail'],
                    'duration': video_info['duration'],
                    'url': video_info['url']
                }
            else:
                return {'success': False, 'error': '유효한 영상 또는 재생목록 정보를 찾을 수 없습니다.'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # 2. 다운로드 시작 (백그라운드 스레드 실행)
    def download(self, url, format_type='video', scope=None):
        """Start a single-video or whole-playlist download in the background."""
        if format_type not in ('audio', 'video'):
            return {'success': False, 'error': '지원하지 않는 다운로드 형식입니다.'}

        # Keep calls from older frontends working while making mixed URLs default to
        # a playlist download. The UI always supplies the scope explicitly.
        if scope is None:
            scope = 'playlist' if 'list=' in url else 'single'
        if scope not in ('playlist', 'single'):
            return {'success': False, 'error': '지원하지 않는 다운로드 범위입니다.'}

        # 메인 UI가 멈추지 않도록 스레드로 실행
        thread = threading.Thread(
            target=self._download_thread,
            args=(url, format_type, scope),
            daemon=True,
        )
        thread.start()
        return {'success': True}

    def _emit_to_frontend(self, function_name, payload):
        """Send JSON, rather than interpolated strings, to the Vue window safely."""
        if not webview.windows:
            return
        try:
            payload_json = json.dumps(payload, ensure_ascii=False)
            webview.windows[0].evaluate_js(f"window.{function_name}({payload_json})")
        except Exception:
            # A closing application window must not stop the downloader thread.
            pass

    @staticmethod
    def _entry_key(info):
        return str(info.get('id') or info.get('playlist_index') or info.get('title') or '')

    @staticmethod
    def _download_template(downloads_dir, scope):
        if scope == 'playlist':
            return os.path.join(
                downloads_dir,
                '%(playlist_title)s',
                '%(playlist_index)02d - %(title)s.%(ext)s',
            )
        return os.path.join(downloads_dir, '%(title)s.%(ext)s')

    def _build_download_options(self, downloads_dir, format_type, scope, progress_hook):
        options = {
            'outtmpl': self._download_template(downloads_dir, scope),
            'progress_hooks': [progress_hook],
            'ffmpeg_location': get_ffmpeg_path(),
        }

        if scope == 'playlist':
            # A deleted/private entry must not prevent the rest of the playlist
            # from completing.
            options['ignoreerrors'] = True
        else:
            # A watch URL can contain a list parameter; this keeps the explicit
            # "current video only" action scoped to that one video.
            options['noplaylist'] = True

        if format_type == 'audio':
            options.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            options.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            })
        return options

    # 3. 실제 다운로드와 FFmpeg 설정 (yt-dlp 로직)
    def _download_thread(self, url, format_type, scope):
        completed_entries = set()
        failed_entries = set()
        playlist_total = 0

        def playlist_state(info):
            nonlocal playlist_total
            current = info.get('playlist_index') if scope == 'playlist' else None
            total = (
                info.get('playlist_count') or info.get('n_entries')
                if scope == 'playlist'
                else None
            )
            if total:
                playlist_total = max(playlist_total, int(total))
            return current, playlist_total or total

        def send_progress(percent, status, info):
            current, total = playlist_state(info)
            self._emit_to_frontend('updateProgress', {
                'percent': max(0, min(percent, 100)),
                'status': status,
                'current': current,
                'total': total,
                'completed': len(completed_entries),
                'failed': len(failed_entries),
            })

        def progress_hook(d):
            info = d.get('info_dict', {})
            current, total = playlist_state(info)
            title = info.get('title', '영상')

            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                if total:
                    percent = (downloaded / total) * 100
                    if scope == 'playlist' and current is not None and playlist_total:
                        overall_percent = ((current - 1) + (percent / 100)) / playlist_total * 100
                        status_text = f"다운로드 중 ({current}/{playlist_total}): {title}"
                        send_progress(overall_percent, status_text, info)
                    else:
                        send_progress(percent, f"다운로드 중: {title}", info)
            elif d['status'] == 'finished':
                completed_entries.add(self._entry_key(info))
                if scope == 'playlist' and current is not None and playlist_total:
                    status_text = f"처리 중 ({current}/{playlist_total}): {title}"
                    send_progress(current / playlist_total * 100, status_text, info)
                else:
                    send_progress(100, f"처리 중: {title}", info)
            elif d['status'] == 'error':
                failed_entries.add(self._entry_key(info))
                if scope == 'playlist' and current is not None and playlist_total:
                    status_text = f"건너뜀 ({current}/{playlist_total}): {title}"
                    send_progress((current / playlist_total) * 100, status_text, info)

        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        ydl_opts = self._build_download_options(downloads_dir, format_type, scope, progress_hook)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result_code = ydl.download([url])

            failed_count = len(failed_entries)
            completed_count = len(completed_entries)
            if scope == 'playlist' and playlist_total:
                # Not every extractor emits an error hook for unavailable entries.
                failed_count = max(failed_count, playlist_total - completed_count)
            elif result_code and not completed_count:
                failed_count = max(failed_count, 1)

            total_count = playlist_total or completed_count + failed_count
            if failed_count:
                message = f"다운로드 완료: {completed_count}/{total_count}개 성공, {failed_count}개 실패"
            else:
                message = '다운로드 완료! (다운로드 폴더를 확인하세요)'
            self._emit_to_frontend('downloadComplete', {
                'success': failed_count == 0,
                'completed': completed_count,
                'failed': failed_count,
                'total': total_count,
                'message': message,
            })
        except Exception as e:
            self._emit_to_frontend('downloadComplete', {
                'success': False,
                'completed': len(completed_entries),
                'failed': max(1, len(failed_entries)),
                'total': playlist_total or len(completed_entries) + 1,
                'message': f"오류 발생: {str(e)}",
            })

def main():
    api = BackendApi()
    
    # 개발 모드일 경우 Vite 구동 주소인 localhost:5173 사용
    url = 'http://localhost:5173'
    
    # sys.frozen은 PyInstaller로 패키징되었을 때 True가 됩니다.
    if getattr(sys, 'frozen', False) or (len(sys.argv) > 1 and sys.argv[1] == '--prod'):
        # 빌드 후 배포 시에는 PyInstaller MEIPASS 또는 상위 폴더 기준의 경로 사용
        url = get_resource_path(os.path.join('frontend', 'dist', 'index.html'))

    window = webview.create_window(
        title='ArchiveTube',
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
