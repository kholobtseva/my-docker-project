from app.main import get_current_date

def test_get_current_date_contains_msk():
    result = get_current_date()
    assert isinstance(result, str)        # возвращает строку
    assert "MSK" in result                 # внутри есть "MSK"
    assert len(result) > 10                # строка не пустая