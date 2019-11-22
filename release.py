from datetime import datetime
from enum import auto, Flag, unique
from itertools import takewhile
import re
import subprocess
from typing import Callable, NamedTuple, Optional, Set, Tuple

import statham as package


@unique
class Bump(Flag):
    PATCH = auto()
    MINOR = auto()
    MAJOR = auto()


CHANGELOG = "CHANGELOG.md"
UNRELEASED_TAG = "## [Unreleased]"


CHANGE_TYPES: Set[str] = {
    "Security",
    "Deprecated",
    "Added",
    "Changed",
    "Removed",
    "Fixed",
}


class Version(NamedTuple):
    major: int
    minor: int
    patch: int

    def __repr__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def parse_version(cls, version_string: str) -> "Version":
        if not re.match(r"^\d+\.\d+\.\d+$", version_string):
            raise ValueError(f"Invalid version: {version_string}")
        return cls(*(int(v) for v in version_string.split(".")))

    def bump(self, bump_type: Bump) -> "Version":
        if bump_type is Bump.MAJOR:
            return Version(self.major + 1, 0, 0)
        if bump_type is Bump.MINOR:
            return Version(self.major, self.minor + 1, 0)
        return Version(self.major, self.minor, self.patch + 1)


def repo_compare(
    old: Optional[Version] = None, new: Optional[Version] = None
) -> str:
    return (
        f"[{new or 'Unreleased'}]: http://github.com/jacksmith15/"
        f"statham-schema/compare/{old or 'initial'}..{new or 'HEAD'}\n"
    )


def bash(command: str, capture: bool = True) -> str:
    if not capture:
        subprocess.call(command.split(" "))
    return subprocess.check_output(command.split(" ")).decode("utf-8")


def bool_input(message, default=True):
    return (
        input(message + (" [Y/n] " if default else " [y/N] "))
        .lower()
        .startswith("n" if default else "y")
        ^ default
    )


def parse_version(version_string):
    if not re.match(r"^\d+\.\d+\.\d+$", version_string):
        raise ValueError(f"Invalid version: {version_string}")
    return Version(*(int(v) for v in version_string.split(".")))


def consume_to_version(version: Version = None) -> Callable[[str], bool]:
    def _consume(line: str):
        if line.startswith("## "):
            if version:
                chglog_version = Version.parse_version(
                    line.replace("## ", "").replace("\n", "").strip("[]")
                )
                assert chglog_version == version, (
                    f"Version in {package.__name__}.__version__ "
                    f"({version}) does not match current "
                    f"version in {CHANGELOG} "
                    f"({chglog_version})"
                )
                return False
            assert line.startswith(
                "## [Unreleased]"
            ), f"No unreleased tag found. It must be the first section."
            return False
        return True

    return _consume


def get_unreleased(current_version: Version) -> Tuple[Version, str]:
    with open(CHANGELOG, "r", encoding="utf8") as file:
        _ = [*takewhile(consume_to_version(), file)]
        unreleased_lines = [
            *takewhile(consume_to_version(current_version), file)
        ]
    assert unreleased_lines, f"No changes found in changelog."
    unreleased_sections = {
        line.replace("### ", "").strip("\n")
        for line in unreleased_lines
        if line.startswith("### ")
    }
    assert (
        unreleased_sections <= CHANGE_TYPES
    ), f"Got unknown change types: {unreleased_sections - CHANGE_TYPES}"
    bump_type = Bump.PATCH
    if unreleased_sections - {"Fixed"}:
        bump_type = Bump.MINOR
    if "BREAKING" in "".join(unreleased_lines):
        bump_type = Bump.MAJOR
    return (
        current_version.bump(bump_type),
        "".join(unreleased_lines).rstrip("\n"),
    )


def update_versions(current_version: Version, new_version: Version):
    with open(package.__file__, "r", encoding="utf8") as file:
        today = datetime.now().strftime("%Y-%m-%d")
        new_init = [
            *takewhile(lambda l: not re.match(r"^__version__ = .*", l), file),
            f'__version__ = "{new_version}"\n',
            *file,
        ]
    with open(package.__file__, "w", encoding="utf8") as file:
        file.writelines(new_init)

    with open(CHANGELOG, "r", encoding="utf8") as file:
        new_changelog = [
            *takewhile(lambda l: not l.startswith("## [Unreleased]"), file),
            "## [Unreleased]\n",
            "\n",
            f"## [{repr(new_version)}] - {today}\n",
            *takewhile(lambda l: not re.match("^[Unreleased]:.*", l), file),
            repo_compare(old=new_version),
            repo_compare(old=current_version, new=new_version),
            *file,
        ]
    with open(CHANGELOG, "w", encoding="utf8") as file:
        file.writelines(new_changelog)


def checkout_master():
    try:
        bash("git diff-index --quiet HEAD --")
    except subprocess.CalledProcessError:
        raise RuntimeError(
            'You have uncommitted changes, "git stash" to save them'
        )

    branch = bash("git rev-parse --abbrev-ref HEAD")[:-1]

    if branch != "master":
        bash("git checkout master")

    bash("git fetch origin")
    latest = bash("git ls-remote origin master").split("\t")[0]
    bash(f"git reset --hard {latest}")
    bash("git pull --tags")


def tag_release(next_version: Version):
    bash(
        f"git commit -i {CHANGELOG} {package.__name__}/__init__.py -m release/{next_version}"
    )
    bash(f"git tag -a {next_version} -m {next_version}")
    bash(f"git push origin master")


def verify_release(
    current_version: Version, next_version: Version, content: str
) -> bool:
    return bool_input(
        f"""
This release would update to {next_version} from {current_version} due to
the following changes:

{content}

Proceed?
"""
    )


def main():
    # checkout_master()
    current_version: Version = Version.parse_version(package.__version__)
    next_version, change_content = get_unreleased(current_version)
    if not verify_release(current_version, next_version, change_content):
        return
    print(f"Bumping to {next_version}")
    update_versions(current_version, next_version)
    # tag_release(next_version)


if __name__ == "__main__":
    main()
