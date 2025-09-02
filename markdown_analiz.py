import sys
import re
from pathlib import Path

def analyze_markdown(file_path: str):
    """
    Анализирует Markdown-файл, подсчитывая количество заголовков
    разных уровней и количество блоков кода.
    """
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Ошибка: файл не найден по пути '{file_path}'")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return

    # Регулярные выражения для поиска заголовков и блоков кода
    heading_pattern = re.compile(r"^(#{1,6})\s+.*$", re.MULTILINE)
    code_block_pattern = re.compile(r"^```[\w\s]*$", re.MULTILINE)

    # Инициализация счетчиков
    heading_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    code_block_count = 0
    in_code_block = False

    lines = content.splitlines()
    for line in lines:
        # Проверяем на начало/конец блока кода
        if code_block_pattern.match(line):
            if not in_code_block:
                code_block_count += 1
            in_code_block = not in_code_block
            continue

        # Если не в блоке кода, ищем заголовки
        if not in_code_block:
            match = heading_pattern.match(line)
            if match:
                level = len(match.group(1))
                heading_counts[level] += 1

    # Вывод отчета
    print("--- Отчет по файлу Markdown ---")
    print(f"Файл: {file_path}")
    print("\nСтатистика заголовков:")
    has_headings = False
    for level, count in heading_counts.items():
        if count > 0:
            print(f"  Заголовки уровня H{level}: {count}")
            has_headings = True
    if not has_headings:
        print("  Заголовки не найдены.")

    print(f"\nКоличество блоков кода: {code_block_count}")
    print("-------------------------------")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Анализ всех файлов .md в текущем каталоге.")
        md_files = sorted(list(Path(".").glob("*.md")))
        if not md_files:
            print("Не найдено ни одного файла .md.")
        else:
            for file in md_files:
                analyze_markdown(str(file))
    else:
        file_to_analyze = sys.argv[1]
        analyze_markdown(file_to_analyze)
