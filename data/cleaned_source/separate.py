import os
from random import random

def get_data(lang):
    data = list()
    files = [f'DW_{lang}.txt', f'FOCUS_{lang}.txt', f'FUNDACION_{lang}.txt', f'IMF_{lang}.txt']
    for file in files:
        lines = open(file, 'r', encoding='utf8').readlines()
        data.extend(lines)
    return data

def print_files(lang, split, lines):
    with open(f'{split}.{lang}.txt', 'w', encoding='utf8') as out_file:
        for line in lines:
            out_file.write(line)

        out_file.close()

qu_data = get_data('qu')
es_data = get_data('es')

train_length = int(len(es_data) * 0.9)
val_length = len(es_data) - train_length

train_qu = list()
train_es = list()
val_qu = list()
val_es = list()

while len(train_es) < train_length:
    loc = int(random() * len(es_data))
    train_qu.append(qu_data.pop(loc))
    train_es.append(es_data.pop(loc))

while len(val_es) < val_length:
    loc = int(random() * len(es_data))
    val_qu.append(qu_data.pop(loc))
    val_es.append(es_data.pop(loc))

print_files('qz', 'train', train_qu)
print_files('qz', 'val', val_qu)
print_files('es', 'train', train_es)
print_files('es', 'val', val_es)