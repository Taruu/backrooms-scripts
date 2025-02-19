import re
import unicodedata
from typing import Tuple

TRANSLIT_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ж': 'z',
    'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c',
    'ч': 'c', 'ы': 'i', 'э': 'e', 'ю': 'u', 'я': 'a', 'і': 'i', 'ї': 'i', 'є': 'e',
    'ь': '', 'ъ': ''
}


# Returns (category, name) from a full name
def get_name(full_name: str) -> Tuple[str, str]:
    split = full_name.split(':', 1)
    if len(split) == 2:
        return split[0], split[1]
    return '_default', split[0]


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def normalize_article_name(full_name: str) -> str:
    # https://github.com/SCPru/RuFoundation/blob/3eab2b27969f5b56633d01e92a76d43a6d8a6e3e/web/controllers/articles.py#L43
    # Okay i go fuck myself?
    full_name = strip_accents(full_name.lower())

    full_name = ''.join(TRANSLIT_MAP.get(c, c) for c in full_name)
    n = re.sub(r'[^A-Za-z0-9\-_:]+', '-', full_name).strip('-')
    n = re.sub(r':+', ':', n).lower().strip(':')
    category, name = get_name(n)
    if category == '_default':
        return name
    return '%s:%s' % (category, name)


# Regex patterns (matching the ones in Rust code)
NON_NORMAL = re.compile(r"[^\w\-:_]")
LEADING_OR_TRAILING_DASHES = re.compile(r"(^-+)|(-+$)")
MULTIPLE_DASHES = re.compile(r"-{2,}")
MULTIPLE_COLONS = re.compile(r":{2,}")
COLON_DASH = re.compile(r"(:-)|(-:)")
UNDERSCORE_DASH = re.compile(r"(_-)|(-_)")
LEADING_OR_TRAILING_COLON = re.compile(r"(^:)|(:$)")


def merge_multi_categories(text: str) -> str:
    indices = []
    first = True

    # Find all colons except the last
    for idx, ch in enumerate(reversed(text)):
        if ch != ':':
            continue

        if first:
            first = False
            continue

        indices.append(len(text) - idx - 1)

    # Replace all colons with dashes
    text_list = list(text)  # Convert string to list to mutate it
    for idx in indices:
        text_list[idx] = '-'

    return ''.join(text_list)


def normalize_nfkc(text: str) -> str:
    # Normalize the string using NFKC
    return unicodedata.normalize('NFKC', text)


def casefold(text: str) -> str:
    # Perform case folding (convert to lowercase)
    return text.casefold()


def replace_underscores(text: str) -> str:
    matches = []
    prev_colon = False

    # Finding matching, non-conforming underscores
    for idx, ch in enumerate(text):
        if ch == '_':
            # If it's not the leading underscore, or after a category,
            # push an index to replace it
            if idx > 0 and not prev_colon:
                matches.append(idx)
        prev_colon = ch == ':'

    # Replace the underscores with dashes
    text_list = list(text)  # Convert string to list to mutate it
    for idx in matches:
        text_list[idx] = '-'

    return ''.join(text_list)


def normalize(text: str) -> str:
    # Remove leading and trailing whitespace
    text = text.strip()

    # Remove leading slash if present
    if text.startswith('/'):
        text = text[1:]

    # Normalize to unicode NFKC
    text = unicodedata.normalize('NFKC', text)

    # Case fold (convert to lowercase)
    # text = text.casefold()
    text = text.lower()

    # Replace all non-normal characters
    text = re.sub(NON_NORMAL, '-', text)

    # Replace all multi-colons with a dash
    text = merge_multi_categories(text)

    # Replace underscores with dashes, except leading ones
    text = replace_underscores(text)

    # Remove any leading or trailing dashes
    text = re.sub(LEADING_OR_TRAILING_DASHES, '', text)

    # Merge multiple dashes and colons into one
    text = re.sub(MULTIPLE_DASHES, '-', text)
    text = re.sub(MULTIPLE_COLONS, ':', text)

    # Remove leading or trailing dashes around colons or underscores
    text = re.sub(COLON_DASH, ':', text)
    text = re.sub(UNDERSCORE_DASH, '_', text)

    # Remove any leading or trailing colons
    text = re.sub(LEADING_OR_TRAILING_COLON, '', text)

    # Remove '_default:' if it exists
    if text.startswith('_default:'):
        text = text[9:]

    return text


import unittest


# Assuming that the normalize function and other helper functions
# (merge_multi_categories and replace_underscores) are already defined


class TestNormalizeFunction(unittest.TestCase):
    def check(self, input_text, expected_text):
        normalized_text = normalize(input_text)
        normalized_text2 = normalize_article_name(input_text)
        print(input_text, expected_text, normalized_text2)
        self.assertEqual(normalized_text, expected_text, f"Normalized text doesn't match expected for '{input_text}'")

    def test_normalize(self):
        self.check("", "")
        self.check("Big Cheese Horace", "big-cheese-horace")
        self.check("bottom--Text", "bottom-text")
        self.check("Tufto's Proposal", "tufto-s-proposal")
        self.check(" - Test - ", "test")
        self.check("--TEST--", "test")
        self.check("-test-", "test")
        self.check(":test", "test")
        self.check("test:", "test")
        self.check(":test:", "test")
        self.check("/Some Page", "some-page")
        self.check("some/Page", "some-page")
        self.check("some,Page", "some-page")
        self.check("End of Death Hub", "end-of-death-hub")
        self.check("$100 is a lot of money", "100-is-a-lot-of-money")
        self.check("$100 is a lot of money!", "100-is-a-lot-of-money")
        self.check("snake_case", "snake-case")
        self.check("long__snake__case", "long-snake-case")
        self.check("snake-_dash", "snake-dash")
        self.check("snake_-dash", "snake-dash")
        self.check("snake_-_dash", "snake-dash")
        self.check("_template", "_template")
        self.check("_template_", "_template")
        self.check("__template", "_template")
        self.check("__template_", "_template")
        self.check("template_", "template")
        self.check("template__", "template")
        self.check("_Template", "_template")
        self.check("_Template_", "_template")
        self.check("__Template", "_template")
        self.check("__Template_", "_template")
        self.check("Template_", "template")
        self.check("Template__", "template")
        self.check(" <[ TEST ]> ", "test")
        self.check("ÄÀ-áö ðñæ_þß*řƒŦ", "äà-áö-ðñæ-þß-řƒŧ")
        self.check("Site-五", "site-五")
        self.check("ᒥᐢᑕᓇᐢᑯᐍᐤ--1", "ᒥᐢᑕᓇᐢᑯᐍᐤ-1")
        self.check("ᒥᐢᑕᓇᐢᑯᐍᐤ:_template", "ᒥᐢᑕᓇᐢᑯᐍᐤ:_template")
        self.check("🚗A‱B⁜C", "a-b-c")
        self.check("Ⰰ_á_X", "ⰰ-á-x")
        self.check("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", "")
        self.check("Component:image block", "component:image-block")
        self.check("fragment:scp-4447-2", "fragment:scp-4447-2")
        self.check("fragment::scp-4447-2", "fragment:scp-4447-2")
        self.check("FRAGMENT:SCP-4447 (2)", "fragment:scp-4447-2")
        self.check("protected_:fragment_:page", "protected-fragment:page")
        self.check("protected:_fragment_:page", "protected-fragment:page")
        self.check("fragment:_template", "fragment:_template")
        self.check("fragment:__template", "fragment:_template")
        self.check("fragment:_template_", "fragment:_template")
        self.check("fragment::_template", "fragment:_template")
        self.check("_default:_template", "_template")
        self.check("_default:__template", "_template")
        self.check("_default:_template_", "_template")
        self.check("_default::_template", "_template")
        self.check("/fragment:_template", "fragment:_template")
        self.check("/fragment:__template", "fragment:_template")
        self.check("/fragment:_template_", "fragment:_template")
        self.check("/fragment::_template", "fragment:_template")
        self.check("/_default:_template", "_template")
        self.check("/_default:__template", "_template")
        self.check("/_default:_template_", "_template")
        self.check("/_default::_template", "_template")
        self.check("protected:fragment:_template", "protected-fragment:_template")
        self.check("protected:fragment:__template", "protected-fragment:_template")
        self.check("protected:fragment:_template_", "protected-fragment:_template")
        self.check("protected:fragment::_template", "protected-fragment:_template")
        self.check("protected::fragment:_template", "protected-fragment:_template")
        self.check("protected::fragment::_template", "protected-fragment:_template")
        self.check("protected:archived:fragment:page", "protected-archived-fragment:page")
        self.check("АБВГҐЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщыэюя",
                   "abvg-eezziiklmnoprstufhcc-ieuaabvgdeezziiklmnoprstufhcc-ieua")


if __name__ == '__main__':
    unittest.main()
