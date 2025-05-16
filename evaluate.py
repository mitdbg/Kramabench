import argparse
import csv
import datetime
import json
import numpy as np
import os
import pandas as pd

from benchmark import Benchmark

def aggregate_results(system_name, results_df):
    # Aggregate metrics
    print("Aggregating results...")
    results_df_additional = pd.DataFrame(columns=results_df.columns)
    workload_results = []
    for (workload, task_id), group in results_df.groupby(["workload", "task_id"]):
        group_dropped_na = group.dropna()
        if len(group[group["metric"] == "bleu"]) > 0:
            bleu = group[group["metric"] == "bleu"]["value"].values[0]
            rouge = group[group["metric"] == "rouge"]["value"].values[0]
            sut = group[group["metric"] == "rouge"]["sut"].values[0]
            llm_paraphrase = group[group["metric"] == "llm_paraphrase"]["value"].values[0]
            score = 0
            if int(llm_paraphrase) > 0:
                score = 1
            elif bleu > 0.2:
                score = rouge
            results_df_additional.loc[len(results_df_additional)] = [sut, workload, task_id, "string_bootstrap", score]
        elif len(group[group["metric"] == "mean_relative_absolute_error"]) > 0:
            rae = group[group["metric"] == "mean_relative_absolute_error"]["value"].values[0]
            sut = group[group["metric"] == "mean_relative_absolute_error"]["sut"].values[0]
            results_df_additional.loc[len(results_df_additional)] = [sut, workload, task_id, "rae_score", 1 / (1+rae)]
    
    results_concat_df = pd.concat([results_df, results_df_additional], ignore_index=True)

    for (workload, metric), group in results_concat_df.groupby(["workload", "metric"]):
        group_dropped_na = group.dropna()
        if metric != "llm_code_eval":
            mean = group_dropped_na["value"].mean()
            std = group_dropped_na["value"].std() if len(group_dropped_na) > 1 else 0
            workload_results.append({
                "sut": system_name,
                "workload": workload,
                "metric": metric,
                "value_mean": mean,
                "value_std": std,
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
                "workload": workload,
                "metric": metric,
                "value_mean": np.mean(values),
                "value_std": np.std(values),
                "value_support": value_support,
                "total_value_support": len(group)
            })

    workload_results_df = pd.DataFrame(workload_results)
    total_support = 0
    total_score = 0
    for _, row in workload_results_df.iterrows():
        if row["metric"] in ["f1", "string_bootstrap", "rae_score", "success"]:
            total_support += row["total_value_support"]
            total_score += row["value_support"] * row["value_mean"]
    print(f"Total score is: {total_score/total_support}")
    return workload_results_df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sut", type=str, default="BaselineLLMSystemGPT4oNaive", help="The system under test.")
    parser.add_argument("--dataset_name", type=str, default="legal", help="Name of dataset.")
    parser.add_argument("--workload_filename", type=str, default="legal-tiny.json", help="Name of workload JSON file.")
    parser.add_argument("--result_directory", type=str, default="results", help="Directory to store benchmark results.")
    parser.add_argument("--task_fixtures", type=str, default="benchmark/fixtures", help="Directory containing task fixture files.")
    parser.add_argument("--project_root", type=str, default=os.getcwd(), help="Project root.")
    parser.add_argument("--use_system_cache", action="store_true", default=False, help="Use cached system outputs if available.")
    parser.add_argument("--use_evaluation_cache", action="store_true", default=False, help="Use cached per-task evaluations if available.")
    parser.add_argument("--cache_system_output", action="store_true", default=True, help="Cache system output.")
    parser.add_argument("--verbose", action="store_true", default=False, help="Verbose logging.")
    parser.add_argument("--skip_subtasks", action="store_true", default=False, help="Skips subtasks.")
    args = parser.parse_args()

    system_name = args.sut
    verbose = args.verbose

    project_root_dir = args.project_root
    result_root_dir = os.path.join(project_root_dir, args.result_directory)

    # Setup output (cache maintained by benchmark) and scratch directories for system under test
    system_result_dir = os.path.join(result_root_dir, system_name)
    workload_filename = args.workload_filename
    workload_name = os.path.basename(workload_filename)
    workload_path = os.path.join(project_root_dir, f"workload/{workload_filename}")
    system_output_dir = os.path.join(project_root_dir, f"system_scratch/{system_name}")
    os.makedirs(system_output_dir, exist_ok=True)
    os.makedirs(system_result_dir, exist_ok=True)

    # Setup benchmark evaluation util directory
    task_fixture_dir = os.path.join(project_root_dir, args.task_fixtures)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    measures_path = os.path.join(system_result_dir, f"{workload_name.split('.')[0]}_measures_{timestamp}.csv")
    aggregated_results_path = os.path.join(result_root_dir, "aggregated_results.csv")

    if not args.use_evaluation_cache or not os.path.exists(measures_path):
        benchmark = Benchmark(
            system_name=system_name,
            task_fixture_directory=task_fixture_dir,
            system_output_directory=system_output_dir,
            use_system_cache=args.use_system_cache,
            cache_system_output=args.cache_system_output,
            verbose=verbose,
            skip_subtasks=args.skip_subtasks,
        )

        print(f"Starting benchmark workflow on workload: {workload_name}")
        if args.dataset_name not in workload_name:
            raise Exception(f"Dataset name {args.dataset_name} not found in workload {workload_name}.")
        _, evaluation_results = benchmark.run_benchmark(
            dataset_directory=os.path.join(project_root_dir, f"data/{args.dataset_name}/input"),
            code_understanding_directory=os.path.join(project_root_dir, f"data/{args.dataset_name}/studies/understanding"),
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
                if metric == "task_id":
                    continue
                parsed_value = value
                if isinstance(value, list): # LLM code eval results, handle list
                    parsed_value = f"\"{json.dumps(value)}\""
                flat_measures.append({
                    "sut": system_name,
                    "workload": workload_name,
                    "task_id": task_id,
                    "metric": metric,
                    "value": parsed_value
                })

        results_df = pd.DataFrame(flat_measures)
        results_df.to_csv(measures_path, index=False)

        if verbose:
            print(results_df)
    else:
        print(f"Using cached detailed evaluation results on workload {workload_name}")
        results_df = pd.read_csv(measures_path)
        converted_df = pd.to_numeric(results_df['value'], errors='coerce')
        results_df['value'] = converted_df.combine_first(results_df['value'])

    aggregated_df = aggregate_results(system_name, results_df)

    # Update aggregated results file
    if os.path.exists(aggregated_results_path):
        old_aggregated_df = pd.read_csv(aggregated_results_path)
        old_aggregated_df = old_aggregated_df[
            ~((old_aggregated_df["sut"] == system_name) & (old_aggregated_df["workload"] == workload_name))
        ]
        aggregated_df = pd.concat([old_aggregated_df, aggregated_df])

    aggregated_df.to_csv(aggregated_results_path, index=False)

    print(f"Done. Aggregated results:")
    print(aggregated_df[aggregated_df["workload"] == workload_name])


if __name__ == "__main__":
    main()
