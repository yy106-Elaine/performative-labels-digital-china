import pandas as pd
import re


AI_SOURCE_CSV = "video_categorization_with_stats_relevant.csv"
AI_OUTPUT_CSV = "evaluation_with_relevant_wlw.csv"

HUMAN_FILES = [
    "Evaluation/test_together.csv",
    "Evaluation/test_zx.csv",
    "Evaluation/test_yy.csv",
]

ORIGINAL_LABELS_FILE = "Evaluation/video_categorization_original_labels.csv"


def normalize_video_id(x):
    if pd.isna(x):
        return ""
    s = str(x).strip()

    match = re.search(r"/video/(\d+)", s)
    if match:
        return match.group(1)

    digits = re.findall(r"\d+", s)
    if digits:
        return max(digits, key=len)

    return s


def clean_value(x):
    if pd.isna(x):
        return "N/A"

    x = str(x).strip()

    if x in {"", "nan", "NaN", "None", "N/A", "n/a", "NA", "na", "N-A", "n-a", "-"}:
        return "N/A"
    if x in {"0", "0.0"}:
        return "0"
    if x in {"1", "1.0"}:
        return "1"
    if x in {"2", "2.0"}:
        return "2"
    if x in {"3", "3.0"}:
        return "3"

    return x


def prepare_ai_reference():
    orig = pd.read_csv(ORIGINAL_LABELS_FILE, encoding="utf-8-sig")
    full = pd.read_csv(AI_SOURCE_CSV, encoding="utf-8-sig")

    if "url" not in orig.columns:
        raise ValueError(f"{ORIGINAL_LABELS_FILE} must contain a 'url' column.")

    orig["url"] = orig["url"].astype(str).str.strip()
    orig["video_id_norm"] = orig["url"].apply(normalize_video_id)

    full["video_id_norm"] = full["video_id"].apply(normalize_video_id)
    full["url"] = "https://www.douyin.com/video/" + full["video_id_norm"]

    full_small = full[
        [
            "video_id_norm",
            "url",
            "relevant_wlw",
            "video_identity_present_visual",
            "caption_identity_involved",
            "caption_identity_category",
        ]
    ].drop_duplicates(subset=["video_id_norm"])

    merged = orig.merge(
        full_small,
        on="video_id_norm",
        how="left",
        suffixes=("", "_from_full"),
    )

    if "url_from_full" in merged.columns:
        merged["url"] = merged["url"].fillna(merged["url_from_full"])
        merged = merged.drop(columns=["url_from_full"])

    cols_order = [
        "url",
        "relevant_wlw",
        "video_identity_present_visual",
        "caption_identity_involved",
        "caption_identity_category",
    ]

    merged_final = merged[[c for c in cols_order if c in merged.columns]]
    merged_final.to_csv(AI_OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"Saved AI evaluation reference: {AI_OUTPUT_CSV}")
    print("Total rows:", len(merged_final))
    print("Matched relevant_wlw:", merged_final["relevant_wlw"].notna().sum())


def clean_human_file(file_path):
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    target_cols = [
        "video_identity_present_visual",
        "caption_identity_involved",
        "caption_identity_category",
    ]

    for col in target_cols:
        df[col] = df[col].apply(clean_value)

    df["relevant_wlw"] = df.apply(
        lambda row: "0" if all(row[col] == "N/A" for col in target_cols) else "1",
        axis=1,
    )

    cols = df.columns.tolist()
    if "relevant_wlw" in cols:
        cols.remove("relevant_wlw")
        if "url" in cols:
            url_idx = cols.index("url")
            cols.insert(url_idx + 1, "relevant_wlw")
        else:
            cols.insert(0, "relevant_wlw")
        df = df[cols]

    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"Cleaned: {file_path}")


def main():
    prepare_ai_reference()

    for file_path in HUMAN_FILES:
        clean_human_file(file_path)


if __name__ == "__main__":
    main()
