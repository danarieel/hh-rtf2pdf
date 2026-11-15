import re
from striprtf.striprtf import rtf_to_text

def parse_hh_rtf(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        rtf_content = f.read()

    text = rtf_to_text(rtf_content)
    lines = [line.replace('|', '').strip() for line in text.split('\n') if line.replace('|', '').strip()]
    
    data = {
        "name": "", "position": "", "contact_email": "", "contact_telegram": "",
        "contact_github": "", "about": "", "skills": [], "experience": [],
        "education": [], "courses": []
    }

    def find_idx(keyword, start=0):
        for i in range(start, len(lines)):
            if lines[i].startswith(keyword) or keyword in lines[i]:
                return i
        return -1

    idx_exp = find_idx("Опыт работы")
    idx_edu = find_idx("Образование")
    idx_courses = find_idx("Повышение квалификации")
    idx_skills = find_idx("Навыки")
    idx_about = find_idx("Обо мне")

    # 1. Базовая информация
    if lines:
        data["name"] = lines[0]

    for i, line in enumerate(lines):
        if "@" in line and "." in line and not data["contact_email"]:
            data["contact_email"] = line
        if "github.com" in line.lower():
            data["contact_github"] = line.split("github.com/")[-1].split()[0]
        if "telegram:" in line.lower() or "t.me" in line.lower():
            data["contact_telegram"] = line.split(":")[-1].strip().replace("@", "")
        if "Желаемая должность" in line and i + 1 < len(lines):
            data["position"] = lines[i+1]

    # 2. Обо мне (сохраняем переносы строк)
    if idx_about != -1:
        about_lines = lines[idx_about:]
        about_text = "\n".join(about_lines)
        about_text = re.sub(r'Обо мне\s*', '', about_text).strip()
        data["about"] = about_text

    # 3. Опыт работы
    if idx_exp != -1:
        end_exp = idx_edu if idx_edu != -1 else len(lines)
        exp_lines = lines[idx_exp+1:end_exp]
        
        current_job = None
        skip_next = False
        for i, line in enumerate(exp_lines):
            if skip_next:
                skip_next = False
                continue

            if re.search(r'(Январь|Февраль|Март|Апрель|Май|Июнь|Июль|Август|Сентябрь|Октябрь|Ноябрь|Декабрь).*\d{4}', line, re.I):
                if current_job:
                    data["experience"].append(current_job)
                current_job = {"company": "", "role": "", "dates": line, "bullets": []}
                continue

            if not current_job:
                continue

            if re.search(r'^\d+\s*(год|лет|месяц)', line, re.I):
                continue

            if line == "Стек:":
                if i + 1 < len(exp_lines):
                    current_job["bullets"].append(f"Стек: {exp_lines[i+1]}")
                    skip_next = True
                continue
            elif line.startswith("Стек:"):
                current_job["bullets"].append(line)
                continue

            if line.startswith("—"):
                current_job["bullets"].append(line.lstrip("— ").strip())
                continue

            if any(x in line for x in ["Ростов-на-Дону", "Санкт-Петербург", "Информационные технологии", "Разработка программного", "Системная интеграция"]):
                continue

            if not current_job["company"]:
                current_job["company"] = line
            elif not current_job["role"] and any(word in line for word in ["Engineer", "Support", "Аналитик", "SOC", "Специалист", "(L1)"]):
                current_job["role"] = line

        if current_job:
            data["experience"].append(current_job)

    # 4. Образование (исправлена склейка)
    if idx_edu != -1:
        end_edu = idx_courses if idx_courses != -1 else len(lines)
        edu_block = lines[idx_edu+1:end_edu]
        
        edu_data = {"institution": "", "degree": "", "dates": ""}
        for line in edu_block:
            if re.match(r'^\d{4}$', line):
                edu_data["dates"] = line
            elif "университет" in line.lower():
                edu_data["institution"] = line.replace("Неоконченное высшее", "").strip()
            elif "Факультет" in line or "Прикладная" in line:
                edu_data["degree"] = line
        
        if edu_data["institution"]:
            data["education"].append(edu_data)

    # 5. Курсы
    if idx_courses != -1:
        end_courses = idx_skills if idx_skills != -1 else len(lines)
        course_lines = lines[idx_courses+1:end_courses]
        i = 0
        while i < len(course_lines):
            line = course_lines[i]
            year_match = re.match(r'(\d{4})', line)
            if year_match and i + 1 < len(course_lines):
                year = year_match.group(1)
                name = line.replace(year, '').strip()
                provider = course_lines[i+1] if i+1 < len(course_lines) else ""
                data["courses"].append({"name": name, "provider": provider, "year": year})
                i += 2
            else:
                i += 1

    # 6. Навыки (ищем строку с двойными пробелами)
    if idx_skills != -1:
        for line in lines[idx_skills+1:]:
            if "Дополнительная информация" in line or "Обо мне" in line:
                break
            # Пропускаем языки
            if "Английский" in line or "Русский" in line or "Знание языков" in line:
                continue
            
            # Навыки в RTF разделены двумя пробелами и часто начинаются с "Навыки"
            if "  " in line:
                clean_l = line.replace("Навыки", "").strip()
                parts = [p.strip() for p in re.split(r'\s{2,}', clean_l) if p.strip()]
                data["skills"].extend(parts)

    return data