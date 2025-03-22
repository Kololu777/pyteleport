#!/usr/bin/env bash
set -x

pipx install uv
uv sync
uv pip install -e .