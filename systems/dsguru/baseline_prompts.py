QUESTION_PROMPT = """
You are a helpful assistant that generates a plan to solve the given request, and you'll be given:Your task is to answer the following question based on the provided data sources.
Question: {query}
Data file names: {file_names}

The following is a snippet of the data files:
{data}

Now think step-by-step carefully. 
First, provide a step-by-step reasoning of how you would arrive at the correct answer.
Do not assume the data files are clean or well-structured (e.g., missing values, inconsistent data type in a column).
Do not assume the data type of the columns is what you see in the data snippet (e.g., 2012 in Year could be a string, instead of an int). So you need to convert it to the correct type if your subsequent code relies on the correct data type (e.g., cast two columns to the same type before joining the two tables).
You have to consider the possible data issues observed in the data snippet and how to handle them.
Output the steps in a JSON format with the following keys:
- id: always "main-task" for the main task. For each subtask, use "subtask-1", "subtask-2", etc.
- query: the question the step is trying to answer. Copy down the question from above for the main task.
- data_sources: the data sources you need to check to answer the question. Include all the file names you need for the main task.
- subtasks: a list of subtasks. Each subtask should have the same structure as the main task.
For example, a JSON object for the task might look like this:
{example_json}
You can have multiple steps, and each step should be a JSON object.
Your output for this task should be a JSON array of JSON objects.
Mark the JSON array with ````json` and ````json` to indicate the start and end of the code block.

Then, provide the corresponding Python code to extract the answer from the data sources. 
The data sources you may need to answer the question are: {file_paths}.

If possible, print the answer (in a JSON format) to each step you provided in the JSON array using the print() function.
Use "id" as the key to print the answer.
For example, if you have an answer to subtask-1, subtask-2, and main-task (i.e., the final answer), you should print it like this:
print(json.dumps(
{{"subtask-1": answer1, 
"subtask-2": answer2, 
"main-task": answer
}}, indent=4))
You can find a suitable indentation for the print statement. Always import json at the beginning of your code.

Mark the code with ````python` and ````python` to indicate the start and end of the code block.
"""

QUESTION_PROMPT_NO_DATA = """
You are a helpful assistant that generates a plan to solve the given request, and you'll be given:Your task is to answer the following question based on the provided data sources.
Question: {query}
Data file names: {file_names}

Now think step-by-step carefully. 
First, provide a step-by-step reasoning of how you would arrive at the correct answer.
Do not assume the data files are clean or well-structured (e.g., missing values, inconsistent data type in a column).
Do not assume the data type of the columns is what you see in the data snippet (e.g., 2012 in Year could be a string, instead of an int). So you need to convert it to the correct type if your subsequent code relies on the correct data type (e.g., cast two columns to the same type before joining the two tables).
You have to consider the possible data issues observed in the data snippet and how to handle them.
Output the steps in a JSON format with the following keys:
- id: always "main-task" for the main task. For each subtask, use "subtask-1", "subtask-2", etc.
- query: the question the step is trying to answer. Copy down the question from above for the main task.
- data_sources: the data sources you need to check to answer the question. Include all the file names you need for the main task.
- subtasks: a list of subtasks. Each subtask should have the same structure as the main task.
For example, a JSON object for the task might look like this:
{example_json}
You can have multiple steps, and each step should be a JSON object.
Your output for this task should be a JSON array of JSON objects.
Mark the JSON array with ````json` and ````json` to indicate the start and end of the code block.

Then, provide the corresponding Python code to extract the answer from the data sources. 
The data sources you may need to answer the question are: {file_paths}.

If possible, print the answer (in a JSON format) to each step you provided in the JSON array using the print() function.
Use "id" as the key to print the answer.
For example, if you have an answer to subtask-1, subtask-2, and main-task (i.e., the final answer), you should print it like this:
print(json.dumps(
{{"subtask-1": answer1, 
"subtask-2": answer2, 
"main-task": answer
}}, indent=4))
You can find a suitable indentation for the print statement. Always import json at the beginning of your code.

Mark the code with ````python` and ````python` to indicate the start and end of the code block.
"""