import json
import tempfile
from pathlib import Path

import pytest

from pyteleport.generator.generate_stab_dir import (
    TEMPLATES,
    generate_stab_dir,
    load_custom_structure,
)


class TestGenerateStabDir:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_generate_basic_template(self, temp_dir):
        # 基本テンプレートのテスト
        assert generate_stab_dir(temp_dir, "basic")

        # ディレクトリの確認
        assert (temp_dir / "dir1" / "subdir1").is_dir()
        assert (temp_dir / "dir2").is_dir()
        assert (temp_dir / ".hidden_dir").is_dir()

        # ファイルの確認
        assert (temp_dir / "file1.txt").is_file()
        assert (temp_dir / "file2.py").is_file()
        assert (temp_dir / ".hidden_file.txt").is_file()
        assert (temp_dir / "dir1" / "file3.txt").is_file()
        assert (temp_dir / "dir1" / "file5.md").is_file()
        assert (temp_dir / "dir1" / "subdir1" / "file4.py").is_file()
        assert (temp_dir / "dir2" / "file5.md").is_file()
        assert (temp_dir / "dir2" / "file6.md").is_file()

        # ファイルの内容確認
        with open(temp_dir / "file1.txt") as f:
            assert f.read() == "test content"
        with open(temp_dir / "file2.py") as f:
            assert f.read() == "print('hello')"

    def test_generate_python_project_template(self, temp_dir):
        # Pythonプロジェクトテンプレートのテスト
        assert generate_stab_dir(temp_dir, "python_project")

        # 主要なファイルとディレクトリの確認
        assert (temp_dir / "src" / "mypackage").is_dir()
        assert (temp_dir / "tests").is_dir()
        assert (temp_dir / "src" / "mypackage" / "__init__.py").is_file()
        assert (temp_dir / "src" / "mypackage" / "main.py").is_file()
        assert (temp_dir / "tests" / "test_main.py").is_file()
        assert (temp_dir / "pyproject.toml").is_file()
        assert (temp_dir / ".gitignore").is_file()

    def test_generate_with_custom_structure(self, temp_dir):
        # カスタム構造のテスト
        custom_structure = {
            "directories": ["custom_dir", "another_dir"],
            "files": {
                "custom_file.txt": "custom content",
                "custom_dir/nested.txt": "nested content",
            },
        }

        # カスタム構造のJSONファイルを作成
        json_path = temp_dir / "custom.json"
        with open(json_path, "w") as f:
            json.dump(custom_structure, f)

        # JSONファイルからカスタム構造を読み込み
        loaded_structure = load_custom_structure(json_path)
        assert loaded_structure == custom_structure

        # 別のディレクトリを作成してそこにカスタム構造を適用
        target_dir = temp_dir / "target"
        assert generate_stab_dir(target_dir, custom_structure=loaded_structure)

        # ディレクトリとファイルの確認
        assert (target_dir / "custom_dir").is_dir()
        assert (target_dir / "another_dir").is_dir()
        assert (target_dir / "custom_file.txt").is_file()
        assert (target_dir / "custom_dir" / "nested.txt").is_file()

        # ファイルの内容確認
        with open(target_dir / "custom_file.txt") as f:
            assert f.read() == "custom content"

    def test_force_option(self, temp_dir):
        # 既存のファイルを作成
        (temp_dir / "file1.txt").write_text("existing content")

        # forceなしの場合は上書きされない
        assert not generate_stab_dir(temp_dir, "basic", force=False)
        with open(temp_dir / "file1.txt") as f:
            assert f.read() == "existing content"

        # forceありの場合は上書きされる
        assert generate_stab_dir(temp_dir, "basic", force=True)
        with open(temp_dir / "file1.txt") as f:
            assert f.read() == "test content"

    def test_invalid_template(self, temp_dir):
        # 存在しないテンプレート名
        with pytest.raises(ValueError) as excinfo:
            generate_stab_dir(temp_dir, "nonexistent_template")
        assert "テンプレート 'nonexistent_template' は存在しません" in str(
            excinfo.value
        )

    def test_templates_structure(self):
        # テンプレート構造の検証
        for template_name, structure in TEMPLATES.items():
            assert "directories" in structure
            assert "files" in structure
            assert isinstance(structure["directories"], list)
            assert isinstance(structure["files"], dict)
