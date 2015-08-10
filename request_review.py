import argparse
#import fnmatch
import json
import os
import sh

git_diff = sh.git.bake("diff-tree", "--no-commit-id", "--name-only", "-r")


def list_changed_files(start, end=None):
    commit_range = start
    if end:
        commit_range += "..%s" % (end,)
    return git_diff(commit_range).split()


def match_owners(owners_filepath, filename):
    if os.path.exists(owners_filepath):
        with open(owners_filepath, 'r') as f:
            raw_data = json.load(f)
            return {
                "reviewers": set(raw_data["reviewers"]),
                "subscribers": set(raw_data["subscribers"])
            }
    else:
        return None


def merge_owners(owners1, owners2):
    return {
        "reviewers": owners1["reviewers"].union(owners2["reviewers"]),
        "subscribers": owners1["subscribers"].union(owners2["subscribers"])
    }


def get_owners(filename):
    cur_path = filename
    owners = {
        "reviewers": set(),
        "subscribers": set()
    }
    while cur_path:
        cur_dir = os.path.dirname(cur_path)
        owners_filepath = os.path.join(cur_dir, "OWNERS.json")
        cur_owners = match_owners(owners_filepath, filename)
        if cur_owners:
            owners = merge_owners(owners, cur_owners)
            return owners
        else:
            # try one level up
            cur_path = cur_dir


def get_commit_owners(start, end=None):
    owners = {
        "reviewers": set(),
        "subscribers": set()
    }
    for f in list_changed_files(start, end):
        print("file: " + f)
        cur_owners =  get_owners(f)
        if owners:
            owners = merge_owners(owners, cur_owners)
            print("owners found")
    return owners


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--single",
                        help="Single-commit mode. Base now means the only \
                        commit to be reviewed",
                        action="store_true")
    parser.add_argument("base",
                        help="The last commit/branch before the work to be \
                        reviewed")
    parser.add_argument("--to",
                        help="The last commit in the work to be reviewed")
    args = parser.parse_args()
    if args.single:
        last_commit = None
    elif args.to:
        last_commit = args.to
    else:
        last_commit = "HEAD"
    print(get_commit_owners(args.base,
                            last_commit))
