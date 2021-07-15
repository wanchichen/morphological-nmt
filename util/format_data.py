
def fix_file(input):

    with open(input, 'r', encoding='utf8') as in_file, open(f"{input}.fixed", 'w', encoding='utf8') as out_file:
        lines = in_file.readlines()

        for line in lines:
            line = line.replace("’", "'")
            line = line.replace("‘", "'")

            out_file.write(line)

        in_file.close()
        out_file.close()

#fix_file("../data/train.id.txt")

def filter_same(train, valid):
    with open(train, 'r', encoding='utf8') as train_file, open(valid, 'r', encoding='utf8') as val_file:
        train_lines = train_file.readlines()
        val_lines = val_file.readlines()
        num_same = 0

        for line in train_lines:
            line = line.split()

        for line in val_lines:
            line = line.split()

        for line in val_lines:
            if line in train_lines:
                num_same += 1
                train_lines.remove(line)
                #print(line)
    with open(f'{train}.fixed', 'w', encoding='utf8' ) as out_file:
        for line in train_lines:
            out_file.write(line)

        out_file.close()
    print(num_same)

def find_diff(en_train, en_val, mr_train, mr_val):
    with open(en_train, 'r', encoding='utf8') as en_train_file, open(en_val, 'r', encoding='utf8') as en_val_file, open(mr_train, 'r', encoding='utf8') as mr_train_file, open(mr_val, 'r', encoding='utf8') as mr_val_file:
        en_train = en_train_file.readlines()
        en_val = en_val_file.readlines()
        mr_train = mr_train_file.readlines()
        mr_val = mr_val_file.readlines()
        en_idxs = list()
        mr_idxs = list()
        for line in en_val:
            if line in en_train:
                en_idxs.append(en_train.index(line))

        for line in mr_val:
            if line in mr_train:
                mr_idxs.append(mr_train.index(line))

        for idx in en_idxs:
            en_train.pop(idx)
            mr_train.pop(idx)
        print(len(en_train))
        print(len(mr_train))
    with open('../data/en_mr/train.en.txt', 'w', encoding='utf8' ) as out_file:
        for line in en_train:
            out_file.write(line)

        out_file.close()

    with open('../data/en_mr/train.mr.txt', 'w', encoding='utf8' ) as out_file:
        for line in mr_train:
            out_file.write(line)

        out_file.close()

#filter_same('../data/en_mr/train.en.txt', '../data/en_mr/validate.en.txt')
find_diff('../data/en_mr/train.en.txt', '../data/en_mr/validate.en.txt', '../data/en_mr/train.mr.txt', '../data/en_mr/validate.mr.txt')