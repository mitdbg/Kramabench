import argparse
import datetime
from email import parser
import json
import logging
import numpy as np
import os
import pandas as pd

from benchmark import Benchmark
from benchmark.benchmark_utils import print_warning

logging.basicConfig(level=logging.WARNING)
    
def aggregate_results(system_name, results_df):
    # Aggregate metrics
    print("Aggregating results...")
    workload_results = []

    for (workload, metric), group in results_df.groupby(["workload", "metric"]):
        if metric in ['code', 'model_output', 'exit_code', 'stderr']:
            continue
        group_dropped_na = group.dropna()
        if metric == "success":
            group_dropped_na["value"] = group_dropped_na["value"].astype(bool).astype(int)

        if metric != "llm_code_eval":
            mean = group_dropped_na["value"].mean()
            std = group_dropped_na["value"].std() if len(group_dropped_na) > 1 else 0
            workload_results.append({
                "sut": system_name,
                "workload": f"{workload}.json",
                "metric": metric,
                "value_mean": mean,
                "value_std": std,
                "value_sum": group_dropped_na["value"].sum(),
                "value_support": len(group_dropped_na),
                "total_value_support": len(group)
            })
        else: # Deal with LLM code evaluation
            value_support = 0
            values = []
            for _, row in group_dropped_na.iterrows():
                eval_list = json.loads(row['value'][1:-1])
                eval_list_int = [1 if b else 0 for b in eval_list]
                if len(eval_list) > 0:
                    values.append(sum(eval_list_int) / len(eval_list))
                    value_support += 1
            workload_results.append({
                "sut": system_name,
                "workload": f"{workload}.json",
                "metric": metric,
                "value_mean": np.mean(values),
                "value_std": np.std(values),
                "value_sum": sum(values),
                "value_support": value_support,
                "total_value_support": len(group)
            })

    workload_results_df = pd.DataFrame(workload_results)
    total_support = 0
    total_score = 0
    for _, row in workload_results_df.iterrows():
        if row["metric"] in ["success", "llm_paraphrase", "rae_score", "f1", "f1_approximate"]:
            total_support += row["total_value_support"]
            total_score += row["value_support"] * row["value_mean"]
    print(f"Total score is: {total_score/total_support*100}")
    return workload_results_df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sut", type=str, default="BaselineLLMSystemGPTo3FewShot", help="The system under test.")
    parser.add_argument("--workload", type=str, default="legal", help="Name of workload to benchmark. Default: legal")
    parser.add_argument("--result_directory", type=str, default="results", help="Directory to store benchmark results. Default: results")
    parser.add_argument("--task_fixtures", type=str, default="benchmark/fixtures", help="Directory containing task fixture files. Default: benchmark/fixtures")
    parser.add_argument("--project_root", type=str, default=os.getcwd(), help="Project root. Default: current working directory")
    parser.add_argument("--use_system_cache", action="store_true", default=False, help="Use cached system outputs if available. Default: False")
    parser.add_argument("--use_evaluation_cache", action="store_true", default=False, help="Use cached per-task evaluations if available. Default: False")
    parser.add_argument("--cache_system_output", action="store_true", default=True, help="Cache system output. Default: True")
    parser.add_argument("--use_deepresearch_subset", action="store_true", default=False, help="Whether to use the subset of files from deepresearch experiments. Default: False")
    parser.add_argument("--use_truth_subset", action="store_true", default=False, help="Whether to use the subset of files from truth data. Default: False")
    parser.add_argument("--verbose", action="store_true", default=False, help="Verbose logging. Default: False")
    parser.add_argument("--run_subtasks", action="store_true", default=False, help="Run subtasks if set. Default: False")
    parser.add_argument("--no_pipeline_eval", action="store_true", default=False, help="Skip pipeline design and implementation evaluation (which uses API calls). Default: False")
    parser.add_argument("--num_workers", type=int, default=8, help="Number of parallel workers for task execution. Default: 8")
    args = parser.parse_args()

    system_name = args.sut
    verbose = args.verbose

    project_root_dir = args.project_root
    result_root_dir = os.path.join(project_root_dir, args.result_directory)

    # Setup output (cache maintained by benchmark) and scratch directories for system under test
    workload = args.workload
    system_result_dir = os.path.join(result_root_dir, system_name)
    workload_path = os.path.join(project_root_dir, f"workload/{workload}.json")
    system_output_dir = os.path.join(project_root_dir, f"system_scratch/{system_name}")
    os.makedirs(system_output_dir, exist_ok=True)
    os.makedirs(system_result_dir, exist_ok=True)

    # Setup benchmark evaluation util directory
    task_fixture_dir = os.path.join(project_root_dir, args.task_fixtures)
    aggregated_results_path = os.path.join(result_root_dir, "aggregated_results.csv")
    evaluate_pipeline = not args.no_pipeline_eval

    print(f"Starting benchmark workflow on dataset: {workload}")
    if "-tiny" in workload:
        print("Using tiny workload for testing")
        dataset_name = workload.replace("-tiny", "")
        dataset_directory = os.path.join(project_root_dir, f"data/{dataset_name}/tiny")
    else:
        # "<domain>_alternative" workloads (e.g. astronomy_alternative.json) hold
        # alternative gold answers for tasks of an existing domain and run
        # against that domain's data directory.
        dataset_name = workload.replace("_alternative", "")

    results_df = None
    if args.use_evaluation_cache:
        # parse the most recent workload file based on the timestamps in the filename
        timestamp = None
        measures_path = ""
        for filename in os.listdir(system_result_dir):
            if filename.startswith(dataset_name) and filename.endswith(".csv"):
                workload_timestamp = filename.split(".csv")[0].split("measures_")[1]
                workload_timestamp = datetime.datetime.strptime(workload_timestamp, "%Y%m%d_%H%M%S")
                if timestamp is None or workload_timestamp > timestamp:
                    measures_path = os.path.join(system_result_dir, filename)
                    timestamp = workload_timestamp

        if not os.path.exists(measures_path):
            print_warning(f"Cached evaluation results not found. Running the benchmark to generate them.")
        else:
            print(f"Using cached detailed evaluation results on workload {workload} from time: {timestamp}")
            results_df = pd.read_csv(measures_path)
            converted_df = pd.to_numeric(results_df['value'], errors='coerce')
            results_df['value'] = converted_df.combine_first(results_df['value'])

            if not args.run_subtasks:
                results_df = results_df[results_df['task_id'].apply(lambda x: x.count('-') < 3)]
                results_df = results_df[results_df['metric'] != 'llm_code_eval']

    if not args.use_evaluation_cache or results_df is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        measures_path = os.path.join(system_result_dir, f"{workload}_measures_{timestamp}.csv")
        benchmark = Benchmark(
            system_name=system_name,
            task_fixture_directory=task_fixture_dir,
            system_output_directory=system_output_dir,
            use_system_cache=args.use_system_cache,
            cache_system_output=args.cache_system_output,
            verbose=verbose,
            run_subtasks=args.run_subtasks,
            use_deepresearch_subset=args.use_deepresearch_subset,
            evaluate_pipeline=evaluate_pipeline,
            use_truth_subset = args.use_truth_subset,
            num_workers=args.num_workers
        )

        dataset_directory = os.path.join(project_root_dir, f"data/{dataset_name}/input")

        evaluation_results = benchmark.run_benchmark(
            dataset_directory=dataset_directory,
            results_directory=system_result_dir,
            workload_path=workload_path,
            verbose=verbose
        )

        # Pretty printing evaluation_results
        flat_measures = []
        for task_result in evaluation_results:
            # TODO: Implement system planned subtask result evaluation
            task_id = task_result["task_id"]
            for metric, value in task_result.items():
                if metric in ["task_id", "code", "model_output", "subresponses"]:
                    continue
                parsed_value = value
                if isinstance(value, list): # LLM code eval results, handle list
                    parsed_value = f"\"{json.dumps(value)}\""
                flat_measures.append({
                    "sut": system_name,
                    "workload": workload,
                    "task_id": task_id,
                    "metric": metric,
                    "value": parsed_value
                })

        results_df = pd.DataFrame(flat_measures)
        results_df.to_csv(measures_path, index=False)

        if verbose:
            print(results_df)

    aggregated_df = aggregate_results(system_name, results_df)
    # Update aggregated results file
    if os.path.exists(aggregated_results_path):
        old_aggregated_df = pd.read_csv(aggregated_results_path)
        old_aggregated_df = old_aggregated_df[
            ~((old_aggregated_df["sut"] == system_name) & (old_aggregated_df["workload"] == f"{workload}.json"))
        ]
        aggregated_df = pd.concat([old_aggregated_df, aggregated_df])

    aggregated_df.to_csv(aggregated_results_path, index=False)

    # print("Done. Aggregated results:")
    # print(aggregated_df[aggregated_df["workload"] == workload_name])


if __name__ == "__main__":
    main()
