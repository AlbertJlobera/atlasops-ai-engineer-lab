import base64
import os

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)


GITHUB_API_URL = "https://api.github.com"

GITHUB_OWNER = os.getenv(
    "GITHUB_OWNER",
    "",
)

GITHUB_REPO = os.getenv(
    "GITHUB_REPO",
    "atlasops-calculation-service",
)

GITHUB_BRANCH = os.getenv(
    "GITHUB_BRANCH",
    "main",
)

GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN",
    "",
)


# =========================================================
# MODELS
# =========================================================

@dataclass
class GitHubFile:
    path: str
    sha: str
    size: int
    content: str | None = None


# =========================================================
# INTERNAL HELPERS
# =========================================================

def _get_headers() -> dict[str, str]:

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = (
            f"Bearer {GITHUB_TOKEN}"
        )

    return headers


def _validate_repository_config():

    if not GITHUB_OWNER:
        raise ValueError(
            "GITHUB_OWNER is not configured."
        )

    if not GITHUB_REPO:
        raise ValueError(
            "GITHUB_REPO is not configured."
        )


def _require_write_token():

    if not GITHUB_TOKEN:
        raise RuntimeError(
            "GITHUB_TOKEN is required "
            "for GitHub write operations."
        )


# =========================================================
# READ OPERATIONS
# =========================================================

def list_repository_files(
    extensions: tuple[str, ...] = (".py",),
    ref: str | None = None,
) -> list[GitHubFile]:

    """
    Lists repository files using the Git tree API.

    By default only Python files are returned.

    extensions=()
    returns every blob in the repository.

    ref can be:
    - branch name
    - tag
    - commit SHA
    """

    _validate_repository_config()

    tree_ref = (
        ref
        or GITHUB_BRANCH
    )

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/"
        f"git/trees/{tree_ref}"
    )

    response = requests.get(
        url,
        headers=_get_headers(),
        params={
            "recursive": "1",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if data.get("truncated"):
        raise RuntimeError(
            "GitHub returned a truncated repository tree."
        )

    files = []

    for item in data.get(
        "tree",
        [],
    ):

        if item.get("type") != "blob":
            continue

        path = item.get(
            "path",
            "",
        )

        # Empty tuple means: include all files.
        if (
            extensions
            and not path.endswith(
                extensions
            )
        ):
            continue

        files.append(
            GitHubFile(
                path=path,
                sha=item["sha"],
                size=item.get(
                    "size",
                    0,
                ),
            )
        )

    return files


def get_file_content(
    file: GitHubFile,
) -> GitHubFile:

    """
    Downloads a Git blob using its SHA and
    returns the decoded UTF-8 content.
    """

    _validate_repository_config()

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/"
        f"git/blobs/{file.sha}"
    )

    response = requests.get(
        url,
        headers=_get_headers(),
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    encoding = data.get(
        "encoding"
    )

    if encoding != "base64":
        raise ValueError(
            "Unsupported GitHub blob encoding: "
            f"{encoding}"
        )

    encoded_content = data.get(
        "content",
        "",
    )

    decoded_content = (
        base64.b64decode(
            encoded_content
        )
        .decode("utf-8")
    )

    return GitHubFile(
        path=file.path,
        sha=file.sha,
        size=file.size,
        content=decoded_content,
    )


def fetch_repository_code() -> list[GitHubFile]:

    """
    Fetches all Python files from the configured repository.
    """

    files = list_repository_files(
        extensions=(".py",)
    )

    return [
        get_file_content(file)
        for file in files
    ]


# =========================================================
# BRANCH OPERATIONS
# =========================================================

def get_branch_sha(
    branch: str = GITHUB_BRANCH,
) -> str:

    """
    Returns the commit SHA currently referenced
    by a repository branch.
    """

    _validate_repository_config()

    encoded_branch = quote(
        branch,
        safe="",
    )

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/"
        f"git/ref/heads/{encoded_branch}"
    )

    response = requests.get(
        url,
        headers=_get_headers(),
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return data[
        "object"
    ][
        "sha"
    ]


def create_branch(
    branch_name: str,
    from_sha: str,
) -> str:

    """
    Creates a new GitHub branch from the supplied
    commit SHA.

    Direct creation/modification of the configured
    base branch is explicitly rejected.
    """

    _validate_repository_config()
    _require_write_token()

    if not branch_name.strip():
        raise ValueError(
            "Branch name cannot be empty."
        )

    if branch_name == GITHUB_BRANCH:
        raise ValueError(
            "Refusing to create or modify "
            "the base branch directly."
        )

    if not from_sha.strip():
        raise ValueError(
            "Source commit SHA cannot be empty."
        )

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/"
        "git/refs"
    )

    response = requests.post(
        url,
        headers=_get_headers(),
        json={
            "ref": (
                f"refs/heads/"
                f"{branch_name}"
            ),
            "sha": from_sha,
        },
        timeout=30,
    )

    response.raise_for_status()

    return branch_name


# =========================================================
# FILE WRITE OPERATIONS
# =========================================================

def update_file(
    path: str,
    content: str,
    original_sha: str,
    branch: str,
    commit_message: str,
) -> str:

    """
    Updates an existing repository file on a
    non-base branch.

    original_sha protects against blindly
    overwriting another version of the file.

    Returns the created commit SHA.
    """

    _validate_repository_config()
    _require_write_token()

    if branch == GITHUB_BRANCH:
        raise ValueError(
            "Direct writes to the base "
            "branch are prohibited."
        )

    if not path.strip():
        raise ValueError(
            "File path cannot be empty."
        )

    if not original_sha.strip():
        raise ValueError(
            "Original file SHA is required."
        )

    if not commit_message.strip():
        raise ValueError(
            "Commit message cannot be empty."
        )

    encoded_path = quote(
        path,
        safe="/",
    )

    encoded_content = (
        base64.b64encode(
            content.encode(
                "utf-8"
            )
        )
        .decode("utf-8")
    )

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/"
        f"contents/{encoded_path}"
    )

    response = requests.put(
        url,
        headers=_get_headers(),
        json={
            "message": commit_message,
            "content": encoded_content,
            "sha": original_sha,
            "branch": branch,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return data[
        "commit"
    ][
        "sha"
    ]


# =========================================================
# PULL REQUEST OPERATIONS
# =========================================================

def create_pull_request(
    branch: str,
    title: str,
    body: str,
    base_branch: str = GITHUB_BRANCH,
) -> dict:

    """
    Creates a Pull Request from branch to base_branch.

    Returns:
    {
        "number": int,
        "url": str
    }
    """

    _validate_repository_config()
    _require_write_token()

    if not branch.strip():
        raise ValueError(
            "Pull request branch cannot be empty."
        )

    if branch == base_branch:
        raise ValueError(
            "Pull request head and base "
            "branches cannot be identical."
        )

    if not title.strip():
        raise ValueError(
            "Pull request title cannot be empty."
        )

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/"
        "pulls"
    )

    response = requests.post(
        url,
        headers=_get_headers(),
        json={
            "title": title,
            "head": branch,
            "base": base_branch,
            "body": body,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return {
        "number": data["number"],
        "url": data["html_url"],
    }

def get_file_sha(
    path: str,
    ref: str = GITHUB_BRANCH,
) -> str:

    """
    Returns the current blob SHA of a file
    at a specific branch, tag or commit.
    """

    _validate_repository_config()

    if not path.strip():
        raise ValueError(
            "File path cannot be empty."
        )

    encoded_path = quote(
        path,
        safe="/",
    )

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/"
        f"contents/{encoded_path}"
    )

    response = requests.get(
        url,
        headers=_get_headers(),
        params={
            "ref": ref,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected file metadata for: {path}"
        )

    return data["sha"]