# -*- coding: utf-8 -*-

from guess_language import guessLanguage
from pyramid.threadlocal import get_current_registry
from Stemmer import Stemmer
from text_sentence import tokenize


def index(text, accepted_languages=None, langs=None):
    registry = get_current_registry()
    if accepted_languages == None:
        accepted_languages = [x.strip() for x in
                              registry.settings["accepted_languages"].split(","
                              )]
    if langs == None:
        lang = guessLanguage(text)
        if lang not in accepted_languages:
            langs = accepted_languages
        else:
            langs = [lang]
    langs = list(set(langs).intersection(set(accepted_languages)))
    if not langs:
        langs = accepted_languages
    indexed_words = set()
    for lang in langs:
        stemmer = Stemmer(lang)
        indexed_words.update([stemmer.stemWord(x.value) for x in
                             tokenize(text)])
    return indexed_words
