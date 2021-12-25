# -*- mode: python ; coding: utf-8 -*-
#from kivy_deps import sdl2, glew

block_cipher = None


a = Analysis(['main.py'],
             pathex=['/home/ubuntu/Repositories/FM_Plotter_Pro/code/frem'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

a.datas += [('Code/landscape.kv', '/home/ubuntu/Repositories/FM_Plotter_Pro/code/frem/landscape.kv', 'DATA')]

exe = EXE(pyz, Tree('/home/ubuntu/Repositories/FM_Plotter_Pro/code/frem', 'Data'),
          a.scripts, 
          [],
          exclude_binaries=True,
          name='frem',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe, Tree('/home/ubuntu/Repositories/FM_Plotter_Pro/code/frem'),
               a.binaries,
               a.zipfiles,
               a.datas, 
	#	*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
