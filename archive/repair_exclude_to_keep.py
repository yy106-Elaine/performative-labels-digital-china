import pandas as pd
from pathlib import Path
import shutil
import re

# =========================
# Paths
# =========================
KEEP_DIR = Path("filtered_data")
EXCL_DIR = Path("excluded_data")

KEEP_META = KEEP_DIR / "metadata_keep.csv"
EXCL_META = EXCL_DIR / "metadata_exclude.csv"

KEEP_VID_DIR = KEEP_DIR / "videos"
EXCL_VID_DIR = EXCL_DIR / "videos"

KEEP_VID_DIR.mkdir(parents=True, exist_ok=True)
EXCL_VID_DIR.mkdir(parents=True, exist_ok=True)

# Fallback source for videos (if not found in excluded/videos)
BASE_DIR = Path("Douyin_Data")
DOWNLOAD_DIR = BASE_DIR / "Download"

# =========================
# Pattern Definitions
# =========================

def token_pattern(token: str) -> str:
    """
    Match standalone tokens (e.g., wlw, le, la) without
    matching inside other English words.
    """
    return rf"(?<![A-Za-z0-9]){re.escape(token)}(?![A-Za-z0-9])"


CORE_PATTERNS = [
    # English shorthand
    token_pattern("wlw"),
    token_pattern("les"),
    token_pattern("lesbian"),
    token_pattern("la"),
    token_pattern("le"),
    token_pattern("gl"),
    token_pattern("t"),

    # Chinese identity / label patterns
    r"铁[ＴTt]",
    r"铁\s*[ＴTt]",
    r"姛",
    r"女姛",
    r"女同",
    r"拉拉",
    r"姬圈",
    r"双女主",
    r"女女",
    r"百合(?!花)",
    r"小狗",
    r"姐姐|姐",
    r"陈乐",
    r"甜妹",
    r"娘[pP]",
    r"奶[ＴTt]",
    r"长发[ＴTt]",
    r"短发[pP]",
    r"彩虹旗",
    r"🌈",
    r"纯拉",
    r"爷[ＴTt]",
    r"小狗型?",
    r"姐t",
    r"姐\s*t",

    # hashtag-style
    r"#le#", r"#la#", r"#wlw#", r"#les#", r"#t#",
    r"#la", r"#拉拉", r"#姬", r"#女同", r"#女女", r"#陈乐",

    # additional contextual phrases
    r"陈土豆",
    r"侄女",
    r"绝望的直女",
    r"女老师和女学生",
]

NOISE_PATTERNS = [
    r"百合花",
    r"盆栽",
    r"种植",
    r"园艺",
    r"养护技巧",
    r"花束",
    r"插花",
    r"百合炒肉",
    r"泰国百合",
]

CORE_REGEX = re.compile("|".join(f"(?:{p})" for p in CORE_PATTERNS), flags=re.I)
NOISE_REGEX = re.compile("|".join(f"(?:{p})" for p in NOISE_PATTERNS), flags=re.I)


def is_relevant(text: str) -> bool:
    if text is None:
        text = ""
    return bool(CORE_REGEX.search(text)) and not bool(NOISE_REGEX.search(text))


# =========================
# Load Existing Data
# =========================
keep_df = pd.read_csv(KEEP_META, dtype={"video_id": "string"})
exclude_df = pd.read_csv(EXCL_META, dtype={"video_id": "string"})


def build_text(df: pd.DataFrame) -> pd.Series:
    hashtags = df["hashtags"].fillna("").astype(str) if "hashtags" in df.columns else ""
    desc = df["description"].fillna("").astype(str) if "description" in df.columns else ""
    return (hashtags + " " + desc).astype(str)


exclude_text = build_text(exclude_df)

# =========================
# Re-screen only excluded samples
# =========================
mask_move = exclude_text.apply(is_relevant)

to_move_df = exclude_df[mask_move].copy()
still_exclude_df = exclude_df[~mask_move].copy()

print(f"[INFO] Recovered {len(to_move_df)} samples from excluded set")

# =========================
# Move or Copy Videos
# =========================
moved = 0
copied_from_download = 0
missing = 0

for vid in to_move_df["video_id"].astype(str):
    src_excl = EXCL_VID_DIR / f"{vid}.mp4"
    dst_keep = KEEP_VID_DIR / f"{vid}.mp4"

    if src_excl.exists():
        shutil.move(str(src_excl), str(dst_keep))
        moved += 1
    else:
        src_download = DOWNLOAD_DIR / f"{vid}.mp4"
        if src_download.exists():
            shutil.copy2(src_download, dst_keep)
            copied_from_download += 1
        else:
            missing += 1

# =========================
# Update Metadata
# =========================
new_keep_df = pd.concat([keep_df, to_move_df], ignore_index=True)
new_keep_df = new_keep_df.drop_duplicates(subset=["video_id"], keep="first")

still_exclude_df = still_exclude_df.drop_duplicates(subset=["video_id"], keep="first")

if "relevant_wlw" in new_keep_df.columns:
    new_keep_df["relevant_wlw"] = 1
if "relevant_wlw" in still_exclude_df.columns:
    still_exclude_df["relevant_wlw"] = 0

new_keep_df.to_csv(KEEP_META, index=False)
still_exclude_df.to_csv(EXCL_META, index=False)

print(
    "[DONE] Repair complete\n"
    f"- Moved to keep: {len(to_move_df)} rows\n"
    f"- Videos: moved {moved}, copied {copied_from_download}, missing {missing}\n"
    f"- Updated files:\n  {KEEP_META}\n  {EXCL_META}"
)
