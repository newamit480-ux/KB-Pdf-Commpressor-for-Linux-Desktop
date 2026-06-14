# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('kb-pdf-compressor.png', '.')]
binaries = []
hiddenimports = ['PIL._tkinter_finder']

# Collect everything for pymupdf, PIL, and tkinterdnd2
for pkg in ['pymupdf', 'PIL', 'tkinterdnd2']:
    tmp_datas, tmp_binaries, tmp_hiddenimports = collect_all(pkg)
    datas += tmp_datas
    binaries += tmp_binaries
    hiddenimports += tmp_hiddenimports

# Also collect fitz just in case, as it is often used as the entry point
tmp_datas, tmp_binaries, tmp_hiddenimports = collect_all('fitz')
datas += tmp_datas
binaries += tmp_binaries
hiddenimports += tmp_hiddenimports

a = Analysis(
    ['pdf_compressor.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='pdf_compressor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
