"""
Fix component name
"""
import re

from utls.regex_parser import s_bracket_dual_regex


def handle(source_page: str) -> str:
    patched_source_page = source_page
    blocks_list = re.findall(s_bracket_dual_regex, source_page)
    split_listed = [block.split() for block in blocks_list]
    only_components = [block for block in split_listed if "include" in block[0]]
    only_to_patch = [block for block in only_components if block[1].count(':') > 2]

    for split_block in only_to_patch:
        old_component_name = split_block[1]
        component_name = old_component_name.split(":")
        component_name.pop(1)
        new_component_name = ":".join(component_name)
        patched_source_page.replace(old_component_name, new_component_name)

    return patched_source_page
