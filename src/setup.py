from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('calibrate-main.py', base=base)
]

setup(name='PeachyToolChain',
      version = '0.1a',
      description = 'Peachy Printer Untilities',
      options = dict(build_exe = buildOptions),
      executables = executables)
