import subprocess
import os
import sacrebleu
import argparse

from datetime import datetime
from util.util import make_run_folder
from util.tokenization import tokenization, detokenization
from util.segmentation import bpe, post_process_bpe, unigram, prpe, prpe_multi
from util.nmt import create_train_yaml, create_vocab_yaml
from util.transforms import append_noisy, postprocess_multilingual

NOW = datetime.now()

parser = argparse.ArgumentParser(description='Specify pipeline flags')
parser.add_argument('--src_segment_type', type=str, default=None, help='prpe_bpe, or none, or prpe, or bpe, or prpe_multi_N or unigram')
parser.add_argument('--tgt_segment_type', type=str, default=None, help='prpe_bpe, or none, or prpe, or bpe, or prpe_multi_N or unigram')
parser.add_argument('--model_type', type=str, default='rnn', help='rnn or transformer')
parser.add_argument('--in_lang', type=str, default='qz', help='qz or id or ga')
parser.add_argument('--out_lang', type=str, default='es', help='es or en')
parser.add_argument('--domain', type=str, default='religious', help='dataset folder name')
parser.add_argument('--save_steps', type=int, default=10000, help='saves every x steps')
parser.add_argument('--validate_steps', type=int, default=2000, help='opnenmt validates model every x steps')
parser.add_argument('--train_steps', type=int, default=100000, help='trains model for x steps')
parser.add_argument('--batch_size', type=int, default=64, help='batch size')
parser.add_argument('--src_tokenization', type=str, default='moses', help='moses, none, custom')
parser.add_argument('--tgt_tokenization', type=str, default='moses', help='moses, none, custom')
parser.add_argument('--filter_too_long', type=int, default=-1, help='max token length, -1 for no filtering')
parser.add_argument('--load_saved', type=str, default=None, help='load from saved model')
parser.add_argument('--vocab_folder', type=str, default=None, help='corpora to build vocab from')
parser.add_argument('--src_token_lang', type=str, default=None, help='tokenizer language')
parser.add_argument('--tgt_token_lang', type=str, default=None, help='tokenizer language')
parser.add_argument('--noisy_data', type=bool, default=None, help= 'include noisy data')
parser.add_argument('--multilingual', type=bool, default=None, help= 'data is multilingual')
opt = parser.parse_args()

in_lang = opt.in_lang
out_lang = opt.out_lang
domain = opt.domain

# this naming convention doesnt work on windows
FOLDER = f'-{domain}-{opt.model_type}-{opt.src_segment_type}-{in_lang}-{opt.tgt_segment_type}-{out_lang}-{NOW.strftime("%m_%d_%Y_%H_%M_%S")}'

SRC_INPUT = f'data/{domain}/train.{in_lang}.txt'
TGT_INPUT = f'data/{domain}/train.{out_lang}.txt'

SRC_PROCESSED = f'model_opennmt/run' + FOLDER  +f'/processed_train.{in_lang}.txt'
TGT_PROCESSED = f'model_opennmt/run' + FOLDER + f'/processed_train.{out_lang}.txt'

SRC_VLD_PROCESSED = f'model_opennmt/run' + FOLDER  +f'/processed_validate.{in_lang}.txt'
TGT_VLD_PROCESSED = f'model_opennmt/run' + FOLDER + f'/processed_validate.{out_lang}.txt'

SRC_TEST_PROCESSED = f'model_opennmt/run' + FOLDER  +f'/processed_test.{in_lang}.txt'
TGT_TEST_PROCESSED = f'model_opennmt/run' + FOLDER + f'/processed_test.{out_lang}.txt'

SRC_TEST = f'data/{domain}/test.{in_lang}.txt'
TGT_TEST = f'data/{domain}/test.{out_lang}.txt'

SRC_VLD = f'data/{domain}/validate.{in_lang}.txt'
TGT_VLD = f'data/{domain}/validate.{out_lang}.txt'

OUTPUT = f'model_opennmt/run' + FOLDER + f'/output.{out_lang}.txt'

DETOKEN_OUTPUT = f'model_opennmt/run' + FOLDER + f'/detoken_output.{out_lang}.txt'
DETOKEN_TGT = f'model_opennmt/run' + FOLDER + f'/detoken.{out_lang}.txt'

PIPELINE = 'model_opennmt/run' + FOLDER + '/pipeline.yaml'

MODEL = f'model_opennmt/run' + FOLDER + f'/subword_model.{in_lang}.txt'

if opt.vocab_folder is not None:
    SRC_TRAIN_VOCAB = f'data/{opt.vocab_folder}/train.{in_lang}.txt'
    TGT_TRAIN_VOCAB = f'data/{opt.vocab_folder}/train.{out_lang}.txt'
    SRC_VLD_VOCAB = f'data/{opt.vocab_folder}/validate.{in_lang}.txt'
    TGT_VLD_VOCAB = f'data/{opt.vocab_folder}/validate.{out_lang}.txt'
    VOCAB_CFG = 'model_opennmt/run' + FOLDER + '/vocab.yaml'

def tokenization_process():

    src_token = in_lang if opt.src_token_lang is None else opt.src_token_lang
    tgt_token = out_lang if opt.tgt_token_lang is None else opt.tgt_token_lang

    tokenization(TGT_INPUT, TGT_PROCESSED, tgt_token, opt.tgt_tokenization)
    tokenization(TGT_VLD, TGT_VLD_PROCESSED, tgt_token, opt.tgt_tokenization)
    tokenization(TGT_TEST, TGT_TEST_PROCESSED, tgt_token, opt.tgt_tokenization)
    tokenization(SRC_INPUT, SRC_PROCESSED, src_token, opt.src_tokenization)
    tokenization(SRC_VLD, SRC_VLD_PROCESSED, src_token, opt.src_tokenization)
    tokenization(SRC_TEST, SRC_TEST_PROCESSED, src_token, opt.src_tokenization)

def detokenization_process():

    tgt_token = out_lang if opt.tgt_token_lang is None else opt.tgt_token_lang
    if opt.multilingual is not None:
            postprocess_multilingual(OUTPUT)

    detokenization(OUTPUT, DETOKEN_OUTPUT, tgt_token)
    detokenization(TGT_TEST_PROCESSED, DETOKEN_TGT, tgt_token)

def segment_process(segment_type, lang):

    PROCESSED = f'model_opennmt/run' + FOLDER  +f'/processed_train.{lang}.txt'
    VLD_PROCESSED = f'model_opennmt/run' + FOLDER  +f'/processed_validate.{lang}.txt'
    TEST_PROCESSED = f'model_opennmt/run' + FOLDER  +f'/processed_test.{lang}.txt'

    BPE_IN = f'model_opennmt/run' + FOLDER + f'/bpe_in.{in_lang}.txt'
    BPE_OUT = f'model_opennmt/run' + FOLDER + f'/bpe_out.{in_lang}.txt'

    VLD_BPE_IN = f'model_opennmt/run' + FOLDER + f'/vld_bpe_in.{in_lang}.txt'
    VLD_BPE_OUT = f'model_opennmt/run' + FOLDER + f'/vld_bpe_out.{in_lang}.txt'

    TEST_BPE_IN = f'model_opennmt/run' + FOLDER + f'/test_bpe_in.{in_lang}.txt'
    TEST_BPE_OUT = f'model_opennmt/run' + FOLDER + f'/test_bpe_out.{in_lang}.txt'

    if segment_type is None:
        return
    
    if segment_type == 'prpe':
        # Segment source train
        prpe(PROCESSED, BPE_OUT, lang, FOLDER)
        post_process_bpe(PROCESSED, BPE_OUT)

        # Segment source validation
        prpe(VLD_PROCESSED, VLD_BPE_OUT, lang, FOLDER , train=False, apply=True)
        post_process_bpe(VLD_PROCESSED, VLD_BPE_OUT)

        # Segment source test
        prpe(TEST_PROCESSED, TEST_BPE_OUT, lang, FOLDER , train=False, apply=True)
        post_process_bpe(TEST_PROCESSED,TEST_BPE_OUT)

    if  'prpe_multi' in segment_type:

        iters = int(segment_type[11:])

        # Segment source train
        prpe_multi(PROCESSED, BPE_OUT, iters, lang, FOLDER)
        post_process_bpe(PROCESSED, BPE_OUT)

        # Segment source validation
        prpe_multi(VLD_PROCESSED, VLD_BPE_OUT, iters, lang, FOLDER, train=False, apply=True)
        post_process_bpe(VLD_PROCESSED, VLD_BPE_OUT)

        # Segment source test
        prpe_multi(TEST_PROCESSED, TEST_BPE_OUT, iters, lang, FOLDER, train=False, apply=True)
        post_process_bpe(TEST_PROCESSED, TEST_BPE_OUT)

    if segment_type == 'prpe_bpe':
    
        # Segment source train
        prpe(PROCESSED, BPE_IN, lang, FOLDER)
        bpe(BPE_IN, PROCESSED, lang, FOLDER)

        # Segment source validation
        prpe(VLD_PROCESSED, VLD_BPE_IN, lang, FOLDER, train=False, apply=True)
        bpe(VLD_BPE_IN, VLD_PROCESSED, lang, FOLDER, train=False)

        # Segment source test
        prpe(TEST_PROCESSED, TEST_BPE_IN, lang, FOLDER, train=False, apply=True)
        bpe(TEST_BPE_IN, TEST_PROCESSED, lang, FOLDER, train=False)

    if segment_type == 'bpe':
        # Segment source train
        bpe(PROCESSED, PROCESSED, lang, FOLDER)

        # Segment source validation
        bpe(VLD_PROCESSED, VLD_PROCESSED, lang, FOLDER, train=False)

        # Segment source test
        bpe(TEST_PROCESSED, TEST_PROCESSED, lang, FOLDER, train=False)

    if segment_type == 'unigram':
        unigram(PROCESSED, PROCESSED, MODEL)
        unigram(VLD_PROCESSED, VLD_PROCESSED, MODEL , train=False)
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

def train():

    # Build vocabulary
    if opt.vocab_folder is not None:
        build = ['onmt_build_vocab', '-config', VOCAB_CFG]
    else:
        build = ['onmt_build_vocab', '-config', PIPELINE]
    subprocess.run(build)

    # Train model
    train = ['onmt_train', '-config', PIPELINE]
    subprocess.run(train)

def test():

    bleu_scores = dict()
    chrf_scores = dict()
    i = opt.train_steps

    model_name = f'/model_step_{i}.pt'

    translate = ['onmt_translate', '-model', 'model_opennmt/run' + FOLDER + model_name, '-src', SRC_TEST_PROCESSED, '-output', OUTPUT, '--replace_unk']
    print(f'Translating {opt.domain} {opt.model_type} + {opt.src_segment_type}: {in_lang}-> {opt.tgt_segment_type}: {out_lang} at step {i}', flush=True)
    subprocess.run(translate)
    detokenization_process()
    bleu_scores[i], chrf_scores[i] = metrics()


def pipeline():

    # Make run folder
    make_run_folder(FOLDER)

    # Generate yaml
    create_train_yaml(opt, SRC_PROCESSED, TGT_PROCESSED, SRC_VLD_PROCESSED, TGT_VLD_PROCESSED, FOLDER, PIPELINE)
    if opt.vocab_folder is not None:
        create_vocab_yaml(opt, SRC_TRAIN_VOCAB, TGT_TRAIN_VOCAB, SRC_VLD_VOCAB, TGT_VLD_VOCAB, FOLDER, VOCAB_CFG)

    # Tokenization pre-processing
    tokenization_process()

    # Segment texts
    segment_process(opt.src_segment_type, in_lang)
    segment_process(opt.tgt_segment_type, out_lang)

    if opt.noisy_data is not None:
        append_noisy(domain, opt.noisy_data, in_lang, out_lang, SRC_PROCESSED, TGT_PROCESSED)

    # Training
    train()

    # Testing
    test()

if __name__ == '__main__':
    pipeline()
