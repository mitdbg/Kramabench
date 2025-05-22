# KramaBench
*KramaBench* is an open-source benchmark for **end-to-end data-science agents**.
Unlike question-answer–only corpora, each task in KramaBench asks a system to build a *complete* data pipeline: load raw files, clean them, transform them, and compute a final answer.
Because ground-truth code is provided, KramaBench can evaluate both the **quality of the final answer** *and* the **correctness of intermediate steps**.

## Breakdown of tasks per domain

| Domain      |  #Tasks | #Sub-tasks | % “Hard” | File count |   Raw size |
| ----------- | ------: | ---------: | ---------: | ---------: | ---------: |
| Archaeology |      12 |         71 |       50 % |          5 |     7.5 MB |
| Astronomy   |      12 |         68 |       50 % |      1 556 |     486 MB |
| Biomedical  |       9 |         38 |       67 % |          7 |     175 MB |
| Environment |      20 |        148 |       70 % |         37 |      31 MB |
| Legal       |      30 |        188 |       53 % |        136 |     1.3 MB |
| Wildfire    |      21 |        120 |       71 % |         23 |       1 GB |
| **Total**   | **104** |    **633** |   **61 %** |      1 764 | **1.7 GB** |

Hard tasks are tasks whose end-to-end solution requires advanced wrangling and transformation steps.

### What does a task look like?

1. **Natural-language prompt** (e.g. *“What is the average Potassium in ppm from the first and last time the study recorded people in the Maltese area?”*).
2. **Reference pipeline** broken into • *key functionalities* and • *natural-language sub-tasks* that test those functionalities individually.

---

### Structure of the repository

The main benchmark repository contains the following folders:
- `benchmark`: This folder contains the code to run the benchmark.
- `data`: This folder contains the input data to be used in solving the benchmark.
- `quickstart`: This folder contains the code for a quickstart example.
- `results`: This folder contains the output data from the different systems under test, produced while running benchmark.
- `scripts`: This folder contains helper scripts.
- `systems`: This folder contains the code to execute the different systems under test.
- `utils`: This folder contains utility code and helper scripts.
- `workload`: This folder contains the questions of the benchmark in JSON format.

## Installation

```bash
git clone https://github.com/<you>/KramaBench.git
cd KramaBench

# create env & install deps
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # numpy, pandas, tqdm, openai-sdk, …
```

## Quick-start — run the benchmark

The **evaluation harness** is a single script:

```bash
python evaluate.py \
  --sut YourSUT            \  # label for this run
  --dataset_name legal          \  # domain to test
  --workload_filename legal.json \
  --verbose
```

Key CLI flags (see `--help`):

| Flag                  | Default                       | Purpose                                                    |
| --------------------- | ----------------------------- | ---------------------------------------------------------- |
| `--sut`               | `YourSUT` | Arbitrary name for your System Under Test (SUT).           |
| `--dataset_name`      | `legal`                       | Must match the domain contained in the workload file.      |
| `--workload_filename` | `legal.json`             | Which set of tasks to execute.                             |
| `--use_system_cache`  | *(false)*                     | Re-use previous system outputs if they exist.              |
| `--skip_subtasks`     | *(false)*                     | Evaluate only the final answer (faster, but less insight). |

`evaluate.py` produces:

```
results/<SUT>/<workload>_measures_<timestamp>.csv   # fine-grained metrics
results/aggregated_results.csv                      # one-row-per-domain summary
```

---

## Writing your own System Under Test (SUT)

1. **Implement a Python class** that, given
   `dataset_directory` and the JSON prompt, returns either:

   * the final answer, **or**
   * executable Python that produces the answer (recommended; lets the harness inspect intermediate values).
2. Place any temporary files under the path passed to you (`system_output_directory`).
3. Make your class importable by `benchmark/Benchmark`; then run `evaluate.py --sut YourClassName`.

---

## Scoring & metrics

For every task the harness logs:

* **Exact-match metrics**: BLEU & ROUGE for strings mean-relative-absolute-error for numerics.
* **LLM code-eval**: unit tests auto-generated from sub-task ground truth.
* **Bootstrapped rubric** that rewards partial credit when the model paraphrases the correct idea.

Aggregation logic lives in `aggregate_results()` inside `evaluate.py`.

---

## Baseline : DS-GURU

DS-GURU is a minimalist agent that:

1. **Samples rows** from every file in the domain lake.
2. Prompts an LLM with the task, the sample, and strict instructions on cleaning/typing.
3. **Executes** the generated Python, sending back errors/output to the LLM for one retry loop.&#x20;

---

## Citing KramaBench

If you use KramaBench in academic work, please cite the preprint:

```
@misc{lai2025KramaBench,
  title  = {KramaBench: Evaluating End-to-End Data-Science Agents},
  author = {Eugenie Lai and Gerardo Vitagliano and Ziyu Zhang and *et al.*},
  year   = {2025},
}
```

---

### Task structure

The structure of any task inside the `{domain}.json` file is the following:

```json
[
    {   "id": "{dataset-id}-{difficulty}-1",
        "query": "...",
        "answer": "...",
        "answer_type": "...",
        "data_sources": ["...", "..."],
        "subtasks":[{
            "..."
        }]
    }
]
``` 