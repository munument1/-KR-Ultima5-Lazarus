#!/usr/bin/env python3
from pathlib import Path
import zipfile,hashlib,sys
root=Path(sys.argv[1]).resolve(); out=Path(sys.argv[2]).resolve(); base=root.parent
fixed=(2026,8,10,8,7,0)
paths=[root]+sorted(root.rglob('*'),key=lambda p:(str(p.relative_to(base)).replace('\\','/').lower(),0 if p.is_dir() else 1))
with zipfile.ZipFile(out,'w') as z:
  for p in paths:
    rel=str(p.relative_to(base)).replace('\\','/')
    if p.is_dir():
      if not rel.endswith('/'):rel+='/'
      zi=zipfile.ZipInfo(rel,fixed);zi.create_system=3;zi.external_attr=(0o40755<<16)|0x10;zi.compress_type=zipfile.ZIP_STORED;z.writestr(zi,b'')
    else:
      zi=zipfile.ZipInfo(rel,fixed);zi.create_system=3;zi.external_attr=(0o100644<<16);zi.compress_type=zipfile.ZIP_STORED;z.writestr(zi,p.read_bytes())
print(out.stat().st_size);print(hashlib.sha256(out.read_bytes()).hexdigest().upper())
