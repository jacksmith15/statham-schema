import re
import subprocess
from datetime import datetime
from itertools import takewhile
from re import match
from typing import NamedTuple, Optional


def parse_version(version_string):
    if not match(r"^\d+\.\d+\.\d+$", version_string):
        raise ValueError(f"Invalid version: {version_string}")
    return Version(*(int(v) for v in version_string.split(".")))


def bash(command, capture=True):
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


def is_semver_update_valid(old, new):
    major_update = Version(old.major + 1, 0, 0)
    minor_update = Version(old.major, old.minor + 1, 0)
    patch_update = Version(old.major, old.minor, old.patch + 1)
    return new in {major_update, minor_update, patch_update}


class Version(NamedTuple):
    major: int
    minor: int
    patch: int

    def __repr__(self):
        return f"{self.major}.{self.minor}.{self.patch}"


class ReleaseFailed(Exception):
    pass


class ReleaseManager:
    def __init__(self):
        self.new_version: Optional[Version] = None
        self.old_version: Optional[Version] = None
        self.url: Optional[str] = None
        self.old_tag: Optional[str] = None

    def release(self):
        self.checkout_master()
        self.validate_changelog()
        self.update_changelog_version()
        self.update_open_api_version()
        self.checkout_release()

    def checkout_master(self):
        try:
            bash("git diff-index --quiet HEAD --")
        except subprocess.CalledProcessError:
            raise ReleaseFailed(
                'You have uncommitted changes, "git stash" to save them'
            )

        branch = bash("git rev-parse --abbrev-ref HEAD")[:-1]

        if branch != "master":
            bash("git checkout master")

        bash("git fetch origin")
        latest = bash("git ls-remote origin master").split("\t")[0]
        bash(f"git reset --hard {latest}")
        bash("git pull --tags")
        self.old_tag = bash('git tag -l "release*" --sort=refname | tail -n1')

    def validate_changelog(self):
        new_release_changes, old_release_changes = self.parse_changelog()

        if not "".join(new_release_changes).strip():
            raise ReleaseFailed("Found no changes to release in changelog.")

        if old_release_changes:
            print(
                "Changes were found added to another release in the changelog:"
            )
            print("\n".join(old_release_changes))
            if not bool_input("Was this intended?", default=False):
                raise ReleaseFailed(
                    "Please make adjustments to the changelog "
                    "and rerun the release."
                )

        self.parse_new_version()

        contains_breaking_changes = (
            "breaking" in "\n".join(new_release_changes).lower()
        )
        same_major_version = self.old_version[0] == self.new_version[0]
        bumped = False

        if same_major_version and contains_breaking_changes:
            if bool_input(
                "Detected a potential breaking change in the changelog, "
                "but the major version was not incremented. "
                "Should the next release bump the major version?"
            ):
                self.new_version = Version(self.old_version.major + 1, 0, 0)
                print(f"Bumping next release version to {self.new_version}")
                bumped = True
            else:
                print(f"Next release version staying as {self.new_version}")

        contains_additions = "+### Added" in new_release_changes
        same_minor_version = self.old_version[1] == self.new_version[1]

        if not bumped and same_minor_version and contains_additions:
            if bool_input(
                "Additional functionality was found added in the changelog, "
                "but the minor version was not incremented. "
                "Should the next release bump the minor version?"
            ):
                self.new_version = Version(
                    self.old_version.major, self.old_version.minor + 1, 0
                )
                print(f"Bumping next release version to {self.new_version}")
            else:
                print(f"Next release version staying as {self.new_version}")

    def parse_changelog(self):
        diff = bash(
            f"git --no-pager diff -U10000 master {self.old_tag} -- CHANGELOG.md"
        )

        if not diff:
            raise ReleaseFailed(
                "No changes were documented in the changelog "
                "for this release, stopping."
            )

        # Ignore everything in changelog until unreleased section.
        diff_iterator = iter(diff.split("\n"))
        unreleased = r".##\s(|.)Unreleased(|.)"
        _detail = list(
            takewhile(lambda l: not re.search(unreleased, l), diff_iterator)
        )

        # Parse changes found in unreleased section.
        new_release_changes = list(
            takewhile(self.parse_old_version, diff_iterator)
        )

        # Parse all changes found in sections already released.
        _old_release_header = next(diff_iterator)
        old_release_changes = list(
            filter(lambda l: l.startswith("+"), diff_iterator)
        )
        return new_release_changes, old_release_changes

    def parse_old_version(self, line):
        if re.search(r"( |\+)##\s\[", line):
            version_string = line[1:].split(" ")[1].lstrip("[").rstrip("]")
            try:
                self.old_version = parse_version(version_string)
            except ValueError as ex:
                raise ReleaseFailed(*ex.args)
            return False
        return True

    def parse_new_version(self):
        def get_new_version():
            version_string = input(
                f"Enter the next version (current {self.old_version}): "
            )
            try:
                return parse_version(version_string)
            except ValueError:
                return Version(0, 0, 0)

        self.new_version = get_new_version()

        while not is_semver_update_valid(self.old_version, self.new_version):
            print(
                f"Upgrading from {self.old_version} to {self.new_version} is invalid."
            )
            print("https://semver.org/")
            self.new_version = get_new_version()

    def take_until_unreleased(self, line):
        if line.startswith("[Unreleased]:"):
            search = re.search(r".*\s(\w+:\/\/(.*?)\/(.*?)\/(.*?))\/.*", line)
            self.url = search.group(1)
            return False
        return True

    def update_changelog_version(self):
        with open("CHANGELOG.md", "r") as file:
            today = datetime.now().strftime("%Y-%m-%d")
            new_version = self.new_version
            old_version = self.old_version
            unreleased = r"##\s(|.)Unreleased(|.)"

            changelog = [
                *takewhile(lambda l: not re.search(unreleased, l), file),
                "## [Unreleased]\n",
                "\n",
                f"## [{repr(new_version)}] - {today}\n",
                *takewhile(self.take_until_unreleased, file),
            ]
            changelog += [
                f"[Unreleased]: {self.url}/compare/release/{new_version}..HEAD\n",
                (
                    f"[{new_version}]: "
                    f"{self.url}/compare/release/{old_version}..release/{new_version}\n"
                ),
                *file,
            ]
        with open("CHANGELOG.md", "w") as file:
            file.writelines(changelog)

    def update_open_api_version(self):
        with open(API_SPEC_FILE, "r") as file:
            open_api = [
                *takewhile(lambda l: not l.startswith("  version:"), file),
                f"  version: {self.new_version}\n",
                *file,
            ]
        with open(API_SPEC_FILE, "w") as file:
            file.writelines(open_api)

    def checkout_release(self):
        bash(
            f"git commit -i CHANGELOG.md {API_SPEC_FILE} -m release/{self.new_version}"
        )
        bash(f"git push origin master")
        bash(f"git checkout -b release/{self.new_version}")
        bash(f"git push origin release/{self.new_version}")


if __name__ == "__main__":
    try:
        ReleaseManager().release()
    except ReleaseFailed as exception:
        print("\n".join(exception.args))
