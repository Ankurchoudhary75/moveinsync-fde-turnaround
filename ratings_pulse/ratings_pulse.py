#!/usr/bin/env python3
"""
MoveInSync Play Store Ratings Pulse Engine
==========================================
Author: Forward Deployed Engineer Candidate
Assignment: MoveInSync FDE (Intern to FTE) - Play Store Rating Turnaround

Description:
  Automates the recurring question: "How are our Play Store ratings?"
  Fetches recent reviews, classifies them across a 10-theme taxonomy,
  computes trailing-30d rating, 7d vs prior-7d velocity, 1-star share,
  lowest-rated app versions, and week-over-week theme shifts mapped to owners.

Dependencies:
  pip install google-play-scraper pandas tabulate
"""

import argparse
import os
import re
from datetime import datetime, timedelta
import pandas as pd

# Multi-Label Review Taxonomy mapped directly to organizational owners
THEMES = {
    "no_show_dispute": r"no[\s-]?show|marked absent|salary|deduct|penal|fine\b",
    "gps_tracking_eta": r"gps|live location|tracking|\beta\b|estimated arrival|arrival time|location.*(wrong|incorrect|not)|vehicle.*location",
    "booking_date_bug": r"wrong date|different date|date.*(change|wrong)|booking.*(fail|error|not working)|can'?t book|unable to book",
    "pickup_time_change": r"pickup time|pick-up time|timing.*(change|wrong)|time keeps? chang|rescheduled",
    "notifications": r"notification|alert|sms|not receiv|push",
    "ui_ux_clutter": r"update|new ui|redesign|interface|confus|too many steps|2 step|difficult to use|user[\s-]?friendly|all cabs",
    "driver_ops": r"driver|rude|late (cab|pickup)|cab (late|didn'?t)|no cab|vehicle (late|not)",
    "app_stability": r"crash|\bhang(s|ing)?\b|freez|\bslow\b|\blag(gy|s)?\b|not (open|load|respond)|\bstuck\b|\bbugs?\b",
    "support_gap": r"no (response|reply|support)|support.*(useless|bad|not)|helpdesk|complaint.*(ignored|no action)",
    "positive": r"\b(good|great|excellent|best|nice|helpful|easy|smooth|love|reliable)\b"
}

THEME_OWNERS = {
    "no_show_dispute": "Product + Ops Policy",
    "gps_tracking_eta": "Mobile + Routing Infra",
    "booking_date_bug": "Mobile Core + Backend API",
    "pickup_time_change": "Routing Engine + Product",
    "notifications": "Platform Notification Service",
    "ui_ux_clutter": "Product Design",
    "driver_ops": "Operations (via Driver Partner App)",
    "app_stability": "Mobile Engineering Squad",
    "support_gap": "Customer Success & Triage Rota",
    "positive": "Core Product Retention"
}

def label_review(text: str):
    """Assigns multi-label theme tags based on keyword patterns."""
    t = (text or "").lower()
    hits = [k for k, rx in THEMES.items() if re.search(rx, t)]
    neg = [h for h in hits if h != "positive"]
    return neg if neg else (["positive"] if hits else ["other"])

def fetch_reviews(app_id: str, count: int, lang: str = "en", country: str = "in") -> pd.DataFrame:
    """Fetches reviews via google-play-scraper with continuation pagination."""
    try:
        from google_play_scraper import reviews, Sort
    except ImportError:
        print("[!] google-play-scraper not found. Please run: pip install google-play-scraper")
        return pd.DataFrame()

    collected, token = [], None
    print(f"[*] Fetching up to {count} reviews for app: {app_id} (country={country}, lang={lang})...")
    while len(collected) < count:
        batch, token = reviews(
            app_id, lang=lang, country=country, sort=Sort.NEWEST,
            count=min(200, count - len(collected)), continuation_token=token
        )
        collected += batch
        if not token or not batch:
            break
    print(f"[+] Successfully fetched {len(collected)} reviews.")
    df = pd.DataFrame(collected)
    if not df.empty and "at" in df.columns:
        df["at"] = pd.to_datetime(df["at"])
    return df

def generate_pulse_report(df: pd.DataFrame, app_id: str) -> str:
    """Generates an executive-ready Markdown summary digest."""
    if df.empty:
        return f"# Ratings Pulse: No reviews available for {app_id}."

    now = df["at"].max()
    cur = df[df["at"] > now - timedelta(days=7)]
    prev = df[(df["at"] <= now - timedelta(days=7)) & (df["at"] > now - timedelta(days=14))]
    r30 = df[df["at"] > now - timedelta(days=30)]

    def calc_1star(d): return (d["score"] == 1).mean() * 100 if len(d) > 0 else 0.0

    cur_avg = cur['score'].mean() if len(cur) > 0 else 0.0
    prev_avg = prev['score'].mean() if len(prev) > 0 else 0.0
    r30_avg = r30['score'].mean() if len(r30) > 0 else 0.0
    lifetime_avg = df['score'].mean() if len(df) > 0 else 0.0

    lines = [
        f"# Ratings Pulse Weekly Digest — {app_id} — {now:%Y-%m-%d}",
        "",
        "## 1. Executive Summary & Headline Metrics",
        f"- **Trailing 30-Day Rating:** **{r30_avg:.2f}★** (n={len(r30)}) | Lifetime Sample Avg: **{lifetime_avg:.2f}★** (n={len(df)})",
        f"- **7-Day Rating Trend:** **{cur_avg:.2f}★** (Last 7d) vs **{prev_avg:.2f}★** (Prior 7d) -> {cur_avg - prev_avg:+.2f}★ WoW",
        f"- **1-Star Review Share:** **{calc_1star(cur):.1f}%** (Last 7d) vs **{calc_1star(prev):.1f}%** (Prior 7d)",
        f"- **Review Velocity:** {len(cur)} reviews in last 7d (vs {len(prev)} in prior 7d)"
    ]

    if "replyContent" in df.columns:
        neg = df[df["score"] <= 3]
        reply_pct = neg['replyContent'].notna().mean() * 100 if len(neg) > 0 else 0.0
        lines.append(f"- **Triage Response Coverage (1–3★):** **{reply_pct:.1f}%**")

    # Release version breakdown
    if "reviewCreatedVersion" in df.columns:
        recent_ver = df[df["at"] > now - timedelta(days=60)]
        v_summary = (recent_ver.groupby("reviewCreatedVersion")["score"]
                     .agg(["mean", "count"]).query("count >= 20")
                     .sort_values("mean").head(5))
        if not v_summary.empty:
            lines += ["", "## 2. Lowest-Rated App Releases (Trailing 60 Days, n >= 20)", v_summary.round(2).to_markdown()]

    # 1-2 Star Review Themes
    low = df[df["score"] <= 2]
    if not low.empty:
        th_counts = low.explode("themes")["themes"].value_counts()
        th_prev = low[low["at"] <= now - timedelta(days=7)].explode("themes")["themes"].value_counts(normalize=True)
        th_cur = low[low["at"] > now - timedelta(days=7)].explode("themes")["themes"].value_counts(normalize=True)

        lines += [
            "",
            "## 3. Negative Review Themes Breakdown (1–2★ Focus)",
            "| Theme | Count | Share | WoW Shift | Assigned Owner |",
            "|---|---|---|---|---|"
        ]
        for k, count in th_counts.head(8).items():
            if k in ["other", "positive"]: continue
            share = (count / len(low)) * 100
            cur_pct = th_cur.get(k, 0.0) * 100
            prev_pct = th_prev.get(k, 0.0) * 100
            shift = f"{cur_pct - prev_pct:+.1f}pp"
            lines.append(f"| `{k}` | {count} | {share:.1f}% | {shift} | {THEME_OWNERS.get(k, 'Unassigned')} |")

    return "\n".join(lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MoveInSync Ratings Pulse")
    parser.add_argument("--app", default="com.moveinsync.ets", help="Android package name")
    parser.add_argument("--count", type=int, default=1000, help="Number of reviews to fetch")
    parser.add_argument("--out", default="pulse_out", help="Output directory")
    parser.add_argument("--csv", default=None, help="Optional existing CSV to analyze")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    if args.csv and os.path.exists(args.csv):
        df = pd.read_csv(args.csv, parse_dates=["at"])
    else:
        df = fetch_reviews(args.app, args.count)

    if not df.empty:
        df["themes"] = df["content"].fillna("").map(label_review)
        csv_path = os.path.join(args.out, "labeled_reviews.csv")
        df.assign(themes=df["themes"].map("|".join)).to_csv(csv_path, index=False)
        print(f"[+] Labeled reviews saved to {csv_path}")

        report = generate_pulse_report(df, args.app)
        md_path = os.path.join(args.out, "pulse.md")
        with open(md_path, "w") as f:
            f.write(report)
        print(f"[+] Executive Pulse digest saved to {md_path}\n")
        print(report)
    else:
        print("[!] No data available to analyze.")
