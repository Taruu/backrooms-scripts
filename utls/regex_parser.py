


# only old links format
# [https://www.backrooms-wiki.ru/level-0 Forward]
# [*https://www.backrooms-wiki.ru/level-0 New page]
solo_regex = r"(?<!\[)\[[^\[\]]*\](?!\[)"

# [[image ]]
# [[component:level-class]]
dual_regex = r"\[\[(?:.|\n)*?\]\]"

# only new links
# [[[http://ru-backrooms-wiki.wikidot.com/level-0|desc]]]
# [[[*http://ru-backrooms-wiki.wikidot.com/level-0|desc]]]
thiple_regex = r"\[\[\[[^\[\]\n]*\]\]\]"