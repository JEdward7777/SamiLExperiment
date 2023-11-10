# Introduction

This is the code for the article [Machine translating the Bible into new languages](https://samiliedes.wordpress.com/2018/03/07/machine-translating-the-bible-into-new-languages/).

The preprocessing step requires a slightly modified version of the Moses tokenizer. This and another dependency are thus included as Git submodules. For this reason, you need to also clone the subrepositories. The easiest way to do this is to use this command to clone the repository:

`git clone --recurse-submodules https://github.com/JEdward7777/SamiLExperiment`

Install PyTorch either from source or from [http://pytorch.org/](http://pytorch.org/).

Install Fairseq:

```
$ pip install --editable ./
```

To prepare the data set:

1. Install the SWORD project's tools on your computer. For example, for Debian derivative distributions they are available in a package named *libsword-utils*.
1. Install the Bible modules you want to include in the corpus. You can do this using the *installmgr* command line tool, or from a Bible software package such as BibleTime.
1. The list of Bible modules currently configured for are in `data/prepare_bible.py`.
1. Edit `data/prepare_bible.py` to list the modules in the MODULES variable. Those prefixed with an asterisk will be romanized. Also set the attention language (variable SRC), and edit TRAIN_STARTS to exclude portions of some translations from training and use them as the validation/test set.
1. Install unidecode used by prepare_bible: `pip install unidecode`
1. Verify that the command `mod2imp` is in your command path from installing libsword-utils.  It is called by `prepare_bible`.

Now run the following commands:

```
$ cd data
$ ./prepare_bible.py
$ cd ..
$ python ./fairseq_cli/preprocess.py --source-lang src --target-lang tgt \
  --trainpref data/bible.prep/train --validpref data/bible.prep/valid \
  --testpref data/bible.prep/test --destdir data-bin/bible.prep
```

Now you will have a binarized dataset in data-bin/bible.prep. You can use `train.py` to train a model:

```
$ mkdir -p checkpoints/bible.prep
$ CUDA_VISIBLE_DEVICES=0 python train.py data-bin/bible.prep \
  --optimizer adam --lr 0.0001 --clip-norm 0.1 --dropout 0.2 --max-tokens 3000 \
  --arch fconv_wmt_en_ro --save-dir checkpoints/bible.prep \
  --tensorboard-logdir tb_logs/bible.prep
```

Adjust the --max-tokens value if you run out of GPU memory.

You can generate translations of the test/validation set with with generate.py:

```
$ python ./fairseq_cli/generate.py data-bin/bible.prep --path checkpoints/bible.prep/checkpoint_best.pt \
  --batch-size 10 --beam 120 --remove-bpe
```

To generate full translations, use the generated template in `data/bible.prep/src-template`. For each line, replace the `TGT_TEMPLATE` tag by one that corresponds to a translation; for example, `TGT_NETfree` for English or `TGT_FinPR` for Finnish:

`$ sed -e s/TGT_TEMPLATE/TGT_FinPR/ <data/bible.prep/src-template >src.FinPR`

Now you can edit src.FinPR to omit the verses you do not want translated. After that, to translate:

```
$ ./batch_translate.py --model checkpoints/bible.prep/checkpoint_best.pt \
  --dictdir data-bin/bible.prep --beam 120 --batch-size 10 src.FinPR >FinPR.raw.txt
```

The output file has the translated sentences in length order. To sort them in the order of the source text, add verse names and apply some minor postprocessing, use `sort_full.py` (you may need to edit it to change the source module):

`$ ./sort_full.py <FinPR.raw.txt >FinPR.txt`

For more useful information in the original README for fairseq-py, consult [README.fairseq.md](README.fairseq.md).
