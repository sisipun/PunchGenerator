import random
from pyphonetics import Soundex
from pymorphy2.analyzer import MorphAnalyzer
from pyphonetics import distance_metrics
from hyphen import Hyphenator

DELIMITERS = ['.', '?', '!', '\n', '–', '(', ')', '[', ']', ' ', '\"', '—', '…', ',', ':', '»', '«', ';', '-', '*',
              '~', '\'']
EMPTY = ''

soundex = Soundex()
analyzer = MorphAnalyzer()
hyphenator = Hyphenator('ru_RU')


def to_soundex(text):
    soundex_text = []
    soundex_dictionary = {}
    word = ''
    text_len = len(text)
    percent = 0
    errors = []
    for i, c in enumerate(text):
        new_percent = int(i * 100 / text_len)
        if new_percent > percent:
            percent = new_percent
            print("Soundex encoding: {}%".format(percent))
        if c in DELIMITERS:
            if word != EMPTY:
                try:
                    soundex_key = soundex.phonetics(word)
                    pos = analyzer.parse(word)[0].tag.POS
                    syllables = len(hyphenator.syllables(word))
                    soundex_key = "{}{}{}".format('N' if pos is None else pos[0], syllables, soundex_key)
                except IndexError:
                    errors.append(word)
                    continue
                soundex_text.append(soundex_key)
                if soundex_key not in soundex_dictionary.keys():
                    soundex_dictionary[soundex_key] = set()
                soundex_dictionary[soundex_key].add(word)
                word = ''
            soundex_text.append(c)
            continue
        word += c
    soundex_text = list(filter(lambda s: s != ' ', soundex_text))
    if errors:
        print('Can\'t encode this words: {}'.format(errors))
    return soundex_text, soundex_dictionary


def to_text(soundex_text, dictionary):
    text = ''
    soundex_key = ''
    text_len = len(soundex_text)
    percent = 0
    for i, c in enumerate(soundex_text):
        new_percent = int(i * 100 / text_len)
        if new_percent > percent:
            percent = new_percent
            print("Text decoding: {}%".format(percent))
        if c in DELIMITERS:
            if soundex_key != EMPTY:
                words = set()
                for key in dictionary:
                    if distance_metrics.levenshtein_distance(key, soundex_key) <= 1:
                        words.update(dictionary[key])
                if words:
                    choice = random.choice(list(words))
                    text += choice
                soundex_key = ''
            text += c
            continue
        soundex_key += c
    return text
