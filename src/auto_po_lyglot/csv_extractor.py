#!/usr/bin/env python
"""Converts output md files from transpopenai.py to CSV files."""
import re
import csv
import sys
import os
import logging

logger = logging.getLogger(__name__)


def extract_translation(line):
    pattern = r'(^|, )(\w+):[^"]*"(.*?)"'
    matches = re.findall(pattern, line)
    res = {lang: trans for start, lang, trans in matches}
    logger.debug(line, res)
    return res


def extract_csv(input_file, output_file, languages=["English", "French", "Italian", "Spanish", "German"]):
    translations = {}
    current_key = None

    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            line = line.strip()
            if line == "=" * len(line) and len(line) > 0:
                current_key = None
            elif current_key is None:
                extracted = extract_translation(line)
                if "English" in extracted and "French" in extracted:
                    current_key = (extracted["English"], extracted["French"])
                    if current_key not in translations:
                        translations[current_key] = {"Italian": "", "Spanish": "", "German": ""}

                if current_key:
                    for lang in ["Italian", "Spanish", "German"]:
                        if lang in extracted:
                            translations[current_key][lang] = extracted[lang]

    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=languages)
        writer.writeheader()
        for (english, french), others in translations.items():
            row = {"English": english, "French": french, **others}
            writer.writerow(row)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = os.path.splitext(input_file)[0] + '.csv'

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    extract_csv(input_file, output_file)
    logger.info(f"Conversion complete. CSV file created : {output_file}")


if __name__ == "__main__":
    main()
