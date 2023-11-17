from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel, GPT2TokenizerFast, GPT2Tokenizer
from omegaconf import OmegaConf
import os

def load_model(model_path):
    model = GPT2LMHeadModel.from_pretrained(model_path)
    return model


def load_tokenizer(tokenizer_path):
    tokenizer = GPT2Tokenizer.from_pretrained(tokenizer_path)
    return tokenizer



def generate_text(sequence, max_length, model_path, tokenizer_path=None, top_k=50, top_p=0.95):
    if tokenizer_path is None: tokenizer_path = model_path
    model = load_model(model_path)
    tokenizer = load_tokenizer(tokenizer_path)
    ids = tokenizer.encode(f'{sequence}', return_tensors='pt')
    final_outputs = model.generate(
        ids,
        do_sample=True,
        max_length=max_length,
        pad_token_id=model.config.eos_token_id,
        top_k=top_k,
        top_p=top_p,
    )
    return tokenizer.decode(final_outputs[0], skip_special_tokens=True)





# %% load options for a config file if it exists.
config_filename = "config.yaml"
if os.path.exists(config_filename):
    options = OmegaConf.load(config_filename)
else:
    #make a empty options object just to simplify the defaults below.
    options = OmegaConf.create()

# %%
#Now load these options from OmegaConf using defaults if they are not there.
tokenizer_path = model = options.get( "output_dir", "./out")
#tokenizer_path = model = "gpt2"
#tokenizer_path = options.get( "output_dir", "./out"); model = os.path.join(tokenizer_path, "../out_backup/checkpoint-580500")


#sequence = input("sequence: ") #
#max_len = int(input("max length: ")) # 20

#sequence = "en arkhe epoiesen o theos ton ouranon kai ten gen TGT_NETfree"
#sequence = "en arkhe epoiesen o theos ton ouranon kai ten gen TGT_FinPR"
#sequence = "texetai de uion kai kaleseis to onoma autou iesoun, autos gar sosei ton laon autou apo ton amartion auton. TGT_NETfree"
#sequence = "epotisan de ton patera auton oinon en te nukti taute kai eiselthousa e presbutera ekoimethe meta tou patros autes ten nukta ekeinen kai ouk edei en to koimethenai auten kai anastenai TGT_GerNeUe"
sequence = "en arkhe epoiesen o theos ton ouranon kai ten gen TGT_GerNeUe"
max_len = (len(sequence.split(" "))+1)*5

for i in range(10):
    print( "test", i )
    print(generate_text(sequence, max_len, model, tokenizer_path=tokenizer_path))

