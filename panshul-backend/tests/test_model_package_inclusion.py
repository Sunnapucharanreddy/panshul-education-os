import subprocess
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_database_models_are_not_ignored_by_git():
    for relative_path in (
        "panshul-backend/app/db/models/__init__.py",
        "panshul-backend/app/db/models/user.py",
        "panshul-backend/app/db/models/learning.py",
    ):
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "-q", "--", relative_path],
            cwd=REPOSITORY_ROOT,
            check=False,
        )

        # git check-ignore exits 1 when a path is not ignored.
        assert result.returncode == 1, f"{relative_path} must remain part of Git source"


def test_docker_context_explicitly_includes_database_models():
    dockerignore = Path(__file__).resolve().parents[1] / ".dockerignore"
    rules = dockerignore.read_text(encoding="utf-8").splitlines()

    assert "!app/db/models/" in rules
    assert "!app/db/models/**" in rules
