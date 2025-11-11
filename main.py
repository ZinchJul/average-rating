"""
Скрипт для обработки CSV-файлов с данными о товарах и формирования отчёта
о среднем рейтинге брендов.
"""

import argparse
import csv
import sys
from typing import List, Dict, Tuple
from tabulate import tabulate



def read_csv_files(file_paths: List[str]) -> List[Dict[str, str]]:
    """
    Читает CSV-файлы и возвращает объединённый список записей.

    Args:
        file_paths: Список путей к CSV-файлам.

    Returns:
        Список словарей с данными из всех файлов.

    Raises:
        FileNotFoundError: Если файл не найден.
        csv.Error: Если ошибка при чтении CSV.
    """
    all_records = []
    for file_path in file_paths:
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    all_records.append(row)
        except FileNotFoundError:
            print(f"Ошибка: файл не найден — {file_path}", file=sys.stderr)
            sys.exit(1)
        except csv.Error as e:
            print(f"Ошибка при чтении CSV-файла {file_path}: {e}", file=sys.stderr)
            sys.exit(1)
    return all_records


def calculate_average_rating(records: List[Dict[str, str]]) -> List[Tuple[str, float]]:
    """
    Вычисляет средний рейтинг для каждого бренда.
    Args:
        records: Список словарей с данными о товарах.
    Returns:
        Список кортежей (бренд, средний рейтинг), отсортированный по рейтингу (убывание).
    """
    brand_ratings = {}
    brand_counts = {}
    for record in records:
        brand = record['brand']
        try:
            rating = float(record['rating'])
        except ValueError:
            print(
                f"Предупреждение: некорректный рейтинг '{record['rating']}' "
                f"для товара {record['name']}, бренд {brand}. Пропускаем.",
                file=sys.stderr
            )
            continue
        if brand not in brand_ratings:
            brand_ratings[brand] = 0.0
            brand_counts[brand] = 0
        brand_ratings[brand] += rating
        brand_counts[brand] += 1
    # Вычисляем средние рейтинги
    average_ratings = [
        (brand, brand_ratings[brand] / brand_counts[brand])
        for brand in brand_ratings
    ]
    # Сортируем по убыванию рейтинга
    average_ratings.sort(key=lambda x: x[1], reverse=True)
    return average_ratings


def generate_report(report_type: str, data: List[Tuple[str, float]]) -> None:
    """
    Генерирует и выводит отчёт в консоль.

    Args:
        report_type: Тип отчёта (сейчас поддерживается только 'average-rating').
        data: Данные для отчёта.

    Raises:
        ValueError: Если тип отчёта не поддерживается.
    """
    if report_type != 'average-rating':
        raise ValueError(f"Неподдерживаемый тип отчёта: {report_type}")

    table_data = [[brand, f"{avg_rating:.1f}"] for brand, avg_rating in data]
    headers = ["Brand", "Rating"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))



def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description="Обработка CSV-файлов и формирование отчётов.")
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="Пути к CSV-файлам с данными о товарах."
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Тип отчёта (сейчас поддерживается только 'average-rating')."
    )

    args = parser.parse_args()

    # Читаем данные из файлов
    records = read_csv_files(args.files)

    # Вычисляем средний рейтинг по брендам
    average_ratings = calculate_average_rating(records)

    # Генерируем отчёт
    try:
        generate_report(args.report, average_ratings)
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)



if __name__ == "__main__":
    main()
