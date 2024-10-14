# For each language


`find . -name "*.py" | xargs xgettext -d POPBDP -o i18n/pl/LC_MESSAGES/POPBDP.pot`

`msgmerge -U i18n/pl/LC_MESSAGES/POPBDP.po i18n/pl/LC_MESSAGES/POPBDP.pot`

update `#, fuzzy` translations

`msgfmt i18n/pl/LC_MESSAGES/POPBDP.po -o i18n/pl/LC_MESSAGES/POPBDP.mo`