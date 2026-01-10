AppImage Installer

A simple Python tool to manage AppImages on Linux. It allows you to install, update, and uninstall AppImages via a right-click or command line.

Features

    🖱️ Right-Click Integration: Install or uninstall AppImages directly from your file manager (Thunar, Nautilus, Dolphin, etc.).
    🧹 Clean Management: Automatically moves files to ~/Applications and organizes icons.
    🔄 Smart Updates: Re-running the installer updates the existing application without creating duplicates.
    ⚙️ GUI & CLI: Works seamlessly via mouse clicks or terminal commands.

Installation
Prerequisites

    Python 3 installed on your system.
    Standard Linux desktop environment (GNOME, KDE, XFCE, etc.).

Quick Setup

    Download appimage_installer.py and install.sh and place them in the same folder.

    Open your terminal in that directory and run the setup script:

    bash install.sh

    Restart your File Manager for the changes to take effect.

Usage
Option A: Graphical Interface (Right-Click)
To Install

    Right-click any .AppImage file.
    Select Open With > AppImage Installer.
    A terminal window will display the installation progress.
    Once finished, the application appears in your system menu!

To Uninstall

    Right-click the .AppImage file (you can use the original downloaded file).
    Select Open With > AppImage Uninstaller.
    The tool will locate the installed version and remove the app, icon, and menu entry.

Option B: Command Line

If you prefer using the terminal, you can use the following commands:

Install an AppImageappimage-installer --install /path/to/application.AppImage# 
Uninstall an AppImageappimage-installer --uninstall /path/to/application.AppImage


File Locations 

The tool organizes your applications in the following directories: 
Type
 	
Location 
Apps	  	~/Applications/ 
Icons	 	~/.local/share/icons/Applications/ 
Shortcuts 	~/.local/share/applications/ 
 
  
Troubleshooting 

"AppImage Installer not showing in Open With menu" 

    Ensure you ran the setup script: bash install.sh. 
    Make sure you restarted your file manager. 
    Check the "Other Application" submenu in the "Open With" dialog. 

"Command not found: appimage-installer" 

    Ensure the symlink was created during setup. Run:
    bash
     
      

    sudo ln -sf ~/.local/bin/appimage-installer /usr/local/bin/appimage-installer
     
     
      

"Application is not appearing in the menu" 

    This usually happens if the AppImage contains a TryExec line that checks for system binaries that don't exist. 
    This script automatically removes TryExec lines to fix this. If the issue persists, check the .desktop file in ~/.local/share/applications/ manually. 

License 

This project is open source and available under the MIT License.
