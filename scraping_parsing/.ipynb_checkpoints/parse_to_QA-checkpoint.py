#!/usr/bin/env python
# coding: utf-8

# In[44]:


# import sys
# sys.executable


# In[45]:


import os
import glob
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import transformers
import torch


# In[7]:





# In[ ]:


#in case you run out of storage
# import os
# os.environ['TRANSFORMERS_CACHE'] = /scratch/md5121/


# In[12]:


import transformers
import torch

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

# Read the token from the file
with open("hf_token.txt", 'r') as file:
    huggingface_token = file.read().strip()

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device="cuda",
    token=huggingface_token
)


# In[47]:


tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3.1-8B-Instruct", token=huggingface_token)


# In[48]:


messages = [
    {"role": "system", "content": "You are a philosopher who responds like one."},
    {"role": "user", "content": "Who are you?"},
]

prompt = pipeline.tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
)

terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

outputs = pipeline(
    prompt,
    max_new_tokens=256,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.6,
    top_p=0.9,
)
print(outputs[0]["generated_text"][len(prompt):])


# In[15]:


# get_ipython().run_line_magic('pip', 'install -qq -U langchain tiktoken pypdf faiss-gpu')


# In[49]:


# get_ipython().run_line_magic('pip', 'install -U langchain-community')


# In[50]:


import langchain

# loaders
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import DirectoryLoader

# splits
from langchain.text_splitter import RecursiveCharacterTextSplitter


# In[5]:


split_chunk_size = 800
split_overlap = 100


# In[2]:


import os

class TextFileLoader:
    def __init__(self, directory):
        self.directory = directory
    
    def load(self):
        documents = []
        for filename in os.listdir(self.directory):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.directory, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    documents.append({"text": text})
        return documents

# Define the path to the data directory
data_path = "articles_text/SEP/"

# Set up the TextFileLoader to load .txt files
loader = TextFileLoader(data_path)

# Load the documents
documents = loader.load()

# Print number of documents loaded
print(f"Loaded {len(documents)} documents.")


# In[154]:





# In[112]:





# In[3]:


print(f'We have    {len(documents)} pages in total')


# In[6]:


from langchain_text_splitters import RecursiveCharacterTextSplitter

# Initialize the text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = split_chunk_size,
    chunk_overlap = split_overlap
)

# Convert the documents to the required format
class Document:
    def __init__(self, text):
        self.page_content = text
        self.metadata = {}  # Add any metadata if needed

# Convert dictionaries to Document instances
formatted_documents = [Document(doc["text"]) for doc in documents]

# Split documents
texts_split = text_splitter.split_documents(formatted_documents)

# Print number of chunks created
print(f'We have created {len(texts_split)} chunks from {len(documents)} documents')


# In[9]:


texts = texts_split


# In[10]:


print(len(texts))


# In[57]:


import re
import json


# In[58]:


def run_llm(tokenizer, prompt):
    sequences = pipeline(
            prompt,
            do_sample=False,
            top_k=10,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
            temperature=0,
            max_length=1000,
        )
    
    return sequences[0]['generated_text'].replace(prompt, "")
answers = []
def generate_answers(text):    
    additional_text = '''
    The format of the output should strictly be:
    {
        "conversations": [
            {"from": "human", "value": "Question"},
            {"from": "gpt", "value": "Answer"}
        ]
    }.
    Provide only this JSON and nothing else.
    
    Instructions:
    - Generate two questions and their corresponding answers from the provided text.
    - The questions should be those that a layman might ask about the philosophical concepts discussed in the text.
    - The answers should be crafted as if a philosopher is explaining the concepts to a layman.
    - Ensure that the answers are as lucid and clear as possible.
    - Include references or sources where applicable to support the explanations.
    '''
    
    # Assuming 'content' contains the text from the PDF you scraped
    ans = run_llm(tokenizer, f'Generate two questions and their corresponding answers based on the following text. {additional_text} "{text}"')
    answers.append(ans)
for text in texts:
    generate_answers(text)



# In[59]:





# In[73]:





# In[74]:


import json
import re
formatted_conversations = []
# Define a function to extract JSON objects from text
def extract_json_objects(text):
    json_objects = []
    json_pattern = re.compile(r'\{(?:[^{}"]|"(?:\\.|[^"\\])*")*\}')
    matches = json_pattern.findall(text)
    
    for match in matches:
        try:
            obj = json.loads(match)
            json_objects.append(obj)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {match} Error: {e}")
    
    return json_objects

# Function to format conversations in a consistent structure
def format_conversations(json_objects):
    
    
    
    for i in range(0, len(json_objects), 2):
        conversation_dict = {"conversations": []}
        human_obj = json_objects[i]
        gpt_obj = json_objects[i + 1] if i + 1 < len(json_objects) else None
        
        if 'from' in human_obj and human_obj['from'] == 'human':
            conversation = {"human": human_obj['value']}
        if gpt_obj and 'from' in gpt_obj and gpt_obj['from'] == 'gpt':
            conversation["gpt"] = gpt_obj['value']
        
        conversation_dict["conversations"].append(conversation)
        formatted_conversations.append(conversation_dict)
    
    
    
    return formatted_conversations

for sample_data in answers:
    # Extract JSON objects from the sample data
    json_objects = extract_json_objects(sample_data)
    # Format conversations consistently
    formatted_conversations = format_conversations(json_objects)

# Write formatted conversations to a file
with open('parsed_convos.json', 'w') as f:
    json.dump(formatted_conversations, f, indent=4)


print("Conversations dumped successfully in parsed_convos.json")
print(f"Total number of JSON objects found: {len(json_objects)}")




