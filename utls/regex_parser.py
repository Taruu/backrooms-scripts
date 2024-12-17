import re
from enum import Enum

# only old links format
# [https://www.backrooms-wiki.ru/level-0 Forward]
# [*https://www.backrooms-wiki.ru/level-0 New page]
s_bracket_one_regex = r"(?<!\[)\[[^\[\]]*\](?!\[)"

# [[image ]]
# [[component:level-class]]
s_bracket_dual_regex = r"\[\[(?:.|\n)*?\]\]"

# only new links
# [[[http://ru-backrooms-wiki.wikidot.com/level-0|desc]]]
# [[[*http://ru-backrooms-wiki.wikidot.com/level-0|desc]]]
s_bracket_triple_regex = r"\[\[\[[^\[\]\n]*\]\]\]"

css_url_regex = r"url\(\s*[\'\"]?(https?:\/\/[^)\'\"]+?)[\'\"]?\s*\)"

css_import_regex = r"@import\s+url\(\s*[\'\"]?(https?:\/\/[^\'\")]+)[\'\"]?\s*\);"

code_block_import_regex = r"@import\s+url\(\s*[\'\"]?[^\'\")]*local--code[^\'\")]*[\'\"]?\s*\);"

module_css_regex = r'\[\[module css\]\](.*?)\[\[/module\]\]'


# TODO add this parser variant:
# http://handbook.wikidot.com/en:modules-all
def get_module_css(source: str) -> list[str] | None:
    """get list [[module css]]"""
    list_all_duals = re.findall(s_bracket_dual_regex, source)

    start_block: str = None
    end_block: str = None

    list_patterns = []

    for block in list_all_duals:
        if ("module" in block.lower()) and ("css" in block.lower()) and not start_block:
            start_block = block
        elif start_block and ("/module" in block.lower()):
            end_block = block
        elif start_block and end_block:
            pattern = re.escape(start_block) + r'(.*?)' + re.escape(end_block)
            list_patterns.append(pattern)

    if not list_patterns:
        return None

    list_matches = []

    for pattern in list_patterns:
        matches = re.finditer(pattern, source, re.DOTALL)
        for match in matches:
            list_matches.append(match)

    css_block = []

    for match in list_matches:
        # can exist multiple blocks BUT fucking block flOooating
        # i know this can be fixed by regex but uhhhhh idk
        css_block.append(source[match.start():match.end()])

    return list(dict.fromkeys(css_block))


class PEARTextHighlighter(Enum):
    ABAP = 'abap'
    AVR_ASSEMBLER = 'avrc'
    C_PLUS_PLUS = 'cpp'
    CSS = 'css'
    DIFF = 'diff'
    DTD = 'dtd'
    HTML = 'html'
    JAVA = 'java'
    JAVASCRIPT = 'javascript'
    MYSQL = 'mysql'
    PERL = 'perl'
    PHP = 'php'
    PYTHON = 'python'
    RUBY = 'ruby'
    SHELL_SCRIPT = 'sh'
    SQL = 'sql'
    VBSCRIPT = 'vbscript'
    XML = 'xml'


def get_code_blocks(source: str, code_type: PEARTextHighlighter = None) -> None | list[str]:
    """get [[code type=]]"""
    # TODO REWRITE TO LIST
    list_all_duals = re.findall(s_bracket_dual_regex, source)

    start_block: str = None
    end_block: str = None

    for block in list_all_duals:
        start_prepare = block.lower().replace("[", "").replace("]", "").split()

        if ("code" in start_prepare) and not start_block:
            if code_type and (len(start_prepare) > 1):
                if (code_type.value in start_prepare[1]) and ("type=" in start_prepare[1]):
                    start_block = block
                    continue
                else:
                    continue
            start_block = block
        elif start_block and ("/code" in block.lower()):
            end_block = block

    if not start_block and not end_block:
        return None

    pattern = re.escape(start_block) + r'(.*?)' + re.escape(end_block)
    matches = re.finditer(pattern, source, re.DOTALL)
    code_blocks = []

    for match in matches:
        # can exist multiple blocks BUT fucking block flOooating
        # i know this can be fixed by regex but uhhhhh idk
        code_blocks.append(source[match.start():match.end()])

    return code_blocks

# text = """Some text before
# [[Module css]]
# body {
#   background-color: #f3f3f3;
# }
#
# tesadasdas
# [[/module]]
# Some text after."""
#
# print()
#
# module_css_text = get_module_css(text)
# print(text.replace(module_css_text, ""))
