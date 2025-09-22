import pytest

def test_always_passes():
    """Простой тест который всегда проходит"""
    assert 1 + 1 == 2

def test_environment():
    """Тест окружения"""
    import sys
    assert sys.version_info.major == 3

def test_imports():
    """Тест что основные библиотеки импортируются"""
    try:
        import requests
        import psycopg2
        import pytest
        assert True
    except ImportError:
        assert False, "Не хватает зависимостей"