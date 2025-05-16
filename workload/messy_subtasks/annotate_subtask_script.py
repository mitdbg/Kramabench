import regex as re
import json
import sys
sys.path.append("./")
from benchmark.llm_tools.ollama_interface import OllamaInterface
import argparse


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--idx', type=int, help='the index of the task to process')
parser.add_argument('--domain', type=str, help='the domain of the task to process', default='archeology')
args = parser.parse_args()
idx = args.idx
domain = args.domain

with open(f"workload/messy_subtasks/{domain}_generated.json", 'r') as f:
    all_tasks = json.load(f)

task = all_tasks[idx]
print(f"Task: {task['id']}")
sub_questions = []
for jdx, kf in enumerate(task['key_functionalities']):
    ollama_interface = OllamaInterface()
    subtask_question = ollama_interface.get_subtask_from_function(
        solution_path=f"solutions/{domain}/{task['id']}.py",
        step=kf['step']
    )

    # Remove all text between <think> and </think> using regex
    cleaned = re.sub(r"<think>.*?</think>", "", subtask_question, flags=re.DOTALL).strip()
    print(f"\tKey functionality: {kf['step']}")
    print(f"\tSubtask question: {cleaned}")
    all_tasks[idx]['key_functionalities'][jdx]['query'] = cleaned
    # Check if the subtask question is empty    

json.dump(all_tasks, open(f"workload/messy_subtasks/{domain}_generated.json", 'w'), indent=2)