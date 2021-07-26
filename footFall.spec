# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['footFall.py'],
             pathex=['/home/dev-24/Downloads/FootFall-20210718T063506Z-001/FootFall/Deploy'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['/home/dev-24/Downloads/FootFall-20210718T063506Z-001/FootFall/Deploy/hooks'],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='footFall',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='footFall')
