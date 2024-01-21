import subprocess, sys

sys.path.append('data')
import osis_tran
SRC_MOD = '2TGreek'

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


def translate( model_path, TGT_MOD, output_file, data_path, beam_size=1000 ):
    src_mod = osis_tran.load_osis_module(SRC_MOD, toascii=True)


    #process = subprocess.run( f'python ./fairseq_cli/interactive.py ./data-bin/bible.prep --path {model_path}  --cpu', input=verses, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8' )
    #process = subprocess.run( ['python', './fairseq_cli/interactive.py', './data-bin/bible.prep', '--path', model_path, '--cpu'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8' )

    #process = subprocess.run( ['cat', './fairseq_cli/interactive.py'],  stdout=subprocess.PIPE )

    with subprocess.Popen( ['python', './fairseq_cli/interactive.py', data_path, '--beam', str(beam_size), '--path', model_path, '--cpu'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8' ) as process:

        for key in src_mod.keys():

            verse_in = f"TGT_{TGT_MOD} " + src_mod[key] + "\n"

            #result, error = process.communicate( verse_in )
            process.stdin.write( verse_in )
            process.stdin.flush()

            while not (result := process.stdout.readline()).startswith( "H"):
                #print( "#ignore " + result )
                pass

            #remove the prefix and the number prefix.
            prefix, score, verse_out = result.split( "\t", 2 )


            verse_out = detokenize(verse_out)

            print( f"{key}\n  Verse in {verse_in.strip()}\n  Verse out: {verse_out}\n")

            print( f"{key} {verse_out}\n", file=output_file )



if __name__ == "__main__":
    # TGT_MOD = "NETfree"
    # model_path = 'checkpoints/bible.prep.roman/checkpoint_best.pt'
    # data_path = './data-bin/bible.prep.amo.roman'
    # output_file = f"{TGT_MOD}_out_roman.txt"
    TGT_MOD = "AMO"
    model_path = 'checkpoints/bible.prep.roman/checkpoint_best.pt'
    data_path = './data-bin/bible.prep.amo.roman'
    output_file = f"{TGT_MOD}_out_roman.txt"

    with open( output_file, "wt" ) as fout:
        translate( model_path, TGT_MOD, fout, data_path=data_path )