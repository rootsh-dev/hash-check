# Hash Check

A small interactive Python tool to verify large file transfers (PC → phone,
external drive, cloud upload, etc.) using SHA-256 hashes — so when a
transfer stops halfway, you only need to resend the files that are
actually missing or corrupted, not everything.

## Why

Copying a folder of heavy files (videos, backups, datasets) sometimes gets
interrupted, and it's not always obvious which files actually made it
across intact. Comparing hashes on both sides tells you exactly what's
fine and what needs to go again.

## Requirements

- Python 3.7+
- No external dependencies (standard library only)

## Usage

```bash
python hash_check.py
```

You'll get a menu:

```
1. Generate hash file for a folder
2. Compare two hash files
3. Exit
```

### 1. Generate a hash file

Point it at a folder; it walks every file recursively and writes a hash
list (`hash<TAB>size<TAB>relative_path` per line).

Run this once on the **source** (e.g. your PC) and once on the
**destination** (e.g. your phone, after copying whatever made it across).

### 2. Compare two hash files

Give it the source hash file and the destination hash file. It reports:

- **MATCHED** — transferred correctly, nothing to do
- **MISMATCH** — present on both sides but the hash differs (incomplete /
  corrupted copy) → needs to be resent
- **MISSING** — on the source but never arrived on the destination →
  needs to be sent
- **EXTRA** — on the destination but not in the source list (safe to
  ignore, or leftover from an old batch)

It also writes a resend list (`resend_list.txt` by default) containing
just the files that need to go again, so your next transfer can be
filtered to only those. If everything matched, the file still gets
created — it just contains a note saying there's nothing to resend,
and the terminal prints a clear `✅ Nothing to resend` message so an
empty result is never ambiguous with a failed run.

## Behavior notes

- **Filenames** — you don't need to type `.txt` when prompted for a
  filename; it's added automatically if missing (`myfile` →
  `myfile.txt`). If you do include it, it's left as-is (no
  `file.txt.txt` doubling).
- **Output location** — files are written relative to wherever you run
  the script from (your current working directory), not the script's
  own folder. Type a full path (e.g. `D:\Transfers\resend.txt`) if you
  want it saved somewhere specific.
- **Missing folders** — if the folder for an output path doesn't exist
  yet, it's created automatically instead of crashing.
- **Same file twice** — if you accidentally give the same hash file for
  both source and destination in step 2, it warns you before
  proceeding (everything would otherwise show as MATCHED, which is
  usually a mistake).
- **Large files** — hashing is streamed in 1 MB chunks, so memory use
  stays flat regardless of file size.
- **Write errors** — permission issues or a full disk are caught and
  reported cleanly instead of crashing with a raw traceback.

## License

MIT — see [LICENSE](LICENSE).
