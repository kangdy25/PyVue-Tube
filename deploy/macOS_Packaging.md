# macOS Packaging Guide (.app to .dmg)

The `build.py` script automatically utilizes PyInstaller to generate the `.app` bundle on macOS. However, to distribute your application smoothly, you typically want to wrap it in a `.dmg` file.

## Prerequisites
Ensure you have `create-dmg` installed. You can install it via Homebrew:
```bash
brew install create-dmg
```
Alternatively, using npm (as you just did):
```bash
npm install -g create-dmg
```

## Step 1: Run the Build Script
First, ensure you are in the project root and run the automated build script:
```bash
python deploy/build.py
```
This will:
1. Build the Vue.js frontend.
2. Copy the correct `ffmpeg` binary.
3. Generate the `app_icon.icns` file from `app_icon.png`.
4. Run PyInstaller and output a `PyVue-Tube.app` in the `dist/` directory.

## Step 2: Test the `.app` Bundle
Before packaging, navigate to the `dist` folder and test your `.app` bundle:
```bash
open dist/PyVue-Tube.app
```
Ensure everything is working properly (including downloading videos using the bundled ffmpeg).

## Step 3: Create the `.dmg` File
Navigate to your project root and run `create-dmg`:

```bash
create-dmg \
  --volname "PyVue-Tube Installer" \
  --volicon "app_icon.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "PyVue-Tube.app" 200 190 \
  --hide-extension "PyVue-Tube.app" \
  --app-drop-link 600 185 \
  "dist/PyVue-Tube.dmg" \
  "dist/PyVue-Tube.app/"
```

### Explanation of flags:
- `--volname`: The name of the mounted disk image.
- `--volicon`: The icon for the mounted volume.
- `--window-pos`, `--window-size`: The initial window position and size when the user opens the dmg.
- `--icon-size`: The size of the icons inside the dmg window.
- `--icon`: The position of your app's icon inside the dmg window.
- `--app-drop-link`: Creates a symbolic link to `/Applications` inside the dmg window for drag-and-drop installation.

## Step 4: Verification
Once the command finishes, `PyVue-Tube.dmg` will be created in the `dist` folder. Double-click it to verify the sleek drag-and-drop installation works as expected!
