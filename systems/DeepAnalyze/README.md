# DeepAnalyze System (KramaBench)


## 1. Quick Start


Use the same environment as Kramabench.

Before running, please check the environment variables at the top of `run.sh`
(such as `DEEPANALYZE_API_KEY`, `OPENAI_API_KEY`, etc.).

Note: when `DEEPANALYZE_API_KEY` is set, the system will use the HeyWhale DeepAnalyze-8B API for evaluation. Otherwise, it will use the [DeepAnalyze-8B](https://huggingface.co/RUC-DataLab/DeepAnalyze-8B) model served by vLLM at `localhost:8000`. Please make sure either the API key is set, or a local DeepAnalyze-8B service is running with vLLM.

Run all workloads by default:

```bash
bash run.sh
```

Run specific workload(s) only:

```bash
bash run.sh astronomy
bash run.sh legal wildfire
```

## 2. Run Sequentially Multiple Times (nohup)

Because model outputs are unstable and score variance can be large, it is recommended to run multiple tests.

Run 5 times sequentially (all workloads):

```bash
nohup bash -c 'for i in {1..5}; do echo "===== run $i/5 ====="; bash run.sh; done' > run_5x.nohup.out 2>&1 &
```

Run 5 times sequentially (biomedical only):

```bash
nohup bash -c 'for i in {1..5}; do echo "===== run $i/5 ====="; bash run.sh biomedical; done' > run_5x_biomedical.nohup.out 2>&1 &
```


## 3. Output Locations


- `systems/DeepAnalyze/logs_<timestamp>/`:
  - `t_logs_<workload>_<timestamp>`
  - `workload_scores.csv`
- `results/DeepAnalyzeSystem/`:
  - `<workload>_measures_<timestamp>.csv`
  - `response_cache/<workload>_<timestamp>.json`
- `system_scratch/DeepAnalyzeSystem/`:
  - `full_response_<query_id>.txt`
  - `result_<query_id>.txt`

## 4. Re-evaluate Cache Only (No Regeneration)

```bash
bash eval_response_cache.sh
```

Useful when `response_cache` already exists and you only need to recompute scores quickly.
