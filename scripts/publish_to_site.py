#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
docs/outputs で生成したスナップショットを docs/charts に昇格する共通ユーティリティ。
指数リポジトリから呼び出して利用する。
"""

from __future__ import annotations
import json
from pathlib import Path
from shutil import copy2
from datetime import datetime, timezone, timedelta

def jst_now_iso():
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).isoformat()

def publish(index_key: str, label: str):
    ROOT = Path(__file__).resolve().parents[1]
    OUT = ROOT / "docs" / "outputs"
    CHARTS = ROOT / "docs" / "charts"
    CHARTS.mkdir(parents=True, exist_ok=True)

    src_png = OUT / f"{index_key.lower()}_intraday.png"
    dst_png = CHARTS / f"{index_key.lower()}_1d.png"
    src_stats = OUT / f"{index_key.lower()}_stats.json"
    dst_stats = CHARTS / f"{index_key.lower()}_stats.json"

    if not src_png.exists() or not src_stats.exists():
        raise FileNotFoundError(f"Missing output files for {index_key}")

    copy2(src_png, dst_png)
    copy2(src_stats, dst_stats)

    stats = json.loads(src_stats.read_text(encoding="utf-8"))
    meta = {
        "index_key": index_key,
        "label": label,
        "pct_intraday": stats.get("pct_intraday", 0.0),
        "basis": stats.get("basis", "prev_close"),
        "session": stats.get("session", {}),
        "updated_at": stats.get("updated_at", jst_now_iso()),
        "image": f"{index_key.lower()}_1d.png",
    }

    (CHARTS / f"_cards_{index_key.lower()}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[publish_to_site] Published {index_key} -> {dst_png}")

if __name__ == "__main__":
    publish("R_BANK9", "R-BANK9")
