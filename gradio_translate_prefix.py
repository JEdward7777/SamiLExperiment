import sys, json, os
import threading
import gradio as gr
import translate_raw
import JLDiff
from unidecode import unidecode
from sentence_transmorgrifier.transmorgrify import Transmorgrifier


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

tm = Transmorgrifier()

def translate( language, reference, forced_output_string ):
    if specific_config["translate_magic_token"]:
        verse_in = f"TGT_{language} " + translate_raw.gen_magic_token_string(reference, translate_raw.magic_token_count)  + "\n"
    else:
        verse_in = f"TGT_{language} " + src_mod[reference] + "\n"
        verse_in = translate_raw.run_bpe( verse_in, code_file=specific_config['code_file'], tgt_key=f"TGT_{language}", fail_glossary=False ) + "\n"

    if forced_output_string:
        forced_output = forced_output_string
        forced_output = forced_output.lower()
        forced_output = unidecode(forced_output)
        forced_output = translate_raw.run_bpe( forced_output, code_file=specific_config['code_file'], tgt_key=f"TGT_{language}", fail_glossary=False )
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

    # #remove the number of tokens from the output that are the number of tokens from the forced_output.
    # forced_output_token_num = len(forced_output.split())
    # if forced_output_token_num > 0:
    #     verse_out = " ".join( verse_out.split()[forced_output_token_num:] )


    verse_out = translate_raw.detokenize(verse_out)

    if "tm_models" in specific_config:
        tm_models_path = specific_config["tm_models"]
        lang_model_path = tm_models_path.format( lang=language )
        if os.path.exists( lang_model_path ):
            tm.load( lang_model_path )

            verse_out = list(tm.execute([verse_out]))[0]

    return verse_out


def get_next_word( shorter, longer ):
    difference = JLDiff.compute_diff( longer, shorter, axis_penalty=True )

    in_index = -1
    out_index = -1
    seen_content = False

    addition = ""
    for diff in difference:
        if diff.state == JLDiff.STATE_MATCH:
            #match
            in_index += 1
            out_index += 1
        elif diff.state == JLDiff.STATE_PASSING_2ND:
            #deletion
            in_index += 1
        elif diff.state == JLDiff.STATE_PASSING_1ST:
            #insertion
            #if we insert past the end of the first string
            #then take the insertion until the insertion
            #is a whitespace unless we haven't seen content yet.
            if in_index >= len(shorter):
                if seen_content and diff.content == " ":
                    break
                else:
                    if diff.content != " ":
                        seen_content = True
                    addition += diff.content
            out_index += 1

    return addition


def accept_word( input_string, output_string ):
    #The diff doesn't like to match on the front.
    #so just feed it enough so that it can return something.

    found_word = False

    space_location = output_string.find( " " )

    while not found_word and space_location != -1:
        truncated_output_string = output_string[0:space_location]

        addition = get_next_word( input_string, truncated_output_string )

        if len( addition ) > 0:
            found_word = True
        else:
            space_location = output_string.find( " ", space_location + 1 )
    

    if not found_word:
        addition = get_next_word( input_string, output_string )


    new_input_words = input_string + addition
        
    return new_input_words

    #return input_string + get_next_word( input_string, output_string )

languages = specific_config["languages"]
references = list(src_mod.keys())

with gr.Blocks() as demo:
    #put drop down for language.
    sel_language = gr.Dropdown( languages, value=languages[0] )
    sel_reference = gr.Dropdown( references, value=references[0] )

    input_textbox = gr.Textbox( label="Translation start." )

    btn = gr.Button("Translate")
    output_textbox = gr.Textbox()
    #accept = gr.Button("Accept word")

    btn.click( translate, inputs=[sel_language, sel_reference, input_textbox], outputs=[output_textbox] )

    #accept.click( accept_word, inputs=[input_textbox,output_textbox], outputs=[input_textbox])

launch_result = demo.launch(share=True)
print( f"Launch result: {launch_result}", file=stdout_save )