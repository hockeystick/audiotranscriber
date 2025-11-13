#!/bin/bash

# Create Mac Application for MP3 Audio Transcriber
# This script creates a .app bundle that can be launched from Finder

echo "Creating MP3 Audio Transcriber.app..."

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create the app bundle structure
APP_NAME="MP3 Audio Transcriber.app"
APP_PATH="$DIR/$APP_NAME"

# Remove old app if it exists
if [ -d "$APP_PATH" ]; then
    rm -rf "$APP_PATH"
fi

# Create app bundle directories
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# Create the Info.plist file
cat > "$APP_PATH/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.audiotranscriber.app</string>
    <key>CFBundleName</key>
    <string>MP3 Audio Transcriber</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
</dict>
</plist>
EOF

# Create the launcher script
cat > "$APP_PATH/Contents/MacOS/launcher" << 'LAUNCHER_EOF'
#!/bin/bash

# Get the app bundle directory
APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"
PROJECT_DIR="$(dirname "$APP_DIR")"

# Open Terminal and run the start script
osascript <<APPLESCRIPT
tell application "Terminal"
    activate
    set currentTab to do script "cd '$PROJECT_DIR' && bash start_app.sh"
end tell
APPLESCRIPT
LAUNCHER_EOF

# Make the launcher executable
chmod +x "$APP_PATH/Contents/MacOS/launcher"

# Make the start_app.sh executable too
chmod +x "$DIR/start_app.sh"

echo ""
echo "✅ Success! Created '$APP_NAME'"
echo ""
echo "You can now:"
echo "  1. Double-click '$APP_NAME' to launch the transcriber"
echo "  2. Drag it to your Applications folder"
echo "  3. Add it to your Dock for quick access"
echo ""
echo "Note: The first time you open it, macOS may ask for permission."
echo "      Click 'Open' to allow it to run."
echo ""
