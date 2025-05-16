"""
This module imports the necessary packages and functions for the BaselineLLMSystem module.
"""
import os
import re
import time
import math


from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_gpt(messages, model):
    
    max_retries = 5
    retry_count = 0
    fatal = False
    fatal_reason = None
    while retry_count < max_retries:
        try:
            ################### use to be openai.Completion.create(), now ChatCompletion ###################
            ################### also parameters are different, now messages=, used to be prompt= ###################
            # note deployment_id=... not model=...
            result = client.chat.completions.create(
                model=model,
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

def get_table_string(table, row_limit = 100):
    """
    Convert a pandas DataFrame to a string with a specified row limit.
    :param table: The pandas DataFrame to convert
    :param row_limit: The maximum number of rows to include in the string
    :return: A string representation of the DataFrame
    """
    try: 
        #table = pd.read_csv(fp, engine='python', on_bad_lines='warn')
        if len(table) <= row_limit:
            return table.to_csv()
        # Randomly sample the table
        #table_string = table.sample(n=min(row_limit, len(table)), random_state=1)
        table_string = table.head(min(row_limit, len(table)))
        # Convert the table to a  comma-separated string
        table_string = table_string.to_csv()
        return table_string
    
        #return table.head(find_number_rows(table, token_limit)).to_csv(sep='|', index=False)
    except Exception as e:
        print("Error:", e) 
        return ""

def clean_nan(obj):
    """
    Convert NaN values to null in a nested structure for strict JSON compliance.
    :param obj: The JSON object to clean
    :return: The cleaned JSON object
    """
    if isinstance(obj, float) and math.isnan(obj):
        return None
    elif isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan(v) for v in obj]
    else:
        return obj

def extract_code(response, pattern=r'```python(.*?)```'):
        """
        Extract the code from the LLM response.
        :param response: LLM response string
        :return: Extracted code string
        """
        # Assuming the code is marked with ````python` and ````python`
        code = re.search(pattern, response, re.DOTALL)
        if code:
            return code.group(1).strip()
        return ""

def find_number_rows(table, token_limit = 900):
    # Get the first row of the table
    m = table.iloc[[0]].to_csv(sep='|', index=False)
    m = re.split('||\s+', m)
    m=[x for x in m if x != '' and x != '|']
    n_row = int(token_limit/len(m))
    if n_row < 1: return 1
    return n_row

if __name__ == "__main__":
    # Example usage
    prompt = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    response = call_gpt(prompt)
    print("Response:", response)