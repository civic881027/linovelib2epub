# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec. Build a single-file executable with:
#   uv run --with pyinstaller pyinstaller linovelib2epub.spec
# The result lands in dist/linovelib2epub (dist/linovelib2epub.exe on Windows).
# A Chromium-based browser (and tesseract, for the PC sites) must still be
# installed on the machine that runs the executable.
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

datas = [('src/linovelib2epub/styles', 'linovelib2epub/styles')]
datas += collect_data_files('fake_useragent')
datas += collect_data_files('DrissionPage')
# readchar reads its own version via importlib.metadata at import time.
datas += copy_metadata('readchar')

a = Analysis(
    ['src/linovelib2epub/cli.py'],
    pathex=['src'],
    datas=datas,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='linovelib2epub',
    console=True,
    upx=False,
)
