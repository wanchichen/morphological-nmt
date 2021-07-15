from sacremoses import MosesTruecaser, MosesTokenizer

trainer = '../data/en_mr/test.en2mr.en'

# Train a new truecaser from a 'big.txt' file.
mtr = MosesTruecaser()
mtok = MosesTokenizer(lang='en')

tokenized_docs = [mtok.tokenize(line) for line in open(trainer, 'r', encoding='utf8')]
mtr.train(tokenized_docs, save_to='token_model/big.truecasemodel')

with open('../data/mr2en.txt', 'r', encoding='utf8') as test_file, open('../data/mr2en_true.txt', 'w', encoding='utf8') as out_file:
    lines = test_file.readlines()
    for line in lines:

        toks = mtr.truecase(line)
        if len(toks) > 0:
            string = toks[0]
            toks[0] =  string[0].upper() + string[1:]
            
        out_file.write(" ".join(toks))
        out_file.write('\n')

    test_file.close()
    out_file.close()
