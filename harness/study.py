"""
Study path resolution — the one place the harness learns where a study's files live.

A *study* is a directory with this layout (see docs/harness.md):

    <study>/
      spec/stimulus.json     the frozen multi-turn script
      spec/codebook.py        the criteria (MARKERS / GRADED_MARKERS / ...)  [optional]
      transcripts/<model>.json   Contract A — runner output  (data/benchmark in conduct)
      labels/<labeler>/<model>.json   Contract B — judge output  (markers/<judge> in conduct)
      store.json              adjudicator output

The harness is study-agnostic: every script takes `--study <dir>` (default: cwd) and
resolves paths through this module. Nothing here knows what a marker is.

`transcripts_dir` / `labels_dir` are overridable per study via spec/paths.json so the
conduct study can keep its historical `data/benchmark` and `markers/` directory names
without the harness hard-coding them.
"""

import json
import importlib.util
from pathlib import Path


class Study:
    def __init__(self, root):
        self.root = Path(root).resolve()
        cfg_path = self.root / "spec" / "paths.json"
        cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
        self._t = cfg.get("transcripts", "transcripts")
        self._l = cfg.get("labels", "labels")
        self._stimulus = cfg.get("stimulus", "spec/stimulus.json")
        self._codebook = cfg.get("codebook", "spec/codebook.py")
        self._store = cfg.get("store", "store.json")

    @property
    def transcripts_dir(self):
        return self.root / self._t

    @property
    def labels_dir(self):
        return self.root / self._l

    @property
    def stimulus_path(self):
        return self.root / self._stimulus

    @property
    def store_path(self):
        return self.root / self._store

    def stimulus(self):
        return json.loads(self.stimulus_path.read_text())

    def codebook(self):
        """Import the study's codebook module (spec/codebook.py). Returns the module."""
        path = self.root / self._codebook
        spec = importlib.util.spec_from_file_location(f"_study_codebook_{self.root.name}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def transcripts(self):
        """All Contract-A files (model -> path), excluding the adjudicated store."""
        return sorted(p for p in self.transcripts_dir.glob("*.json")
                      if p.name not in ("markers.json", "store.json"))
