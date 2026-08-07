import webview
import yt_dlp
import threading
import sys
import os
import imageio_ffmpeg
import platform
import json
import uuid


class DownloadCancelled(Exception):
    """Raised from a yt-dlp hook when the user cancels an active job."""

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
        self._jobs = {}
        self._jobs_lock = threading.Lock()
        self._active_job_id = None

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
                    raw_entries = p_info.get('entries') or []
                    thumbnails = p_info.get('thumbnails') or []
                    thumbnail_url = thumbnails[-1].get('url') if thumbnails else None
                    if not thumbnail_url:
                        first_entry = next((entry for entry in raw_entries if entry), None)
                        if first_entry and first_entry.get('thumbnails'):
                            thumbnail_url = first_entry['thumbnails'][-1].get('url')

                    playlist_entries = []
                    unavailable_states = {
                        'private', 'premium_only', 'subscriber_only', 'needs_auth'
                    }
                    for index, entry in enumerate(raw_entries, start=1):
                        entry = entry or {}
                        entry_thumbnails = entry.get('thumbnails') or []
                        availability = entry.get('availability')
                        playlist_entries.append({
                            'index': index,
                            'id': entry.get('id'),
                            'title': entry.get('title') or f'영상 {index}',
                            'thumbnail': (
                                entry_thumbnails[-1].get('url') if entry_thumbnails else None
                            ),
                            'duration': entry.get('duration'),
                            'is_available': bool(entry.get('id')) and availability not in unavailable_states,
                        })
                    playlist_info = {
                        'title': p_info.get('title'),
                        'thumbnail': thumbnail_url,
                        'video_count': len(raw_entries),
                        'url': playlist_url,
                        'entries': playlist_entries,
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
                    'entries': playlist_info['entries'],
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
                    'url': playlist_info['url'],
                    'entries': playlist_info['entries'],
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

    # 2. 다운로드 작업 관리
    def download(self, url, format_type='video', scope=None, playlist_items=None):
        """Start a single-video or selected-playlist download in the background."""
        if format_type not in ('audio', 'video'):
            return {'success': False, 'error': '지원하지 않는 다운로드 형식입니다.'}

        if scope is None:
            scope = 'playlist' if 'list=' in url else 'single'
        if scope not in ('playlist', 'single'):
            return {'success': False, 'error': '지원하지 않는 다운로드 범위입니다.'}

        normalized_items = None
        if scope == 'playlist':
            normalized_items = self._normalize_playlist_items(playlist_items)
            if playlist_items is not None and not normalized_items:
                return {'success': False, 'error': '다운로드할 영상을 하나 이상 선택하세요.'}

        return self._start_download_job(url, format_type, scope, normalized_items)

    @staticmethod
    def _normalize_playlist_items(playlist_items):
        if playlist_items is None:
            return None
        try:
            return sorted({int(item) for item in playlist_items if int(item) > 0})
        except (TypeError, ValueError):
            return []

    def _start_download_job(self, url, format_type, scope, playlist_items):
        with self._jobs_lock:
            active_job = self._jobs.get(self._active_job_id)
            if active_job and active_job['status'] in {'queued', 'running', 'cancelling'}:
                return {'success': False, 'error': '이미 진행 중인 다운로드가 있습니다.'}

            job_id = uuid.uuid4().hex[:12]
            job = {
                'id': job_id,
                'url': url,
                'format_type': format_type,
                'scope': scope,
                'playlist_items': playlist_items,
                'cancel_event': threading.Event(),
                'status': 'queued',
                'completed_items': [],
                'failed_items': [],
            }
            self._jobs[job_id] = job
            self._active_job_id = job_id

        thread = threading.Thread(
            target=self._download_thread,
            args=(job_id, url, format_type, scope, playlist_items),
            daemon=True,
        )
        job['thread'] = thread
        thread.start()
        return {'success': True, 'job_id': job_id}

    def cancel_download(self, job_id):
        with self._jobs_lock:
            job = self._jobs.get(job_id)
            if not job:
                return {'success': False, 'error': '다운로드 작업을 찾을 수 없습니다.'}
            if job['status'] not in {'queued', 'running'}:
                return {'success': False, 'error': '취소할 수 있는 상태가 아닙니다.'}
            job['status'] = 'cancelling'
            job['cancel_event'].set()
        return {'success': True}

    def retry_download(self, job_id):
        with self._jobs_lock:
            job = self._jobs.get(job_id)
            if not job:
                return {'success': False, 'error': '다운로드 작업을 찾을 수 없습니다.'}
            retry_items = list(job.get('failed_items') or [])
            if not retry_items:
                return {'success': False, 'error': '재시도할 항목이 없습니다.'}
            url = job['url']
            format_type = job['format_type']
            scope = job['scope']

        playlist_items = retry_items if scope == 'playlist' else None
        return self._start_download_job(url, format_type, scope, playlist_items)

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

    def _build_download_options(
        self, downloads_dir, format_type, scope, progress_hook, playlist_items=None
    ):
        options = {
            'outtmpl': self._download_template(downloads_dir, scope),
            'progress_hooks': [progress_hook],
            'ffmpeg_location': get_ffmpeg_path(),
        }

        if scope == 'playlist':
            # A deleted/private entry must not prevent the rest of the playlist
            # from completing.
            options['ignoreerrors'] = True
            if playlist_items:
                options['playlist_items'] = ','.join(str(item) for item in playlist_items)
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

    def _finish_job(self, job_id, status, completed_items, failed_items):
        with self._jobs_lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job['status'] = status
            job['completed_items'] = sorted(completed_items)
            job['failed_items'] = sorted(failed_items)
            if self._active_job_id == job_id:
                self._active_job_id = None

    # 3. 실제 다운로드와 FFmpeg 설정 (yt-dlp 로직)
    def _download_thread(self, job_id, url, format_type, scope, playlist_items=None):
        completed_entries = set()
        failed_entries = set()
        playlist_total = len(playlist_items) if playlist_items else 0
        selection_positions = {
            item: position for position, item in enumerate(playlist_items or [], start=1)
        }
        last_progress = 0

        with self._jobs_lock:
            job = self._jobs[job_id]
            cancel_event = job['cancel_event']
            job['status'] = 'running'

        def playlist_state(info):
            nonlocal playlist_total
            original_index = info.get('playlist_index') if scope == 'playlist' else None
            try:
                original_index = int(original_index) if original_index is not None else None
            except (TypeError, ValueError):
                original_index = None

            reported_total = (
                info.get('playlist_count') or info.get('n_entries')
                if scope == 'playlist'
                else None
            )
            if not playlist_items and reported_total:
                playlist_total = max(playlist_total, int(reported_total))

            current = selection_positions.get(original_index, original_index)
            return current, playlist_total or reported_total, original_index

        def send_progress(percent, status, info):
            nonlocal last_progress
            current, total, _ = playlist_state(info)
            last_progress = max(last_progress, max(0, min(percent, 100)))
            self._emit_to_frontend('updateProgress', {
                'job_id': job_id,
                'percent': last_progress,
                'status': status,
                'current': current,
                'total': total,
                'completed': len(completed_entries),
                'failed': len(failed_entries),
            })

        def progress_hook(d):
            if cancel_event.is_set():
                raise DownloadCancelled()

            info = d.get('info_dict', {})
            current, total, original_index = playlist_state(info)
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
                entry_key = original_index if scope == 'playlist' else self._entry_key(info)
                if entry_key is not None:
                    completed_entries.add(entry_key)
                    failed_entries.discard(entry_key)
                if scope == 'playlist' and current is not None and playlist_total:
                    status_text = f"처리 중 ({current}/{playlist_total}): {title}"
                    send_progress(current / playlist_total * 100, status_text, info)
                else:
                    send_progress(100, f"처리 중: {title}", info)
            elif d['status'] == 'error':
                entry_key = original_index if scope == 'playlist' else self._entry_key(info)
                if entry_key is not None:
                    failed_entries.add(entry_key)
                if scope == 'playlist' and current is not None and playlist_total:
                    status_text = f"건너뜀 ({current}/{playlist_total}): {title}"
                    send_progress((current / playlist_total) * 100, status_text, info)

        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        ydl_opts = self._build_download_options(
            downloads_dir, format_type, scope, progress_hook, playlist_items
        )

        try:
            if cancel_event.is_set():
                raise DownloadCancelled()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result_code = ydl.download([url])
            if cancel_event.is_set():
                raise DownloadCancelled()

            if scope == 'playlist':
                if playlist_items:
                    requested_entries = set(playlist_items)
                    failed_entries.update(requested_entries - completed_entries)
                    completed_entries.intersection_update(requested_entries)
            elif result_code and not completed_entries:
                failed_entries.add(1)

            completed_count = len(completed_entries)
            failed_count = (
                len(failed_entries)
                if playlist_items or scope == 'single'
                else max(len(failed_entries), playlist_total - completed_count)
            )
            total_count = playlist_total or completed_count + failed_count or 1
            job_status = 'completed' if failed_count == 0 else 'failed'
            self._finish_job(job_id, job_status, completed_entries, failed_entries)
            if failed_count:
                message = f"다운로드 완료: {completed_count}/{total_count}개 성공, {failed_count}개 실패"
            else:
                message = '다운로드 완료! (다운로드 폴더를 확인하세요)'
            self._emit_to_frontend('downloadComplete', {
                'job_id': job_id,
                'success': failed_count == 0,
                'cancelled': False,
                'can_retry': bool(failed_entries),
                'completed': completed_count,
                'failed': failed_count,
                'total': total_count,
                'progress': 100,
                'message': message,
            })
        except DownloadCancelled:
            if scope == 'playlist' and playlist_items:
                remaining_entries = set(playlist_items) - completed_entries
            else:
                remaining_entries = {1} if not completed_entries else set()
            self._finish_job(job_id, 'cancelled', completed_entries, remaining_entries)
            self._emit_to_frontend('downloadComplete', {
                'job_id': job_id,
                'success': False,
                'cancelled': True,
                'can_retry': bool(remaining_entries),
                'completed': len(completed_entries),
                'failed': 0,
                'remaining': len(remaining_entries),
                'total': playlist_total or 1,
                'progress': last_progress,
                'message': '다운로드가 취소되었습니다.',
            })
        except Exception as e:
            if scope == 'playlist' and playlist_items:
                failed_entries.update(set(playlist_items) - completed_entries)
            elif scope == 'single' and not completed_entries:
                failed_entries.add(1)
            self._finish_job(job_id, 'failed', completed_entries, failed_entries)
            self._emit_to_frontend('downloadComplete', {
                'job_id': job_id,
                'success': False,
                'cancelled': False,
                'can_retry': bool(failed_entries),
                'completed': len(completed_entries),
                'failed': max(1, len(failed_entries)),
                'total': playlist_total or len(completed_entries) + 1,
                'progress': last_progress,
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
