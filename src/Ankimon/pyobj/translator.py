import json
from ..resources import lang_path_de, lang_path_ch, lang_path_en, lang_path_fr, lang_path_jp, lang_path_sp, lang_path_kr, lang_path_it, lang_path_cz, lang_path_po, lang_path_vi

# UI language code -> translation file
LANG_PATHS = {
    "de": lang_path_de,
    "ch": lang_path_ch,
    "en": lang_path_en,
    "fr": lang_path_fr,
    "jp": lang_path_jp,
    "sp": lang_path_sp,
    "kr": lang_path_kr,
    "it": lang_path_it,
    "cz": lang_path_cz,
    "po": lang_path_po,
    "vi": lang_path_vi
}

# Game language id (misc.language, from PokeAPI) -> UI language code.
# Kept for backward compatibility with code that still passes the game
# language id to the Translator. Vietnamese is NOT a PokeAPI language,
# so it can only appear here via the UI language code, never via an id.
LANG_NUMBERS = {
    1: 'jp',
    2: 'jp',
    3: 'kr',
    4: 'ch',
    5: 'fr',
    6: 'de',
    7: 'sp',
    8: 'it',
    9: 'en',
    10: 'cz',
    11: 'jp',
    12: 'ch',
    13: 'po',
}

class Translator:
    def __init__(self, ui_language="en"):
        # Accept either a UI language code ("en", "vi", ...) or, for backward
        # compatibility, a game language id (1-13) which we map to a code.
        if isinstance(ui_language, int):
            short_language = LANG_NUMBERS.get(ui_language, 'en')
        else:
            short_language = str(ui_language) if str(ui_language) in LANG_PATHS else 'en'
        self.filepath = LANG_PATHS.get(short_language, lang_path_en)
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            raise Exception(f"Translation file not found: {self.filepath}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON format in translation file: {self.filepath}")

    def translate(self, key, **kwargs):
        # Track which translation file is being used
        source_file = self.filepath
        template = self.translations.get(key, None)

        # Fallback to English if key not found
        if template is None:
            try:
                with open(lang_path_en, 'r', encoding='utf-8') as f:
                    fallback_translations = json.load(f)
                template = fallback_translations.get(key, key)
                source_file = lang_path_en  # Now using fallback file
            except Exception as e:
                raise Exception(f"Fallback translation failed: {str(e)}")

        try:
            return template.format(**kwargs)
        except KeyError as e:
            missing_key = str(e).strip("'")
            available = list(kwargs.keys())
            raise Exception(
                f"Translation error in key '{key}'\n"
                f"• Missing placeholder: {missing_key}\n"
                f"• Translation file: {source_file}\n"
                f"• Available arguments: {available}"
            )
