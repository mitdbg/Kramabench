"""
DeepAnalyze System for Kramabench
Implements DeepAnalyze's capabilities using local vLLM API for benchmark testing
"""

import os
import json
import sys
import ast
import tempfile
import subprocess
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import re
from .prompt import DEEPANALYZE_PROMPT

# Import the System base class
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from benchmark.benchmark_api import System




class WorkspaceTracker:
    """Track workspace file changes and collect artifacts into generated/ folder."""

    def __init__(self, workspace_dir: str, generated_dir: str):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.generated_dir = Path(generated_dir).resolve()
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        self.before_state = self._snapshot()
        self.generated_files_in_workspace: List[Path] = []  # Track new files in workspace for deletion

    def _snapshot(self) -> Dict[Path, tuple]:
        try:
            return {
                p.resolve(): (p.stat().st_size, p.stat().st_mtime_ns)
                for p in self.workspace_dir.rglob("*")
                if p.is_file()
            }
        except Exception:
            return {}

    def diff_and_collect(self) -> List[Path]:
        """Compute added/modified files, copy into generated/, and return artifact paths."""
        try:
            after_state = {
                p.resolve(): (p.stat().st_size, p.stat().st_mtime_ns)
                for p in self.workspace_dir.rglob("*")
                if p.is_file()
            }
        except Exception:
            after_state = {}

        added = [p for p in after_state.keys() if p not in self.before_state]
        modified = [
            p for p in after_state.keys()
            if p in self.before_state and after_state[p] != self.before_state[p]
        ]

        artifact_paths: List[Path] = []
        for p in added:
            try:
                if not str(p).startswith(str(self.generated_dir)):
                    dest = self.generated_dir / p.name
                    # Directly overwrite if file exists
                    shutil.copy2(str(p), str(dest))
                    artifact_paths.append(dest.resolve())
                    # Record the original file path for later deletion
                    self.generated_files_in_workspace.append(p)
                else:
                    artifact_paths.append(p)
            except Exception as e:
                print(f"Error moving file {p}: {e}")

        for p in modified:
            try:
                dest = self.generated_dir / f"{p.stem}_modified{p.suffix}"
                # Directly overwrite if file exists
                shutil.copy2(str(p), str(dest))
                artifact_paths.append(dest.resolve())
            except Exception as e:
                print(f"Error copying modified file {p}: {e}")

        self.before_state = after_state
        return artifact_paths

    def cleanup_workspace_files(self, verbose: bool = False) -> None:
        """Delete all generated files from the workspace directory."""
        for file_path in self.generated_files_in_workspace:
            try:
                if file_path.exists():
                    file_path.unlink()
                    if verbose:
                        print(f"Deleted generated file from workspace: {file_path}")
            except Exception as e:
                if verbose:
                    print(f"Error deleting file {file_path}: {e}")

        # Clear the tracking list after cleanup
        self.generated_files_in_workspace.clear()


class DeepAnalyzeSystem(System):
    """
    DeepAnalyze system implementation that uses local vLLM API instead of DeepAnalyze's API.
    Follows DeepAnalyze's prompt structure with # Instruction and # Data sections.
    """

    def __init__(
        self,
        model: str = "DeepAnalyze-8B",
        name: str = "DeepAnalyze",
        vllm_endpoint: str = "http://localhost:8000/v1",
        verbose: bool = False,
        *args,
        **kwargs
    ):
        """
        Initialize DeepAnalyze system with vLLM configuration

        Args:
            model: Model name for vLLM
            name: System name for benchmark identification
            vllm_endpoint: Local vLLM API endpoint
            verbose: Enable verbose logging
        """
        super().__init__(name, verbose, *args, **kwargs)
        self.model = model
        self.vllm_endpoint = vllm_endpoint.rstrip('/')
        self.deepanalyze_api_key = os.getenv("DEEPANALYZE_API_KEY", "").strip()
        self.deepanalyze_api_base = os.getenv(
            "DEEPANALYZE_API_BASE",
            "https://www.heywhale.com/api/model/services/691d42c36c6dda33df0bf645/app/v1",
        ).rstrip('/')
        self.use_deepanalyze_api = bool(self.deepanalyze_api_key)
        self._deepanalyze_api_model: Optional[str] = None
        self.dataset_directory = None
        self.file_info_cache = {}
        self.dataset_file_info_str = ""
        self.intermediate_files = []
        self.max_files_in_prompt = int(os.getenv("DEEPANALYZE_MAX_FILES_IN_PROMPT", "1200"))
        self.max_data_chars_in_prompt = int(os.getenv("DEEPANALYZE_MAX_DATA_CHARS_IN_PROMPT", "45000"))
        self.max_message_chars = int(os.getenv("DEEPANALYZE_MAX_MESSAGE_CHARS", "120000"))
        self.max_single_message_chars = int(os.getenv("DEEPANALYZE_MAX_SINGLE_MESSAGE_CHARS", "20000"))
        self.max_execute_output_chars = int(os.getenv("DEEPANALYZE_MAX_EXECUTE_OUTPUT_CHARS", "12000"))
        self.complex_prompt_data_chars = int(os.getenv("DEEPANALYZE_COMPLEX_PROMPT_DATA_CHARS", "18000"))
        self.complex_prompt_max_files = int(os.getenv("DEEPANALYZE_COMPLEX_PROMPT_MAX_FILES", "450"))
        self.complex_large_dir_file_threshold = int(
            os.getenv("DEEPANALYZE_COMPLEX_LARGE_DIR_FILE_THRESHOLD", "200")
        )
        self.complex_dataset_mode = False
        self.dataset_complexity_profile: Dict[str, Any] = {}
        self.complex_large_directories: Dict[str, int] = {}

        # Track the previous workspace tracker for cleanup
        self.previous_tracker: Optional[WorkspaceTracker] = None

        # Create output directory for intermediate files
        self.output_dir = kwargs.get("output_dir", os.path.join(os.getcwd(), "deepanalyze_results"))
        os.makedirs(self.output_dir, exist_ok=True)

        if self.verbose:
            endpoint = self.deepanalyze_api_base if self.use_deepanalyze_api else self.vllm_endpoint
            mode = "DeepAnalyze API key" if self.use_deepanalyze_api else "local vLLM"
            print(f"[{self.name}] Initialized with model: {model}, endpoint: {endpoint}, mode: {mode}")

    def _resolve_deepanalyze_api_model(self, client: Any) -> str:
        """Resolve a valid model ID for DeepAnalyze API and cache it."""
        if self._deepanalyze_api_model:
            return self._deepanalyze_api_model

        try:
            model_ids = [m.id for m in client.models.list().data]
        except Exception as e:
            if self.verbose:
                print(f"[{self.name}] Failed to list DeepAnalyze models, fallback to configured model: {e}")
            model_ids = []

        if model_ids:
            if self.model in model_ids:
                self._deepanalyze_api_model = self.model
            else:
                self._deepanalyze_api_model = model_ids[0]
                if self.verbose:
                    print(
                        f"[{self.name}] Configured model '{self.model}' not found in DeepAnalyze API, "
                        f"use '{self._deepanalyze_api_model}' instead"
                    )
        else:
            self._deepanalyze_api_model = self.model

        return self._deepanalyze_api_model

    
    def collect_file_info(self, directory: str) -> str:
        """
        Collect file information from directory (recursive)
        Returns formatted string for DeepAnalyze's # Data section
        """
        all_file_info_str = ""
        dir_path = Path(directory)

        if not dir_path.exists():
            return ""

        def collect_files_recursive(path: Path, prefix: str = "") -> List[Path]:
            """Recursively collect all files"""
            files = []
            try:
                for item in sorted(path.iterdir()):
                    if item.is_file():
                        files.append(item)
                    elif item.is_dir() and not item.name.startswith('.'):
                        files.extend(collect_files_recursive(item, prefix + item.name + "/"))
            except PermissionError:
                pass  # Skip directories we can't access
            return files

        files = collect_files_recursive(dir_path)

        for idx, file_path in enumerate(files, start=1):
            try:
                size_bytes = os.path.getsize(file_path)
                size_kb = size_bytes / 1024
                if size_kb > 1024:
                    size_str = f"{size_kb/1024:.1f}MB"
                else:
                    size_str = f"{size_kb:.1f}KB"

                # Calculate relative path from dataset directory
                rel_path = os.path.relpath(file_path, directory)

                file_info = {
                    "file": rel_path,
                    "size": size_str
                }
                file_info_str = json.dumps(file_info, indent=4, ensure_ascii=False)
                all_file_info_str += f"File {idx}:\n{file_info_str}\n\n"

                # Cache file info for later use
                self.file_info_cache[rel_path] = file_info

            except (OSError, PermissionError) as e:
                if self.verbose:
                    print(f"[{self.name}] Warning: Could not access {file_path}: {e}")
                continue

        return all_file_info_str

    def _truncate_text(self, text: str, max_chars: int) -> str:
        if max_chars <= 0 or len(text) <= max_chars:
            return text
        omitted_chars = len(text) - max_chars
        return f"{text[:max_chars]}\n...[truncated {omitted_chars} chars]"

    def _scan_dataset_complexity(self, dataset_path: Path) -> Dict[str, Any]:
        total_files = 0
        total_dirs = 0
        max_depth = 0
        deepest_dir = "."
        max_files_in_single_dir = 0

        for root, dirs, files in os.walk(dataset_path):
            rel_root = os.path.relpath(root, dataset_path)
            depth = 0 if rel_root == "." else len(Path(rel_root).parts)
            if depth > max_depth:
                max_depth = depth
                deepest_dir = rel_root

            total_dirs += len(dirs)
            total_files += len(files)
            if len(files) > max_files_in_single_dir:
                max_files_in_single_dir = len(files)

        complex_layout = (
            total_files >= 1200
            and total_dirs >= 20
            and max_depth >= 4
            and max_files_in_single_dir >= 500
        )

        return {
            "total_files": total_files,
            "total_dirs": total_dirs,
            "max_depth": max_depth,
            "deepest_dir": deepest_dir,
            "max_files_in_single_dir": max_files_in_single_dir,
            "complex_layout": complex_layout,
        }

    def _is_path_under_large_directory(self, rel_path: str) -> bool:
        if not self.complex_large_directories:
            return False
        for dir_rel in self.complex_large_directories.keys():
            if rel_path == dir_rel or rel_path.startswith(f"{dir_rel}/"):
                return True
        return False

    def _copy_file_with_unique_name(self, src_file: Path, workspace_dir: Path, target_name: str) -> None:
        sanitized_name = target_name.replace(" ", "_")
        dest_path = workspace_dir / sanitized_name
        if not dest_path.exists():
            shutil.copy2(src_file, dest_path)
            return

        stem = dest_path.stem
        suffix = dest_path.suffix
        counter = 1
        while True:
            candidate = workspace_dir / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                shutil.copy2(src_file, candidate)
                return
            counter += 1

    def _build_prompt_file_info(self) -> str:
        if not self.file_info_cache:
            return ""

        sorted_items = sorted(self.file_info_cache.items(), key=lambda item: item[0])
        if not self.complex_dataset_mode:
            max_files = max(self.max_files_in_prompt, 1)
            selected_items = sorted_items[:max_files]
            chunks: List[str] = []
            used_chars = 0
            max_chars = max(self.max_data_chars_in_prompt, 2000)

            for idx, (rel_path, file_info) in enumerate(selected_items, start=1):
                compact_info = {
                    "file": rel_path,
                    "size": file_info.get("size", "")
                }
                chunk = f"File {idx}:\n{json.dumps(compact_info, indent=4, ensure_ascii=False)}\n"
                if used_chars + len(chunk) > max_chars:
                    break
                chunks.append(chunk)
                used_chars += len(chunk)

            remaining = len(sorted_items) - len(chunks)
            if remaining > 0:
                chunks.append(
                    f"Note: only the first {len(chunks)} files are listed; {remaining} additional files are omitted.\n"
                )
            return "\n".join(chunks)

        # Complex dataset mode: list small-directory files, and list large directories as directory entries.
        candidate_entries: List[Dict[str, Any]] = []

        for dir_rel, file_count in sorted(self.complex_large_directories.items()):
            candidate_entries.append(
                {
                    "kind": "directory",
                    "path": dir_rel,
                    "file_count": file_count,
                }
            )

        for rel_path, file_info in sorted_items:
            if self._is_path_under_large_directory(rel_path):
                continue
            candidate_entries.append(
                {
                    "kind": "file",
                    "path": rel_path,
                    "size": file_info.get("size", ""),
                }
            )

        max_entries = max(self.complex_prompt_max_files, 1)
        selected_entries = candidate_entries[:max_entries]

        chunks: List[str] = []
        used_chars = 0
        max_chars = min(max(self.max_data_chars_in_prompt, 2000), max(self.complex_prompt_data_chars, 2000))
        listed_count = 0

        for idx, entry in enumerate(selected_entries, start=1):
            if entry["kind"] == "directory":
                payload = {
                    "path": entry["path"],
                    "type": "directory",
                    "direct_file_count": entry["file_count"],
                    "note": "This is a directory (not a file). Explore it only if relevant to the question.",
                }
                chunk = f"Directory {idx}:\n{json.dumps(payload, indent=4, ensure_ascii=False)}\n"
            else:
                payload = {
                    "file": entry["path"],
                    "size": entry.get("size", ""),
                }
                chunk = f"File {idx}:\n{json.dumps(payload, indent=4, ensure_ascii=False)}\n"

            if used_chars + len(chunk) > max_chars:
                break
            chunks.append(chunk)
            used_chars += len(chunk)
            listed_count += 1

        remaining = len(candidate_entries) - listed_count
        if remaining > 0:
            chunks.append(
                f"Note: only the first {listed_count} entries are listed; {remaining} additional entries are omitted.\n"
            )

        return "\n".join(chunks)

    def _prune_messages(self, messages: List[Dict[str, str]], max_chars: int) -> List[Dict[str, str]]:
        if not messages:
            return messages

        def message_len(message: Dict[str, str]) -> int:
            return len(str(message.get("content", "")))

        while len(messages) > 3 and sum(message_len(m) for m in messages) > max_chars:
            del messages[1]
        return messages

    def _shrink_messages_on_context_error(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if len(messages) <= 2:
            return messages
        keep_tail = min(6, len(messages) - 1)
        return [messages[0], *messages[-keep_tail:]]

    def _build_query_file_hints(self, query: str, max_hints: int = 30, max_chars: int = 2800) -> str:
        """根据 query 关键词从文件列表中挑选候选文件，帮助模型快速定位。"""
        if not query or not self.file_info_cache:
            return ""

        q = query.lower()
        raw_tokens = re.findall(r"[a-z0-9._\-]+", q)
        hint_tokens = set()
        for token in raw_tokens:
            if len(token) >= 4:
                hint_tokens.add(token)
            if re.match(r"^wu\d+$", token):
                hint_tokens.add(token)
            if re.match(r"^\d{8}$", token) or re.match(r"^\d{4}$", token):
                hint_tokens.add(token)

        if not hint_tokens:
            return ""

        scored: List[tuple[int, str]] = []
        for rel_path in self.file_info_cache.keys():
            path_lower = rel_path.lower()
            score = 0
            for token in hint_tokens:
                if token in path_lower:
                    score += 3

            filename = os.path.basename(path_lower)
            if filename in q:
                score += 5

            if score > 0:
                scored.append((score, rel_path))

        if not scored:
            return ""

        scored.sort(key=lambda x: (-x[0], x[1]))
        selected = scored[:max_hints]

        lines: List[str] = [
            "### Query-Aware File Hints",
            "Potentially relevant files inferred from query keywords (filename/path match):"
        ]

        used_chars = sum(len(line) + 1 for line in lines)
        for idx, (_, rel_path) in enumerate(selected, start=1):
            line = f"{idx}. {rel_path}"
            if used_chars + len(line) + 1 > max_chars:
                break
            lines.append(line)
            used_chars += len(line) + 1

        if len(lines) <= 2:
            return ""

        return "\n".join(lines)

    def _coerce_answer_value(self, answer_text: str) -> Any:
        """将答案文本尽量转为 Python 字面量，失败则保留字符串。"""
        import re

        text = (answer_text or "").strip()
        if not text:
            return ""

        text = text.strip("` ")

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        candidate_pool: List[str] = [text]
        if lines:
            candidate_pool.extend([lines[0], lines[-1]])

        for candidate in candidate_pool:
            try:
                parsed = ast.literal_eval(candidate)
                if isinstance(parsed, (str, int, float, list, dict, tuple, bool)) or parsed is None:
                    return parsed
            except Exception:
                pass

        numeric_match = re.match(r"^([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)(?:\b|$)", text)
        if numeric_match:
            raw = numeric_match.group(1)
            try:
                if any(marker in raw.lower() for marker in [".", "e"]):
                    return float(raw)
                return int(raw)
            except Exception:
                pass

        return text

    def _extract_answer_from_response(self, response: str) -> Any:
        """从模型完整回复中鲁棒提取最终答案。"""
        import re

        text = response or ""
        candidates: List[str] = []

        answer_blocks = re.findall(r"<Answer>(.*?)</Answer>", text, flags=re.DOTALL | re.IGNORECASE)
        for block in answer_blocks:
            block = block.strip()
            if not block:
                continue
            candidates.append(block)
            for line in [ln.strip() for ln in block.splitlines() if ln.strip()]:
                if re.match(r"^Answer\s*:\s*", line, flags=re.IGNORECASE):
                    candidates.append(re.sub(r"^Answer\s*:\s*", "", line, flags=re.IGNORECASE).strip())

        line_matches = re.findall(r"^\s*Answer\s*:\s*(.+?)\s*$", text, flags=re.MULTILINE | re.IGNORECASE)
        candidates.extend([m.strip() for m in line_matches if m and m.strip()])

        if "Answer:" in text:
            tail = text.split("Answer:")[-1].replace("</Answer>", "").strip()
            if tail:
                candidates.append(tail)

        filtered_candidates: List[str] = []
        for candidate in candidates:
            cleaned = (candidate or "").strip().strip("`")
            if not cleaned:
                continue
            lowered = cleaned.lower()
            if "<final answer to the question>" in lowered:
                continue
            if "analysis pending" in lowered:
                continue
            filtered_candidates.append(cleaned)

        if not filtered_candidates:
            return ""

        final_candidate = filtered_candidates[-1]
        return self._coerce_answer_value(final_candidate)

    def process_dataset(self, dataset_directory: str | os.PathLike) -> None:
        """
        Process dataset by collecting file information from directory and subdirectories.
        Sets DeepAnalyze working directory and caches file information for prompt building.

        Args:
            dataset_directory: Path to dataset directory containing files to analyze
        """
        if self.verbose:
            print(f"[{self.name}] Processing dataset: {dataset_directory}")

        # Clean up generated files from previous session if exists
        if self.previous_tracker is not None:
            try:
                self.previous_tracker.cleanup_workspace_files(verbose=self.verbose)
                if self.verbose:
                    print(f"[{self.name}] Cleaned up generated files from previous session")
            except Exception as e:
                if self.verbose:
                    print(f"[{self.name}] Error during previous session cleanup: {e}")
            finally:
                self.previous_tracker = None

        # Create workspace directory under dataset_directory
        dataset_path = Path(dataset_directory).resolve()
        self.dataset_complexity_profile = self._scan_dataset_complexity(dataset_path)
        self.complex_dataset_mode = bool(self.dataset_complexity_profile.get("complex_layout", False))
        self.complex_large_directories = {}

        if self.verbose:
            print(f"[{self.name}] Dataset complexity profile: {self.dataset_complexity_profile}")
            print(f"[{self.name}] Complex dataset mode: {self.complex_dataset_mode}")

        workspace_path = dataset_path / "workspace"
        try:
            if workspace_path.exists():
                print(f"[{self.name}] Removing existing workspace: {workspace_path}")
                shutil.rmtree(workspace_path)
        except Exception as e:
            print(f"[{self.name}] Warning: Failed to remove existing workspace {workspace_path}: {e}")

        workspace_path.mkdir(parents=True, exist_ok=True)

        if self.verbose:
            print(f"[{self.name}] Created workspace directory: {workspace_path}")

        # Copy all files from dataset_directory to workspace
        # - complex_dataset_mode: mixed strategy (small dirs flattened, large dirs keep structure)
        # - others: keep original non-complex logic
        def copy_files_to_workspace(source_dir: Path, workspace_dir: Path, parent_path: str = ""):
            """Recursively copy files to workspace with subdirectory prefix in filename
            
            Args:
                source_dir: Source directory to copy from
                workspace_dir: Workspace directory to copy to
                parent_path: Accumulated parent directory path (joined with underscores)
            """
            for item in source_dir.iterdir():
                # Skip the workspace directory itself
                if item == workspace_dir:
                    continue
                
                if item.is_file():
                    if self.complex_dataset_mode:
                        rel_file_path = os.path.relpath(item, dataset_path)
                        rel_parent = os.path.dirname(rel_file_path)
                        rel_parent = "" if rel_parent == "." else rel_parent

                        # For files in large directories, preserve directory structure.
                        if rel_parent in self.complex_large_directories:
                            dest_dir = workspace_dir / rel_parent
                            dest_dir.mkdir(parents=True, exist_ok=True)
                            dest_path = dest_dir / item.name
                            display_name = os.path.join(rel_parent, item.name)
                            if not dest_path.exists():
                                try:
                                    shutil.copy2(item, dest_path)
                                    if self.verbose:
                                        print(f"[{self.name}] Copied (keep dir): {item.name} -> {display_name}")
                                except Exception as e:
                                    if self.verbose:
                                        print(f"[{self.name}] Error copying {item}: {e}")
                            else:
                                if self.verbose:
                                    print(f"[{self.name}] Skipped (exists): {display_name}")
                        else:
                            # For files in small directories, flatten into workspace root.
                            if rel_parent:
                                new_filename = f"{rel_parent.replace('/', '_')}_{item.name}"
                            else:
                                new_filename = item.name
                            new_filename = new_filename.replace(" ", "_")
                            try:
                                self._copy_file_with_unique_name(item, workspace_dir, new_filename)
                                if self.verbose:
                                    print(f"[{self.name}] Copied (flatten): {item.name} -> {new_filename}")
                            except Exception as e:
                                if self.verbose:
                                    print(f"[{self.name}] Error copying {item}: {e}")
                        continue
                    else:
                        # Flatten filename for non-complex workloads
                        # For multi-level subdirectories, all levels are joined with underscores
                        if parent_path:
                            new_filename = f"{parent_path}_{item.name}"
                        else:
                            new_filename = item.name
                        new_filename = new_filename.replace(" ", "_")
                        dest_path = workspace_dir / new_filename
                        display_name = new_filename
                    
                    # Only copy if file doesn't exist
                    if not dest_path.exists():
                        try:
                            shutil.copy2(item, dest_path)
                            if self.verbose:
                                print(f"[{self.name}] Copied: {item.name} -> {display_name}")
                        except Exception as e:
                            if self.verbose:
                                print(f"[{self.name}] Error copying {item}: {e}")
                    else:
                        if self.verbose:
                            print(f"[{self.name}] Skipped (exists): {display_name}")
                
                elif item.is_dir() and not item.name.startswith('.'):
                    # Recursively process subdirectories
                    if self.complex_dataset_mode:
                        # parent_path is not used in complex mode filename generation
                        new_parent_path = parent_path
                    else:
                        # Accumulate directory path with underscores for multi-level nesting
                        new_parent_path = f"{parent_path}_{item.name}" if parent_path else item.name
                    copy_files_to_workspace(item, workspace_dir, new_parent_path)

        if self.complex_dataset_mode:
            # Identify high-file-count directories (direct children files count) for structure-preserving copy.
            for root, _, files in os.walk(dataset_path):
                rel_root = os.path.relpath(root, dataset_path)
                if rel_root in {".", "workspace"}:
                    continue
                if len(files) >= self.complex_large_dir_file_threshold:
                    self.complex_large_directories[rel_root] = len(files)

            if self.verbose:
                print(
                    f"[{self.name}] Complex mode large directories: "
                    f"{len(self.complex_large_directories)} (threshold={self.complex_large_dir_file_threshold})"
                )

        # Execute file copying
        copy_files_to_workspace(dataset_path, workspace_path)

        # Set working directory to workspace
        self.dataset_directory = str(workspace_path)

        if self.verbose:
            print(f"[{self.name}] Set working directory to: {self.dataset_directory}")

        # Clear previous cache
        self.file_info_cache.clear()
        self.dataset_file_info_str = ""
        self.intermediate_files.clear()

        # Collect file information recursively from workspace
        self.collect_file_info(self.dataset_directory)
        self.dataset_file_info_str = self._build_prompt_file_info()

        if self.verbose:
            print(f"[{self.name}] Found {len(self.file_info_cache)} files in workspace")
            print(f"[{self.name}] File info preview: {self.dataset_file_info_str[:200]}...")

        # Save file info to intermediate file
        info_file_path = os.path.join(self.output_dir, "dataset_file_info.json")
        with open(info_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.file_info_cache, f, indent=2, ensure_ascii=False)

        self.intermediate_files.append(info_file_path)

        if self.verbose:
            print(f"[{self.name}] Dataset file info saved to: {info_file_path}")

    def build_deepanalyze_prompt(self, query: str) -> str:
        """
        Build DeepAnalyze-style prompt with # Instruction and # Data sections

        Args:
            query: The instruction/task query

        Returns:
            Formatted prompt string following DeepAnalyze template
        """

    
        instruction_body = DEEPANALYZE_PROMPT.format(
            query=query
        )

        if self.complex_dataset_mode:
            instruction_body += (
                "\n\n### Large Dataset Strategy\n"
                "The dataset has complex multi-level structure and many files. "
                "In # Data, some entries are files and some entries are directories. "
                "If a listed file already answers the question, use it directly. "
                "If only a relevant directory is listed, explore that directory selectively based on the question. "
                "Do not scan all files blindly; inspect only the minimal necessary files and then compute the final value/list/dict. "
                "Note: some small-directory files are flattened in workspace names (slashes replaced by underscores). "
                "If an expected path is not found, use glob/listdir to match by distinctive filename suffix."
            )

        # Get file information for the # Data section
        data_section = self.dataset_file_info_str
        if self.complex_dataset_mode:
            data_section = self._build_prompt_file_info()

        if self.dataset_directory and data_section:
            prompt = f"# Instruction\n{instruction_body}\n\n# Data\n{data_section}"
        else:
            prompt = f"# Instruction\n{instruction_body}"
            if self.verbose:
                print(f"[{self.name}] Warning: No dataset files available for # Data section")

        hint_section = self._build_query_file_hints(query)
        if hint_section:
            prompt = f"{prompt}\n\n{hint_section}"

        return prompt

    def call_vllm_api(self, prompt: str, temperature: float = 0.0, max_tokens: int = 8192, tracker: Optional[WorkspaceTracker] = None, failed_code_map = []) -> tuple[str, int]:
        """
        Call vLLM API with the given prompt, following DeepAnalyze's chat_completion pattern.
        Supports multi-round reasoning with code execution.

        Args:
            prompt: The input prompt text
            temperature: Sampling temperature
            max_tokens: Maximum number of new tokens to generate

        Returns:
            Tuple of (complete_response, total_tokens_consumed)
        """
        import openai
        import re

        if self.use_deepanalyze_api:
            client = openai.OpenAI(base_url=self.deepanalyze_api_base, api_key=self.deepanalyze_api_key)
            model_name = self._resolve_deepanalyze_api_model(client)
        else:
            client = openai.OpenAI(base_url=self.vllm_endpoint, api_key="dummy")
            model_name = self.model

        # Stop token IDs for local DeepAnalyze vLLM model
        STOP_TOKEN_IDS = [151676, 151645]

       
        # Prepare messages in vLLM format
        # print(sys_prompt)
     
        messages = [
            {"role": "user", "content": prompt}
            ]

        assistant_reply = ""
        finished = False
        max_round = 50
        cnt = 0
        total_tokens_consumed = 0
        context_retry_count = 0
        max_context_retry = 5
        answer_repair_round = 0
        max_answer_repair_round = 2
        # last_failed_code_block = None
        while not finished:
            # Call vLLM API with streaming
            if cnt == max_round:
                return '', total_tokens_consumed
            messages = self._prune_messages(messages, self.max_message_chars)
            try:
                if self.use_deepanalyze_api:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=0.0,
                        max_tokens=max_tokens,
                        stop=["</Code>"]
                    )
                else:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=0.0,
                        # stream=True,
                        extra_body={
                            "add_generation_prompt": False,
                            "stop_token_ids": STOP_TOKEN_IDS,
                            "max_new_tokens": max_tokens,
                        },
                    )
            except Exception as e:
                error_text = str(e)
                if "maximum context length" in error_text and context_retry_count < max_context_retry:
                    context_retry_count += 1
                    old_len = len(messages)
                    messages = self._shrink_messages_on_context_error(messages)
                    if self.verbose:
                        print(
                            f"[{self.name}] Context overflow, shrinking history and retrying "
                            f"({context_retry_count}/{max_context_retry}), messages: {old_len}->{len(messages)}"
                        )
                    continue
                raise
            cnt += 1
            context_retry_count = 0
            

            cur_res = ""
            last_finish_reason = None
            cur_res = response.choices[0].message.content or ""
            assistant_reply += cur_res
            completion_tokens = 0
            if response.usage is not None:
                completion_tokens = (
                    getattr(response.usage, "completion_tokens", None)
                    or getattr(response.usage, "output_tokens", 0)
                    or 0
                )
            total_tokens_consumed += completion_tokens
            if response.choices[0].finish_reason:
                last_finish_reason = response.choices[0].finish_reason
            if "</Answer>" in cur_res:
                finished = True

            # Check for code segments and handle completion
            has_code_segment = "<Code>" in cur_res
            has_closed_code = "</Code>" in cur_res

            if last_finish_reason == "stop" and not finished:
                if has_code_segment and not has_closed_code:
                    # Close unclosed code tag
                    cur_res += "</Code>"
                    assistant_reply += "</Code>"
                    has_closed_code = True
                elif not has_code_segment:
                    has_answer_signal = ("</Answer>" in assistant_reply) or ("Answer:" in assistant_reply)
                    if not has_answer_signal and answer_repair_round < max_answer_repair_round:
                        answer_repair_round += 1
                        messages.append({
                            "role": "assistant",
                            "content": self._truncate_text(cur_res, self.max_single_message_chars)
                        })
                        messages.append({
                            "role": "user",
                            "content": "Please provide only one final line in exact format: Answer: <python literal>. No extra text."
                        })
                        continue
                    finished = True
            elif last_finish_reason == 'length':
                has_answer_signal = ("</Answer>" in assistant_reply) or ("Answer:" in assistant_reply)
                if not has_answer_signal and answer_repair_round < max_answer_repair_round:
                    answer_repair_round += 1
                    messages.append({
                        "role": "assistant",
                        "content": self._truncate_text(cur_res, self.max_single_message_chars)
                    })
                    messages.append({
                        "role": "user",
                        "content": "Continue briefly and end with exactly one line: Answer: <python literal>."
                    })
                    continue
                finished = True

            # Handle code execution if we have a complete code segment and not finished
            if has_code_segment and has_closed_code and not finished:
                messages.append({
                    "role": "assistant",
                    "content": self._truncate_text(cur_res, self.max_single_message_chars)
                })

                # Extract code from the segment
                code_match = re.search(r"<Code>(.*?)</Code>", cur_res, re.DOTALL)
                if code_match:
                    code_content = code_match.group(1).strip()
                    # Remove markdown code fences if present
                    md_match = re.search(r"```(?:python)?(.*?)```", code_content, re.DOTALL)
                    code_str = md_match.group(1).strip() if md_match else code_content

                    if code_str:
                        # Execute the code safely
                        exe_output, exe_error = self.execute_code_safe(code_str)
                        if exe_output == '' and  exe_error and 'Traceback' in exe_error:
                            failed_code_map.append(True)
                        else :
                            failed_code_map.append(False)
                        
                        execute_payload = exe_output + exe_error
                        execute_payload = self._truncate_text(execute_payload, self.max_execute_output_chars)
                        exe_str = f"\n<Execute>\n```\n{execute_payload}\n```\n</Execute>\n"
                        assistant_reply += exe_str
                        if self.use_deepanalyze_api:
                            messages.append({"role": "user", "content": exe_str.strip()})
                        else:
                            messages.append({"role": "execute", "content": execute_payload})

                        # Detect and collect intermediate files if tracker is available
                        if tracker:
                            try:
                                artifacts = tracker.diff_and_collect()
                                if artifacts and self.verbose:
                                    print(f"[{self.name}] Detected {len(artifacts)} intermediate files:")
                                    for artifact in artifacts:
                                        print(f"  - {artifact.name}")

                                # Add file information to execution output
                                if artifacts:
                                    file_info = "\n<Files>\n"
                                    for artifact in artifacts:
                                        rel_path = os.path.relpath(artifact, tracker.generated_dir)
                                        file_info += f"Generated file: {rel_path}\n"
                                    file_info += "</Files>\n"
                                    assistant_reply += file_info

                            except Exception as e:
                                if self.verbose:
                                    print(f"[{self.name}] Error tracking intermediate files: {e}")
                    else:
                        finished = True
                else:
                    finished = True

        return assistant_reply, total_tokens_consumed

    def execute_code_safe(
        self, code_str: str, timeout_sec: int = 120
    ):
        """Execute Python code in a separate process with timeout"""
        workspace_dir = self.dataset_directory
        exec_cwd = os.path.abspath(workspace_dir)
        os.makedirs(exec_cwd, exist_ok=True)
        tmp_path = None
        try:
            fd, tmp_path = tempfile.mkstemp(suffix=".py", dir=exec_cwd)
            os.close(fd)
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(code_str)

            child_env = os.environ.copy()
            child_env.setdefault("MPLBACKEND", "Agg")
            child_env.setdefault("QT_QPA_PLATFORM", "offscreen")
            child_env.pop("DISPLAY", None)

            completed = subprocess.run(
                [sys.executable, tmp_path],
                cwd=exec_cwd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                env=child_env,
            )
            output = (completed.stdout or "") , (completed.stderr or "")
            return output
        except subprocess.TimeoutExpired:
            return "", f"[Timeout]: execution exceeded {timeout_sec} seconds"
        except Exception as e:
            return "", f"[Error]: {str(e)}"
        finally:
            try:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

    def serve_query(self, query: str, query_id: str = "default_query", subset_files: Optional[List[str]] = None) -> Dict:
        """
        Process a query and return benchmark-compliant response.

        Args:
            query: The input query string
            query_id: Unique identifier for this query

        Returns:
            Dictionary with "explanation" and "pipeline_code" keys following benchmark format:
            {
                "explanation": {"answer": final_answer},
                "pipeline_code": extracted_code
            }
        """
        import re
        import json

        if self.verbose:
            print(f"[{self.name}] Processing query '{query_id}': {query[:100]}...")

        # Setup file tracking for intermediate files detection
        workspace_dir = self.dataset_directory or os.getcwd()
        generated_dir = os.path.join(self.output_dir, "generated", f"query_{query_id}_{int(time.time())}")
        os.makedirs(generated_dir, exist_ok=True)
        tracker = WorkspaceTracker(workspace_dir, generated_dir)

        if self.verbose:
            print(f"[{self.name}] Tracking intermediate files in: {workspace_dir}")
            print(f"[{self.name}] Generated files will be saved to: {generated_dir}")

        # Build DeepAnalyze-style prompt
        prompt = self.build_deepanalyze_prompt(query)

        if self.verbose:
            print(f"[{self.name}] Generated prompt length: {len(prompt)} characters")

        # Call vLLM API
        code_failed_map = []
        response = ""
        tokens_consumed = 0
        try:
            response, tokens_consumed = self.call_vllm_api(prompt, tracker=tracker, failed_code_map=code_failed_map)

            if self.verbose:
                print(f"[{self.name}] API response received, length: {len(response)} characters")
                print(f"[{self.name}] Total tokens consumed: {tokens_consumed}")

        except Exception as e:
            error_msg = f"Error calling vLLM API: {str(e)}"
            if self.verbose:
                print(f"[{self.name}] {error_msg}")
            try:
                tracker.cleanup_workspace_files(verbose=self.verbose)
            except Exception:
                pass
            return {
                "explanation": {"answer": error_msg},
                "pipeline_code": "# Error occurred during API call",
                "token_usage": tokens_consumed 
            }

        # Extract all code blocks from response
        pipeline_code = ""

        # Find all <Code>...</Code> blocks
        code_matches = list(re.finditer(r"<Code>(.*?)</Code>", response, re.DOTALL))

        if code_matches:
            extracted_codes = []
            for cnt, code_match in enumerate(code_matches, start=1):
                if code_failed_map and code_failed_map[cnt-1]:
                    continue
                code_content = code_match.group(1).strip()
                # Remove markdown code fences if present
                md_match = re.search(r"```(?:python)?(.*?)```", code_content, re.DOTALL)
                clean_code = md_match.group(1).strip() if md_match else code_content

                # Add prefix with counter
                code_with_prefix = f"<code_file_{cnt}>\n{clean_code}\n</code_file_{cnt}>"
                extracted_codes.append(code_with_prefix)

            pipeline_code = "\n\n".join(extracted_codes)
        else:
            pipeline_code = "# No code blocks found in response"

        # Extract answer from response
        answer = self._extract_answer_from_response(response)
        

        # Final check for any remaining intermediate files
        try:
            final_artifacts = tracker.diff_and_collect()
            if final_artifacts and self.verbose:
                print(f"[{self.name}] Final detection: {len(final_artifacts)} intermediate files saved")
                # Save a summary of all generated files
                summary_file = os.path.join(generated_dir, "files_summary.txt")
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(f"Query ID: {query_id}\n")
                    f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Workspace: {workspace_dir}\n")
                    f.write(f"Output directory: {generated_dir}\n")
                    f.write(f"\nGenerated files ({len(final_artifacts)}):\n")
                    for i, artifact in enumerate(final_artifacts, 1):
                        rel_path = os.path.relpath(artifact, tracker.generated_dir)
                        f.write(f"{i}. {rel_path}\n")

                if self.verbose:
                    print(f"[{self.name}] Files summary saved to: {summary_file}")
        except Exception as e:
            if self.verbose:
                print(f"[{self.name}] Error in final file detection: {e}")


        # Return in benchmark format
        result = {
            "explanation":  { "answer": answer },
            "pipeline_code": pipeline_code,
            "token_usage": tokens_consumed
        }

        if self.verbose:
            print(f"[{self.name}] Query '{query_id}' completed successfully")
            print(f"[{self.name}] Answer length: {len(str(answer))}, Code length: {len(pipeline_code)}")
            
        if self.verbose:
            with open(os.path.join(self.output_dir, f"result_{query_id}.txt"), 'w', encoding='utf-8') as f:
                f.write(json.dumps(result, indent=2))
            with open(os.path.join(self.output_dir, f"full_response_{query_id}.txt"), 'w', encoding='utf-8') as f:
                f.write(prompt+'\n\n'+response)

        try:
            tracker.cleanup_workspace_files(verbose=self.verbose)
        except Exception as e:
            if self.verbose:
                print(f"[{self.name}] Error during workspace cleanup: {e}")

        # Store current tracker for cleanup in next process_dataset call
        self.previous_tracker = tracker

        return result

# Factory function for easier instantiation
def create_deepanalyze_system(**kwargs) -> DeepAnalyzeSystem:
    """Create DeepAnalyze system with default configuration"""
    return DeepAnalyzeSystem(**kwargs)
