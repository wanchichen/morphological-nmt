import subprocess
import os
import sacrebleu
import argparse

from datetime import datetime
from util.tokenization import tokenization, detokenization
from util.segmentation import bpe, post_process_bpe, unigram, prpe, prpe_multi
from util.transforms import postprocess_multilingual

NOW = datetime.now()

parser = argparse.ArgumentParser(description='Specify pipeline flags')
parser.add_argument('--src_segment_type', type=str, default=None, help='prpe_bpe, or none, or prpe, or bpe, or prpe_multi_N or unigram')
parser.add_argument('--tgt_segment_type', type=str, default=None, help='prpe_bpe, or none, or prpe, or bpe, or prpe_multi_N or unigram')
parser.add_argument('--in_lang', type=str, default='qz', help='qz or id or ga')
parser.add_argument('--out_lang', type=str, default='es', help='es or en')
parser.add_argument('--save_steps', type=int, default=100000, help='model to evaluate')
parser.add_argument('--src_tokenization', type=str, default='moses', help='moses, none, custom')
parser.add_argument('--tgt_tokenization', type=str, default='moses', help='moses, none, custom')
parser.add_argument('--src_token_lang', type=str, default=None, help='tokenizer language')
parser.add_argument('--tgt_token_lang', type=str, default=None, help='tokenizer language')
parser.add_argument('--multilingual', type=bool, default=None, help= 'data is multilingual')
parser.add_argument('--folder', type=str, default='run', help='run folder')
parser.add_argument('--eval', type=str, default=None, help='file to eval against with metrics')
parser.add_argument('--input', type=str, default='input.txt', help='to be translated')

opt = parser.parse_args()

in_lang = opt.in_lang
out_lang = opt.out_lang

# this naming convention doesnt work on windows
FOLDER = opt.folder

SRC_TEST_PROCESSED = f'model_opennmt/' + FOLDER  +f'/processed_test.{in_lang}.txt'
TGT_TEST_PROCESSED = f'model_opennmt/' + FOLDER + f'/processed_test.{out_lang}.txt'

SRC_TEST = opt.input

if opt.eval is not None:
    TGT_TEST = opt.eval

OUTPUT = f'model_opennmt/' + FOLDER + f'/output.{out_lang}.txt'

DETOKEN_OUTPUT = f'model_opennmt/' + FOLDER + f'/detoken_output.{out_lang}.txt'
DETOKEN_TGT = f'model_opennmt/' + FOLDER + f'/detoken.{out_lang}.txt'

MODEL = f'model_opennmt/' + FOLDER + f'/subword_model.{in_lang}.txt'

def tokenization_process():

    src_token = in_lang if opt.src_token_lang is None else opt.src_token_lang
    tgt_token = out_lang if opt.tgt_token_lang is None else opt.tgt_token_lang

    tokenization(SRC_TEST, SRC_TEST_PROCESSED, src_token, opt.src_tokenization)
    if opt.eval is not None:
        tokenization(TGT_TEST, TGT_TEST_PROCESSED, tgt_token, opt.tgt_tokenization)
    

def detokenization_process():

    tgt_token = out_lang if opt.tgt_token_lang is None else opt.tgt_token_lang
    if opt.multilingual is not None:
            postprocess_multilingual(OUTPUT)

    detokenization(OUTPUT, DETOKEN_OUTPUT, tgt_token)
    if opt.eval is not None:
        detokenization(TGT_TEST_PROCESSED, DETOKEN_TGT, tgt_token)

def segment_process(segment_type, lang):

    TEST_PROCESSED = f'model_opennmt/run' + FOLDER  +f'/processed_test.{lang}.txt'
    TEST_BPE_IN = f'model_opennmt/run' + FOLDER + f'/test_bpe_in.{in_lang}.txt'
    TEST_BPE_OUT = f'model_opennmt/run' + FOLDER + f'/test_bpe_out.{in_lang}.txt'

    if segment_type is None:
        return
    
    if segment_type == 'prpe':

        # Segment source test
        prpe(TEST_PROCESSED, TEST_BPE_OUT, lang, FOLDER , train=False, apply=True)
        post_process_bpe(TEST_PROCESSED,TEST_BPE_OUT)

    if  'prpe_multi' in segment_type:

        iters = int(segment_type[11:])

        # Segment source test
        prpe_multi(TEST_PROCESSED, TEST_BPE_OUT, iters, lang, FOLDER, train=False, apply=True)
        post_process_bpe(TEST_PROCESSED, TEST_BPE_OUT)

    if segment_type == 'prpe_bpe':

        # Segment source test
        prpe(TEST_PROCESSED, TEST_BPE_IN, lang, FOLDER, train=False, apply=True)
        bpe(TEST_BPE_IN, TEST_PROCESSED, lang, FOLDER, train=False)

    if segment_type == 'bpe':

        # Segment source test
        bpe(TEST_PROCESSED, TEST_PROCESSED, lang, FOLDER, train=False)

    if segment_type == 'unigram':

        unigram(TEST_PROCESSED, TEST_PROCESSED, MODEL , train=False)

def metrics():
    
    with open(DETOKEN_OUTPUT, encoding='utf8') as output, open(DETOKEN_TGT, encoding='utf8') as reference:
        output_arr = output.readlines()
        ref_arr = [reference.readlines()]

        bleu = sacrebleu.corpus_bleu(output_arr, ref_arr).score
        chrf = sacrebleu.corpus_chrf(output_arr, ref_arr).score

        print(f'BLEU SCORE: {bleu}')
        print(f'CHRF SCORE: {chrf}')

        return bleu, chrf

def test():

    bleu_scores = dict()
    chrf_scores = dict()
    i = opt.save_steps

    best = (0,0)
    model_name = f'/model_step_{i}.pt'

    translate = ['onmt_translate', '-model', 'model_opennmt/' + FOLDER + model_name, '-src', SRC_TEST_PROCESSED, '-output', OUTPUT, '--replace_unk']
    print(f'Translating {opt.src_segment_type}: {in_lang}-> {opt.tgt_segment_type}: {out_lang} at step {i}', flush=True)
    subprocess.run(translate)
    detokenization_process()

    if opt.eval is not None:
        bleu_scores[i], chrf_scores[i] = metrics()

        if bleu_scores[i] > best[0]:
            best = bleu_scores[i], chrf_scores[i]

def pipeline():

    # Tokenization pre-processing
    tokenization_process()

    # Segment texts
    segment_process(opt.src_segment_type, in_lang)
    if opt.eval is not None:
        segment_process(opt.tgt_segment_type, out_lang)

    # Testing
    test()

if __name__ == '__main__':
    pipeline()
