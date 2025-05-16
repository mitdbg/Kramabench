"""
This file contains the Generator classes and generator factory.
"""
from __future__ import annotations
import logging

import os
import time
import ollama

from openai import OpenAI

# from tenacity import retry, stop_after_attempt, wait_exponential
from together import Together
import PyPDF2

OpenAIModelList = ["gpt-4o", "gpt-4o-mini", "gpt-4o-v", "gpt-4o-mini-v", "o3"]
TogetherModelList = ["google/gemma-2b-it", "meta-llama/Llama-2-13b-chat-hf", "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B","google/gemma-3-27b-it", "deepseek-ai/DeepSeek-R1", "Qwen/Qwen2.5-Coder-32B-Instruct", "meta-llama/Llama-3.3-70B-Instruct-Turbo"]

def get_api_key(key: str) -> str:
    # get API key from environment or throw an exception if it's not set
    if key not in os.environ:
        print(f"KEY: {key}")
        print(f"{os.environ.keys()}")
        raise ValueError("key not found in environment variables")

    return os.environ[key]


class Generator():
    def __init__(self, model: str, verbose=False):
        self.model = model
        if model in OpenAIModelList:
            self.client = OpenAI(api_key=get_api_key("OPENAI_API_KEY"))
        elif model in TogetherModelList:
            self.client = Together(api_key=get_api_key("TOGETHER_API_KEY"))

        self.verbose = verbose

    def generate(self, prompt: str) -> str:
        if self.verbose:
            print(f"Generating with {self.model}")
            print(f"Prompt: {prompt}")
        if isinstance(self.client, OpenAI):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                # temperature=0.0,
                max_tokens=4000,
            )
            return response.choices[0].message.content
        elif isinstance(self.client, Together):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
            )
            return response.choices[0].message.content
        else:
            raise Exception(f"Unsupported model: {self.model}")
        

    # GV: This function is the call_gpt function from the baseline_utils.py file. But for Ollama we substitute it
    def __call__(self, messages):
    
        max_retries = 5
        retry_count = 0
        fatal = False
        fatal_reason = None
        while retry_count < max_retries:
            try:
                ################### use to be openai.Completion.create(), now ChatCompletion ###################
                ################### also parameters are different, now messages=, used to be prompt= ###################
                # note deployment_id=... not model=...
                result = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    # temperature=0.2,
                )
                
                break # break out of while loop if no error
            
            except Exception as e:
                print(f"An error occurred: {e}.")
                if "context_length_exceeded" in f"{e}":
                    fatal = True
                    fatal_reason = f"{e}"
                    break
                else:
                    print("Retrying...")
                    retry_count += 1
                    time.sleep(10 * retry_count)  # Wait 
        
        if fatal:
            print(f"Fatal error occured. ERROR: {fatal_reason}")
            res = f"Fatal error occured. ERROR: {fatal_reason}"
        elif retry_count == max_retries:
            print("Max retries reached. Skipping...")
            res = "Max retries reached. Skipping..."
        else:
            try:
                res = result.choices[0].message.content
            except Exception as e:
                print("Error:", e)
                res = ""
            #print(res)
        return res

def pdf_to_text(pdf_path: str) -> str:
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

class OllamaGenerator(Generator):
    def __init__(self, model: str, 
                verbose=False,
                server_url="http://localhost:11434",
                *args, 
                **kwargs
                ):
        super().__init__(model, verbose)
        self.model = model
        self.client = ollama.Client(host=server_url)


    def __call__(self, messages):

        max_retries = 5
        retry_count = 0
        fatal = False
        fatal_reason = None
        while retry_count < max_retries:

            try:
                response = self.client.chat(
                    model=self.model,
                    messages=messages,
                    format="json",
                    stream=False,
                    options= {"num_ctx": 640000}
                )
                if not response["done"]:
                    logging.warning("WARNING - Conversation kept going! Maybe output is truncated.")
                break

            except Exception as e:
                print(f"An error occurred: {e}.")
                if "context_length_exceeded" in f"{e}":
                    fatal = True
                    fatal_reason = f"{e}"
                    break
                else:
                    print("Retrying...")
                    retry_count += 1
                    time.sleep(10 * retry_count)  # Wait 
        
        if fatal:
            print(f"Fatal error occured. ERROR: {fatal_reason}")
            res = f"Fatal error occured. ERROR: {fatal_reason}"
        elif retry_count == max_retries:
            print("Max retries reached. Skipping...")
            res = "Max retries reached. Skipping..."
        else:
            try:
                res = response["message"]["content"]
            except Exception as e:
                print("Error:", e)
                res = ""
            #print(res)
        return res
