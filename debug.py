from striprtf.striprtf import rtf_to_text

with open('input/sample_hh.rtf', 'r', encoding='utf-8', errors='ignore') as f:
    rtf_content = f.read()

text = rtf_to_text(rtf_content)

# Выведем первые 40 непустых строк, чтобы понять структуру
lines = [line.strip() for line in text.split('\n') if line.strip()]
for i, line in enumerate(lines[40:100], start=40):
    print(f"{i}: {line}")