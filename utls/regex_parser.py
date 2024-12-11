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
