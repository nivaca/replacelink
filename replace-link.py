#!/usr/bin/env python3
import shutil
import sys
import os.path


def check_path(path):
    if not os.path.exists(path):
        return "non_existent"
    elif os.path.isdir(path):
        if os.path.islink(path):
            return "directory_link"
        else:
            return "directory"
    elif os.path.islink(path):
        return "file_link"
    else:
        return "file"


def remove_item(path):
    status = check_path(path)
    if (status == "file") or (status == "file_link") or (status == "directory_link"):
        try:
            os.remove(path)
            return True
        except OSError():
            return False
    elif status == "directory":
        try:
            shutil.rmtree(path)
            return True
        except OSError():
            return False


def process_file(f):
    destination = os.path.realpath(f)
    destination = os.readlink(f)
    symlink = os.path.abspath(f)
    backup = symlink + ".bak"

    try:
        os.rename(symlink, backup)
    except OSError():
        print(f"***Error making backup of symlink {f}.")
        print(f"Do you wish to continue?", end=" ")
        if input("(y/n) ").lower() == "n":
            print("Aborting...")
            sys.exit(1)

    # Make a copy of the destination f
    try:
        shutil.copy2(destination, symlink)
    except OSError():
        print(f"***Error creating copy of destination file {f}.")
        try:
            os.rename(backup, symlink)
        except OSError():
            print(f"***Error restoring symlink {f}.")
        sys.exit(1)

    # remove backup
    if not remove_item(backup):
        print(f"***Error removing backup file {backup}.")

    print(f"Replaced symlink {f} with file {f}.")
    print(f"Remove original destination file {destination}?", end=" ")
    if input("(y/n) ").lower() == "y":
        if not remove_item(destination):
            print(f"***Error removing backup file {destination}.")


def process_directory(f):
    destination = os.path.realpath(f)
    symlink = os.path.abspath(f)
    backup = symlink + ".bak"

    try:
        os.rename(symlink, backup)
    except OSError():
        print(f"***Error making backup of symlink {f}.")
        print(f"Do you wish to continue?", end=" ")
        if input("(y/n) ").lower() == "n":
            print("Aborting...")
            sys.exit(1)

    # Copy the directory
    try:
        shutil.copytree(destination, symlink)
    except OSError():
        print(f"***Error creating copy of destination directory {f}.")
        try:
            os.rename(backup, symlink)
        except OSError():
            print(f"***Error restoring {f}.")
        sys.exit(1)

    # remove backup
    if not remove_item(backup):
        print(f"***Error removing backup file {backup}.")

    print(f"Replaced symlink {f} with directory {f}.")
    print(f"Remove destination directory {destination}?", end=" ")
    if input("(y/n) ").lower() == "y":
        if not remove_item(destination):
            print(f"***Error: could not remove destination directory {destination}.")
            sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(f"Usage: python {sys.argv[0]} symlink")
        print("Replaces symlink with destination and optionally deletes it.")
        sys.exit(1)
    paths = sys.argv[1:]
    for path in paths:
        status = check_path(path)
        if status == "non_existent":
            print(f"***Error: {path} doesn't exist. Aborting...")
            sys.exit(1)
        elif status == "file":
            print(f"***Error: {path} is not a symlink but a file. Aborting...")
            sys.exit(1)
        elif status == "directory":
            print(f"***Error: {path} is not a symlink but a directory. Aborting...")
            sys.exit(1)
        elif status == "file_link":
            print(f"Processing file symlink {path}...")
            process_file(path)
        elif status == "directory_link":
            print(f"Processing directory symlink {path}...")
            process_directory(path)
