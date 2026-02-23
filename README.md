# PyVue-Tube 🎵

![PyVue-Tube Icon](frontend/public/app_icon.png)

A modern, fast, and lightweight YouTube video and audio downloader built with **Vue 3** for the frontend and **Python (pywebview + yt-dlp)** for the backend.

PyVue-Tube runs as a standalone desktop application by leveraging web technologies for a beautiful UI and native Python for robust video downloading capabilities.

---

## 🌟 Features

- **Beautiful Glassmorphic UI:** Modern and sleek interface with smooth animations built using standard SCSS and Vue 3.
- **Fast & Reliable Downloads:** Powered by the industry-standard `yt-dlp` library.
- **Video & Audio Options:** Download videos in the best available quality (merged with FFmpeg) or extract audio directly to MP3 (192kbps).
- **Real-time Progress:** Displays download progress directly in the UI.
- **Cross-Platform:** Can be packaged into `.exe` for Windows and `.dmg` for macOS.

---

## 🛠️ Tech Stack

- **Frontend:** Vue 3 (Composition API), Vite, SCSS (Glassmorphism design)
- **Backend:** Python 3, `pywebview`
- **Downloading Core:** `yt-dlp`, `imageio-ffmpeg`
- **Packaging:** PyInstaller, create-dmg (macOS)

---

## 🚀 Getting Started (Development)

To run the application in a development environment with hot-reloading:

### 1. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 2. Backend Setup
In a new terminal window:
```bash
cd backend
python -m venv venv

# Activate venv (Windows)
venv\Scripts\activate
# Activate venv (macOS/Linux)
# source venv/bin/activate

pip install -r requirements.txt
python main.py
```
*Note: Make sure your Vite server is running on `http://localhost:5173` before starting `main.py`.*

---

## 📦 Building for Production

We provide an automated build script `build.py` to package the application into a single executable file.

### Prerequisites
Make sure your custom app icon is located at `frontend/public/app_icon.png`.

### Build Command
Run the build script from the project root:
```bash
# Ensure your python virtual environment is activated
python deploy/build.py
```

### Outputs
- **Windows:** You will find `PyVue-Tube.exe` in the `dist/` directory.
- **macOS:** You will find `PyVue-Tube.app` in the `dist/` directory.

### macOS `.dmg` Packaging
If you are on macOS, you can wrap the `.app` into a `.dmg` installer using `create-dmg`. Refer to the [macOS Packaging Guide](deploy/macOS_Packaging.md) for detailed instructions.

---

## 📝 License
This project is for educational and personal use. Ensure you comply with YouTube's Terms of Service when using this tool.
