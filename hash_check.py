#!/usr/bin/env python3
r"""
hash_check.py — Interactive menu version of the transfer-verification tool.

Just run it, no command-line arguments needed:
    python hash_check.py

You'll get a menu:
    1. Generate hash file (point it at a folder)
    2. Compare two hash files (find missing/corrupted transfers)
    3. Exit
"""

import hashlib
import os

CHUNK_SIZE = 1024 * 1024  # 1 MB


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def ask_path(prompt):
    while True:
        path = input(prompt).strip().strip('"')
        if path:
            return path
        print("  Please enter a value.\n")


def generate_hashes():
    print("\n--- Generate Hash File ---")
    folder = ask_path("Enter folder path to scan: ")
    folder = os.path.abspath(folder)
    if not os.path.isdir(folder):
        print(f"  Error: '{folder}' is not a valid directory.\n")
        return

    output = ask_path("Enter output file name (e.g. hashes.txt): ")
    if not output.lower().endswith(".txt"):
        output += ".txt"

    out_dir = os.path.dirname(os.path.abspath(output))
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as e:
        print(f"  Error: couldn't create folder for output file '{out_dir}': {e}\n")
        return

    entries = []
    for dirpath, _dirnames, filenames in os.walk(folder):
        for name in filenames:
            full_path = os.path.join(dirpath, name)
            rel_path = os.path.relpath(full_path, folder).replace(os.sep, "/")
            entries.append((full_path, rel_path))

    entries.sort(key=lambda x: x[1])
    total = len(entries)

    if total == 0:
        print("  No files found in that folder.\n")
        return

    try:
        with open(output, "w", encoding="utf-8") as out:
            for i, (full_path, rel_path) in enumerate(entries, 1):
                try:
                    size = os.path.getsize(full_path)
                    print(f"  [{i}/{total}] Hashing ({size/1e6:.1f} MB): {rel_path}")
                    digest = sha256_of_file(full_path)
                    out.write(f"{digest}\t{size}\t{rel_path}\n")
                    out.flush()
                except (OSError, PermissionError) as e:
                    print(f"    !! Skipped (couldn't read): {rel_path} -> {e}")
    except (OSError, PermissionError) as e:
        print(f"\n  Error: couldn't write to '{output}': {e}\n")
        return

    print(f"\n  Done. Wrote {total} entries to: {os.path.abspath(output)}\n")


def load_hash_file(path):
    data = {}
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) == 3:
                digest, size, rel_path = parts
                data[rel_path] = (digest, size)
            else:
                # tolerate "hash  filename" two-column format
                parts2 = line.split(None, 1)
                if len(parts2) == 2:
                    data[parts2[1].strip()] = (parts2[0].strip(), None)
    return data


def compare_hashes():
    print("\n--- Compare Two Hash Files ---")
    file1 = ask_path("Enter path to FIRST hash file (source, e.g. PC): ")
    if not os.path.isfile(file1):
        print(f"  Error: '{file1}' not found.\n")
        return

    file2 = ask_path("Enter path to SECOND hash file (destination, e.g. mobile): ")
    if not os.path.isfile(file2):
        print(f"  Error: '{file2}' not found.\n")
        return

    if os.path.abspath(file1) == os.path.abspath(file2):
        print("  Warning: both paths point to the SAME file. Every entry will")
        print("  show as MATCHED, which is probably not what you meant.")
        confirm = input("  Continue anyway? (y/N): ").strip().lower()
        if confirm != "y":
            print("  Cancelled.\n")
            return

    resend_out = input("Output file for resend list [default: resend_list.txt]: ").strip()
    if not resend_out:
        resend_out = "resend_list.txt"
    elif not resend_out.lower().endswith(".txt"):
        resend_out += ".txt"

    source = load_hash_file(file1)
    dest = load_hash_file(file2)

    all_paths = sorted(set(source) | set(dest))

    matched, mismatched, missing, extra = [], [], [], []

    for path in all_paths:
        in_src = path in source
        in_dst = path in dest
        if in_src and in_dst:
            src_hash, _ = source[path]
            dst_hash, _ = dest[path]
            if src_hash == dst_hash:
                matched.append(path)
            else:
                mismatched.append(path)
        elif in_src and not in_dst:
            missing.append(path)
        else:
            extra.append(path)

    def section(title, items):
        print(f"\n  === {title} ({len(items)}) ===")
        for p in items:
            print(f"    {p}")

    section("MATCHED (fully transferred, skip)", matched)
    section("MISMATCH (corrupted/incomplete - RESEND)", mismatched)
    section("MISSING (never arrived - RESEND)", missing)
    section("EXTRA on destination (not in source)", extra)

    resend = mismatched + missing

    out_dir = os.path.dirname(os.path.abspath(resend_out))
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(resend_out, "w", encoding="utf-8") as f:
            if resend:
                for p in resend:
                    f.write(p + "\n")
            else:
                f.write("# Nothing to resend - all files matched.\n")
    except (OSError, PermissionError) as e:
        print(f"\n  Error: couldn't write resend list to '{resend_out}': {e}\n")
        return

    print()
    if resend:
        print(f"  {len(resend)} file(s) need to be (re)sent.")
    else:
        print("  ✅ Nothing to resend — every file matched perfectly!")
    print(f"  List written to: {os.path.abspath(resend_out)}\n")


def main():
    while True:
        print("=" * 50)
        print("  FILE TRANSFER HASH CHECKER")
        print("=" * 50)
        print("  1. Generate hash file for a folder")
        print("  2. Compare two hash files")
        print("  3. Exit")
        choice = input("\nChoose an option (1/2/3): ").strip()

        if choice == "1":
            generate_hashes()
        elif choice == "2":
            compare_hashes()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("  Invalid choice, try again.\n")


if __name__ == "__main__":
    main()
