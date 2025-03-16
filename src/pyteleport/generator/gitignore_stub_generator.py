"""
.gitignoreのスタブファイルを生成するツール

このモジュールは、一般的なプロジェクトタイプに基づいて.gitignoreファイルのスタブを生成します。
"""

import os
from pathlib import Path
from typing import List, Optional, Union

# 一般的なプロジェクトタイプごとの.gitignoreテンプレート
TEMPLATES = {
    "python": [
        "# Byte-compiled / optimized / DLL files",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        "",
        "# C extensions",
        "*.so",
        "",
        "# Distribution / packaging",
        ".Python",
        "build/",
        "develop-eggs/",
        "dist/",
        "downloads/",
        "eggs/",
        ".eggs/",
        "lib/",
        "lib64/",
        "parts/",
        "sdist/",
        "var/",
        "wheels/",
        "*.egg-info/",
        ".installed.cfg",
        "*.egg",
        "",
        "# PyInstaller",
        "#  Usually these files are written by a python script from a template",
        "#  before PyInstaller builds the exe, so as to inject date/other infos into it.",
        "*.manifest",
        "*.spec",
        "",
        "# Installer logs",
        "pip-log.txt",
        "pip-delete-this-directory.txt",
        "",
        "# Unit test / coverage reports",
        "htmlcov/",
        ".tox/",
        ".coverage",
        ".coverage.*",
        ".cache",
        "nosetests.xml",
        "coverage.xml",
        "*.cover",
        ".hypothesis/",
        ".pytest_cache/",
        "",
        "# Environments",
        ".env",
        ".venv",
        "env/",
        "venv/",
        "ENV/",
        "env.bak/",
        "venv.bak/",
        "",
        "# IDE settings",
        ".idea/",
        ".vscode/",
        "*.swp",
        "*.swo",
    ],
    "node": [
        "# Logs",
        "logs",
        "*.log",
        "npm-debug.log*",
        "yarn-debug.log*",
        "yarn-error.log*",
        "",
        "# Runtime data",
        "pids",
        "*.pid",
        "*.seed",
        "*.pid.lock",
        "",
        "# Dependency directories",
        "node_modules/",
        "jspm_packages/",
        "",
        "# Distribution directories",
        "dist/",
        "build/",
        "",
        "# Optional npm cache directory",
        ".npm",
        "",
        "# Optional eslint cache",
        ".eslintcache",
        "",
        "# dotenv environment variables file",
        ".env",
        "",
        "# IDE settings",
        ".idea/",
        ".vscode/",
    ],
    "java": [
        "# Compiled class file",
        "*.class",
        "",
        "# Log file",
        "*.log",
        "",
        "# BlueJ files",
        "*.ctxt",
        "",
        "# Mobile Tools for Java (J2ME)",
        ".mtj.tmp/",
        "",
        "# Package Files #",
        "*.jar",
        "*.war",
        "*.nar",
        "*.ear",
        "*.zip",
        "*.tar.gz",
        "*.rar",
        "",
        "# virtual machine crash logs, see http://www.java.com/en/download/help/error_hotspot.xml",
        "hs_err_pid*",
        "",
        "# Maven",
        "target/",
        "pom.xml.tag",
        "pom.xml.releaseBackup",
        "pom.xml.versionsBackup",
        "pom.xml.next",
        "release.properties",
        "dependency-reduced-pom.xml",
        "",
        "# Gradle",
        ".gradle/",
        "build/",
        "",
        "# IDE settings",
        ".idea/",
        ".vscode/",
        "*.iml",
        "*.iws",
        "*.ipr",
        ".classpath",
        ".project",
        ".settings/",
    ],
    "general": [
        "# OS generated files",
        ".DS_Store",
        ".DS_Store?",
        "._*",
        ".Spotlight-V100",
        ".Trashes",
        "ehthumbs.db",
        "Thumbs.db",
        "",
        "# Editor backup files",
        "*~",
        "*.bak",
        "*.swp",
        "*.swo",
        "",
        "# IDE settings",
        ".idea/",
        ".vscode/",
    ],
}


def detect_project_type(directory: Union[str, Path]) -> str:
    """
    ディレクトリの内容に基づいてプロジェクトタイプを検出します。

    Args:
        directory: 検査するディレクトリのパス

    Returns:
        検出されたプロジェクトタイプ（"python", "node", "java", "general"）
    """
    directory = Path(directory)

    # Pythonプロジェクトの検出
    if (
        (directory / "setup.py").exists()
        or (directory / "pyproject.toml").exists()
        or list(directory.glob("*.py"))
    ):
        return "python"

    # Node.jsプロジェクトの検出
    if (directory / "package.json").exists() or (directory / "node_modules").exists():
        return "node"

    # Javaプロジェクトの検出
    if (
        list(directory.glob("*.java"))
        or (directory / "pom.xml").exists()
        or (directory / "build.gradle").exists()
    ):
        return "java"

    # デフォルトは一般的なテンプレート
    return "general"


def generate_gitignore(
    directory: Union[str, Path],
    project_type: Optional[str] = None,
    custom_rules: Optional[List[str]] = None,
) -> str:
    """
    指定されたプロジェクトタイプに基づいて.gitignoreファイルの内容を生成します。

    Args:
        directory: プロジェクトディレクトリのパス
        project_type: プロジェクトタイプ（指定しない場合は自動検出）
        custom_rules: 追加のカスタムルール

    Returns:
        生成された.gitignoreファイルの内容
    """
    directory = Path(directory)

    # プロジェクトタイプが指定されていない場合は自動検出
    if project_type is None:
        project_type = detect_project_type(directory)

    # 指定されたプロジェクトタイプのテンプレートを取得
    if project_type not in TEMPLATES:
        project_type = "general"

    template = TEMPLATES[project_type].copy()

    # カスタムルールを追加
    if custom_rules:
        template.append("")
        template.append("# Custom rules")
        template.extend(custom_rules)

    # テンプレートを文字列に変換
    return "\n".join(template)


def create_gitignore_file(
    directory: Union[str, Path],
    project_type: Optional[str] = None,
    custom_rules: Optional[List[str]] = None,
    force: bool = False,
) -> bool:
    """
    指定されたディレクトリに.gitignoreファイルを作成します。

    Args:
        directory: .gitignoreファイルを作成するディレクトリのパス
        project_type: プロジェクトタイプ（指定しない場合は自動検出）
        custom_rules: 追加のカスタムルール
        force: Trueの場合、既存の.gitignoreファイルを上書きします

    Returns:
        ファイルが作成されたかどうか
    """
    directory = Path(directory)
    gitignore_path = directory / ".gitignore"

    # 既存の.gitignoreファイルをチェック
    if gitignore_path.exists() and not force:
        return False

    # .gitignoreファイルの内容を生成
    content = generate_gitignore(directory, project_type, custom_rules)

    # ファイルに書き込み
    with open(gitignore_path, "w") as f:
        f.write(content)

    return True


if __name__ == "__main__":
    import argparse

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

    args = parser.parse_args()

    success = create_gitignore_file(args.directory, args.type, args.custom, args.force)

    if success:
        print(
            f".gitignoreファイルが作成されました: {os.path.join(args.directory, '.gitignore')}"
        )
    else:
        print(
            f".gitignoreファイルは既に存在します: {os.path.join(args.directory, '.gitignore')}"
        )
        print("上書きするには --force オプションを使用してください。")
