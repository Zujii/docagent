"""Eval runner skeleton: one config in, one results JSON out.
Config example (evals/default.json):
{"parser":"docling","retrieval":"hybrid","use_critic":true,"guardrails":true,"gold":"evals/gold.jsonl"}
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
from ..config import Config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    run_cfg = json.loads(Path(args.config).read_text())
    cfg = Config(use_critic=run_cfg.get("use_critic", True), guardrails=run_cfg.get("guardrails", True))
    # TODO: load docs/chunks for run_cfg["parser"], build index with run_cfg["retrieval"] mode,
    # build graph, loop over gold questions, compute metrics from eval.metrics, write results.
    gold = [json.loads(l) for l in Path(run_cfg["gold"]).read_text().splitlines() if l.strip()]
    results = {"config": run_cfg, "n_questions": len(gold), "timestamp": time.time(), "metrics": {}}
    out = cfg.data_dir.parent / "evals" / f"results_{int(time.time())}.json"
    out.write_text(json.dumps(results, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
