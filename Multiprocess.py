#!/usr/bin/env python3

import subprocess
import os
from multiprocessing import Pool


def sync_directory(sync_pair):
    """Sync a single directory pair using rsync"""
    src, dest = sync_pair
    try:
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        result = subprocess.run(["rsync", "-arq", src + "/", dest + "/"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            return f"Success: {src} -> {dest}"
        else:
            return f"Error syncing {src} -> {dest}: {result.stderr}"
    except Exception as e:
        return f"Exception syncing {src} -> {dest}: {str(e)}"


def discover_sync_pairs(base_src, base_dest, max_depth=4):
    """Use os.walk to discover all subdirectories to sync"""
    sync_pairs = []

    for root, dirs, files in os.walk(base_src):
        # Calculate relative path from base source
        rel_path = os.path.relpath(root, base_src)

        # Skip the root directory itself
        if rel_path == ".":
            continue

        # Limit depth if specified
        depth = rel_path.count(os.sep) + 1
        if max_depth and depth > max_depth:
            dirs[:] = []  # Don't descend further
            continue

        # Create corresponding destination path
        dest_path = os.path.join(base_dest, rel_path)
        sync_pairs.append((root, dest_path))

    return sync_pairs


if __name__ == "__main__":
    base_src = "/home/student/data/prod"
    base_dest = "/home/student/data/prod_backup"

    # Discover all subdirectories to sync
    sync_pairs = discover_sync_pairs(base_src, base_dest, max_depth=2)

    print(f"Found {len(sync_pairs)} directories to sync")

    # Use Pool to sync directories concurrently
    with Pool(processes=4) as pool:
        results = pool.map(sync_directory, sync_pairs)

    # Print results
    for result in results:
        print(result)