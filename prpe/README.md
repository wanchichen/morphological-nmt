# PRPE (Prefix-Root-Postfix-Encoding) Segmenter

This repository contains Python (2 and 3) text segmentation scripts for machine translation.

## The main principles

  - Performs close-to-morphological segmentation
  - For the present, tuned for English and Latvian languages
  - Requires minor adaptation for using in other languages:
  -- small source code changes
  -- tuning of hyperparameters
  - to support open-vocabulary (in machine translation), segmented texts should be post-processed (e.g., using [BPE])

## Usage instructions

PRPE is used in the following way:
  - Learning phase (files of potential segments produced): learn_prpe.py
  - Segmentation phase (using produced files of the previous phase): apply_prpe.py
  - Removing segmentation: unprocess_prpe.py

### Phase #1. Learning ([learn_prpe.py])

During this phase several 'code' files are produced from the {corpus} representing building blocks for the segmentation:
  - {prefixes}
  - {roots}
  - {suffixes}
  - {postfixes} (in the lastest version this particular file is redundant for segmentation but is left as legacy and for the purpose to potentially assist in hyperparamter adaptation)
  - {endings}
  - vocabulary of most frequent {words} to avoid segmentation

**Terminology of word parts in the context of this program**

Word "unbelievables" consists of:
 * prefix: **un**
 * root: **believ**
 * postfix: **ables**

where postfix "ables" consists of:
 * suffix: **abl**
 * ending: **es**


**Running the learning script**:

```sh
prpe6/learn_prpe.py -i {corpus} -p {prefixes} -r {roots} -s {suffixes} -t {postfixes} -u {endings} -w {words} -a {prefix rate} -b {suffix rate} -c {postfix rate} -v {vocabulary size} -l {language}
```

***where***:
  - prefix rate: how many prefixes to collect (greater than 1 means exact number, less means percentage)
  - suffix rate: how many suffixes to collect (greater than 1 means exact number, less means percentage)
  - postfix rate: how many postfixes to collect (greater than 1 means exact number, less means percentage) (in the latest version this particular parameter is redundant)
  - vocabulary size: how many the most frequent words to store to avoid segmentations for them (in order to reduce number of segments)
  - language: for the present, only 'lv' and 'en' are acceptable; otherwise 'en' scripts will be run

All the rates (prefix, suffix, postfix, vocabulary) should be experimentally tuned. Fitness conditions for roots and endings (not represented in parameters) are hardcoded.

**Sample configuration** used for **Latvian** (see produced files in 'codefiles-lv' directory):
```sh
prpe6/learn_prpe.py -i corpus.lv -p prefixes.lv -r roots.lv -s suffixes.lv -t postfixes.lv -u endings.lv -w words.lv -a 32 -b 1000 -c 0.1 -v 5000 -l lv
```

**Sample configuration** used for **English** (see produced files in 'codefiles-en' directory):
```sh
prpe6/learn_prpe.py -i corpus.en -p prefixes.en -r roots.en -s suffixes.en -t postfixes.en -u endings.en -w words.en -a 32 -b 200 -c 180 -v 5000 -l en
```

Just for a brief insight; the first 10 English prefixes collected in the learning phase (in file {prefixes}):
 * re 1
 * un 2
 * de 3
 * in 4
 * dis 5
 * mis 6
 * sub 7
 * over 8
 * ac 9
 * im 10


### Phase #2. Segmentation ([apply_prpe.py])

During this phase, input text is segmented using 'code' files produced in the learning phase.

**Running the segmentation script**:

```sh
prpe6/apply_prpe.py -i {input text} -o {output text} -p {prefixes} -r {roots} -s {suffixes} -t {postfixes} -u {endings} -w {words} -l {language} -d {segmentation mode} -m {segmentation marker} -n {uppercase marker}
```

***where***:
  - prefixes, roots, suffixes, postfixes, endings: files produced in the learning phase
  - language: for the present, only 'lv' and 'en' are acceptable
  - segmentation mode -- to determine segmentation optimization, processing words with uppercase and usage of segmentation markers (see below)
  - segmentation marker -- a character or sequence of character to mark segments to constitute words (if sequence of digits, then is converted to the character represented by that number, default '9474')
  - upercase marker -- a character or sequence of character to mark next word as starting with uppercase (if sequence of digits, then is converted to the character represented by that number, default '9553')

##### Segmentation mode

Segmentation mode is a positive integer number up to 4 digits in the form ABCC, where
  - A: optimization mode
  - B: uppercase mode
  - CC: marking mode

In the next examples the text *"Unbelievable salespersons"* will be used, "/" -- segmentation marker, "|" -- uppercase marker.

**A: Optimization mode**
Optimization mode is intended to reduce number of segments, thus the length of sequence of segments.

Value 0 -- no optimization:
*Un/ believ/ able sal/ es/ person/ s*

Value 1 -- small optimization:
*Un/ believ/ able sales/ persons*

Value 2 -- full optimization:
*Unbeliev/ able sales/ person/ s*

**B: Uppercase mode**
Uppercase mode converts word starting with uppercase and the rest symbols in lowercase to lowercase with putting uppercase marker before it:

Value 0 -- uppercase processing ON:
*| unbeliev/ able sales/ person/ s*

Value 1 -- uppercase processing OFF:
*Unbeliev/ able sales/ person/ s*

**C: Marking mode**
Although there are modes 0, 1, 2, 3 available, we suggest using mode 3 (marker indicates that the next segment is of the same word)

Examples of valid segmentation modes: 3, 103, 2103, 1003

**Sample configuration** of segmentation used for **English** (paramaters for markers omitted):
```sh
prpe6/apply_prpe.py -i input.en -o output.en -p prefixes.en -r roots.en -s suffixes.en -t postfixes.en -u endings.en -w words.en -l en -d 2103
```

### 3. Removing segmentation ([unprocess_prpe.py])

During this operation, a segmented text is coverted back to a normal text:

```sh
prpe6/unprocess_prpe.py -i {input text} -o {output text} -d {segmentation mode} -m {segmentation marker} -n {uppercase marker}
```

For example:
```sh
prpe6/unprocess_prpe.py -i input.en -o output.en -d 2103 -m / -n |
```
will convert text
*"| un/ believ/ able sales/ persons"*
back into
*"Unbelievable salespersons"*

### 4. Summary of the best configurations for NMT discovered by far

**English:**
 - Prefix rate a = 32
 - Suffix rate b = 200
 - Vocabulary size v = 5000 (or less if NMT system not sensitive to long sequences)
 - Segmentation mode d = 2003

**Latvian:**
 - Prefix rate a = 32
 - Suffix rate b = 1000
 - Vocabulary size v = 5000 (or less if NMT system not sensitive to long sequences)
 - Segmentation mode d = 2003

### 5. Adaptation to other languages

To make the adaptation, it is unfortunately required that you have some understanding about the language.

A brief activity list for adaptation:
  - in [prpe.py], add the language specific information to the function "add_heuristics" which can eventually cause creation of several language specific function (such as "is_good_root")
  - run learning phase with looser hyperparameters for code files, i.e., "-a 1000 -b 0.1 -c 0.1"
  - go through the code files (prefixes, postfixes, suffixes, endings) to determine the number of words parts to be collected for segmentation, and eventually to additionally adjust the language specific source code.

## Publications

Jānis Zuters, Gus Strazds, and Kārlis Immers. Semi-automatic Quasi-morphological Word Segmentation for Neural Machine Translation: 13th International Baltic Conference, DB&IS 2018, Trakai, Lithuania, July 1-4, 2018, Proceedings.

## Acknowledgements

The research has been supported by the European Regional Development Fund within the research project ”Neural Network Modelling for Inflected Natural Languages” No. 1.1.1.1/16/A/215, and the Faculty of Computing, University of Latvia.

   [BPE]: <https://github.com/rsennrich/subword-nmt>
   [learn_prpe.py]: <https://github.com/zuters/prpe/prpe6/learn_prpe.py>
   [apply_prpe.py]: <https://github.com/zuters/prpe/prpe6/apply_prpe.py>
   [unprocess_prpe.py]: <https://github.com/zuters/prpe/prpe6/unprocess_prpe.py>
   [prpe.py]: <https://github.com/zuters/prpe/prpe6/prpe.py>
