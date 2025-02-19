import unicodedata
import unittest

import regex

import unicodedata
import regex as re


# https://github.com/scpwiki/wikijump/blob/legacy-php/web/php/Utils/WDStringUtils.php#L34

def to_unix_name(text: str) -> str:
    text = text.strip()

    # Normalize the text to Normalization Form KC (NFKC)
    normalized_text = unicodedata.normalize('NFKC', text)

    # Perform case folding
    text = normalized_text.lower()

    text = re.sub(r'[^\p{L}\p{N}\-:_]', '-', text, flags=re.UNICODE)  # Replace non-alphanumeric or non-slug characters
    # Allow leading underscores (e.g., _default, _template)
    text = re.sub(r'^_', ':_', text)

    text = re.sub(r'(?<!:)_', '-', text)

    # Remove leading and trailing hyphens
    text = re.sub(r'(^\-*|\-*$)', '', text)

    text = re.sub(r'/[\-]{2,}', '-', text)
    text = re.sub(r'/[:]{2,}', ':', text)

    # Clean up boundaries
    text = re.sub(r'^:', '', text)
    text = re.sub(r':$', '', text)

    text = re.sub(r"(:-|-:)", ":", text)
    text = re.sub(r'(_-|-_)', "_", text)
    text = re.sub('/(^:|:$)', "", text)

    text = re.sub(r'-+', '-', text)
    text = re.sub(r'::', ':', text)
    text = re.sub(r'_(?=:)', '-', text)
    return text


class TestNormalize(unittest.TestCase):
    def test_normalize(self):
        test_cases = [
            ("", ""),
            ("Big Cheese Horace", "big-cheese-horace"),
            ("bottom--Text", "bottom-text"),
            ("Tufto's Proposal", "tufto-s-proposal"),
            (" - Test - ", "test"),
            ("--TEST--", "test"),
            ("-test-", "test"),
            (":test", "test"),
            ("test:", "test"),
            (":test:", "test"),
            ("/Some Page", "some-page"),
            ("some/Page", "some-page"),
            ("some,Page", "some-page"),
            ("End of Death Hub", "end-of-death-hub"),
            ("$100 is a lot of money", "100-is-a-lot-of-money"),
            ("$100 is a lot of money!", "100-is-a-lot-of-money"),
            ("snake_case", "snake-case"),
            ("long__snake__case", "long-snake-case"),
            ("snake-_dash", "snake-dash"),
            ("snake_-dash", "snake-dash"),
            ("snake_-_dash", "snake-dash"),
            ("_template", "_template"),
            ("_template_", "_template"),
            ("__template", "_template"),
            ("__template_", "_template"),
            ("template_", "template"),
            ("template__", "template"),
            ("_Template", "_template"),
            ("_Template_", "_template"),
            ("__Template", "_template"),
            ("__Template_", "_template"),
            ("Template_", "template"),
            ("Template__", "template"),
            (" <[ TEST ]> ", "test"),
            ("ÄÀ-áö ðñæ_þß*řƒŦ", "äà-áö-ðñæ-þß-řƒŧ"),
            ("Site-五", "site-五"),
            ("ᒥᐢᑕᓇᐢᑯᐍᐤ--1", "ᒥᐢᑕᓇᐢᑯᐍᐤ-1"),
            ("ᒥᐢᑕᓇᐢᑯᐍᐤ:_template", "ᒥᐢᑕᓇᐢᑯᐍᐤ:_template"),
            ("🚗A‱B⁜C", "a-b-c"),
            ("Ⰰ_á_X", "ⰰ-á-x"),
            ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ""),
            ("Component:image block", "component:image-block"),
            ("fragment:scp-4447-2", "fragment:scp-4447-2"),
            ("fragment::scp-4447-2", "fragment:scp-4447-2"),
            ("FRAGMENT:SCP-4447 (2)", "fragment:scp-4447-2"),
            ("protected_:fragment_:page", "protected-fragment:page"),
            ("protected:_fragment_:page", "protected-fragment:page"),
            ("fragment:_template", "fragment:_template"),
            ("fragment:__template", "fragment:_template"),
            ("fragment:_template_", "fragment:_template"),
            ("fragment::_template", "fragment:_template"),
            ("_default:_template", "_template"),
            ("_default:__template", "_template"),
            ("_default:_template_", "_template"),
            ("_default::_template", "_template"),
            ("/fragment:_template", "fragment:_template"),
            ("/fragment:__template", "fragment:_template"),
            ("/fragment:_template_", "fragment:_template"),
            ("/fragment::_template", "fragment:_template"),
            ("/_default:_template", "_template"),
            ("/_default:__template", "_template"),
            ("/_default:_template_", "_template"),
            ("/_default::_template", "_template"),
            ("protected:fragment:_template", "protected-fragment:_template"),
            ("protected:fragment:__template", "protected-fragment:_template"),
            ("protected:fragment:_template_", "protected-fragment:_template"),
            ("protected:fragment::_template", "protected-fragment:_template"),
            ("protected::fragment:_template", "protected-fragment:_template"),
            ("protected::fragment::_template", "protected-fragment:_template"),
            ("protected:archived:fragment:page", "protected-archived-fragment:page"),
        ]
        for input_text, expected in test_cases:
            result = to_unix_name(input_text)
            self.assertEqual(result, expected, f"Input: {input_text!r}, Expected: {expected!r}, Got: {result!r}")


if __name__ == '__main__':
    unittest.main()
