"""
TalkTask (https://talktask.si): a data-analysis room that answers questions about a folder of files in plain words.
Every figure is computed by the room's engine from the rows and carries its receipt; the room states one committed
answer on an "Answer:" line, or withholds an answer when the data cannot carry one.

This adapter sends each KramaBench query to a running TalkTask room over HTTP and hands the harness the room's
committed answer line, converted to a value by fixed rules (no model is involved in the hand-in):
  - items separated by "; " become a list;
  - an item that starts with a number becomes that number (thousands separators, a leading "$" and a trailing
    "%" or unit word are dropped: "$5,435 million" -> 5435, "68.08 years" -> 68.08);
  - anything else stays a string;
  - a turn in which the room withheld its answer is handed in as no answer.

The room itself is not part of this repository. Two modes:
  TALKTASK_URL=http://host:port   live: POST {"question": ...} to <url>/api/ask, one room per domain
  TALKTASK_REPLAY=answers.jsonl   replay: the stored answers of a recorded run, one JSON object per line with
                                  "task_id", "answer_line" and "abstained" (used for the single-run row in README)
"""
import json
import os
import re
from typing import Any, Dict, List

import requests

from benchmark.benchmark_api import System

NUMBER = re.compile(r"^\s*\$?\s*(-?[\d,]*\.?\d+(?:[eE][-+]?\d+)?)\s*%?(?:\s+[A-Za-z][\w /.^-]*)?\s*$")


def to_value(item: str) -> Any:
    """One committed item as the harness reads it: a number when it starts as one, else the words."""
    m = NUMBER.match(item)
    if m:
        try:
            v = float(m.group(1).replace(",", ""))
            return int(v) if v.is_integer() and "." not in m.group(1) and "e" not in m.group(1).lower() else v
        except ValueError:
            pass
    return item.strip()


def answer_value(line: str | None) -> Any:
    """The room's committed answer line -> the value handed to the harness (a list when it names several)."""
    if not line or not str(line).strip():
        return None
    text = str(line).strip().rstrip(".")
    parts = [p for p in (s.strip() for s in text.split("; ")) if p]
    return [to_value(p) for p in parts] if len(parts) > 1 else to_value(parts[0])


class TalkTask(System):
    def __init__(self, name: str = "TalkTask", verbose: bool = False, *args, **kwargs):
        super().__init__(name, verbose=verbose, *args, **kwargs)
        self.url = os.environ.get("TALKTASK_URL", "").rstrip("/")
        self.replay = {}
        path = os.environ.get("TALKTASK_REPLAY")
        if path:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rec = json.loads(line)
                        self.replay[rec["task_id"]] = rec

    def process_dataset(self, dataset_directory: str | os.PathLike) -> None:
        # The room stages the domain's files itself before it is asked; the harness only names the folder here.
        self.dataset_directory = dataset_directory

    def _ask(self, query: str) -> Dict[str, Any]:
        r = requests.post(f"{self.url}/api/ask", json={"question": query}, timeout=3600)
        r.raise_for_status()
        p = r.json()
        line = p.get("answer_line")
        if not line:
            m = re.match(r"\s*Answer:\s*(.+?)(?:\.\s|\.$|\n|$)", str(p.get("answer") or ""))
            line = m.group(1) if m else None
        return {"answer_line": line, "abstained": bool(p.get("abstain")), "text": p.get("answer") or ""}

    def serve_query(self, query: str, query_id: str = "default_name-0", subset_files: List[str] | None = None) -> Dict:
        rec = self.replay.get(query_id) if self.replay else None
        if rec is None:
            rec = self._ask(query) if self.url else {"answer_line": None, "abstained": True, "text": ""}
        value = None if rec.get("abstained") else answer_value(rec.get("answer_line"))
        return {
            "explanation": {"id": "main-task", "answer": value},
            "pipeline_code": "",
            "token_usage": 0,
            "token_usage_input": 0,
            "token_usage_output": 0,
        }
