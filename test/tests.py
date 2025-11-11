"""Тесты для скрипта обработки CSV-файлов и формирования отчётов."""

import pytest
import csv
from io import StringIO
from unittest.mock import patch, mock_open
from main import (
    read_csv_files,
    calculate_average_rating,
    generate_report
)


# --- Тесты для read_csv_files ---

def test_read_csv_files_single_file():
    """Тест чтения одного корректного CSV-файла."""
    mock_csv = StringIO("name,brand,price,rating\nphone,apple,1000,4.5")

    with patch("builtins.open", mock_open(read_data=mock_csv.getvalue())):
        result = read_csv_files(["file1.csv"])

    assert len(result) == 1
    assert result[0]["name"] == "phone"
    assert result[0]["brand"] == "apple"
    assert result[0]["price"] == "1000"
    assert result[0]["rating"] == "4.5"


def test_read_csv_files_multiple_files():
    """Тест чтения нескольких CSV-файлов."""
    mock_csv1 = StringIO("name,brand,price,rating\nphone1,apple,1000,4.5")
    mock_csv2 = StringIO("name,brand,price,rating\nphone2,samsung,900,4.7")

    with patch("builtins.open", side_effect=[
        mock_open(read_data=mock_csv1.getvalue()).return_value,
        mock_open(read_data=mock_csv2.getvalue()).return_value
    ]):
        result = read_csv_files(["file1.csv", "file2.csv"])

    assert len(result) == 2
    assert result[0]["brand"] == "apple"
    assert result[1]["brand"] == "samsung"


def test_read_csv_files_file_not_found():
    """Тест обработки ошибки отсутствия файла."""
    with patch("builtins.open", side_effect=FileNotFoundError()):
        with pytest.raises(SystemExit):
            read_csv_files(["nonexistent.csv"])


def test_read_csv_files_csv_error():
    """Тест обработки ошибки чтения CSV."""
    with patch("builtins.open", mock_open(read_data="invalid,csv,data")):
        with patch("csv.DictReader", side_effect=csv.Error("CSV error")):
            with pytest.raises(SystemExit):
                read_csv_files(["bad.csv"])


# --- Тесты для calculate_average_rating ---

def test_calculate_average_rating_normal():
    """Тест расчёта среднего рейтинга для нескольких брендов."""
    records = [
        {"name": "p1", "brand": "apple", "price": "1000", "rating": "4.5"},
        {"name": "p2", "brand": "samsung", "price": "900", "rating": "4.7"},
        {"name": "p3", "brand": "apple", "price": "1100", "rating": "4.9"},
    ]

    result = calculate_average_rating(records)

    assert len(result) == 2
    assert result[0][0] == "apple"  # apple: (4.5 + 4.9) / 2 = 4.7
    assert pytest.approx(result[0][1]) == 4.7
    assert result[1][0] == "samsung"  # samsung: 4.7
    assert pytest.approx(result[1][1]) == 4.7


def test_calculate_average_rating_single_brand():
    """Тест для одного бренда."""
    records = [
        {"name": "p1", "brand": "xiaomi", "price": "500", "rating": "4.2"},
        {"name": "p2", "brand": "xiaomi", "price": "600", "rating": "4.8"},
    ]

    result = calculate_average_rating(records)

    assert len(result) == 1
    assert result[0][0] == "xiaomi"
    assert pytest.approx(result[0][1]) == 4.5  # (4.2 + 4.8) / 2


def test_calculate_average_rating_invalid_rating():
    """Тест пропуска записей с некорректным рейтингом."""
    records = [
        {"name": "p1", "brand": "apple", "price": "1000", "rating": "invalid"},
        {"name": "p2", "brand": "apple", "price": "1100", "rating": "4.9"},
    ]

    with patch("sys.stderr"):
        result = calculate_average_rating(records)

    assert len(result) == 1
    assert result[0][0] == "apple"
    assert pytest.approx(result[0][1]) == 4.9


def test_calculate_average_rating_empty_list():
    """Тест для пустого списка записей."""
    result = calculate_average_rating([])
    assert result == []


def test_calculate_average_rating_sorting():
    """Тест сортировки по убыванию рейтинга."""
    records = [
        {"name": "p1", "brand": "a", "price": "1", "rating": "3.0"},
        {"name": "p2", "brand": "b", "price": "2", "rating": "5.0"},
        {"name": "p3", "brand": "c", "price": "3", "rating": "4.0"},
    ]

    result = calculate_average_rating(records)

    assert [brand for brand, _ in result] == ["b", "c", "a"]  # 5.0 > 4.0 > 3.0


# --- Тесты для generate_report ---

def test_generate_report_average_rating():
    """Тест генерации отчёта average-rating."""
    data = [("apple", 4.7), ("samsung", 4.6)]

    with patch("builtins.print") as mock_print:
        generate_report("average-rating", data)

    output = mock_print.call_args[0][0]
    assert "Brand | Average Rating! in output"
    assert "apple | 4.7! in output"
    assert "samsung | 4.6! in output"


def test_generate_report_unsupported_type():
    """Тест ошибки для неподдерживаемого типа отчёта."""
    with pytest.raises(ValueError, match="Неподдерживаемый тип отчёта: invalid"):
        generate_report("invalid", [])


def test_generate_report_empty_data():
    """Тест отчёта с пустыми данными."""
    with patch("builtins.print") as mock_print:
        generate_report("average-rating", [])

    output = mock_print.call_args[0][0]
    assert "Brand | Average Rating! in output"
    # Таблица будет без строк данных


# --- Вспомогательные тесты ---

def test_calculate_average_rating_case_sensitive_brands():
    """Тест учёта регистра в названиях брендов."""
    records = [
        {"name": "p1", "brand": "Apple", "price": "1000", "rating": "4.5"},
        {"name": "p2", "brand": "apple", "price": "1100", "rating": "4.9"},
    ]

    result = calculate_average_rating(records)

    # Бренды с разным регистром считаются разными
    assert len(result) == 2
    assert ("Apple", 4.5) in result
    assert ("apple", 4.9) in result


def test_calculate_average_rating_zero_ratings():
    """Тест для бренда с нулевым рейтингом."""
    records = [
        {"name": "p1", "brand": "zero", "price": "100", "rating": "0.0"},
    ]

    result = calculate_average_rating(records)

    assert len(result) == 1
    assert result[0][0] == "zero"
