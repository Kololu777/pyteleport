set -x

mypy
ruff check src tests
ruff format src tests --check
echo "✨lint check : success"