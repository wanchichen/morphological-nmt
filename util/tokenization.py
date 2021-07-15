from sacremoses import MosesTokenizer, MosesDetokenizer
from .segmentation import process_unigram_list
import sentencepiece as spm

def tokenization(source, output, lang, method):
    if method == 'moses':
        moses_tokenization(source, output, lang)
    elif method == 'none':
        moses_tokenization(source, output, lang, False)
    else:
        custom(source, output, method)

def moses_tokenization(source, output, lang, moses=True):
    tokenizer = MosesTokenizer(lang=lang)

    with open(source, encoding='utf8') as src_input, open(output, 'w', encoding='utf8') as src_out:
        src_arr = src_input.readlines()

        for src_line in src_arr:

            if moses:
                src_tok = tokenizer.tokenize(src_line)

                src_w = " ".join(src_tok)

                # Lower case the strings
                #src_w = src_w.lower()

                src_out.write(src_w)

                src_out.write("\n")

            else:
                src_out.write(src_line)

        src_out.close()
        src_input.close()

def detokenization(source, out, lang):
    detokenizer = MosesDetokenizer(lang=lang)

    with open(source, encoding='utf8') as output, open(out, 'w', encoding='utf8') as detoken_out:
        output_arr = output.readlines()

        for line in output_arr:
            tokens = line.split(' ')

            detoken = detokenizer.detokenize(tokens)

            detoken_out.write(detoken)
            detoken_out.write("\n")

        output.close()
        detoken_out.close()

def custom(src, out, model_name):

    with open(src, 'r', encoding='utf8') as in_file:
        src = in_file.readlines()
    sp = spm.SentencePieceProcessor(model_file=f'util/token_model/{model_name}')
    lines = sp.encode(src, out_type=str)

    with open(out, 'w', encoding='utf8') as out_file:
        for line in lines:
            line = f'{process_unigram_list(line)}\n'
            out_file.write(line)
        out_file.close()