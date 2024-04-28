# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# Get the path to the directory containing the spec file
spec_file_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

# Get the path to the Python environment
python_env_path = os.path.join(spec_file_dir, '..', 'env', 'Lib', 'site-packages')

block_cipher = None


a = Analysis(
    ['main_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('db/aero.db', 'db'),
    ('guis/AIRCRAFT_PARAMETERS_800_800.png', 'guis'),
    ('guis/FLIGHT_CONDITIONS_800_800.png', 'guis'),
    ('guis/RESULTS_800_800.png', 'guis'),
    ('../env/Lib/site-packages/mpl_toolkits/basemap/*', 'mpl_toolkits/basemap'),
    ('../env/Lib/site-packages/mpl_toolkits/basemap_data/*', 'mpl_toolkits/basemap_data')
    ],
    hiddenimports=["rasterio.sample", "mpl_toolkits.basemap"],
    hookspath=["hooks/mpl_toolkits.py"],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    exclude_binaries=False,
    name='Aircraft_Performance_Parameters',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Aircraft_Performance_Parameters',
)