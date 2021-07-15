# Morphologically-Guided Neural Machine Translation

This is the code used for our LoResMT 2021 Paper [Morphologically-Guided Segmentation For Translation of Agglutinative Low-Resource Languages](). This repository contains the implementations of the subword segmentation algorithms we used and the cleaned Quechua dataset, along with the pipeline of how our model is run.

## Dependencies
```
pip install requirements.txt
```

## PRPE
 - Originally from [Semi-automatic Quasi-morphological Word Segmentation for Neural Machine Translation](https://link.springer.com/chapter/10.1007/978-3-319-97571-9_23)
 - The base code for PRPE was taken from https://github.com/zuters/prpe.
 - Samples of the heuristics, separated out from the main algorithm for convenience, can be accessed below:
    -  [Quechua Heuristic](https://github.com/wanchichen/morphological-nmt/blob/main/qz_heuristic.py) 
    -  [Indonesian Heuristic](https://github.com/wanchichen/morphological-nmt/blob/main/id_heuristic.py)
    -  The generic heuristic (the general parameters of PRPE) can be found [here](https://github.com/smaint/PRPE-Translator/blob/main/generic_heuristic.py)

## Datasets
 - The data we cleaned is found in `data/cleaned_source`. `test.es.txt` and `test.qz.txt` were created by random shuffling of all of the parallel lines. The source data from Annette Rios can be found [here](https://github.com/a-rios/squoia).
 - The Religious, News, and General Indonesian-English datasets from [Benchmarking Multidomain English-Indonesian Machine Translation](https://www.aclweb.org/anthology/2020.bucc-1.6.pdf) can be found at their [repository here](https://github.com/gunnxx/indonesian-mt-data).
 - The Religious and Magazine data from [Neural machine translation with a polysynthetic low resource language ](https://link.springer.com/article/10.1007/s10590-020-09255-9) can be found [here](https://github.com/johneortega/mt_quechua_spanish).

## Running the Code
Our entire pipeline can be run with:
```
python pipeline.py
```
The pipeline can take in several flags:
 - `--src_segment_type` and `--tgt_segment_type` can be `none`, `bpe`,`unigram`, `prpe`, `prpe_bpe`, `prpe_multiN` (where N is number of iterations).
 - `--model_type` can be `rnn`(aka LSTM) or `transformer`. Defaults to LSTM.
 - `--in_lang` specifies the input language to be translated. We used `qz` for Quechua and `id` for Indonesian. Defaults to Quechua.
 - `--out_lang` specifies the output language to be translated to. We used `es` for Spanish and `en` for English. Defaults to Spanish.
 - `--domain` specifies the name of dataset to be used, which should be located in `data/` under the same name. Defaults to religious.
    - A dataset folder should include: 
        - `train.{in_lang}.txt`
        - `validate.{in_lang}.txt`
        - `test.{in_lang}.txt`
        - `train.{out_lang}.txt`, 
        - `validate.{out_lang}.txt`
        - `test.{out_lang}.txt`
    - Example: `train.qz.txt`, `train.es.txt` for Quechua-Spanish translation.
 - `--train_steps` specifies how many steps the model should be trained. Default value is 100,000.
 - `--save_steps` specifies how often the trained model is saved. Default is every 10,000 steps.
 - `--validate_steps` specifies how often the model should be evaluated against the validation set. Default is every 2000 steps.
 - `--batch_size` is the batch size for training. Default is 64.
 - `--filter_too_long` specifies the max token length of a line in the training set. Any line that passes this value is filtered out. Default is no filtering.
 - `--src_token_lang` and `--tgt_token_lang` specifies the tokenization language Moses uses. We use `es` for both languages in QZ-ES, and `en` for ID-EN.
 
The pipeline will automatically test the model after training is finished and output a BLEU and CHRF score.
