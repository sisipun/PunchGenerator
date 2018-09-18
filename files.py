import io


def read(file_name, lower=True):
    with io.open(file_name, encoding='utf-8') as f:
        return f.read().lower() if lower else f.read()


def write(text, file_name):
    with open(file_name, "w", encoding='utf-8') as f:
        f.write(text)


def add(text, file_name):
    with open(file_name, "a", encoding='utf-8') as f:
        f.write(text)
