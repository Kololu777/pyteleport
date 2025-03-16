#!/usr/bin/env python
"""
.gitignoreスタブジェネレーターのコマンドラインインターフェース
"""

import argparse
import os
import sys
from pathlib import Path

from pyteleport.generator.gitignore_stub_generator import (
    create_gitignore_file,
    detect_project_type,
)


def main():
    """
    コマンドラインから.gitignoreスタブジェネレーターを実行するためのエントリーポイント
    """
    parser = argparse.ArgumentParser(
        description=".gitignoreファイルのスタブを生成します。"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="プロジェクトディレクトリのパス（デフォルト: カレントディレクトリ）",
    )
    parser.add_argument(
        "--type",
        "-t",
        choices=["python", "node", "java", "general"],
        help="プロジェクトタイプ（指定しない場合は自動検出）",
    )
    parser.add_argument(
        "--custom", "-c", action="append", help="追加のカスタムルール（複数指定可）"
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="既存の.gitignoreファイルを上書きする",
    )
    parser.add_argument(
        "--detect-only",
        "-d",
        action="store_true",
        help="プロジェクトタイプを検出するだけで、ファイルは作成しない",
    )

    args = parser.parse_args()
    directory = Path(args.directory)

    # ディレクトリが存在するか確認
    if not directory.exists():
        print(f"エラー: ディレクトリが存在しません: {directory}")
        sys.exit(1)
    if not directory.is_dir():
        print(f"エラー: 指定されたパスはディレクトリではありません: {directory}")
        sys.exit(1)

    # プロジェクトタイプの検出のみ
    if args.detect_only:
        project_type = detect_project_type(directory)
        print(f"検出されたプロジェクトタイプ: {project_type}")
        sys.exit(0)

    # .gitignoreファイルの作成
    success = create_gitignore_file(directory, args.type, args.custom, args.force)

    if success:
        print(
            f".gitignoreファイルが作成されました: {os.path.join(args.directory, '.gitignore')}"
        )
    else:
        print(
            f".gitignoreファイルは既に存在します: {os.path.join(args.directory, '.gitignore')}"
        )
        print("上書きするには --force オプションを使用してください。")


if __name__ == "__main__":
    main()
