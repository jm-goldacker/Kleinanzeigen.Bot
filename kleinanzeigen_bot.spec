# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Kleinanzeigen-Bot."""

import os
from pathlib import Path

src_dir = Path("src") / "kleinanzeigen_bot"

a = Analysis(
    [str(src_dir / "__main__.py")],
    pathex=["src"],
    datas=[
        (str(src_dir / "static"), "kleinanzeigen_bot/static"),
        (str(src_dir / "categories" / "tree.json"), "kleinanzeigen_bot/categories"),
    ],
    hiddenimports=[
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "multipart",
        "multipart.multipart",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="kleinanzeigen-bot",
    debug=False,
    strip=False,
    upx=True,
    console=True,
)
