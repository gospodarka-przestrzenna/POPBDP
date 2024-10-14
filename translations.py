import gettext
import os
from PyQt5.QtCore import QLocale

def setup_translations(domain="POPBDP", locale_path="i18n"):
    """
    Initializes the translation system based on the local settings from Qt.

    Args:
        domain (str): The domain name for translations (e.g., "my_plugin").
        locale_path (str): Path to the directory containing translation files.

    Returns:
        function: The `_` function for translations.
    """
    # Retrieve the system's locale settings from Qt
    qt_locale = QLocale.system().name()  # Example: "pl_PL"
    lang = qt_locale.split("_")[0]  # Extract the language code, e.g., "pl"

    # Determine the absolute path to the translation files
    abs_locale_path = os.path.join(os.path.dirname(__file__), locale_path)

    # Configure gettext for translations
    gettext.bindtextdomain(domain, abs_locale_path)
    gettext.textdomain(domain)

    # Load translations for the detected language
    translator = gettext.translation(domain, abs_locale_path, languages=[lang], fallback=True)
    return translator.gettext

# Initialize the `_` function for translations
_ = setup_translations()