# Translation Guide

This guide provides instructions for translating the QuickBDL plugin into different languages. The steps below describe how to extract translatable strings, update translation files, and compile them for use.
Prerequisites

GNU gettext tools must be installed:
On Ubuntu/Debian: sudo apt install gettext
On macOS: brew install gettext
On Windows: Use gettext binaries or WSL.
Ensure the project has the following folder structure for translations:
```
i18n/
  └── [language_code]/
      └── LC_MESSAGES/
          ├── QuickBDL.pot  # Template file for translations
          ├── QuickBDL.po   # Translations for the language
          └── QuickBDL.mo   # Compiled translations
```
Extracting Translatable Strings

Run the following command to extract all translatable strings from the plugin's Python files:
`find . -name "*.py" | xargs xgettext -d QuickBDL -o i18n/[language_code]/LC_MESSAGES/QuickBDL.pot`
Replace [language_code] with the desired language code (e.g., pl for Polish or en for English).
This command generates a .pot file containing all strings marked for translation.
Updating Translations

To update the existing .po file with new strings from the .pot file, use:
`msgmerge -U i18n/[language_code]/LC_MESSAGES/QuickBDL.po i18n/[language_code]/LC_MESSAGES/QuickBDL.pot`
This merges any new strings from the .pot file into the .po file for the language.
Review and edit the .po file to provide translations for new or updated strings.
Strings marked with `#, fuzzy` require confirmation or correction.
Compiling Translations

Once translations are updated, compile the .po file into a .mo file for use by the plugin:
`msgfmt i18n/[language_code]/LC_MESSAGES/QuickBDL.po -o i18n/[language_code]/LC_MESSAGES/QuickBDL.mo`
The .mo file is the binary format used by the plugin to load translations.
Adding a New Language

To add a new language:
Create a new directory for the language:
`mkdir -p i18n/[language_code]/LC_MESSAGES`
Copy the template .pot file to initialize the .po file:
`cp i18n/en/LC_MESSAGES/QuickBDL.pot i18n/[language_code]/LC_MESSAGES/QuickBDL.po`
Translate strings in the .po file.
Tips for Translators

Always review `#, fuzzy` entries in the `.po` file. These are auto-filled guesses that may need corrections.
Use a translation editor like Poedit or Lokalize for easier editing.
Testing Translations

To test translations:
Start QGIS with the desired language set in its settings.
Load the plugin and verify that the interface uses the correct translations.
Example Workflow for Polish (pl)

# Extract strings
`find . -name "*.py" | xargs xgettext -d QuickBDL -o i18n/pl/LC_MESSAGES/QuickBDL.pot`

# Update translations
`msgmerge -U i18n/pl/LC_MESSAGES/QuickBDL.po i18n/pl/LC_MESSAGES/QuickBDL.pot`

# Review translations in i18n/pl/LC_MESSAGES/QuickBDL.po

# Compile translations
`msgfmt i18n/pl/LC_MESSAGES/QuickBDL.po -o i18n/pl/LC_MESSAGES/QuickBDL.mo`
This guide ensures that contributors and maintainers have clear instructions for managing translations efficiently.