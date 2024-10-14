# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2024 Wawrzyniec Zipser, Maciej Kamiński (maciej.kaminski@pwr.edu.pl)
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.
#
###############################################################################
__author__ = 'Wawrzyniec Zipser, Maciej Kamiński Politechnika Wrocławska'

import gettext
import os
from PyQt5.QtCore import QLocale

def setup_translations(domain="QuickBDL", locale_path="../i18n"):
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
    return translator.gettext, 'pl' if lang == 'pl' else 'en'

# Initialize the `_` function for translations
_, gus_language = setup_translations()