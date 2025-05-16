from benchmark.benchmark_api import System
import os
import pandas as pd


class ExampleBaselineSystem(System):
    def __init__(self, model: str, name="example", *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.dataset_directory = None  # TODO(SUT engineer): Update me
        self.model = model
        self.llm = None # TODO(SUT engineer): Update me

    def process_dataset(self, dataset_directory: str | os.PathLike) -> None:
        # read files based on the dataset_directory, could be pdf, csv, etc.
        # store the data in a dictionary
        # store the dictionary in self.dataset_directory
        self.dataset_directory = dataset_directory
        self.dataset = {}
        # read the files
        for file in os.listdir(dataset_directory):
            if file.endswith(".csv"):
                self.dataset[file] = pd.read_csv(os.path.join(dataset_directory, file))

    def serve_query(self, query: str) -> dict | str:
        results = self.llm.generate(query)
        # print(results)
        return results
