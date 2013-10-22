# -*- mode: python -*-
a = Analysis(['makePPT.py'],
             pathex=['C:\\Users\\ChengJC\\home\\PyDesk\\PPTX\\ProjectFolder\\Common\\Post'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='makePPT.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
