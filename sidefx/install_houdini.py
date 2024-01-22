#https://www.sidefx.com/docs/houdini/licensing/script_houdini_installations.html#script_houdini_install
import argparse
import sys
import os
import stat
import requests
import shutil
import subprocess
import platform

import sidefx

# Return the current platform keyword that can be passed into
# the SideFX Web API functions if current platform can be
# recognized; Otherwise, an empty string '' will be returned.
def get_current_platform():
    current_platform = platform.system()
    if current_platform == 'Windows' or current_platform.startswith('CYGWIN'):
        return 'win64'
    elif current_platform == 'Darwin':
        return 'macos'
    elif current_platform == 'Linux':
        return 'linux'
    else:
        return ''


# Return a sidefx.service object allowing access to API functions.
def create_service(client_id, client_secret_key):
    return sidefx.service(
        access_token_url="https://www.sidefx.com/oauth2/application_token",
        client_id=client_id,
        client_secret_key=client_secret_key,
        endpoint_url="https://www.sidefx.com/api/")


# Download the file specified in "build" argument and return the
# downloaded filename on success.
def download_build(service, build):
    platform = get_current_platform()
    build_info = service.download.get_daily_build_download(
        build["product"], build["version"], build["build"], platform)
    download_file(build_info["download_url"], build_info["filename"])
    return build_info["filename"]


# Download the file hosted on "url" and name it as "filename"
def download_file(url, filename):
    with requests.get(url, stream=True) as response:
        with open(filename, "wb") as open_file:
            shutil.copyfileobj(response.raw, open_file)
    make_executable(filename)


# Add executable privilege to the file specified in "file_path"
def make_executable(file_path):
    stat_info = os.stat(file_path)
    os.chmod(file_path, stat.ST_MODE | stat.S_IEXEC | stat.S_IXUSR |
            stat.S_IXGRP | stat.S_IRUSR | stat.S_IRGRP)


def run(username, password):
    product = "houdini-launcher"
    platform = get_current_platform()
    service = create_service(username, password)

    # Retrieve the daily builds list, if you want the latest production
    # you can skip this step
    builds = service.download.get_daily_builds_list(
        product, version=None, platform=platform, only_production=True)

    # Retrieve the latest daily build available
    launcher_file = download_build(service, builds[0])

    # Installation part
    #TODO: May need to wait until download has completed.
    # Mount the Launcher ".dmg" file.
    subprocess.call(["hdiutil", "attach", launcher_file])

    # Create "houdini_launcher" folder if not exists
    # if not os.path.exists("houdini_launcher"):
    #     os.mkdir("houdini_launcher")

    # # Install Launcher to "houdini_launcher" folder next to current script, 
    # # which could be modified to your prefered path.
    # subprocess.call(["cp", "-R", "/Volumes/Houdini/Houdini Launcher.app", "houdini_launcher"])

    # # Unmount the Launcher ".dmg" file
    # subprocess.call(["hdiutil", "unmount", "/Volumes/Houdini"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", type=str, help="SideFx account username")
    parser.add_argument("-p", "--password", type=str, help="SideFx account password")

    _args, other_args = parser.parse_known_args()
    username = _args.username
    password = _args.password
    if not username or not password:
        print('Please set username and password')
        print('Example: -u username -p password')
        sys.exit()
    else:
        run(username, password)