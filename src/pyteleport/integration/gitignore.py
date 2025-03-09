import os

def read_gitignore(path: str) -> tuple[list[str], list[str]]:
    if os.path.isdir(path):
        path = os.path.join(path, ".gitignore")  # i.e.: ("./", "./src")
    elif not os.path.isfile(path):
        raise FileNotFoundError(
            f"gitignore file not found: {path}"
        )  # i.e.: ("./src/.gitignore", "./gitignore")

    include_set = set()
    exclude_set = set()
    with open(path, "r") as f:
        for line in f:
            # Ignore comment and empty line
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue

            if line.startswith("!"):
                include_set.add(line[1:])
            else:
                exclude_set.add(line)
    include_list = list(include_set)
    exclude_list = list(exclude_set)
    if include_list == []: # [".*"]
        include_list.append(".*")

    return include_list, exclude_list

import os
import re
from pathlib import Path

class GitignorePattern:
    def __init__(self, pattern, is_negated=False):
        self.original_pattern = pattern
        self.is_negated = is_negated
        self.regex = self._convert_to_regex(pattern)
    
    def _convert_to_regex(self, pattern):
        """Gitignoreパターンを正規表現に変換する"""
        # 否定パターンの処理
        if pattern.startswith('!'):
            pattern = pattern[1:]
            self.is_negated = True
        
        # コメントや空行の処理
        if not pattern or pattern.startswith('#'):
            return None
        
        # 末尾のスペースを削除
        pattern = pattern.rstrip()
        
        # パターンの先頭に / がある場合は、ルートディレクトリからの相対パスを意味する
        is_absolute = pattern.startswith('/')
        if is_absolute:
            pattern = pattern[1:]
        
        # パターンの末尾に / がある場合は、ディレクトリのみマッチする
        is_dir_only = pattern.endswith('/')
        if is_dir_only:
            pattern = pattern[:-1]
        
        # 正規表現に変換
        regex_pattern = ''
        
        # 絶対パスの場合は先頭に ^ を追加
        if is_absolute:
            regex_pattern += '^'
        
        # パターンを正規表現に変換
        i = 0
        while i < len(pattern):
            c = pattern[i]
            if c == '*':
                if i + 1 < len(pattern) and pattern[i + 1] == '*':
                    # ** は任意のディレクトリを意味する
                    if i + 2 < len(pattern) and pattern[i + 2] == '/':
                        # /**/
                        regex_pattern += '(?:.*?/)?'
                        i += 3
                    else:
                        # **
                        regex_pattern += '.*'
                        i += 2
                else:
                    # * は / 以外の任意の文字列を意味する
                    regex_pattern += '[^/]*'
                    i += 1
            elif c == '?':
                # ? は / 以外の任意の1文字を意味する
                regex_pattern += '[^/]'
                i += 1
            elif c == '[':
                # 文字クラス
                end = pattern.find(']', i)
                if end != -1:
                    regex_pattern += pattern[i:end+1]
                    i = end + 1
                else:
                    regex_pattern += '\\['
                    i += 1
            elif c in '.+(){}^$\\':
                # 特殊文字はエスケープ
                regex_pattern += '\\' + c
                i += 1
            else:
                regex_pattern += c
                i += 1
        
        # ディレクトリのみの場合は末尾に / を追加
        if is_dir_only:
            regex_pattern += '/$'
        
        return re.compile(regex_pattern)
    
    def matches(self, path):
        """パスがパターンにマッチするかどうかを判定する"""
        if self.regex is None:
            return False
        
        return bool(self.regex.search(path))

class GitignoreMatcher:
    def __init__(self, gitignore_path='.gitignore'):
        self.patterns = []
        self.load_gitignore(gitignore_path)
    
    def load_gitignore(self, gitignore_path):
        """gitignoreファイルを読み込む"""
        try:
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.patterns.append(GitignorePattern(line))
        except FileNotFoundError:
            print(f"Warning: {gitignore_path} not found")
    
    def is_ignored(self, path):
        """パスが無視されるべきかどうかを判定する"""
        # 相対パスに変換
        path = str(Path(path))
        if path.startswith('./'):
            path = path[2:]
        
        # ディレクトリの場合は末尾に / を追加
        if os.path.isdir(path) and not path.endswith('/'):
            path += '/'
        
        # パターンを順番に適用
        ignored = False
        for pattern in self.patterns:
            if pattern.matches(path):
                ignored = not pattern.is_negated
        
        return ignored
    
    def find_ignored_files(self, directory='.'):
        """指定されたディレクトリ内の無視されるファイルを見つける"""
        ignored_files = []
        
        for root, dirs, files in os.walk(directory):
            # ディレクトリの相対パスを取得
            rel_root = os.path.relpath(root, directory)
            if rel_root == '.':
                rel_root = ''
            
            # ディレクトリが無視される場合はスキップ
            if rel_root and self.is_ignored(rel_root):
                dirs[:] = []  # サブディレクトリの走査をスキップ
                continue
            
            # ファイルをチェック
            for file in files:
                rel_path = os.path.join(rel_root, file)
                if self.is_ignored(rel_path):
                    ignored_files.append(rel_path)
            
            # ディレクトリをチェック（次の走査のため）
            dirs_to_remove = []
            for i, dir_name in enumerate(dirs):
                rel_path = os.path.join(rel_root, dir_name)
                if self.is_ignored(rel_path):
                    dirs_to_remove.append(i)
            
            # 無視されるディレクトリを削除（逆順で削除）
            for i in reversed(dirs_to_remove):
                del dirs[i]
        
        return ignored_files


# 使用例
if __name__ == "__main__":
    matcher = GitignoreMatcher(gitignore_path="./.gitignore")
    
    # 特定のファイルが無視されるかチェック
    print(f"node_modules/package.json is ignored: {matcher.is_ignored('node_modules/package.json')}")
    print(f"src/main.py is ignored: {matcher.is_ignored('src/main.py')}")
    
    # 無視されるファイルを一覧表示
    ignored_files = matcher.find_ignored_files()
    print("\nIgnored files:")
    for file in ignored_files:
        print(f"- {file}")

    include_list, exclude_list = read_gitignore("./")
    print(include_list)
    print(exclude_list)
