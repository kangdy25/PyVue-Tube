import importlib.util
import json
import sys
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
                'entries': [{'id': 'one'}, {'id': 'two'}],
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


class PlaylistDownloadTests(unittest.TestCase):
    def test_download_defaults_mixed_urls_to_playlist_scope(self):
        started = []

        class CapturingThread:
            def __init__(self, target, args, daemon):
                self.target = target
                self.args = args
                self.daemon = daemon

            def start(self):
                started.append(self)

        with patch.object(backend.threading, 'Thread', CapturingThread):
            result = backend.BackendApi().download(
                'https://www.youtube.com/watch?v=current&list=playlist-id', 'video'
            )

        self.assertTrue(result['success'])
        self.assertEqual(started[0].args[-1], 'playlist')
        self.assertTrue(started[0].daemon)

    def test_get_info_distinguishes_playlist_and_current_video(self):
        with patch.object(backend.yt_dlp, 'YoutubeDL', FakeYoutubeDL):
            result = backend.BackendApi().get_info(
                'https://www.youtube.com/watch?v=current&list=playlist-id'
            )

        self.assertTrue(result['success'])
        self.assertTrue(result['is_playlist'])
        self.assertEqual(result['video_count'], 2)
        self.assertEqual(result['url'], 'https://www.youtube.com/playlist?list=playlist-id')
        self.assertEqual(result['video_url'], 'https://www.youtube.com/watch?v=current&list=playlist-id')

    def test_download_options_keep_playlist_files_together(self):
        api = backend.BackendApi()
        options = api._build_download_options('/Downloads', 'audio', 'playlist', lambda _: None)

        self.assertEqual(
            options['outtmpl'],
            '/Downloads/%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s',
        )
        self.assertTrue(options['ignoreerrors'])
        self.assertEqual(options['postprocessors'][0]['preferredcodec'], 'mp3')
        self.assertEqual(options['postprocessors'][0]['preferredquality'], '192')

    def test_single_video_options_ignore_a_list_parameter(self):
        options = backend.BackendApi()._build_download_options(
            '/Downloads', 'video', 'single', lambda _: None
        )

        self.assertEqual(options['outtmpl'], '/Downloads/%(title)s.%(ext)s')
        self.assertTrue(options['noplaylist'])
        self.assertEqual(options['merge_output_format'], 'mp4')

    def test_playlist_failure_continues_and_reports_json_safe_summary(self):
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

        window = FakeWindow()
        with patch.object(backend.webview, 'windows', [window]), patch.object(
            backend.yt_dlp, 'YoutubeDL', DownloadingYoutubeDL
        ):
            backend.BackendApi()._download_thread('https://youtube.com/playlist?list=abc', 'video', 'playlist')

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

        self.assertEqual(progress_payloads[0]['total'], 3)
        self.assertIn("O'Reilly", progress_payloads[0]['status'])
        self.assertEqual(completion['completed'], 2)
        self.assertEqual(completion['failed'], 1)
        self.assertEqual(completion['total'], 3)


if __name__ == '__main__':
    unittest.main()
