import markovify as mk

CONTENT_FILENAME = 'content.txt'

with open(CONTENT_FILENAME, encoding='utf8') as f:
    text = f.read()

text_model = mk.Text(text)

for i in range(4):
    print(text_model.make_short_sentence(150, 50))

