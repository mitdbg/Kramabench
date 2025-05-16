### Structure of the repository

The main benchmark repository contains the following folders:
- `benchmark`: This folder contains the code to run the benchmark.
- `data`: This folder contains the input data to be used in solving the benchmark.
- `quickstart`: This folder contains the code for the quickstart example.
- `results`: This folder contains the output data from the different systems under test, produced while running benchmark.
- `scripts`: This folder contains helper scripts.
- `systems`: This folder contains the code to execute the different systems under test.
- `utils`: This folder contains utility code and helper scripts.
- `workload`: This folder contains the questions of the benchmark in JSON format.

### Add a new dataset/questions to the benchmark

To add a new dataset to the benchmark, you need to follow these steps:
1. Create a new folder in the `data` directory with the name of the dataset. 
The name of the dataset should be a semantic name that reflects the domain or the type of data it contains, e.g., `environment` is the name of the dataset for Massachussets Water pollution data. This name will be used in the benchmark as the tag for the questions associated to the dataset.

2. The structure of any dataset folder is the following.
    - A `studies` folder that contains studies, e.g., reports, papers, or otherwise human-readable data science reports that are used to identify interesting pipelines to include in the benchmark. 
    - A `raw` folder should contain any raw data files collected when assembling the questions. The raw folder is not synced in the repository (it might contain very large files)
    - A `resources.txt` file should contain a list of resources that are used to create the dataset. This file is purely for human consumption, it should contain the URLs of the original studies and raw data collected. The `resources.txt` file is used to track the provenance of the dataset and to provide references for the questions.
    - An `input` folder that contains the data files that are used to run the benchmark. should be placed in an `input` folder. For example, to run the environment questions, the systems will load the content of `data\environment\input`. The input folder will be synced in the repository.

3. Collect the studies to create the dataset question. Place them under the `data\{dataset-id}\studies` folder. Document the studies in the `resources.txt` file.

4. Collect the data files from the original studies and place them in the  `data\{dataset-id}\raw` folder. Document the raw data in the `resources.txt` file, add descriptions, caveats, etc. etc.

5. When curating the questions, you should create a new file in the `workload` directory with the name of the dataset. The file will be named `{dataset-id}.json`. The file should contain a JSON object with the following structure (refer to quickstart notebook for more details):

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