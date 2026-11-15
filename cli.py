import sys
import json
import os
from src.parser import parse_hh_rtf
from src.pdf_generator import generate_pdf

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 cli.py input/имя_файла.rtf")
        sys.exit(1)

    rtf_file = sys.argv[1]
    if not os.path.exists(rtf_file):
        print(f"Файл {rtf_file} не найден.")
        sys.exit(1)

    print(f"Парсим {rtf_file}...")
    data = parse_hh_rtf(rtf_file)
    
    # Сохраняем JSON в output
    json_path = "output/parsed_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSON сохранен в {json_path}")

    # Генерируем PDF в output
    pdf_path = "output/parsed_resume.pdf"
    generate_pdf(data, pdf_path)
    print(f"PDF сохранен в {pdf_path}")