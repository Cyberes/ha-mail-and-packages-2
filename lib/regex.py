import re


def find_re_matches(text: str, regex_list: list) -> list:
    matches = []
    for regex in regex_list:
        found_matches = re.findall(regex, text)
        matches.extend(found_matches)
    return list(set(matches))
