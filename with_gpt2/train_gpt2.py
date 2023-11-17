# %%

#install pytorch

#pip install accelerate -U
#pip install transformers[torch]
#pip install omegaconf


#pip install pandas

# %%
# import the things.

import os
import pandas as pd
import numpy as np
import re
from transformers import TextDataset, DataCollatorForLanguageModeling
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import Trainer, TrainingArguments, PretrainedConfig
from omegaconf import OmegaConf
from tokenizers import ByteLevelBPETokenizer

#import OmegaConf


# %%
#Define the functions.

#training code copied from
#https://www.kaggle.com/code/changyeop/how-to-fine-tune-gpt-2-for-beginners/notebook

def load_dataset(file_path, tokenizer, block_size = 128):
    dataset = TextDataset(
        tokenizer = tokenizer,
        file_path = file_path,
        block_size = block_size,
    )
    return dataset

def load_data_collator(tokenizer, mlm = False):
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, 
        mlm=mlm,
    )
    return data_collator


def train(train_file_path,model_name,
          output_dir,
          overwrite_output_dir,
          per_device_train_batch_size,
          num_train_epochs, save_steps, from_scratch ):


    bos_token = "<|startoftext|>"
    eos_token = "<|endoftext|>"
    unk_token = "<unk>"

    if from_scratch: 
        
        #looking at 
        #https://github.com/huggingface/tokenizers/blob/main/bindings/python/examples/train_bytelevel_bpe.py
        #https://www.programcreek.com/python/?code=minimaxir%2Faitextgen%2Faitextgen-master%2Faitextgen%2Ftokenizers.py
        #train tokenizer
        tokenizer_trainer = ByteLevelBPETokenizer()
        tokenizer_trainer.train( [train_file_path],

            special_tokens=[bos_token, eos_token, unk_token],
            vocab_size=10000,
            min_frequency=2,
            show_progress=True, )
        #tokenizer_trainer.save(os.path.join(output_dir,"tokenizer.json"))
        tokenizer_trainer.save_model(output_dir)

    tokenizer = GPT2Tokenizer.from_pretrained(output_dir)

    train_dataset = load_dataset(train_file_path, tokenizer)
    data_collator = load_data_collator(tokenizer)
    
    tokenizer.save_pretrained(output_dir)
      
    if not from_scratch:
        model = GPT2LMHeadModel.from_pretrained(model_name)
    else:
        config = PretrainedConfig( 
            hidden_size = 768,
            activation_function = "gelu_new",
            attn_pdrop = 0.1,
            bos_token_id = tokenizer.get_id(bos_token),
            embd_pdrop = 0.1,
            eos_token_id = tokenizer.get_id(eos_token),
            initializer_range = 0.02,
            layer_norm_epsilon = 1e-05,
            #model_type = "gpt2",
            n_ctx = 1024,
            n_embd = 768,
            n_head = 12,
            n_inner = None,
            n_layer = 12,
            n_positions = 1024,
            reorder_and_upcast_attn = False,
            resid_pdrop = 0.1,
            scale_attn_by_inverse_layer_idx = False,
            scale_attn_weights = True,
            summary_activation = None,
            summary_first_dropout = 0.1,
            summary_proj_to_labels = True,
            summary_type = "cls_index",
            summary_use_proj = True,
            # task_specific_params": {
            #     "text-generation": {
            #     "do_sample": true,
            #     "max_length": 50
            #     }
            # },
            torch_dtype = "float32",
            #transformers_version = "4.35.0",
            use_cache = True,
            vocab_size = tokenizer.vocab_size,
        )

        model = GPT2LMHeadModel( config )
    
    model.save_pretrained(output_dir)


    logging_dir = os.path.join(output_dir, 'logs')
    os.makedirs(logging_dir, exist_ok = True)
    
    training_args = TrainingArguments(
          output_dir=output_dir,
          overwrite_output_dir=overwrite_output_dir,
          per_device_train_batch_size=per_device_train_batch_size,
          num_train_epochs=num_train_epochs,
          save_total_limit=4,
          logging_dir=logging_dir,
      )
    
    trainer = Trainer(
          model=model,
          args=training_args,
          data_collator=data_collator,
          train_dataset=train_dataset,
    )
    

    trainer.train()
    trainer.save_model()

# %% load options for a config file if it exists.
config_filename = "config.yaml"
if os.path.exists(config_filename):
    options = OmegaConf.load(config_filename)
else:
    #make a empty options object just to simplify the defaults below.
    options = OmegaConf.create()

# %%
#Now load these options from OmegaConf using defaults if they are not there.
output_dir                   = options.output_dir                   if "output_dir"                  in options else "./out"
train_file_path              = options.train_file_path              if "train_file_path"             in options else "./bible.prep/train.txt"
per_device_train_batch_size  = options.per_device_train_batch_size  if "per_device_train_batch_size" in options else 8
num_train_epochs             = options.num_train_epochs             if "num_train_epochs"            in options else 5
save_steps                   = options.save_steps                   if "save_steps"                  in options else 500
from_scratch = options.get( "from_scratch", True )


model_name = "gpt2"
if not os.path.exists(output_dir):
    print( "Making output directory" )
    os.makedirs(output_dir)
else:
    print( "Found directory, continue training" )
    model_name = output_dir


# %%
train(
    train_file_path=train_file_path,
    model_name=model_name,
    output_dir=output_dir,
    overwrite_output_dir=True,
    per_device_train_batch_size=per_device_train_batch_size,
    num_train_epochs=num_train_epochs,
    save_steps=save_steps,
    from_scratch=from_scratch
)
# %%
