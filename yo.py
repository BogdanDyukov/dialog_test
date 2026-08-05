import codecs
import re

def load_yo_dictionary(dictionary_path="yo.dat"):
    dictionary = {}

    with codecs.open(dictionary_path, "r", "utf-8") as f:
        for line in f:
            if "*" in line:
                continue

            cline = line.rstrip("\n")

            if "(" in cline:
                bline, sline = cline.split("(", 1)
                sline = re.sub(r"\)", "", sline)
            else:
                bline = cline
                sline = ""

            if "|" in sline:
                for ss in sline.split("|"):
                    value = bline + ss
                    key = value.replace("ё", "е")
                    dictionary[key] = value
            else:
                value = bline
                key = value.replace("ё", "е")
                dictionary[key] = value

    return dictionary


def yoficate_text(text, dictionary):
    splitter = re.compile(r"(\s+|\w+|\W+|\S+)", re.UNICODE)
    tokens = splitter.findall(text)

    result = []

    for token in tokens:
        result.append(dictionary.get(token, token))

    return "".join(result)