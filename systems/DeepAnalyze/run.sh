#!/bin/bash
# Assumptions:
# - Current working directory is this script directory (systems/DeepAnalyze)
# - The data directory is at the Kramabench project root (../../data)
# - Snapshot JSON is stored under this directory (./data_files_snapshot.json)
#
# Clean extra files in data/ based on the snapshot JSON:
# 1) If snapshot JSON does not exist, save all filenames under data/ to JSON
# 2) Compare current data/ with snapshot JSON; delete files not in the snapshot

export DEBUG=False
# export DEEPANALYZE_API_KEY="xxx"
# export OPENAI_API_KEY="xxx"


DATA_DIR="../../data"
SNAPSHOT_JSON="./data_files_snapshot.json"

if [ ! -f "$SNAPSHOT_JSON" ]; then
    echo "Snapshot file not found: $SNAPSHOT_JSON"
    echo "Generating snapshot: saving all filenames under $DATA_DIR to JSON..."
    python3 - "$DATA_DIR" "$SNAPSHOT_JSON" <<'PY'
import json
import os
import sys

data_dir, out_path = sys.argv[1], sys.argv[2]
files = []
for root, _, filenames in os.walk(data_dir):
    for name in filenames:
        full_path = os.path.join(root, name)
        if os.path.isfile(full_path):
            files.append(os.path.relpath(full_path, data_dir))
files.sort()
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(files, f, ensure_ascii=False, indent=2)
print(f"Snapshot generated: {out_path} (total {len(files)} files)")
PY
fi

echo "Comparing $DATA_DIR against snapshot $SNAPSHOT_JSON and deleting extra files..."
python3 - "$DATA_DIR" "$SNAPSHOT_JSON" <<'PY'
import json
import os
import sys

data_dir, snapshot_path = sys.argv[1], sys.argv[2]
with open(snapshot_path, "r", encoding="utf-8") as f:
    allowed = set(json.load(f))

deleted = 0
for root, _, filenames in os.walk(data_dir):
    for name in filenames:
        full_path = os.path.join(root, name)
        if not os.path.isfile(full_path):
            continue
        rel = os.path.relpath(full_path, data_dir)
        if rel not in allowed:
            print(f"Deleting extra file: {full_path}")
            os.remove(full_path)
            deleted += 1
print(f"Cleanup completed: deleted {deleted} files")
PY

# Notes:
# - If evaluate.py is run directly under systems/DeepAnalyze, project_root would default to this directory,
#   which breaks workload/data path resolution.
# - Here project_root is explicitly set to the Kramabench root (../..),
#   so results/ and system_scratch/ match the standard layout.
PROJECT_ROOT="../.."
TS="$(date +%Y%m%d_%H%M%S)"
LOG_DIR="logs_${TS}"
mkdir -p "${LOG_DIR}"

# By default, evaluate all workloads.
# If arguments are provided, evaluate only the given workloads (e.g., bash run_parallel.sh legal wildfire).
# Keep lexical order for easier comparison and reproducibility.
DEFAULT_WORKLOADS=(archeology astronomy biomedical environment legal wildfire)
if [ "$#" -gt 0 ]; then
    WORKLOADS=("$@")
else
    WORKLOADS=("${DEFAULT_WORKLOADS[@]}")
fi

FAILED=0

# Run each workload's evaluate.py in parallel (one log file per workload).
PIDS=()
LOG_FILES=()
for WORKLOAD in "${WORKLOADS[@]}"; do
    LOG_FILE="${LOG_DIR}/t_logs_${WORKLOAD}_${TS}"
    echo "Starting evaluation for workload: ${WORKLOAD} (log: ${LOG_FILE})"
    python "${PROJECT_ROOT}/evaluate.py" \
      --project_root "${PROJECT_ROOT}" \
      --sut DeepAnalyzeSystem \
      --workload "${WORKLOAD}" \
      --no_pipeline_eval \
      --verbose >> "${LOG_FILE}" 2>&1 &
    PIDS+=("$!")
    LOG_FILES+=("${LOG_FILE}")
done

# Wait for all parallel jobs and aggregate exit codes.
for IDX in "${!PIDS[@]}"; do
    WORKLOAD="${WORKLOADS[$IDX]}"
    LOG_FILE="${LOG_FILES[$IDX]}"
    PID="${PIDS[$IDX]}"
    wait "${PID}"
    RC=$?
    if [ "${RC}" -ne 0 ]; then
        echo "Workload ${WORKLOAD} failed (exit code=${RC}), see: ${LOG_FILE}"
        FAILED=1
    else
        echo "Workload ${WORKLOAD} completed"
    fi
done

# Summarize final score per workload (extract from the last line of each log file).
SCORES=()
for WORKLOAD in "${WORKLOADS[@]}"; do
    LOG_FILE="${LOG_DIR}/t_logs_${WORKLOAD}_${TS}"
    LAST_LINE="$(tail -n 1 "${LOG_FILE}" 2>/dev/null || true)"
    SCORE="${LAST_LINE#*Total score is: }"
    SCORE="${SCORE//$'\r'/}"
    if [ -z "${LAST_LINE}" ]; then
        SCORE=""
    fi
    SCORES+=("${SCORE}")
done

SCORES_CSV="${LOG_DIR}/workload_scores.csv"
(IFS=,; echo "${WORKLOADS[*]}") > "${SCORES_CSV}"
(IFS=,; echo "${SCORES[*]}") >> "${SCORES_CSV}"

echo "Results directory: ${PROJECT_ROOT}/results/DeepAnalyzeSystem"
echo "System scratch directory: ${PROJECT_ROOT}/system_scratch/DeepAnalyzeSystem"
echo "Log directory: $(pwd)/${LOG_DIR}"
echo "Score summary CSV: $(pwd)/${SCORES_CSV}"
exit "${FAILED}"



