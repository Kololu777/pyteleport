#!/usr/bin/env python
"""
ディレクトリ構造生成ツールのコマンドラインインターフェース
"""

import sys

from pyteleport.generator.generate_stab_dir import main

if __name__ == "__main__":
    sys.exit(main())
