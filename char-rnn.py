from __future__ import print_function

import random
import sys
import numpy as np
from keras.callbacks import LambdaCallback
from keras.layers import Dense
from keras.layers import LSTM
from keras.models import Sequential
from keras.optimizers import RMSprop
from soundex import to_soundex, to_text
from files import read, write, add

style_text = read('style.txt')
content_text = read('content.txt')

print('Soundex encoding...')
style_soundex, _ = to_soundex(style_text)
_, content_soundex_dictionary = to_soundex(content_text)

chars = sorted(set(style_soundex))
print('total chars:', len(chars))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

print('Sentences creation...')
max_len = 10
sentences = []
next_chars = []
for i in range(0, len(style_soundex) - max_len):
    sentences.append(style_soundex[i: i + max_len])
    next_chars.append(style_soundex[i + max_len])
print('nb sequences:', len(sentences))

print('Vectorization...')
x = np.zeros((len(sentences), max_len, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        x[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1

print('Build model...')
model = Sequential()
model.add(LSTM(128, input_shape=(max_len, len(chars))))
model.add(Dense(len(chars), activation='softmax'))

print('Start optimization...')
optimizer = RMSprop(lr=0.01)
model.compile(loss='categorical_crossentropy', optimizer=optimizer)


def sample(preds, temperature=0.5):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


def on_epoch_end(epoch, _):
    print()
    print('----- Generating text after Epoch: %d' % epoch)

    start_index = random.randint(0, len(style_soundex) - max_len - 1)
    for diversity in [0.2, 0.5, 1.0, 1.2]:
        print('----- diversity:', diversity)
        add('\n------------------\n', 'out_soundex.txt')

        generated = ''
        gen_sentence = style_soundex[start_index: start_index + max_len]
        generated += ' '.join(gen_sentence)
        print('----- Generating with seed: "' + str(gen_sentence) + '"')
        sys.stdout.write(generated)

        for i in range(400):
            x_prediction = np.zeros((1, max_len, len(chars)))
            for t, char in enumerate(gen_sentence):
                x_prediction[0, t, char_indices[char]] = 1.

            preds = model.predict(x_prediction, verbose=0)[0]
            next_index = sample(preds, diversity)
            next_char = indices_char[next_index]

            generated += next_char
            gen_sentence = gen_sentence[1:]
            gen_sentence.append(next_char)

            add(next_char + ' ', 'out_soundex.txt')
        print()


model.fit(x, y, batch_size=128, epochs=60, callbacks=[LambdaCallback(on_epoch_end=on_epoch_end)])

out_soundex = read('out_soundex.txt', False)
text = to_text(out_soundex, content_soundex_dictionary)
write(text, 'out_text.txt')
