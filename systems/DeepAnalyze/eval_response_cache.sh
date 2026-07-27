export DEBUG=False
# export DEEPANALYZE_API_KEY="xxx"
# export OPENAI_API_KEY="xxx"
TS="$(date +%Y%m%d_%H%M%S)"
LOG_DIR="logs_${TS}"
mkdir -p "${LOG_DIR}"
python ../../evaluate.py --project_root ../.. --sut DeepAnalyzeSystem --workload biomedical --use_system_cache --no_pipeline_eval --verbose >> "${LOG_DIR}/t_logs_biomedical_${TS}" 2>&1
python ../../evaluate.py --project_root ../.. --sut DeepAnalyzeSystem --workload legal --use_system_cache --no_pipeline_eval --verbose >> "${LOG_DIR}/t_logs_legal_${TS}" 2>&1
python ../../evaluate.py --project_root ../.. --sut DeepAnalyzeSystem --workload wildfire --use_system_cache --no_pipeline_eval --verbose >> "${LOG_DIR}/t_logs_wildfire_${TS}" 2>&1
python ../../evaluate.py --project_root ../.. --sut DeepAnalyzeSystem --workload environment --use_system_cache --no_pipeline_eval --verbose >> "${LOG_DIR}/t_logs_environment_${TS}" 2>&1
python ../../evaluate.py --project_root ../.. --sut DeepAnalyzeSystem --workload astronomy --use_system_cache --no_pipeline_eval --verbose >> "${LOG_DIR}/t_logs_astronomy_${TS}" 2>&1
python ../../evaluate.py --project_root ../.. --sut DeepAnalyzeSystem --workload archeology --use_system_cache --no_pipeline_eval --verbose >> "${LOG_DIR}/t_logs_archeology_${TS}" 2>&1

# Summarize final score per workload (extract from the last line of each log file).
WORKLOADS=(biomedical legal wildfire environment astronomy archeology)
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
