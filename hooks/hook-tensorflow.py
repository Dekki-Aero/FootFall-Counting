from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('tensorflow')
hiddenimports += collect_submodules('tensorflow_core')
hiddenimports += collect_submodules('astor')