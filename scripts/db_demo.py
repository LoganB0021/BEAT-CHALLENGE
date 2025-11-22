from datetime import date
from typing import cast
from beat_challenge_generator import config
from beat_challenge_generator.db import init_db, get_session
from beat_challenge_generator.models import Sound, Pack
import os
import json

# Ensure DB/tables exist
init_db()

def resolve_sound_path(relative_path: str) -> str:
    abs_path = os.path.abspath(os.path.join(config.BEAT_DIR, relative_path))
    if os.path.commonpath([os.path.abspath(config.BEAT_DIR), abs_path]) != os.path.abspath(config.BEAT_DIR):
        raise ValueError("Path outside BEAT_DIR")
    return abs_path

with get_session() as session:
    # 1) Insert a sample Sound (idempotent demo)
    s = session.query(Sound).filter_by(relative_path="drum_kits/demo_kick.wav").first()
    if not s:
        s = Sound(name="demo_kick.wav", category="drum_kits", relative_path="drum_kits/demo_kick.wav",
                  is_folder=False, checksum="demo-check", size_bytes=12345)
        session.add(s)
        session.commit()
        print("Inserted Sound:", s.id)

    # 2) Query sounds in a category
    drums = session.query(Sound).filter_by(category="drum_kits").all()
    print("Drum sounds in DB:", [d.relative_path for d in drums])

    # 3) Create a Pack record for today (simulating generator)
    today = date.today().isoformat()
    pack_name = f"beat_{today}.zip"
    p = session.query(Pack).filter_by(date=today).first()
    if not p:
        p = Pack(name=pack_name, date=today, seed=today,
                 zip_path=os.path.join(config.PACKS_DIR, pack_name),
                 items=json.dumps([s.relative_path]), status="ready", size_bytes=0, checksum=None)
        session.add(p)
        session.commit()
        print("Created Pack:", p.name)

    # 4) Resolve and print the absolute path for each item in the pack
    items = json.loads(cast(str, p.items))
    print("Resolved files for pack:")
    for rp in items:
        print(" -", resolve_sound_path(rp))