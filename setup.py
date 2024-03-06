import os, subprocess, json, sys, shutil
from urllib.request import Request, urlopen
from urllib.parse import urlparse

# Will download or update LunarCore.jar for Dockerfile & StarRailData with LunarCore-Configs repos preparing resources directory for compose volume mount

DOWNLOADS_FOLDER = "downloads"
if not os.path.exists(DOWNLOADS_FOLDER):
    os.mkdir(DOWNLOADS_FOLDER)

LUNAR_CORE_REPOSITORY = "https://github.com/Melledy/LunarCore"
LUNAR_CORE_DOWNLOAD_URL = f"{LUNAR_CORE_REPOSITORY}/releases/latest/download/LunarCore.jar"

LUNAR_CORE_CONFIGS_REPOSITORY = "https://gitlab.com/Melledy/LunarCore-Configs"
LUNAR_CORE_CONFIGS_GIT_URL = f"{LUNAR_CORE_CONFIGS_REPOSITORY}.git"
LUNAR_CORE_CONFIGS_FOLDER = os.path.join(
    DOWNLOADS_FOLDER,
    os.path.basename(urlparse(LUNAR_CORE_CONFIGS_REPOSITORY).path)
)

STARRAIL_DATA_REPOSITORY = "https://github.com/Dimbreath/StarRailData"
STARRAIL_DATA_GIT_URL = f"{STARRAIL_DATA_REPOSITORY}.git"
STARRAIL_DATA_FOLDER = os.path.join(
    DOWNLOADS_FOLDER,
    os.path.basename(urlparse(STARRAIL_DATA_REPOSITORY).path)
)

common_github_headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def github_get_latest_release(url):
    repository = urlparse(url).path[1:]
    data = urlopen(
        Request(
            f"https://api.github.com/repos/{repository}/releases/latest",
            headers=common_github_headers
        )
    ).read()

    return json.loads(data)

def github_get_latest_version(repository):
    return github_get_latest_release(repository)["tag_name"]

def download_file(url, path):
    with open(path, "wb") as f:
        f.write(urlopen(
            Request(
                url,
                headers=common_github_headers
            )
        ).read())

def clone_repository(repository, path, branch = "main"):
    subprocess.run(
        [
            "git", "clone",
            "--depth", "1",
            "-b", branch,
            repository, path
        ],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

def pull_repository(path):
    subprocess.run(
        ["git", "pull"],
        cwd=path,
        stdout=sys.stdout,
        stderr=sys.stderr
    )

def download_or_update_resources():
    '''
    returns true when updated false otherwise
    '''
    VERSION = github_get_latest_version(LUNAR_CORE_REPOSITORY)

    with open(os.path.join(DOWNLOADS_FOLDER, "VERSION"), "w") as f:
        print(VERSION)
        f.write(VERSION)

    LATEST_LUNARCORE = os.path.join(DOWNLOADS_FOLDER, f"LunarCore{VERSION}.jar")

    if not os.path.exists(LATEST_LUNARCORE):
        download_file(LUNAR_CORE_DOWNLOAD_URL, LATEST_LUNARCORE)

        lunar_core_symlink_path = os.path.join(
            DOWNLOADS_FOLDER,
            "LunarCore.jar"
        )
        if os.path.exists(lunar_core_symlink_path):
            os.remove(lunar_core_symlink_path)
        # Symlink to allow Dockerfile just use LunarCore.jar as reference
        os.symlink(LATEST_LUNARCORE, lunar_core_symlink_path)

    if not os.path.exists(LUNAR_CORE_CONFIGS_FOLDER):
        clone_repository(LUNAR_CORE_CONFIGS_GIT_URL, LUNAR_CORE_CONFIGS_FOLDER, "main")
    else:
        pull_repository(LUNAR_CORE_CONFIGS_FOLDER)

    if not os.path.exists(STARRAIL_DATA_FOLDER):
        clone_repository(STARRAIL_DATA_GIT_URL, STARRAIL_DATA_FOLDER, "master")
    else:
        pull_repository(STARRAIL_DATA_FOLDER)

if __name__ == "__main__":
    download_or_update_resources()
    shutil.copytree(
        LUNAR_CORE_CONFIGS_FOLDER,
        STARRAIL_DATA_FOLDER,
        ignore=shutil.ignore_patterns(".git"),
        dirs_exist_ok=True
    )
