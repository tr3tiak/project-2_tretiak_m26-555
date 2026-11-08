#!/usr/bin/env python3
"""Точка входа: консольная команда database."""

from . import engine


def main():
    """Запускает интерактивную базу данных."""
    engine.run()
