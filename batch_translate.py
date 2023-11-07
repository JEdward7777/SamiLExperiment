#!/usr/bin/env python3

#INPUT_FILE = 'val.src.bpe'
#DATA_DIR = 'data-bin/bible.prep'
#MODEL = 'checkpoints/bible.prep/checkpoint_best.pt'
#SRC_DIC = 'data-bin/bible.prep/dict.src.txt'
#TGT_DIC = 'data-bin/bible.prep/dict.tgt.txt'
#BEAM_SIZE = 5
#STOP_EARLY = True

SRC_LANG = 'src'
TGT_LANG = 'tgt'

import sys
import argparse
import os
import torch

import fairseq
from fairseq import dictionary, indexed_dataset, utils, options
from fairseq.tokenizer import Tokenizer
from fairseq.sequence_generator import SequenceGenerator

def main():
    parser = argparse.ArgumentParser(description='Batch translate')
    #parser.add_argument('--no-progress-bar', action='store_true', help='disable progress bar')
    parser.add_argument('--model', metavar='FILE', required=True, action='append',
                        help='path(s) to model file(s)')
    parser.add_argument('--dictdir', metavar='DIR', required=True, help='directory of dictionary files')
    parser.add_argument('--batch-size', default=32, type=int, metavar='N',
                        help='batch size')

    parser.add_argument('--beam', default=5, type=int, metavar='N',
                       help='beam size (default: 5)')
    #parser.add_argument('--nbest', default=1, type=int, metavar='N',
    #                   help='number of hypotheses to output')
    #parser.add_argument('--remove-bpe', nargs='?', const='@@ ', default=None,
    #                   help='remove BPE tokens before scoring')
    parser.add_argument('--no-early-stop', action='store_true',
                       help=('continue searching even after finalizing k=beam '
                             'hypotheses; this is more correct, but increases '
                             'generation time by 50%%'))
    #parser.add_argument('--unnormalized', action='store_true',
    #                   help='compare unnormalized hypothesis scores')
    parser.add_argument('--cpu', action='store_true', help='generate on CPU')
    parser.add_argument('--no-beamable-mm', action='store_true',
                       help='don\'t use BeamableMM in attention layers')
    parser.add_argument('--lenpen', default=1, type=float,
                       help='length penalty: <1.0 favors shorter, >1.0 favors longer sentences')
    parser.add_argument('--unkpen', default=0, type=float,
                       help='unknown word penalty: <0 produces more unks, >0 produces fewer')
    #parser.add_argument('--replace-unk', nargs='?', const=True, default=None,
    #                   help='perform unknown replacement (optionally with alignment dictionary)')
    #parser.add_argument('--quiet', action='store_true',
    #                   help='Only print final scores')

    parser.add_argument('input', metavar='INPUT', help='Input file')

    args = parser.parse_args()
    
    # required by progress bar
    args.log_format = None
    
    USE_CUDA = not args.cpu and torch.cuda.is_available()

    print('Loading model...', file=sys.stderr)
    models, _ = utils.load_ensemble_for_inference(args.model, data_dir=args.dictdir)
    src_dic = models[0].src_dict
    dst_dic = models[0].dst_dict

    for model in models:
        model.make_generation_fast_(beamable_mm_beam_size=args.beam)

    translator = SequenceGenerator(
        models, beam_size=args.beam, stop_early=(not args.no_early_stop),
        len_penalty=args.lenpen, unk_penalty=args.unkpen)
    if USE_CUDA:
        translator.cuda()

    max_positions = min(model.max_encoder_positions() for model in models)

    print('Loading input data...', file=sys.stderr)

    raw_dataset = indexed_dataset.IndexedRawTextDataset(args.input, src_dic)
    dataset = fairseq.data.LanguageDatasets(SRC_LANG, TGT_LANG, src_dic, dst_dic)
    dataset.splits['test'] = fairseq.data.LanguagePairDataset(
        raw_dataset, raw_dataset, pad_idx=dataset.src_dict.pad(),
        eos_idx=dataset.src_dict.eos())

#    itr = dataset.eval_dataloader(
#        'test', max_sentences=args.batch_size, max_positions=max_positions)
    itr = dataset.eval_dataloader('test', max_sentences=args.batch_size)
    itr = utils.build_progress_bar(args, itr)

    #out = []

    for sample_id, src_tokens, _, hypos in translator.generate_batched_itr(
        itr, cuda_device=0 if USE_CUDA else None):
        src_str = dataset.src_dict.string(src_tokens, '@@ ')
        #print(src_str)
        hypo_tokens, hypo_str, alignment = utils.post_process_prediction(
            hypo_tokens=hypos[0]['tokens'].int().cpu(),
            src_str=src_str,
            alignment=hypos[0]['alignment'].int().cpu(),
            align_dict=None,
            dst_dict=dataset.dst_dict,
            remove_bpe='@@ ')
        #out.append((sample_id, hypo_str))
        print('{}\t{}'.format(sample_id, hypo_str), flush=True)

    #out.sort()
    #for sample_id, hypo_str in out:    
    #    print('{}\t{}'.format(sample_id, hypo_str))

if __name__ == '__main__':
    main()
