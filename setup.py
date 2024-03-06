import os, subprocess, json, sys, shutil
from urllib.request import Request, urlopen
from urllib.parse import urlparse

# Will download or update LunarCore.jar for Dockerfile & StarRailData with LunarCore-Configs repos preparing resources directory for compose volume mount

LUNAR_CORE_REPOSITORY = "https://github.com/Melledy/LunarCore"
LUNAR_CORE_DOWNLOAD_URL = f"{LUNAR_CORE_REPOSITORY}/releases/latest/download/LunarCore.jar"

LUNAR_CORE_CONFIGS_REPOSITORY = "https://gitlab.com/Melledy/LunarCore-Configs"
LUNAR_CORE_CONFIGS_GIT_URL = f"{LUNAR_CORE_CONFIGS_REPOSITORY}.git"
LUNAR_CORE_CONFIGS_FOLDER = os.path.basename(urlparse(LUNAR_CORE_CONFIGS_REPOSITORY).path)

STARRAIL_DATA_REPOSITORY = "https://github.com/Dimbreath/StarRailData"
STARRAIL_DATA_GIT_URL = f"{STARRAIL_DATA_REPOSITORY}.git"
STARRAIL_DATA_FOLDER = os.path.basename(urlparse(STARRAIL_DATA_REPOSITORY).path)

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

def clone_repository(repository, branch = "main"):
    subprocess.run(
        [
            "git", "clone",
            "--depth", "1",
            "-b", branch,
            repository
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
    LATEST_LUNARCORE = f"LunarCore{VERSION}.jar"

    if not os.path.exists(LATEST_LUNARCORE):
        download_file(LUNAR_CORE_DOWNLOAD_URL, LATEST_LUNARCORE)

        if not os.path.exists(LUNAR_CORE_CONFIGS_FOLDER):
            clone_repository(LUNAR_CORE_CONFIGS_GIT_URL)
        else:
            pull_repository(LUNAR_CORE_CONFIGS_FOLDER)

        if not os.path.exists(STARRAIL_DATA_FOLDER):
            clone_repository(STARRAIL_DATA_GIT_URL)
        else:
            pull_repository(STARRAIL_DATA_FOLDER)
        return True
    else:
        return False

def build_resources():
    shutil.rmtree("resources", ignore_errors=True)
    os.mkdir("resources")

    entlist = os.listdir(STARRAIL_DATA_FOLDER)
    ignore_git = shutil.ignore_patterns(".git")
    ignored_names = ignore_git(STARRAIL_DATA_FOLDER, entlist)
    for ent in entlist:
        if ent in ignored_names:
            continue
        os.symlink(
            os.path.join(f"../{STARRAIL_DATA_FOLDER}", ent),
            os.path.join("resources", ent), target_is_directory=os.path.isdir(ent)
        )

    shutil.copytree(LUNAR_CORE_CONFIGS_FOLDER, "resources", ignore=ignore_git, dirs_exist_ok=True)

if __name__ == "__main__":
    if download_or_update_resources():
        build_resources()
