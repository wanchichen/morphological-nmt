
def count(file_name):

    length_dict = dict()
    average_length = 0
    max_length = 0
    counter = 0
    threshold = 200

    with open(file_name, 'r', encoding='utf8') as in_file:
        lines = in_file.readlines()
        for line in lines:
            line = line.split()
            #print(line)
            length = len(line)

            if length in length_dict:
                length_dict[length] += 1
            else:
                length_dict[length] = 1

            average_length += length
            max_length = max(max_length, length)
            if length < threshold:
                counter += 1

        average_length /= len(lines)
        
        for i in range(max_length):
            if i in length_dict:
                print(i, length_dict[i])

        print(f"AVERAGE: {average_length}")
        print(f"LINES LESS THAN {threshold} TOKENS: {counter}")

def analyze_vocab(train, valid, test):
    with open(train, 'r', encoding='utf8') as train_file, open(valid, 'r', encoding='utf8') as valid_file, open(test, 'r', encoding='utf8') as test_file:
        train_lines = train_file.readlines()
        valid_lines = valid_file.readlines()
        test_lines = test_file.readlines()

        train_dict = dict()
        valid_dict = dict()
        test_dict = dict()

        valid_common = 0
        test_common = 0
        for line in train_lines:
            line = line.split()
            for word in line:
                if word in train_dict:
                    train_dict[word] += 1
                else:
                    train_dict[word] =1
        for line in valid_lines:
            line = line.split()
            for word in line:
                if word in valid_dict:
                    valid_dict[word] += 1
                else:
                    valid_dict[word] =1
        for line in test_lines:
            line = line.split()
            for word in line:
                if word in test_dict:
                    test_dict[word] += 1
                else:
                    test_dict[word] =1
        for word in train_dict:
            if word in valid_dict:
                valid_common += 1
            if word in test_dict:
                test_common += 1
        print(f'{valid_common} in {len(valid_dict)} ({float(valid_common) / float(len(valid_dict))}) of validation words appear in train. ')
        print(f'{test_common} in {len(test_dict)} ({float(test_common) / float(len(test_dict))}) of test words appear in train. ')

#count("processed_train.id.txt")
#analyze_vocab('../data/en_mr/train.mr.txt', '../data/en_mr/validate.mr.txt', '../../loresmt-2021/test/test.mr2en.mr')