import subprocess
import sentencepiece as spm
from util.util import copy_content

def post_process_bpe(src, bpe_out):
    with open(bpe_out, encoding='utf8') as seg_out, open(src, 'w', encoding='utf8') as train_in:
        seg_arr = seg_out.readlines()

        for line in seg_arr:
            detoken = line#.replace("@@", "")

            train_in.write(detoken)

        seg_out.close()
        train_in.close()

def bpe(input, output, lang, folder, train=True, apply=True):

    bpe_codes = f'model_opennmt/run' + folder + f'/codes.{lang}.txt'
    intermediary = f'model_opennmt/run' + folder + f'/bpe_out.{lang}.txt'

    if train:
        train_bpe = ['subword-nmt', 'learn-bpe', '--input', input, '--output', bpe_codes]
        subprocess.run(train_bpe)

    if apply:
        test_bpe = ['subword-nmt', 'apply-bpe', '--codes', bpe_codes,'--input', input, '--output', intermediary]
        subprocess.run(test_bpe)

    post_process_bpe(output, intermediary)

def process_unigram_list(list):
    string = ""
    for word in list:
        word = word.replace('▁', '')
        if word == ' ' or len(word.strip()) < 1:
            continue
        word = word.strip()
        string = string + ' ' + word
    return string[1:]

def unigram(src, out, model, train=True):
    if train:
        spm.SentencePieceTrainer.train(input=src, model_prefix=model)
    with open(src, 'r', encoding='utf8') as in_file:
        src = in_file.readlines()
    sp = spm.SentencePieceProcessor(model_file=f'{model}.model')
    lines = sp.encode(src, out_type=str)

    with open(out, 'w', encoding='utf8') as out_file:
        for line in lines:
            line = f'{process_unigram_list(line)}\n'
            out_file.write(line)
        out_file.close()

def prpe(src, out, lang, FOLDER, train=True, apply=True):

    PREFIXES = f'model_opennmt/run' + FOLDER  + f'/prefixes.{lang}'
    POSTFIXES = f'model_opennmt/run' + FOLDER  + f'/postfixes.{lang}'
    WORDS = f'model_opennmt/run' + FOLDER  + f'/words.{lang}'
    SUFFIXES = f'model_opennmt/run' + FOLDER  + f'/suffixes.{lang}'
    ROOTS = f'model_opennmt/run' + FOLDER  + f'/roots.{lang}'
    ENDINGS = f'model_opennmt/run' + FOLDER  + f'/endings.{lang}'

    train_prpe = ['python', 'prpe/prpe6/learn_prpe.py', 
                  '-i',  src,
                  '-p',  PREFIXES,
                  '-r',  ROOTS, 
                  '-s',  SUFFIXES,
                  '-t',  POSTFIXES,
                  '-u',  ENDINGS,
                  '-w',  WORDS,
                  '-a', '32',
                  '-b', '500',
                  '-c', '500',
                  '-v', '500',
                  '-l', f'{lang}']

    apply_prpe = ['python', 'prpe/prpe6/apply_prpe.py', 
                  '-i',  src,
                  '-o',  out,
                  '-p',  PREFIXES,
                  '-r',  ROOTS, 
                  '-s',  SUFFIXES,
                  '-t',  POSTFIXES,
                  '-u',  ENDINGS,
                  '-w',  WORDS,
                  '-d', '0000',
                  '-m', '0',
                  '-n', '0',
                  '-l', f'{lang}']

    if train:
        subprocess.run(train_prpe)
    if apply:
        subprocess.run(apply_prpe)

def prpe_multi(src, out, iters, lang, FOLDER, train=True, apply=True):

    PRPE_MULTI_TEMP = f'model_opennmt/run' + FOLDER + f'/prpe_mul_temp.{lang}.txt'
    prpe(src, out, train, apply)

    for i in range(iters):
        print(f"Iteration {i}")
        copy_content(out, PRPE_MULTI_TEMP)
        prpe(PRPE_MULTI_TEMP, out, lang, train, apply)