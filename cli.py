import sys
import json
import os
from pathlib import Path
from src.parser import parse_hh_rtf
from src.pdf_generator import generate_pdf

def main():
    # Если путь не указан, ищем первый .rtf в папке input/
    if len(sys.argv) < 2:
        files = list(Path("input").glob("*.rtf"))
        if not files:
            print("В папке input/ нет RTF-файлов. Положи туда файл с hh.ru.")
            sys.exit(1)
        rtf_file = str(files[0])
        print(f"Файл не указан, беру: {rtf_file}")
    else:
        rtf_file = sys.argv[1]

    if not os.path.exists(rtf_file):
        print(f"Файл {rtf_file} не найден.")
        sys.exit(1)

    print(f"Парсим {rtf_file}...")
    data = parse_hh_rtf(rtf_file)

    # Имя выходных файлов берем из имени RTF
    stem = Path(rtf_file).stem
    json_path = Path("output") / f"{stem}.json"
    pdf_path = Path("output") / f"{stem}.pdf"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSON: {json_path}")

    generate_pdf(data, str(pdf_path))
    print(f"PDF:  {pdf_path}")

if __name__ == "__main__":
    main()