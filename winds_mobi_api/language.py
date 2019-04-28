from accept_language import parse_accept_language
from stop_words import LANGUAGE_MAPPING

supported_languages = list(LANGUAGE_MAPPING.keys())


def negotiate_language(accept_language, default='en'):
    for locale in parse_accept_language(accept_language):
        if locale.language in supported_languages:
            return locale.language
    return default
