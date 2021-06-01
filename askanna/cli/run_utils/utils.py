# -*- coding: utf-8 -*-
import os
import re


def string_expand_variables(strings: list) -> list:
    var_matcher = re.compile(r"\$\{(?P<MYVAR>[\w\-]+)\}")
    for idx, line in enumerate(strings):
        matches = var_matcher.findall(line)
        for m in matches:
            line = line.replace("${" + m + "}", os.getenv(m.strip()))
        strings[idx] = line
    return strings
