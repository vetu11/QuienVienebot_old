# coding=utf-8
# Archivo: lang
# Descripción: Descripción de la clase Lang y otras funciones útiles, que se usarán para obtener los textos de los
# mensajes del bot.

import json


_LANGS_INICIADOS = {}
_IDIOMAS_DISPONIBLES = ["ES-es"]
_SINONIMOS_IDIOMAS = {"es": "ES-es",
                      "ES-es": "es"}


class Lang:
    # Esta clase es la definicion de un idioma.

    def __init__(self, lang_code="ES-es"):

        if lang_code is _SINONIMOS_IDIOMAS:
            lang_code = _SINONIMOS_IDIOMAS[lang_code]
        elif lang_code is not _IDIOMAS_DISPONIBLES:
            lang_code = "ES-es"

        with open("lang/%s.json" % lang_code) as f:
            self.texts = json.load(f)

    def get_text(self, text_code, *args, **kwargs):
        # Este método devuelve el texto correspondiente al solicitado en el lenguaje Lang, y si el text necesita
        # inserciones de variables, las hace (args, kwargs).

        if text_code in self.texts:
            try:
                return self.texts[text_code].format(*args, **kwargs)
            except IndexError or KeyError:
                return self.texts[text_code]
        else:
            return self.texts["not_found"].format(failed_text_code=text_code)


def get_lang(lang_code):
    # Esta función devuelve una instancia de Lang del idioma solicitado.
    if lang_code in _LANGS_INICIADOS:
        return _LANGS_INICIADOS[lang_code]
    else:
        lang = Lang(lang_code)
        _LANGS_INICIADOS.update({lang_code: lang})
        return lang
