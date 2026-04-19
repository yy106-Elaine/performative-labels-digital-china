import os
import re
import pandas as pd

VISUAL_CSV = "video_categorization.csv"
CAPTION_CSV = "metadata_keep_coded.csv"
INTERACTION_CSV = "video_interactions.csv"

OUTPUT_CSV = "video_categorization_with_stats.csv"


def normalize_id(x: object) -> str:
    """
    Extract the longest digit sequence as a normalized video ID.
    Works for file paths, URLs, and numeric-looking cells.
    """
    if pd.isna(x):
        return ""

    s = str(x).strip()
    s = os.path.basename(s)
    s = os.path.splitext(s)[0]

    digits = re.findall(r"\d+", s)
    if not digits:
        return ""

    return max(digits, key=len)


def main():
    visual_df = pd.read_csv(VISUAL_CSV)
    caption_df = pd.read_csv(CAPTION_CSV)
    interaction_df = pd.read_csv(INTERACTION_CSV, dtype={"video_id": str})

    print("Loaded visual rows:", len(visual_df))
    print("Loaded caption rows:", len(caption_df))
    print("Loaded interaction rows:", len(interaction_df))

    # ----------------------------
    # Normalize IDs
    # ----------------------------
    if "file_path" not in visual_df.columns:
        raise ValueError(f"{VISUAL_CSV} must contain a 'file_path' column.")

    if "video_id" not in caption_df.columns:
        raise ValueError(f"{CAPTION_CSV} must contain a 'video_id' column.")

    if "video_id" not in interaction_df.columns:
        raise ValueError(f"{INTERACTION_CSV} must contain a 'video_id' column.")

    visual_df["video_id"] = visual_df["file_path"].apply(normalize_id)
    caption_df["video_id"] = caption_df["video_id"].apply(normalize_id)
    interaction_df["video_id"] = interaction_df["video_id"].apply(normalize_id)

    # ----------------------------
    # Keep only needed caption columns
    # ----------------------------
    caption_small = caption_df[
        [
            "video_id",
            "caption_identity_involved",
            "caption_identity_category",
        ]
    ].copy()

    caption_small = caption_small.drop_duplicates(subset=["video_id"])

    # ----------------------------
    # Merge visual + caption
    # ----------------------------
    merged_df = visual_df.merge(caption_small, on="video_id", how="left")

    print(
        "Matched caption rows:",
        merged_df["caption_identity_involved"].notna().sum(),
        "/",
        len(merged_df),
    )

    # ----------------------------
    # Keep only needed interaction columns
    # ----------------------------
    interaction_small = interaction_df[
        ["video_id", "digg_count", "comment_count"]
    ].copy()

    interaction_small = interaction_small.drop_duplicates(subset=["video_id"])

    # ----------------------------
    # Merge interactions
    # ----------------------------
    merged_df = merged_df.merge(interaction_small, on="video_id", how="left")

    missing_interactions = merged_df["digg_count"].isna().sum()
    if missing_interactions > 0:
        print(
            f"[WARNING] {missing_interactions} videos did not find matching interaction data."
        )

    # ----------------------------
    # Drop audit / intermediate columns
    # ----------------------------
    drop_cols = [
        "raw_output",
        "file_path",
        "parse_ok",
    ]

    merged_df = merged_df.drop(
        columns=[c for c in drop_cols if c in merged_df.columns],
        errors="ignore",
    )

    # ----------------------------
    # Normalize categorical formatting
    # ----------------------------
    categorical_cols = [
        "video_style",
        "video_identity_present_visual",
        "video_identity_visual_type",
        "caption_identity_involved",
        "caption_identity_category",
    ]

    for col in categorical_cols:
        if col not in merged_df.columns:
            continue

        s = (
            merged_df[col]
            .astype(str)
            .replace({"N/A": "", "NA": "", "n/a": "", "na": "", "nan": "", "None": ""})
            .str.strip()
        )

        s_num = pd.to_numeric(s, errors="coerce")
        s_int = s_num.astype("Int64")
        merged_df[col] = s_int.astype(str).replace({"<NA>": "N/A"})

    # ----------------------------
    # Save
    # ----------------------------
    merged_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"[SUCCESS] Saved merged dataset: {OUTPUT_CSV}")
    print("Final columns:", list(merged_df.columns))
    print("Total rows:", len(merged_df))


if __name__ == "__main__":
    main()
