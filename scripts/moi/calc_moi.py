#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOI（Market Overheat Index） 計算スクリプト v2
- 0 = 冷静, 100 = 過熱
- 出力:
    data/moi.json            … 現在値（リアルタイム/5分）
    data/moi_state.json      … 前回値の保持（自然減衰用）
    data/moi_daily.json      … 日次スナップショット（--snapshot 時のみ）
- 使い方:
    python scripts/moi/calc_moi.py                 # 通常（5分更新など）
    python scripts/moi/calc_moi.py --snapshot     # 毎朝7時の確定値
    python scripts/moi/calc_moi.py --output-dir docs/data   # Pagesをdocs配信にしている場合
"""

import argparse, json, os, math, datetime as dt
from pathlib import Path

JST = dt.timezone(dt.timedelta(hours=9))

def clamp(x, lo=0.0, hi=100.0): return max(lo, min(hi, x))

def normalize_to_0_100(z, mean=50, sigma=15):
    """ z(=0基準) を 0–100 に正規化（平均=50, 1σ=15pt 相当） """
    return clamp(mean + sigma * z, 0, 100)

def label_for(v: float) -> str:
    if v >= 90: return "過熱(極)"
    if v >= 75: return "過熱"
    if v >= 60: return "やや過熱"
    if v >= 40: return "平常"
    if v >= 20: return "やや冷静"
    return "静穏"

def load_state(state_path: Path) -> float:
    if state_path.exists():
        try:
            o = json.loads(state_path.read_text())
            return float(o.get("value", 50.0))
        except Exception:
            pass
    return 50.0

def save_state(state_path: Path, v: float):
    state_path.write_text(json.dumps({"value": float(v)}, ensure_ascii=False, indent=2))

def calc_moi(prev_value: float, light: bool) -> tuple[float, list[str]]:
    """
    MVP実装：
      - 自然減衰（平均=50へ戻る）
      - 軽い市場ノイズ（例: 為替/先物/件数）を擬似的に +α
    本実装に差し替えるときは、ここで Surprise/Reaction/Decay を計算してください。
    """
    # --- decay 設計（週末は冷却強め） ---
    today = dt.datetime.now(JST).weekday()  # Mon=0 .. Sun=6
    decay = 0.05 if today not in (5, 6) else 0.08

    # --- 擬似ノイズ（軽量時は小さめ） ---
    market_noise_z = 0.15 if not light else 0.05  # z値として足し込み

    cooled = prev_value * (1 - decay) + 50 * decay
    # zへ変換 → ノイズ加算 → 0-100へ
    z = (cooled - 50) / 15 + market_noise_z
    value = normalize_to_0_100(z)

    # 主因（本実装時は寄与ランキングの上位を返す）
    factors = ["特筆すべき経済イベントなし"]
    return value, factors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", action="store_true",
                    help="日次スナップショット（moi_daily.json）も出力")
    ap.add_argument("--output-dir", default=os.environ.get("MOI_OUTPUT_DIR", "data"),
                    help="出力先ディレクトリ（既定: data）")
    ap.add_argument("--light", action="store_true",
                    help="軽量計算モード（5分更新向け）")
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    state_path = out_dir / "moi_state.json"
    moi_path   = out_dir / "moi.json"
    daily_path = out_dir / "moi_daily.json"

    prev = load_state(state_path)
    value, factors = calc_moi(prev, light=args.light)

    now = dt.datetime.now(JST)
    delta = round(value - prev, 1)
    out = {
        "value": round(value, 1),
        "delta": delta,
        "main_factors": factors[:2],
        "updated_at": now.strftime("%Y/%m/%d %H:%M"),
        "label": label_for(value),
    }

    moi_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    save_state(state_path, value)

    # スナップショット（毎朝7時用）
    if args.snapshot:
        daily_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))

    print(f"Wrote {moi_path}")
    if args.snapshot:
        print(f"Wrote {daily_path}")

if __name__ == "__main__":
    main()
