#!/usr/bin/env python3
"""실습 1·2 용 합성 리뷰 데이터 생성기 (Day 1).

Pandas·sklearn 실습용 데이터를 직접 만든다.
슬라이드 '실습 1' 시나리오와 동일한 잡음을 일부러 섞는다:
  - 이모티콘 / URL / 광고문구([광고], 협찬, 구매처:)
  - rating 일부 결측
  - created_at 형식 제각각

사용:
    python data/make_reviews.py            # data/reviews.csv (10,000행)
    python data/make_reviews.py --rows 500 # 행 수 지정
"""
from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

POS = [
    "배송이 정말 빨라서 깜짝 놀랐어요",
    "가성비 최고입니다 또 살게요",
    "포장도 꼼꼼하고 품질이 기대 이상이에요",
    "색감이 사진이랑 똑같아서 만족합니다",
    "재구매 의사 100% 강추합니다",
    "사이즈도 딱 맞고 마감이 깔끔해요",
]
NEG = [
    "생각보다 너무 작고 부실해요",
    "배송이 일주일이나 걸렸습니다 별로",
    "사진과 색이 완전히 달라서 실망했어요",
    "한 번 쓰고 고장났습니다 환불 원해요",
    "냄새가 너무 심해서 못 쓰겠어요",
    "고객센터 연결도 안 되고 최악이에요",
]
NEUTRAL = [
    "무난합니다 그냥 평타",
    "아직 잘 모르겠어요 더 써봐야 할 듯",
    "가격대비 그럭저럭이에요",
]
EMOJI = ["", "", " 😍", " 👍", " ㅠㅠ", " 🔥", " 😡", " 🙏"]
ADS = [
    "[광고] 지금 구매하면 사은품 증정! ",
    "협찬 받아 작성한 후기입니다. ",
    "구매처: http://shop.example.com 방문하세요 ",
    "",
    "",
    "",
]
URLS = ["", "", " http://bit.ly/abc123", " https://example.com/event", ""]
USERS = [f"user{n:03d}" for n in range(1, 121)]


def make_date(rng: random.Random, i: int) -> str:
    """일부러 형식을 뒤섞은 created_at."""
    y, m, d = 2026, rng.randint(1, 6), rng.randint(1, 28)
    hh, mm = rng.randint(0, 23), rng.randint(0, 59)
    fmt = i % 5
    if fmt == 0:
        return f"{y}-{m:02d}-{d:02d}"
    if fmt == 1:
        return f"{y}/{m:02d}/{d:02d} {hh:02d}:{mm:02d}"
    if fmt == 2:
        return f"{d:02d}.{m:02d}.{y}"
    if fmt == 3:
        return f"{y}-{m:02d}-{d:02d}T{hh:02d}:{mm:02d}:00"
    return ""  # 결측


def make_row(rng: random.Random, i: int) -> dict:
    bucket = rng.random()
    if bucket < 0.5:
        base, rating = rng.choice(POS), rng.choice([4, 5])
    elif bucket < 0.85:
        base, rating = rng.choice(NEG), rng.choice([1, 2])
    else:
        base, rating = rng.choice(NEUTRAL), 3

    text = rng.choice(ADS) + base + rng.choice(EMOJI) + rng.choice(URLS)
    # rating 5% 결측
    rating_out = "" if rng.random() < 0.05 else rating
    return {
        "id": i,
        "user": rng.choice(USERS),
        "text": text,
        "rating": rating_out,
        "created_at": make_date(rng, i),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=10_000)
    ap.add_argument("--out", default=str(Path(__file__).parent / "reviews.csv"))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    out = Path(args.out)
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "user", "text", "rating", "created_at"])
        w.writeheader()
        for i in range(1, args.rows + 1):
            w.writerow(make_row(rng, i))
    print(f"==> {out} 생성 완료 ({args.rows:,}행)")


if __name__ == "__main__":
    main()
