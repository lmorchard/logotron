#!/bin/sh
cd "$(dirname "$0")"
poetry install
$HOME/.local/bin/poetry run python3 bot.py
