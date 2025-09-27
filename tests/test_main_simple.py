from app.main import get_current_date

def test_get_current_date_returns_string_with_msk():
    result = get_current_date()

    # Должен вернуться текст
    assert isinstance(result, str)

    # Убираем пробелы/переносы, чтобы точно поймать "MSK"
    assert "MSK" in result.strip()

    # Проверим, что строка не пустая и выглядит как дата
    assert len(result) > 10