import os

def is_windows():
    return os.name == 'nt'

def make_run_folder(FOLDER):
    os.mkdir('./model_opennmt/run' + FOLDER)

def copy_content(input_file, output_file):
    with open(input_file, encoding='utf8') as src_input, open(output_file, 'w', encoding='utf8') as src_out:
        src_arr = src_input.readlines()
        for src_line in src_arr:
            src_out.write(src_line)

        src_input.close()
        src_out.close()