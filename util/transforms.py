import os
import random
def append_noisy(domain, name, in_lang, out_lang, src_tok, tgt_tok):
    src_noisy = f'data/{domain}/{name}.{in_lang}.txt'
    tgt_noisy = f'data/{domain}/{name}.{out_lang}.txt'
    with open(src_tok, 'r', encoding='utf8') as src_in, open(tgt_tok, 'r', encoding='utf8') as tgt_in, open(src_noisy, 'r', encoding='utf8') as src_noisy_in, open(tgt_noisy, 'r', encoding='utf8') as tgt_noisy_in:
        src_noisy_lines = src_noisy_in.readlines()
        tgt_noisy_lines = tgt_noisy_in.readlines()
        src_lines = src_in.readlines()
        tgt_lines = tgt_in.readlines()

        for i in range(len(src_noisy_lines)):
            if src_noisy_lines[i] not in src_lines and tgt_noisy_lines[i] in tgt_lines:
                src_lines.append(src_noisy_lines[i])
                tgt_lines.append(tgt_noisy_lines[i])

        src_lines.extend(src_noisy_lines)
        tgt_lines.extend(tgt_noisy_lines)

    with open(src_tok, 'w', encoding='utf8') as src_out, open(tgt_tok, 'w', encoding='utf8') as tgt_out:
        for line in src_lines:
            src_out.write(line)
        for line in tgt_lines:
            tgt_out.write(line)

        src_out.close()
        tgt_out.close()

def shuffle_lines(src, tgt):
    src_shuffled = list()
    tgt_shuffled = list()

    for i in range(len(src)):
        rand = int(random.random() * len(src))
        src_shuffled.append(src[rand])
        tgt_shuffled.append(tgt[rand])

        src.pop(rand)
        tgt.pop(rand)

    return src_shuffled, tgt_shuffled

def postprocess_multilingual(output):
    with open(output, 'r', encoding='utf8') as in_file:
        lines = output.readlines()
    with open(output, 'w', encoding='utf8') as out_file:
        for line in lines:
            out_file.write(line[6:])
        out_file.close()
        
def make_multilingual(domain1, domain2):
    folder = f'../data/{domain1}+{domain2}'
    if not os.path.isdir(folder):
        os.mkdir(folder)

    domains = [domain1, domain2]
    for domain in domains:
        lang1, lang2 = domain.split('_')
        with open(f'../data/{domain}/train.{lang1}.txt', 'r', encoding='utf8') as file_1, open(f'../data/{domain}/train.{lang2}.txt', 'r', encoding='utf8') as file_2:
            src = file_1.readlines()
            tgt = file_2.readlines()

            src_out = list()
            tgt_out = list()
            for i in range(len(src)):
                if i % 1000 == 0:
                    print(i)
                src_out.append(f'{lang1}-{lang2}: {src[i]}')
                src_out.append(f'{lang2}-{lang1}: {tgt[i]}')
                tgt_out.append(tgt[i])
                tgt_out.append(src[i])

        src_out, tgt_out = shuffle_lines(src_out, tgt_out)

        with open(f'{folder}/train.m1.txt', 'a+', encoding='utf8') as out_1, open(f'{folder}/train.m2.txt', 'a+', encoding='utf8') as out_2:
            for i in range(len(src_out)):
                out_1.write(src_out[i]) 
                out_2.write(tgt_out[i])

            out_1.close()
            out_2.close()

if __name__ == '__main__':
    make_multilingual('en_ga', 'en_mr') 
