import json
import re


def parse_quiz_files(questions_path, answers_path, output_json_path):
    # Чтение файлов
    with open(questions_path, "r", encoding="utf-8") as f:
        q_text = f.read()

    with open(answers_path, "r", encoding="utf-8") as f:
        a_text = f.read()

    # Разделение файлов на блоки по метке "Question Цифра"
    q_blocks = re.split(r"Question \d+", q_text)
    a_blocks = re.split(r"Question \d+", a_text)

    # Очистка пустых элементов
    q_blocks = [b.strip() for b in q_blocks if b.strip()]
    a_blocks = [b.strip() for b in a_blocks if b.strip()]

    json_output = []

    # Итерируемся параллельно по вопросам и ответам
    for q_block, a_block in zip(q_blocks, a_blocks):
        # 1. Парсинг блока вопроса
        q_lines = [line.strip() for line in q_block.split("\n") if line.strip()]

        # Поиск строки, где начинаются варианты ответов (например, "A)")
        opt_start_idx = -1
        for i, line in enumerate(q_lines):
            if re.match(r"^[A-Z]\)", line):
                opt_start_idx = i
                break

        if opt_start_idx == -1:
            continue  # Пропускаем блок, если не нашли варианты ответов

        # Собираем текст вопроса (перенос строк в вопросе склеиваем через пробел)
        question_str = " ".join(q_lines[:opt_start_idx])
        options = q_lines[opt_start_idx:]

        # 2. Парсинг блока ответа
        a_lines = [line.strip() for line in a_block.split("\n") if line.strip()]
        correct_letter = None
        explanation = ""

        for line in a_lines:
            if "(Correct Answer)" in line:
                match = re.match(r"^([A-Z])\)", line)
                if match:
                    correct_letter = match.group(1)
            elif line.startswith("Explanation:"):
                explanation = line.replace("Explanation:", "").strip()

        # 3. Определение индекса правильного ответа
        correct_answers = []
        if correct_letter:
            for idx, opt in enumerate(options):
                if opt.startswith(f"{correct_letter})"):
                    correct_answers.append(idx)
                    break

        # Формирование структуры
        item = {
            "question": question_str,
            "options": options,
            "correctAnswers": correct_answers,
            "Explanation": explanation,
            "type": "single" if len(correct_answers) <= 1 else "multiple",
        }
        json_output.append(item)

    # Сохранение в файл JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)

    print(
        f"Успешно обработано вопросов: {len(json_output)}. Файл сохранен: {output_json_path}"
    )


# Пример запуска (замените названия файлов на свои)
parse_quiz_files("questions.txt", "answers.txt", "quiz_output.json")
