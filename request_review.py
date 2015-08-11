import argparse
import fnmatch
import json
import os
import sh
import subprocess

arc_diff = sh.Command._create('arc').bake("diff",
                                          allow_untracked=True,
                                          browse=True)
git_diff = sh.Command._create('git').bake("diff-tree",
                                          "--no-commit-id",
                                          "--name-only",
                                          "-r")


def list_changed_files(start, end=None):
    commit_range = start
    if end:
        commit_range += "..%s" % (end,)
    return git_diff(commit_range).split()


def match_owners(owners_filepath, filename):
    if os.path.exists(owners_filepath):
        with open(owners_filepath, 'r') as f:
            raw_data = json.load(f)
            # handle simple file format
            if type(raw_data) == dict:
                return {
                    "reviewers": set(raw_data["reviewers"]),
                    "subscribers": set(raw_data["subscribers"])
                }
            else:
                assert type(raw_data) == list
                owners = {
                    "reviewers": set(),
                    "subscribers": set()
                }
                for data in raw_data:
                    patterns = data["includes"]
                    if any(fnmatch.fnmatch(filename, pat)
                           for pat in patterns):
                        cur_owners = {
                            "reviewers": set(data["reviewers"]),
                            "subscribers": set(data["subscribers"])
                        }
                        owners = merge_owners(owners, cur_owners)
                return owners
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
        # continue one level up
        cur_path = cur_dir
        return owners

def get_commit_owners(start, end=None):
    owners = {
        "reviewers": set(),
        "subscribers": set()
    }
    for f in list_changed_files(start, end):
        print("file: " + f)
        cur_owners = get_owners(f)
        if cur_owners:
            owners = merge_owners(owners, cur_owners)
            print("owners found")
    return owners


def create_review(start, end=None):
    owners = get_commit_owners(start, end)
    _arc_diff = arc_diff
    # take this off once done testing
    # only=True)
    if end != "HEAD":
        _arc_diff = _arc_diff.bake(head=end)
    reviewers = ','.join(owners["reviewers"])
    subs = ','.join(owners["subscribers"])
    if subs:
        _arc_diff = _arc_diff.bake(cc=subs)
    subprocess.call(str(_arc_diff.bake(start, reviewers=reviewers)),
                    shell=True)

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
    create_review(args.base,
                  last_commit)
