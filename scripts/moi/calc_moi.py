#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOI（Market Overheat Index） MVP
- 出力: data/moi.json
- 値域: 0–100（0=冷静, 100=過熱）
- ここではMVP用の簡易計算（Surprise/Reaction/Decayの枠だけ用意）
"""

import json, os, math, datetime as dt
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
OUT = DATA_DIR / "moi.json"
STATE = DATA_DIR / "moi_state.json"  # 自然減衰用に前回値を保持

JST = dt.timezone(dt.timedelta(hours=9))

def clamp(x, lo=0.0, hi=100.0): return max(lo, min(hi, x))

def load_prev():
    if STATE.exists():
        try:
            o = json.loads(STATE.read_text())
            return float(o.get("value", 50.0))
        except Exception:
            pass
    return 50.0

def save_state(v):
    STATE.write_text(json.dumps({"value": v}, ensure_ascii=False, indent=2))

def normalize(z):
    # 平常=50, 標準偏差=15 相当のスケーリング（MVP簡易版）
    return clamp(50 + 15 * z)

def calc_mvp_today(prev_value: float):
    """
    MVP: イベント寄与が無い日は自然減衰、ちょっとした市場の動きで±微調整。
    本実装では、あなたの既存パイプに接続して Surprise/Reaction を差し替えてください。
    """
    # ---- TODO: ここを本実装で置換 ----
    # 例: 既存の為替/先物・ニュース件数などから擬似zスコアを作る
    pseudo_event_z = 0.0     # 例: CPIなど材料が無ければ0
    market_noise = 0.0       # 例: USDJPYや先物の変化をATRで割ったもの

    # デモ：週末は冷却、平日たまに小幅+（あとで削除OK）
    today = dt.datetime.now(JST).weekday()
    if today in (5,6):  # Sat/Sun
        decay = 0.08
    else:
        decay = 0.05
        market_noise = 0.2  # 微加熱
    # ---------------------------------

    # 自然減衰（平均50へ）
    cooled = prev_value*(1-decay) + 50*decay
    # イベント/反応の寄与（とりあえずZ= ±1相当を±15pt）
    moi = normalize((cooled-50)/15 + pseudo_event_z + market_noise)
    return moi, ["特筆すべき経済イベントなし"] if abs(pseudo_event_z) < 0.01 else ["米CPI上振れ"]

def main():
    prev = load_prev()
    value, factors = calc_mvp_today(prev)
    now = dt.datetime.now(JST)
    # 前日比（STATEの値と比較）
    delta = round(value - prev, 1)

    out = {
        "value": round(value, 1),
        "delta": delta,
        "main_factors": factors[:2],
        "updated_at": now.strftime("%Y/%m/%d %H:%M"),
        "label": ("過熱" if value>=75 else "やや過熱" if value>=60 else
                  "平常" if value>=40 else "やや冷静" if value>=20 else "静穏")
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    save_state(value)
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
