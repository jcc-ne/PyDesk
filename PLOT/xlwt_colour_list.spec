# -*- mode: python -*-
a = Analysis(['xlwt_colour_list.py'],
             pathex=['/Users/janine/Dropbox/Apps/AppCore/PyDesk/PLOT'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build/pyi.darwin/xlwt_colour_list', 'xlwt_colour_list'),
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'xlwt_colour_list'))
