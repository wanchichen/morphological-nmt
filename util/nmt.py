
def create_train_yaml(opt, train_src, train_tgt, val_src, val_tgt, folder, cfg_file):
    f = 'model_opennmt/run' + folder
    with open(cfg_file, 'w') as pl:

        pl.write('skip_empty_level: silent\n')
        pl.write('save_data: ' + f + '/result\n')

        pl.write('src_vocab: ' + f + f'/{opt.in_lang}.vocab.src\n')
        pl.write('tgt_vocab: ' + f + f'/{opt.out_lang}.vocab.src\n')

        pl.write('data:\n')
        pl.write('    corpus_1:\n')
        pl.write('        path_src: ' + train_src + '\n')
        pl.write('        path_tgt: ' + train_tgt + '\n')
        if opt.filter_too_long > -1:
            pl.write('        transforms: [filtertoolong]\n')
            pl.write(f'        src_seq_length: {opt.filter_too_long}\n')
            pl.write(f'        tgt_seq_length: {opt.filter_too_long}\n')
        pl.write('    valid:\n')
        pl.write('        path_src: ' + val_src + '\n')
        pl.write('        path_tgt: ' + val_tgt + '\n')

        pl.write('world_size: 1\n')
        pl.write('gpu_ranks: [0]\n')

        pl.write('batch-type: \"tokens\"\n')

        if opt.load_saved is not None:
            pl.write(f'train_from: {opt.load_saved}\n')
            pl.write('update_vocab: true\n')
            pl.write('reset_optim: all\n')

        # Default is 10,000
        pl.write(f'valid_steps: {opt.validate_steps}\n')
        pl.write(f'save_checkpoint_steps: {opt.save_steps}\n')
        pl.write(f'train_steps: {opt.train_steps}\n') 
        pl.write(f'batch_size: {opt.batch_size}\n')
            
            # default type is tokens, default batch_size is 64

            # sgd is default optimizer

            # default dropout is 0.3

        if opt.model_type == 'transformer':    

	        # Transformer specific batch settings
            #pl.write('queue_size: 10000\n')
            #pl.write('bucket_size: 32768\n')
            pl.write('valid_batch_size: 8\n')
            pl.write('accum_count: [4]\n')
            pl.write('accum_steps: [0]\n')

            # By default rnn is two layer, with 500 hidden units.
            # rnn default type is LSTM, uncomment this line for transformer
            pl.write('model_dtype: "fp32"\n')
	
            # default task is seq2seq (other option is lm)

            # sgd is the default optimizer. use adam for transformer
            pl.write('optim: "adam"\n')

            # Default dropout is 0.3. Use 0.1 for transformer
            pl.write('dropout: [0.1]\n')

            # default learning_rate is 1, 2 for transformer. learning_rate_decay is 0.5 and start_decay_steps is 50,000 
            # decay_steps is 10,000
            pl.write('learning_rate: 2\n')

	        # transformer specific optimization settings
            pl.write('warmup_steps: 8000\n')
            pl.write('decay_method: "noam"\n')
            pl.write('adam_beta2: 0.998\n')
            pl.write('max_grad_norm: 0\n')
            pl.write('label_smoothening: 0.1\n')
            pl.write('param_init: 0\n')
            pl.write('param_init_glorot: true\n')
            pl.write('normalization: "tokens"\n')

	        # transformer specific model settings
            pl.write('encoder_type: transformer\n')
            pl.write('decoder_type: transformer\n')
            pl.write('position_encoding: true\n')
            pl.write('enc_layers: 6\n')
            pl.write('dec_layers: 6\n')
            pl.write('heads: 8\n')
            pl.write('rnn_size: 256\n') #def 512 but i ran out of vram
            pl.write('word_vec_size: 256\n')
            pl.write('transformer_ff: 2048\n')
            pl.write('dropout_steps: [0]\n')
            pl.write('attention_dropout: [0.1]\n')
            
	
        pl.write('save_model: ' + f + '/model\n')

        pl.write('tensorboard: false\n')
        
        pl.close()

def create_vocab_yaml(opt, train_src, train_tgt, val_src, val_tgt, folder, cfg_file):
    f = 'model_opennmt/run' + folder
    with open(cfg_file, 'w') as pl:

        pl.write('skip_empty_level: silent\n')
        pl.write('save_data: ' + f + '/result\n')

        pl.write('src_vocab: ' + f + f'/{opt.in_lang}.vocab.src\n')
        pl.write('tgt_vocab: ' + f + f'/{opt.out_lang}.vocab.src\n')

        pl.write('data:\n')
        pl.write('    corpus_1:\n')
        pl.write('        path_src: ' + train_src + '\n')
        pl.write('        path_tgt: ' + train_tgt + '\n')
        if opt.filter_too_long > -1:
            pl.write('        transforms: [filtertoolong]\n')
            pl.write(f'        src_seq_length: {opt.filter_too_long}\n')
            pl.write(f'        tgt_seq_length: {opt.filter_too_long}\n')
        pl.write('    valid:\n')
        pl.write('        path_src: ' + val_src + '\n')
        pl.write('        path_tgt: ' + val_tgt + '\n')

    pl.close()
