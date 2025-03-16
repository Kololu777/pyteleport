import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

# テンプレート定義
TEMPLATES = {
    "basic": {
        "directories": ["dir1/subdir1", "dir2", ".hidden_dir"],
        "files": {
            "file1.txt": "test content",
            "file2.py": "print('hello')",
            ".hidden_file.txt": "hidden content",
            "dir1/file3.txt": "nested content",
            "dir1/file5.md": "nested markdown",
            "dir1/subdir1/file4.py": "nested python",
            "dir2/file5.md": "# markdown",
            "dir2/file6.md": "# markdown",
        },
    },
    "python_project": {
        "directories": ["src/mypackage", "tests", "docs", ".github/workflows"],
        "files": {
            "README.md": "# My Python Project\n\nA sample Python project.",
            "pyproject.toml": '[project]\nname = "mypackage"\nversion = "0.1.0"\ndescription = "A sample Python project"\n',
            ".gitignore": "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n.env\n.venv\nvenv/\nENV/\n",
            "src/mypackage/__init__.py": "# Package initialization\n",
            "src/mypackage/main.py": "def main():\n    print('Hello, world!')\n\nif __name__ == '__main__':\n    main()\n",
            "tests/__init__.py": "",
            "tests/test_main.py": "import unittest\nfrom mypackage.main import main\n\nclass TestMain(unittest.TestCase):\n    def test_main(self):\n        # Just a placeholder test\n        self.assertTrue(True)\n",
            ".github/workflows/python-test.yml": "name: Python Tests\non: [push, pull_request]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n    - uses: actions/checkout@v2\n    - name: Set up Python\n      uses: actions/setup-python@v2\n      with:\n        python-version: '3.10'\n    - name: Install dependencies\n      run: |\n        python -m pip install --upgrade pip\n        pip install pytest\n        pip install -e .\n    - name: Test with pytest\n      run: pytest\n",
        },
    },
    "web_project": {
        "directories": ["css", "js", "images", "fonts"],
        "files": {
            "index.html": '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Web Project</title>\n    <link rel="stylesheet" href="css/style.css">\n</head>\n<body>\n    <h1>Hello, World!</h1>\n    <script src="js/main.js"></script>\n</body>\n</html>',
            "css/style.css": "body {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n    background-color: #f5f5f5;\n}\n\nh1 {\n    color: #333;\n}",
            "js/main.js": "document.addEventListener('DOMContentLoaded', function() {\n    console.log('Page loaded');\n});",
        },
    },
    "node_project": {
        "directories": ["src", "test", "dist"],
        "files": {
            "package.json": '{\n  "name": "node-project",\n  "version": "1.0.0",\n  "description": "A sample Node.js project",\n  "main": "src/index.js",\n  "scripts": {\n    "test": "echo \\"Error: no test specified\\" && exit 1",\n    "start": "node src/index.js"\n  },\n  "keywords": [],\n  "author": "",\n  "license": "ISC"\n}',
            ".gitignore": "# Node.js\nnode_modules/\nnpm-debug.log\nyarn-error.log\n.env\ndist/\n",
            "src/index.js": "console.log('Hello, world!');\n",
            "README.md": "# Node.js Project\n\nA sample Node.js project.",
        },
    },
}


def generate_stab_dir(
    target_dir: Union[str, Path],
    template_name: str = "basic",
    custom_structure: Optional[Dict[str, Any]] = None,
    force: bool = False,
) -> bool:
    """
    指定されたテンプレートに基づいてディレクトリ構造を生成します。

    Args:
        target_dir: 生成先のディレクトリパス
        template_name: 使用するテンプレート名
        custom_structure: カスタム構造（指定した場合はテンプレートより優先）
        force: 既存のファイルを上書きするかどうか

    Returns:
        生成が成功したかどうか
    """
    target_dir = Path(target_dir)

    # ディレクトリが存在するか確認
    if not target_dir.exists():
        target_dir.mkdir(parents=True)
    elif not target_dir.is_dir():
        raise ValueError(f"{target_dir} はディレクトリではありません")

    # 空でないディレクトリの場合は確認
    if not force and any(target_dir.iterdir()):
        print(f"警告: ディレクトリ {target_dir} は空ではありません")
        return False

    # 構造の取得
    structure = custom_structure or TEMPLATES.get(template_name)
    if not structure:
        available_templates = ", ".join(TEMPLATES.keys())
        raise ValueError(
            f"テンプレート '{template_name}' は存在しません。利用可能なテンプレート: {available_templates}"
        )

    # ディレクトリの作成
    for dir_path in structure.get("directories", []):
        full_path = target_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"ディレクトリを作成しました: {full_path}")

    # ファイルの作成
    for file_path, content in structure.get("files", {}).items():
        full_path = target_dir / file_path

        # 親ディレクトリが存在しない場合は作成
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # ファイルが存在し、forceがFalseの場合はスキップ
        if not force and full_path.exists():
            print(f"スキップ: ファイル {full_path} は既に存在します")
            continue

        # ファイルの作成
        with open(full_path, "w") as f:
            f.write(content)
        print(f"ファイルを作成しました: {full_path}")

    return True


def list_templates():
    """利用可能なテンプレートの一覧と説明を表示します"""
    print("利用可能なテンプレート:")
    for name in TEMPLATES.keys():
        dirs_count = len(TEMPLATES[name].get("directories", []))
        files_count = len(TEMPLATES[name].get("files", {}))
        print(
            f"  - {name}: {dirs_count}個のディレクトリと{files_count}個のファイルを含むテンプレート"
        )


def load_custom_structure(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    JSONファイルからカスタム構造を読み込みます。

    Args:
        file_path: JSONファイルのパス

    Returns:
        カスタム構造の辞書
    """
    with open(file_path, "r") as f:
        return json.load(f)


def main():
    """コマンドラインインターフェースのエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="テスト用のディレクトリ構造を生成します。"
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="生成先のディレクトリパス（デフォルト: カレントディレクトリ）",
    )
    parser.add_argument(
        "--template",
        "-t",
        choices=list(TEMPLATES.keys()),
        default="basic",
        help="使用するテンプレート（デフォルト: basic）",
    )
    parser.add_argument(
        "--custom", "-c", help="カスタム構造を定義したJSONファイルのパス"
    )
    parser.add_argument(
        "--force", "-f", action="store_true", help="既存のファイルを上書きする"
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="利用可能なテンプレートを一覧表示する"
    )

    args = parser.parse_args()

    # テンプレート一覧の表示
    if args.list:
        list_templates()
        return

    try:
        # カスタム構造の読み込み
        custom_structure = None
        if args.custom:
            custom_structure = load_custom_structure(args.custom)

        # ディレクトリ構造の生成
        success = generate_stab_dir(
            args.target_dir, args.template, custom_structure, args.force
        )

        if success:
            print(f"ディレクトリ構造の生成が完了しました: {args.target_dir}")
        else:
            print(
                "ディレクトリ構造の生成をスキップしました。--force オプションを使用すると強制的に生成できます。"
            )

    except Exception as e:
        print(f"エラー: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
