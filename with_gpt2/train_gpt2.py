# %%

#pip install accelerate -U
#pip install transformers[torch]
#pip install omegaconf

# %%
# import the things.

import os
import pandas as pd
import numpy as np
import re
from transformers import TextDataset, DataCollatorForLanguageModeling
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import Trainer, TrainingArguments
from omegaconf import OmegaConf

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
          num_train_epochs, save_steps ):
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    train_dataset = load_dataset(train_file_path, tokenizer)
    data_collator = load_data_collator(tokenizer)
    
    tokenizer.save_pretrained(output_dir)
      
    model = GPT2LMHeadModel.from_pretrained(model_name)
    
    model.save_pretrained(output_dir)
    
    training_args = TrainingArguments(
          output_dir=output_dir,
          overwrite_output_dir=overwrite_output_dir,
          per_device_train_batch_size=per_device_train_batch_size,
          num_train_epochs=num_train_epochs,
          save_total_limit=4,
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


# %%
train(
    train_file_path=train_file_path,
    model_name="gpt2",
    output_dir=output_dir,
    overwrite_output_dir=True,
    per_device_train_batch_size=per_device_train_batch_size,
    num_train_epochs=num_train_epochs,
    save_steps=save_steps
)
# %%
