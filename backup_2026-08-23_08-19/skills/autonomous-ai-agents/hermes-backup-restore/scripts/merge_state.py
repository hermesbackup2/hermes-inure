#!/usr/bin/env python3
"""Merge session history from a backup state.db into the live state.db.

Usage: merge_state.py <backup_state.db> [live_state.db]
(live defaults to ~/.hermes/state.db)

Why SQL merge instead of file replace:
- the gateway holds the live state.db open (never overwrite it)
- sessions use TEXT ids (no collision -> INSERT OR IGNORE)
- messages use INTEGER ids, both sides start at 1 -> remap by +max(local id)
- FTS triggers on messages fire automatically on insert (verify after)
- column lists are derived via PRAGMA table_info so schema drift is tolerated
"""
import sqlite3
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)

OLD = sys.argv[1]
LOCAL = sys.argv[2] if len(sys.argv) > 2 else str(Path.home() / '.hermes' / 'state.db')

c = sqlite3.connect(LOCAL, timeout=15)
c.execute("PRAGMA busy_timeout=15000")
c.execute("ATTACH DATABASE ? AS olddb", (OLD,))

cols_s = [r[1] for r in c.execute("PRAGMA table_info(sessions)")]
cols_m = [r[1] for r in c.execute("PRAGMA table_info(messages)")]
cols_u = [r[1] for r in c.execute("PRAGMA table_info(session_model_usage)")]

offset = c.execute("SELECT coalesce(max(id),0) FROM messages").fetchone()[0]
n_old_m = c.execute("SELECT count(*) FROM olddb.messages").fetchone()[0]
assert n_old_m > 0, "backup has no messages?"

c.execute("BEGIN")
n_s = c.execute(
    f"INSERT OR IGNORE INTO sessions ({','.join(cols_s)}) "
    f"SELECT {','.join(cols_s)} FROM olddb.sessions"
).rowcount
sel_m = ", ".join(f"id+{offset}" if col == 'id' else col for col in cols_m)
n_m = c.execute(
    f"INSERT OR IGNORE INTO messages ({','.join(cols_m)}) "
    f"SELECT {sel_m} FROM olddb.messages"
).rowcount
n_u = c.execute(
    f"INSERT OR IGNORE INTO session_model_usage ({','.join(cols_u)}) "
    f"SELECT {','.join(cols_u)} FROM olddb.session_model_usage"
).rowcount
c.execute("COMMIT")

print(f"merged: {n_s} sessions, {n_m} messages (offset +{offset}), {n_u} usage rows")
print("now: sessions =", c.execute("SELECT count(*) FROM sessions").fetchone()[0],
      "| messages =", c.execute("SELECT count(*) FROM messages").fetchone()[0])
c.close()
