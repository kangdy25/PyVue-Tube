import importlib.util
import json
import sys
import threading
import types
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = BACKEND_DIR / 'main.py'


def load_backend_module():
    """Load the backend without requiring desktop-only dependencies in CI."""
    sys.modules.setdefault('webview', types.SimpleNamespace(windows=[]))
    sys.modules.setdefault('imageio_ffmpeg', types.SimpleNamespace(get_ffmpeg_exe=lambda: 'ffmpeg'))
    sys.modules.setdefault('yt_dlp', types.SimpleNamespace(YoutubeDL=None))

    spec = importlib.util.spec_from_file_location('archivetube_backend', MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


backend = load_backend_module()


class FakeYoutubeDL:
    def __init__(self, options):
        self.options = options

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def extract_info(self, url, download=False):
        if 'playlist?list=' in url:
            return {
                'title': 'My playlist',
                'thumbnails': [{'url': 'playlist.jpg'}],
                'entries': [
                    {'id': 'one', 'title': 'First', 'duration': 60, 'availability': 'public'},
                    {'id': 'two', 'title': 'Second', 'duration': 90, 'availability': 'public'},
                ],
            }
        return {
            'title': 'Current video',
            'thumbnail': 'video.jpg',
            'duration': 120,
        }


class FakeWindow:
    def __init__(self):
        self.scripts = []

    def evaluate_js(self, script):
        self.scripts.append(script)


class CapturingThread:
    instances = []

    def __init__(self, target, args, daemon):
        self.target = target
        self.args = args
        self.daemon = daemon

    def start(self):
        self.instances.append(self)


def register_job(api, job_id, playlist_items, cancel_event=None):
    api._jobs[job_id] = {
        'id': job_id,
        'url': 'https://youtube.com/playlist?list=abc',
        'format_type': 'video',
        'scope': 'playlist',
        'playlist_items': playlist_items,
        'cancel_event': cancel_event or threading.Event(),
        'status': 'queued',
        'completed_items': [],
        'failed_items': [],
    }
    api._active_job_id = job_id


class PlaylistDownloadTests(unittest.TestCase):
    def setUp(self):
        CapturingThread.instances = []

    def test_download_defaults_mixed_urls_to_playlist_scope(self):
        with patch.object(backend.threading, 'Thread', CapturingThread):
            result = backend.BackendApi().download(
                'https://www.youtube.com/watch?v=current&list=playlist-id', 'video'
            )

        thread = CapturingThread.instances[0]
        self.assertTrue(result['success'])
        self.assertEqual(thread.args[3], 'playlist')
        self.assertIsNone(thread.args[4])
        self.assertTrue(thread.daemon)

    def test_empty_playlist_selection_is_rejected(self):
        result = backend.BackendApi().download(
            'https://youtube.com/playlist?list=abc', 'video', 'playlist', []
        )

        self.assertFalse(result['success'])
        self.assertIn('하나 이상', result['error'])

    def test_get_info_returns_selectable_playlist_entries(self):
        with patch.object(backend.yt_dlp, 'YoutubeDL', FakeYoutubeDL):
            result = backend.BackendApi().get_info(
                'https://www.youtube.com/watch?v=current&list=playlist-id'
            )

        self.assertTrue(result['success'])
        self.assertTrue(result['is_playlist'])
        self.assertEqual(result['video_count'], 2)
        self.assertEqual(result['url'], 'https://www.youtube.com/playlist?list=playlist-id')
        self.assertEqual(result['video_url'], 'https://www.youtube.com/watch?v=current&list=playlist-id')
        self.assertEqual([entry['index'] for entry in result['entries']], [1, 2])
        self.assertTrue(all(entry['is_available'] for entry in result['entries']))

    def test_download_options_keep_selected_playlist_files_together(self):
        api = backend.BackendApi()
        options = api._build_download_options(
            '/Downloads', 'audio', 'playlist', lambda _: None, [2, 4]
        )

        self.assertEqual(
            options['outtmpl'],
            '/Downloads/%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s',
        )
        self.assertEqual(options['playlist_items'], '2,4')
        self.assertTrue(options['ignoreerrors'])
        self.assertEqual(options['postprocessors'][0]['preferredcodec'], 'mp3')
        self.assertEqual(options['postprocessors'][0]['preferredquality'], '192')

    def test_download_options_enable_the_bundled_node_runtime(self):
        with patch.object(backend, 'get_node_path', return_value='/bundle/bin/node'):
            options = backend.BackendApi()._build_download_options(
                '/Downloads', 'video', 'single', lambda _: None
            )

        self.assertEqual(options['js_runtimes'], {'node': {'path': '/bundle/bin/node'}})

    def test_single_video_options_ignore_a_list_parameter(self):
        options = backend.BackendApi()._build_download_options(
            '/Downloads', 'video', 'single', lambda _: None
        )

        self.assertEqual(options['outtmpl'], '/Downloads/%(title)s.%(ext)s')
        self.assertTrue(options['noplaylist'])
        self.assertEqual(options['merge_output_format'], 'mp4')

    def test_cancel_marks_an_active_job(self):
        api = backend.BackendApi()
        with patch.object(backend.threading, 'Thread', CapturingThread):
            started = api.download(
                'https://youtube.com/playlist?list=abc', 'video', 'playlist', [1, 3]
            )
            cancelled = api.cancel_download(started['job_id'])

        job = api._jobs[started['job_id']]
        self.assertTrue(cancelled['success'])
        self.assertEqual(job['status'], 'cancelling')
        self.assertTrue(job['cancel_event'].is_set())

    def test_retry_starts_only_failed_playlist_items(self):
        api = backend.BackendApi()
        register_job(api, 'old-job', [1, 2, 3, 4])
        api._jobs['old-job']['status'] = 'failed'
        api._jobs['old-job']['failed_items'] = [2, 4]
        api._active_job_id = None

        with patch.object(backend.threading, 'Thread', CapturingThread):
            result = api.retry_download('old-job')

        self.assertTrue(result['success'])
        self.assertEqual(CapturingThread.instances[0].args[4], [2, 4])

    def test_playlist_failure_continues_and_reports_retry_items(self):
        class DownloadingYoutubeDL(FakeYoutubeDL):
            def download(self, urls):
                hook = self.options['progress_hooks'][0]
                first = {
                    'id': 'one', 'title': "O'Reilly's first video", 'playlist_index': 1,
                    'playlist_count': 3,
                }
                unavailable = {
                    'id': 'two', 'title': 'Private video', 'playlist_index': 2,
                    'playlist_count': 3,
                }
                third = {
                    'id': 'three', 'title': 'Last video', 'playlist_index': 3,
                    'playlist_count': 3,
                }
                hook({'status': 'downloading', 'total_bytes': 100, 'downloaded_bytes': 50, 'info_dict': first})
                hook({'status': 'finished', 'info_dict': first})
                hook({'status': 'error', 'info_dict': unavailable})
                hook({'status': 'finished', 'info_dict': third})
                return 0

        api = backend.BackendApi()
        register_job(api, 'test-job', [1, 2, 3])
        window = FakeWindow()
        with patch.object(backend.webview, 'windows', [window]), patch.object(
            backend.yt_dlp, 'YoutubeDL', DownloadingYoutubeDL
        ):
            api._download_thread(
                'test-job', 'https://youtube.com/playlist?list=abc', 'video', 'playlist', [1, 2, 3]
            )

        progress_payloads = [
            json.loads(script.removeprefix('window.updateProgress(').removesuffix(')'))
            for script in window.scripts
            if script.startswith('window.updateProgress(')
        ]
        completion = json.loads(
            next(script for script in window.scripts if script.startswith('window.downloadComplete('))
            .removeprefix('window.downloadComplete(')
            .removesuffix(')')
        )

        self.assertEqual(progress_payloads[0]['job_id'], 'test-job')
        self.assertEqual(progress_payloads[0]['total'], 3)
        self.assertIn("O'Reilly", progress_payloads[0]['status'])
        self.assertEqual(completion['completed'], 2)
        self.assertEqual(completion['failed'], 1)
        self.assertTrue(completion['can_retry'])
        self.assertEqual(api._jobs['test-job']['failed_items'], [2])

    def test_cancelled_job_can_retry_remaining_items(self):
        cancel_event = threading.Event()

        class CancellingYoutubeDL(FakeYoutubeDL):
            def download(self, urls):
                hook = self.options['progress_hooks'][0]
                first = {
                    'id': 'one', 'title': 'First', 'playlist_index': 1, 'playlist_count': 3,
                }
                second = {
                    'id': 'two', 'title': 'Second', 'playlist_index': 2, 'playlist_count': 3,
                }
                hook({'status': 'finished', 'info_dict': first})
                cancel_event.set()
                hook({'status': 'downloading', 'total_bytes': 100, 'downloaded_bytes': 10, 'info_dict': second})

        api = backend.BackendApi()
        register_job(api, 'cancel-job', [1, 2, 3], cancel_event)
        window = FakeWindow()
        with patch.object(backend.webview, 'windows', [window]), patch.object(
            backend.yt_dlp, 'YoutubeDL', CancellingYoutubeDL
        ):
            api._download_thread(
                'cancel-job', 'https://youtube.com/playlist?list=abc', 'video', 'playlist', [1, 2, 3]
            )

        completion = json.loads(
            next(script for script in window.scripts if script.startswith('window.downloadComplete('))
            .removeprefix('window.downloadComplete(')
            .removesuffix(')')
        )
        self.assertTrue(completion['cancelled'])
        self.assertEqual(completion['remaining'], 2)
        self.assertTrue(completion['can_retry'])
        self.assertEqual(api._jobs['cancel-job']['failed_items'], [2, 3])


if __name__ == '__main__':
    unittest.main()
