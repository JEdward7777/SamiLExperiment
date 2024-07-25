import sys, json, os
import threading
import gradio as gr
import translate_raw


sys.path.append('data' )
import osis_tran

config_file = "gradio_translate_prefix_config.json"
with open( config_file, "rt" ) as fin:
    config = json.load( fin )

specific_config = config["configs"][config["active_config"]]


SRC_MOD = '2TGreek'
src_mod = osis_tran.load_osis_module(SRC_MOD, toascii=True)

#Set up fairseq.
command = ['./fairseq_cli/interactive.py', specific_config["data_path"], '--beam', str(specific_config.get("beam_size", 1000)), '--path', specific_config["model_path"]]
if specific_config["use_cpu"]:
    command.append('--cpu')

# Create pipes for stdin and stdout
stdin_reader, stdin_writer = os.pipe()
stdout_reader, stdout_writer = os.pipe()

stdin_reader_file = os.fdopen( stdin_reader, 'rt', buffering=1 )
stdin_writer_file = os.fdopen( stdin_writer, 'wt', buffering=1 )
stdout_reader_file = os.fdopen( stdout_reader, 'rt', buffering=1 )
stdout_writer_file = os.fdopen( stdout_writer, 'wt', buffering=1 )

# argv_save = sys.argv
# stdin_save = sys.stdin
stdout_save = sys.stdout

sys.argv = command
sys.stdin = stdin_reader_file
sys.stdout = stdout_writer_file

import fairseq_cli.interactive

def main_wrapper():
    fairseq_cli.interactive.cli_main()

#call fairseq_cli.interactive.main() from a new thread.
fairseq_thread = threading.Thread(target=main_wrapper)
fairseq_thread.start()


def translate( language, reference, forced_output_string ):
    if specific_config["translate_magic_token"]:
        verse_in = f"TGT_{language} " + translate_raw.gen_magic_token_string(reference, translate_raw.magic_token_count)  + "\n"
    else:
        verse_in = f"TGT_{language} " + src_mod[reference] + "\n"
        verse_in = translate_raw.run_bpe( verse_in, code_file=specific_config['code_file'], tgt_key=f"TGT_{language}", fail_glossary=False ) + "\n"

    if forced_output_string:
        forced_output = translate_raw.run_bpe( forced_output_string, code_file=specific_config['code_file'], tgt_key=f"TGT_{language}", fail_glossary=False )
    else:
        forced_output = ""
    stdin_writer_file.write( f"output: {forced_output}\n" )
    stdin_writer_file.write( verse_in )
    stdin_writer_file.flush()

    while not (result := stdout_reader_file.readline()).startswith( "H" ):
        print( result, file=stdout_save )
        pass
    print( result, file=stdout_save )

    #remove the prefix and the number prefix.
    prefix, score, verse_out = result.split( "\t", 2 )


    verse_out = translate_raw.detokenize(verse_out)

    return verse_out

def accept_word( language, reference, input_string, output_string ):
    input_words = input_string.split()
    output_words = output_string.split()



languages = specific_config["languages"]
references = list(src_mod.keys())

with gr.Blocks() as demo:
    #put drop down for language.
    sel_language = gr.Dropdown( languages, value=languages[0] )
    sel_reference = gr.Dropdown( references, value=references[0] )

    input_textbox = gr.Textbox()

    btn = gr.Button("Translate")
    output_textbox = gr.Textbox()
    accept = gr.Button("Accept word")

    btn.click( translate, inputs=[sel_language, sel_reference, input_textbox], outputs=[output_textbox] )

    #accept.click( accept_word, inputs=[sel_language, sel_reference, input_textbox,output_textbox], outputs=[input_textbox, output_textbox])

launch_result = demo.launch(share=True)
print( f"Launch result: {launch_result}", file=stdout_save )