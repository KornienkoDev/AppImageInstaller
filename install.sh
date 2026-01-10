#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting AppImage Installer Setup...${NC}"

# 1. Check if python script exists
if [ ! -f "appimage_installer.py" ]; then
    echo "Error: appimage_installer.py not found in this folder!"
    exit 1
fi

# 2. Install the Python script to user bin
mkdir -p ~/.local/bin
cp appimage_installer.py ~/.local/bin/appimage-installer
chmod +x ~/.local/bin/appimage-installer
echo -e "${GREEN}[1/6] Script installed to ~/.local/bin${NC}"

# 3. Create System Symlink (Requires Sudo)
echo -e "${YELLOW}Enter your password to create a system-wide shortcut (or press Ctrl+C to skip):${NC}"
sudo ln -sf ~/.local/bin/appimage-installer /usr/local/bin/appimage-installer
echo -e "${GREEN}[2/6] System shortcut created${NC}"

# 4. Create the Installer Desktop Entry (Updated to use --install)
mkdir -p ~/.local/share/applications
cat <<EOF > ~/.local/share/applications/appimage-installer.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=AppImage Installer
Comment=Install AppImage files locally
Exec=appimage-installer --install %f
Icon=package-x-generic
Categories=Utility;System;
NoDisplay=false
MimeType=application/vnd.appimage;
EOF
echo -e "${GREEN}[3/6] Installer entry created${NC}"

# 5. Create the Uninstaller Desktop Entry
cat <<EOF > ~/.local/share/applications/appimage-uninstaller.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=AppImage Uninstaller
Comment=Remove an installed AppImage
Exec=appimage-installer --uninstall %f
Icon=edit-delete
Categories=Utility;System;
NoDisplay=false
MimeType=application/vnd.appimage;
EOF
echo -e "${GREEN}[4/6] Uninstaller entry created${NC}"

# 6. Create MIME Type
mkdir -p ~/.local/share/mime/packages
cat <<EOF > ~/.local/share/mime/packages/appimage.xml
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/vnd.appimage">
    <comment>AppImage Application</comment>
    <glob pattern="*.AppImage"/>
    <glob pattern="*.appimage"/>
    <icon name="application-x-executable"/>
  </mime-type>
</mime-info>
EOF
echo -e "${GREEN}[5/6] MIME type registered${NC}"

# 7. Update Databases
update-mime-database ~/.local/share/mime
update-desktop-database ~/.local/share/applications/
echo -e "${GREEN}[6/6] System databases updated${NC}"

# Finish
echo ""
echo -e "${GREEN}Installation Complete!${NC}"