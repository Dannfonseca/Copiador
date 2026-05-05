# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['copiador_celular.py'],
    pathex=[],
    binaries=[],
    datas=[('platform-tools/adb.exe', '.'), ('platform-tools/AdbWinApi.dll', '.'), ('platform-tools/AdbWinUsbApi.dll', '.')],
    hiddenimports=[],
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
    name='Copiador da Tammy',
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
    icon='NONE',
)
