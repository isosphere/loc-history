import argparse
import os
from datetime import datetime
from typing import Any, Dict, List

from dateutil.parser import parse as dateparse


def get_command_output(cmd: str, redirect_error: bool = False) -> str:
    """Return the command line output of a command."""
    try:
        with os.popen(
            "{}{}".format(cmd, " 2> /dev/null" if redirect_error else "")
        ) as f:
            return f.read()
    except:
        return ""


class Pygount:
    @classmethod
    def get_locs(cls, suffix: str) -> int:
        """Return the number of LOCs from actual project."""
        lines: List[str] = [
            line.strip()
            for line in get_command_output(
                "pygount --suffix={}".format(suffix), redirect_error=True
            )
            .strip()
            .split("\n")
            if line.strip()
        ]
        result = 0
        for line in lines:
            result += int(line.split()[0])
        return result


class Commit:
    """Store the commit info: sha1 and commit date."""

    def __init__(self, commit_sha1: str, date_str: str):
        self.commit_sha1: str = commit_sha1
        self.date: datetime = dateparse(date_str)

    @classmethod
    def sort(cls, commit_list, reverse: bool = False):
        """Return a sorted list of commits."""
        return sorted(
            commit_list, key=lambda commit: commit.date, reverse=reverse
        )

    def __repr__(self) -> str:
        return "{} - {}".format(self.commit_sha1, self.date)

    @classmethod
    def working_directory_clean(cls) -> bool:
        """Return if the current directory is clean or not."""
        message = "nothing to commit, working directory clean"
        return message in get_command_output("git status")

    @classmethod
    def clean_directory(cls):
        """Undo any modification in the current project."""
        get_command_output("git checkout -- .", redirect_error=True)
        get_command_output("git reset .", redirect_error=True)
        get_command_output("git clean -ffd", redirect_error=True)
        get_command_output(
            "git submodule foreach git reset .", redirect_error=True
        )
        get_command_output(
            "git submodule foreach git checkout -- .", redirect_error=True
        )
        get_command_output(
            "git submodule foreach git clean -ffd", redirect_error=True
        )
        get_command_output(
            "git submodule update --checkout", redirect_error=True
        )

    def checkout(self):
        """Change the current git project to this commit.

        This method doesn't check if the current project have untracked/modifed
        files.
        """
        if not Commit.working_directory_clean():
            Commit.clean_directory()
        get_command_output(
            "git checkout {}".format(self.commit_sha1), redirect_error=True
        )
        Commit.clean_directory()

    @classmethod
    def get_commits_list(cls):
        """Return a list of Git Commits."""
        git_command: str = 'git log --format="%H %cI"'
        lines: List[str] = [
            line.strip()
            for line in get_command_output(git_command).strip().split("\n")
            if line.strip()
        ]
        return [Commit(*line.split()) for line in lines]


class BaseOutput:
    def __init__(self, output_file_like: Any, suffix: str):
        self.output_file_like: Any = output_file_like
        self.suffix: str = suffix

    def __enter__(self):
        return self

    def __exit__(self, *args):
        raise NotImplementedError

    def output_commit(self, commit: Commit):
        raise NotImplementedError


class CSVOutput(BaseOutput):
    def __init__(self, *args, csv_separator: str = ";", **kwargs):
        self.csv_separator: str = csv_separator
        super(CSVOutput, self).__init__(*args, **kwargs)

    def __enter__(self):
        headers: List[str] = ["Date", "LOCs"]
        self.output_file_like.write(
            "{}\n".format(self.csv_separator.join(headers))
        )
        return super(CSVOutput, self).__enter__()

    def output_commit(self, commit: Commit):
        values: List[str] = [
            str(commit.date),
            str(Pygount.get_locs(self.suffix)),
        ]
        self.output_file_like.write(
            "{}\n".format(self.csv_separator.join(values))
        )

    def __exit__(self, *args):
        pass


class JSONOutput(BaseOutput):
    def __enter__(self):
        self.output_file_like.write("{\n")
        return super(JSONOutput, self).__enter__()

    def __exit__(self, *args):
        self.output_file_like.write("}\n")

    def output_commit(self, commit: Commit):
        # fixme > the last line ends with a comma, that is invalid in JSON
        self.output_file_like.write(
            '   "{}": {},\n'.format(commit.date, Pygount.get_locs(self.suffix))
        )


def get_output_class(output_name: str):
    """Return the output class from a output name.

    Arguments:
        - output_name: can be: csv or json
    """
    output_class = {
        "csv": CSVOutput,
        "json": JSONOutput,
    }.get(output_name)
    if not output_class:
        raise ValueError("Invalid output name: '{}'".format(output_name))
    return output_class


def print_if_verbose(msg: str, args: argparse.Namespace):
    """Print the message only if the verbose flag is present in args."""
    if not args.verbose:
        return
    print(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Outputs the LOCs of a git project over time. Useful for project "
            "growth analysis."
        )
    )
    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        help="The output format",
        default="csv",
    )
    parser.add_argument(
        "-v",
        help="Output the checkout operations to the terminal (stdout)",
        default=False,
        dest="verbose",
        action="store_true",
    )
    parser.add_argument(
        "--output",
        help=(
            "The output file. If not defined, the output is shown in the "
            "terminal."
        ),
        default="/dev/stdout",
    )
    parser.add_argument(
        "--suffix",
        help=("Indicates which files will be used to count the LOCs."),
        default="py",
    )
    args = parser.parse_args()

    print_if_verbose("Getting commit list...", args)
    commits: List[Commit] = Commit.sort(Commit.get_commits_list())
    with open(args.output, "w") as file_like:
        with get_output_class(args.format)(file_like, args.suffix) as output:
            for commit in commits:
                print_if_verbose("Checking out {}".format(commit), args)
                commit.checkout()
                output.output_commit(commit)
                print_if_verbose("Getting LOCs", args)
                print_if_verbose(
                    "LOCs: {}".format(Pygount.get_locs(args.suffix)), args
                )
