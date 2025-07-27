import json
import os
import subprocess, sys
import codecs
import threading
import traceback
from sentence_transmorgrifier.transmorgrify import Transmorgrifier

sys.path.append('data' )
sys.path.append('data/subword-nmt' )
import osis_tran
SRC_MOD = '2TGreek'
import apply_bpe

# def translate( model_path, TGT_MOD ):
#     src_mod = osis_tran.load_osis_module(SRC_MOD, toascii=True)

#     keys = list(src_mod.keys())

#     verses = "\n".join( f"TGT_{TGT_MOD} " + src_mod[key] for key in keys )


#     #process = subprocess.run( f'python ./fairseq_cli/interactive.py ./data-bin/bible.prep --path {model_path}  --cpu', input=verses, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8' )
#     process = subprocess.run( ['python', './fairseq_cli/interactive.py', './data-bin/bible.prep', '--path', model_path, '--cpu'], input=verses, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8' )

#     #process = subprocess.run( ['cat', './fairseq_cli/interactive.py'],  stdout=subprocess.PIPE )

#     for line in process.stdout.splitlines():

#         print(line)

def detokenize( x ):
    x = x.replace( "@@ ", "" ).replace( " .", "." ).replace( " ,", "," ).replace( "&quot;", '"' ).strip().replace( "&apos;", "'" )
    return x


def run_bpe( input_string, code_file, tgt_key, fail_glossary=False ):
    codes = codecs.open(code_file, encoding='utf-8')
    bpe = apply_bpe.BPE(codes=codes, glossaries=([tgt_key] if not fail_glossary else []))
    return bpe.segment( input_string.strip() )


def translate( model_path, TGT_MOD, output_file, data_path, code_file,beam_size=1000, fail_glossary=False, use_cpu=True, tm_model_path=None ):
    src_mod = osis_tran.load_osis_module(SRC_MOD, toascii=True)


    #process = subprocess.run( f'python ./fairseq_cli/interactive.py ./data-bin/bible.prep --path {model_path}  --cpu', input=verses, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8' )
    #process = subprocess.run( ['python', './fairseq_cli/interactive.py', './data-bin/bible.prep', '--path', model_path, '--cpu'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8' )

    #process = subprocess.run( ['cat', './fairseq_cli/interactive.py'],  stdout=subprocess.PIPE )

    command = ['python', './fairseq_cli/interactive.py', data_path, '--beam', str(beam_size), '--path', model_path]
    if use_cpu:
        command.append('--cpu')

    tm_model = None
    if tm_model_path:
        tm_model = Transmorgrifier()
        tm_model.load( tm_model_path )


    with subprocess.Popen( command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8' ) as process:

        for key in src_mod.keys():

            verse_in = f"TGT_{TGT_MOD} " + src_mod[key] + "\n"

            verse_in_tokenized = run_bpe( verse_in, code_file=code_file, tgt_key=f"TGT_{TGT_MOD}", fail_glossary=fail_glossary )

            #result, error = process.communicate( verse_in )
            process.stdin.write( verse_in_tokenized + "\n" )
            process.stdin.flush()

            while not (result := process.stdout.readline()).startswith( "H"):
                #print( "#ignore " + result )
                pass

            #remove the prefix and the number prefix.
            prefix, score, verse_out = result.split( "\t", 2 )


            verse_out = detokenize(verse_out)

            if tm_model:
                verse_out = list( tm_model.execute( [verse_out] ) )[0]
        

            print( f"{key}\n  Verse in {verse_in.strip()}\n  Verse out: {verse_out}\n")

            print( f"{key} {verse_out}\n", file=output_file )

def gen_magic_token_string(reference, magic_token_count):
    magic_token_list = []
    for i in range(magic_token_count):
        mt = f"{reference.upper()}_MT_{i+1}".replace( " ", "_")
        magic_token_list.append(mt)
        # if not mt in GLOSSARIES:
        #     GLOSSARIES.append(mt)
    return " ".join(magic_token_list)

def translate__magic_token( model_path, TGT_MOD, output_file, data_path, code_file, beam_size=1000, magic_token_count = 3, use_cpu=True, tm_model_path=None ):
    #load the NET_FREE just so we can get the references too.  If this is a different style ENG/ORG etc then the target translation this could be wrong.
    net_free = osis_tran.load_osis_module( "NETfree", toascii=False )
                                          
                                          
    command = ['python', './fairseq_cli/interactive.py', data_path, '--beam', str(beam_size), '--path', model_path]
    if use_cpu:
        command.append('--cpu')

    tm_model = None
    if tm_model_path:
        tm_model = Transmorgrifier()
        tm_model.load( tm_model_path )

    with subprocess.Popen( command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8' ) as process:
        for key in net_free.keys():
            verse_in = f"TGT_{TGT_MOD} " + gen_magic_token_string(key, magic_token_count)  + "\n"

            process.stdin.write( verse_in )
            process.stdin.flush()

            while not (result := process.stdout.readline()).startswith( "H" ):
                pass

            #remove the prefix and the number prefix.
            prefix, score, verse_out = result.split( "\t", 2 )


            verse_out = detokenize(verse_out)

            if tm_model:
                verse_out = list( tm_model.execute( [verse_out] ) )[0]

            print( f"{key}\n  Verse in {verse_in.strip()}\n  Verse out: {verse_out}\n")

            print( f"{key} {verse_out}\n", file=output_file )
            output_file.flush()


def translate__magic_token__python_import( model_path, TGT_MOD, output_file, data_path, code_file, beam_size=1000, magic_token_count = 3, use_cpu=True, nbest=1, tm_model_path=None ):
    #load the NET_FREE just so we can get the references too.  If this is a different style ENG/ORG etc then the target translation this could be wrong.
    net_free = osis_tran.load_osis_module( "NETfree", toascii=False )
                                          



    #command = ['python', './fairseq_cli/interactive.py', data_path, '--beam', str(beam_size), '--path', model_path]
    command = ['./fairseq_cli/interactive.py', data_path, '--beam', str(beam_size), '--path', model_path, '--nbest', str(nbest)]
    if use_cpu:
        command.append('--cpu')

    tm_model = None
    if tm_model_path:
        tm_model = Transmorgrifier()
        tm_model.load( tm_model_path )


    # Create pipes for stdin and stdout
    stdin_reader, stdin_writer = os.pipe()
    stdout_reader, stdout_writer = os.pipe()

    stdin_reader_file = os.fdopen( stdin_reader, 'rt', buffering=1 )
    stdin_writer_file = os.fdopen( stdin_writer, 'wt', buffering=1 )
    stdout_reader_file = os.fdopen( stdout_reader, 'rt', buffering=1 )
    stdout_writer_file = os.fdopen( stdout_writer, 'wt', buffering=1 )


    argv_save = sys.argv
    stdin_save = sys.stdin
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


    for key in net_free.keys():
        verse_in = f"TGT_{TGT_MOD} " + gen_magic_token_string(key, magic_token_count)  + "\n"

        # forced_output = run_bpe( "Once upon a time", code_file=code_file, tgt_key=f"TGT_{TGT_MOD}", fail_glossary=False )
        # stdin_writer_file.write( f"output: {forced_output}\n" )
        stdin_writer_file.write( verse_in )
        stdin_writer_file.flush()

        for n in range(nbest):
            while not (result := stdout_reader_file.readline()).startswith( "H" ):
                pass

            #remove the prefix and the number prefix.
            prefix, score, verse_out = result.split( "\t", 2 )


            verse_out = detokenize(verse_out)

            if tm_model:
                verse_out = list( tm_model.execute( [verse_out] ) )[0]

            print( f"{key}\n  Verse in {verse_in.strip()}\n  Verse out n {n}: {verse_out}\n", file=stdout_save )
            print( f"{key} {n}: {verse_out}\n", file=output_file )
            output_file.flush()

    #close things.
    stdin_writer_file.close()
    stdout_reader_file.close()

    #join the thread
    fairseq_thread.join()

    sys.argv = argv_save
    sys.stdin = stdin_save
    sys.stdout = stdout_save

if __name__ == "__main__":
    # TGT_MOD = "NETfree"
    # model_path = 'checkpoints/bible.prep.roman/checkpoint_best.pt'
    # data_path = './data-bin/bible.prep.amo.roman'
    # output_file = f"{TGT_MOD}_out_roman.txt"

    # TGT_MOD = "AMO"
    # model_path = 'checkpoints/bible.prep.roman/checkpoint_best.pt'
    # data_path = './data-bin/bible.prep.amo.roman'
    # output_file = f"{TGT_MOD}_out_roman_gpu.txt"
    # fail_glossary = True
    # beam_size = 120
    # code_file = './data/bible.prep.with.amo/code'
    # use_cpu = False

    # TGT_MOD = "NETfree"
    # model_path = 'checkpoints/bible.prep.roman/checkpoint_best.pt'
    # data_path = './data-bin/bible.prep.amo.roman'
    # output_file = f"{TGT_MOD}_out_roman.txt"
    # beam_size = 120
    # code_file = './data/bible.prep.with.amo/code'
    # fail_glossary = False
    # use_cpu = False

    # with open( output_file, "wt" ) as fout:
    #     try:
    #         translate( model_path, TGT_MOD, fout, data_path=data_path, beam_size=beam_size, code_file=code_file, fail_glossary=fail_glossary, use_cpu=use_cpu )
    #     except:
    #         pass

    # model_path = 'checkpoints/bible.prep.magic_tokens/checkpoint246.pt'
    # TGT_MOD = "NETfree"
    # output_file = f"{TGT_MOD}_out_magic_token.txt"
    # data_path = "data-bin/bible.prep.magic_tokens"
    # beam_size = 1000
    # code_file = './data/bible.prep.magic_tokens/code'
    # use_cpu=True
    # with open( output_file, "wt" ) as fout:
    #     try:
    #         translate__magic_token( model_path, TGT_MOD, fout, data_path=data_path, beam_size=beam_size, code_file=code_file, use_cpu=use_cpu )
    #     except:
    #         pass    config_file = "translate_raw_config.json"


    config_file = "translate_raw_config.json"
    with open( config_file, "rt" ) as fin:
        config = json.load( fin )

    for TGT_MOD in config["TGT_MODS"]:
        model_path = config["targets"][TGT_MOD]["model_path"]
        data_path = config["targets"][TGT_MOD]["data_path"]
        output_file = config["targets"][TGT_MOD]["output_file"] if "output_file" in config["targets"][TGT_MOD] else f"{TGT_MOD}_out.txt"
        beam_size = config["targets"][TGT_MOD]["beam_size"] if "beam_size" in config["targets"][TGT_MOD] else 1000
        code_file = config["targets"][TGT_MOD]["code_file"]
        use_cpu = config["targets"][TGT_MOD]["use_cpu"] if "use_cpu" in config["targets"][TGT_MOD] else False
        tm_model_path = config["targets"][TGT_MOD]["tm_model_path"] if "tm_model_path" in config["targets"][TGT_MOD] else None


        with open( output_file, "wt" ) as fout:
            try:
                if "translate_magic_token" in config["targets"][TGT_MOD] and config["targets"][TGT_MOD]["translate_magic_token"]:
                    #translate__magic_token( model_path, TGT_MOD, fout, data_path=data_path, beam_size=beam_size, code_file=code_file, use_cpu=use_cpu )
                    translate__magic_token__python_import( model_path, TGT_MOD, fout, data_path=data_path, beam_size=beam_size, code_file=code_file, use_cpu=use_cpu, tm_model_path=tm_model_path )
                else:
                    translate( model_path, TGT_MOD, fout, data_path=data_path, beam_size=beam_size, code_file=code_file, use_cpu=use_cpu, tm_model_path=tm_model_path )
            except:
                print( f"The exception trace is {traceback.format_exc()}" )
                pass