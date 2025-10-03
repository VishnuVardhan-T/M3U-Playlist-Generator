import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

# Build command
PyInstaller.__main__.run([
    'm3u_playlist_gen.py',
    '--onedir',              # Faster than --onefile
    '--windowed',            # No console
    '--upx-dir=C:/Users/vishn/Downloads/upx-5.0.0-win64/upx-5.0.0-win64',     # Path to UPX
    '--name=M3U_Playlist_Gen',
    '--add-data=assets/*;assets/',
    '--icon=assets/icon.ico',
    '--exclude-module=tests',  # Remove unnecessary modules
    '--clean'                # Clean cache
])