#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import glob
import configparser
import tempfile
import pathlib

def uninstall_appimage(source_path):
    """
    Removes an installed AppImage, its icon, and desktop entry based on the filename.
    """
    filename = os.path.basename(source_path)
    apps_bin_dir = os.path.expanduser("~/Applications")
    applications_dir = os.path.expanduser("~/.local/share/applications")
    icons_dir = os.path.expanduser("~/.local/share/icons/Applications")
    
    installed_binary = os.path.join(apps_bin_dir, filename)
    
    print(f"Checking for installation of: {filename}")

    if not os.path.exists(installed_binary):
        print(f"'{filename}' is not installed in {apps_bin_dir}")
        return

    # 1. Find the .desktop file associated with this binary
    desktop_file = None
    icon_to_delete = None

    print("Searching for desktop entry...")
    for f in glob.glob(os.path.join(applications_dir, "*.desktop")):
        try:
            # Read Exec line to see if it matches our binary
            with open(f, 'r') as dfile:
                content = dfile.readlines()
                
                for line in content:
                    if line.strip().lower().startswith("exec="):
                        # Extract the path from Exec=/path/to/app %u
                        # We split to get the first part (the command)
                        cmd_path = line.strip().split('=', 1)[1].split()[0]
                        
                        if cmd_path == installed_binary:
                            desktop_file = f
                            # While we are here, let's find the icon too
                            for icon_line in content:
                                if icon_line.strip().lower().startswith("icon="):
                                    icon_path = icon_line.strip().split('=', 1)[1]
                                    # Check if it's in our custom icons folder
                                    if icon_path.startswith(icons_dir):
                                        icon_to_delete = icon_path
                            break
                if desktop_file:
                    break
        except Exception as e:
            print(f"Error reading {f}: {e}")

    # 2. Delete the files
    removed_items = []
    
    # Remove Binary
    if os.path.exists(installed_binary):
        os.remove(installed_binary)
        removed_items.append(installed_binary)

    # Remove Desktop Entry
    if desktop_file and os.path.exists(desktop_file):
        os.remove(desktop_file)
        removed_items.append(desktop_file)
    elif not desktop_file:
        print("Warning: Could not find a matching .desktop entry for this AppImage.")

    # Remove Icon
    if icon_to_delete and os.path.exists(icon_to_delete):
        os.remove(icon_to_delete)
        removed_items.append(icon_to_delete)

    # 3. Feedback
    if removed_items:
        print("\nUninstallation Complete! Removed:")
        for item in removed_items:
            print(f"  - {item}")
        try:
            subprocess.Popen(['notify-send', 'AppImage Uninstaller', f"Successfully removed {filename}"])
        except FileNotFoundError:
            pass
    else:
        print("Nothing was removed.")

def install_appimage(source_appimage):
    """
    Installs an AppImage into the system.
    """
    source_appimage = os.path.abspath(source_appimage)

    if not os.path.exists(source_appimage):
        print(f"Error: File not found: {source_appimage}")
        sys.exit(1)

    print(f"Installing: {os.path.basename(source_appimage)}")

    # Create a temporary directory for extraction work
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Extract the AppImage
        print("Extracting files...")
        try:
            subprocess.run(
                [source_appimage, "--appimage-extract"],
                cwd=temp_dir,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            print("Error: Failed to extract AppImage. Is it corrupted?")
            sys.exit(1)

        extracted_root = os.path.join(temp_dir, "squashfs-root")

        # 2. Find the .desktop file inside the extracted files
        desktop_files = glob.glob(os.path.join(extracted_root, "*.desktop"))
        
        if not desktop_files:
            print("Error: No .desktop file found inside AppImage.")
            sys.exit(1)

        # Usually there is only one, but if multiple, we pick the first one
        source_desktop = desktop_files[0]
        desktop_filename = os.path.basename(source_desktop)

        # 3. Parse the source desktop file to find icon and name info
        config = configparser.ConfigParser(interpolation=None)
        config.read(source_desktop)
        
        if "Desktop Entry" not in config:
            print("Error: Invalid .desktop file format.")
            sys.exit(1)

        app_name = config["Desktop Entry"].get("Name", "AppImageApp")
        icon_name = config["Desktop Entry"].get("Icon", None)

        # Prepare destination directories
        applications_dir = os.path.expanduser("~/.local/share/applications")
        icons_dir = os.path.expanduser("~/.local/share/icons/Applications")
        apps_bin_dir = os.path.expanduser("~/Applications")

        os.makedirs(applications_dir, exist_ok=True)
        os.makedirs(icons_dir, exist_ok=True)
        os.makedirs(apps_bin_dir, exist_ok=True)

        # 4. Handle AppImage File (Overwrite if exists)
        final_appimage_path = os.path.join(apps_bin_dir, os.path.basename(source_appimage))
        
        if os.path.exists(final_appimage_path):
            print(f"Updating existing file: {os.path.basename(source_appimage)}")
        
        shutil.copy2(source_appimage, final_appimage_path)
        os.chmod(final_appimage_path, 0o755)

        # 5. Handle Icon
        final_icon_path = ""
        if icon_name:
            # Search for icon inside extracted AppImage
            possible_icon_files = glob.glob(os.path.join(extracted_root, f"{icon_name}.*")) + \
                                  glob.glob(os.path.join(extracted_root, f"usr/share/icons/hicolor/*/apps/{icon_name}.*"))

            # Fallback to .DirIcon
            if not possible_icon_files:
                possible_icon_files = glob.glob(os.path.join(extracted_root, ".DirIcon"))

            if possible_icon_files:
                source_icon = possible_icon_files[0]
                icon_ext = os.path.splitext(source_icon)[1]
                
                # Base name for the icon
                appimage_basename = os.path.basename(final_appimage_path)
                final_icon_path = os.path.join(icons_dir, f"{appimage_basename}{icon_ext}")

                print(f"Copying icon to: {final_icon_path}")
                shutil.copy2(source_icon, final_icon_path)

        # 6. Create/Update .desktop entry
        target_desktop_path = os.path.join(applications_dir, desktop_filename)

        with open(source_desktop, 'r') as f:
            desktop_content = f.readlines()

        new_content = []
        for line in desktop_content:
            # Remove TryExec
            if line.strip().lower().startswith("tryexec="):
                continue
            # Update Exec line
            elif line.strip().lower().startswith("exec="):
                parts = line.strip().split(' ', 1)
                args = parts[1] if len(parts) > 1 else ""
                new_content.append(f"Exec={final_appimage_path} {args}\n")
            # Update Icon line
            elif line.strip().lower().startswith("icon="):
                if final_icon_path:
                    new_content.append(f"Icon={final_icon_path}\n")
                else:
                    new_content.append(f"Icon={final_appimage_path}\n")
            # Remove Path
            elif line.strip().lower().startswith("path="):
                continue
            else:
                new_content.append(line)

        # Ensure Icon is present if it wasn't in the original
        if not any(line.startswith("Icon=") for line in new_content):
             new_content.append(f"Icon={final_icon_path or final_appimage_path}\n")

        print(f"Creating menu entry: {target_desktop_path}")
        with open(target_desktop_path, 'w') as f:
            f.writelines(new_content)
        
        os.chmod(target_desktop_path, 0o755)

    print("\nInstallation Complete!")
    print(f"Check your application menu for '{app_name}'.")
    
    try:
        subprocess.Popen(['notify-send', 'AppImage Installer', f"Successfully installed {app_name}!"])
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Install: python3 appimage_installer.py --install <path_to_appimage>")
        print("  Remove:  python3 appimage_installer.py --uninstall <path_to_appimage>")
        sys.exit(1)

    # Filter out flags to get the path
    args = [a for a in sys.argv[1:] if a != "--install" and a != "--uninstall"]

    if not args:
        print("Error: No AppImage file path provided.")
        sys.exit(1)

    target_file = args[0]

    if "--install" in sys.argv:
        install_appimage(target_file)
    elif "--uninstall" in sys.argv:
        uninstall_appimage(target_file)
    else:
        print("Error: Please specify --install or --uninstall.")