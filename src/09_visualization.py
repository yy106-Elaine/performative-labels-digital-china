import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ---------------------------
# Global style
# ---------------------------
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 11,
    "figure.dpi": 200,
})

INPUT_CSV = "video_categorization_with_stats_relevant_clean.csv"

COL_VIDEO_ONLY = "#5B4AA8"
COL_BOTH = "#8F7FD0"
COL_CAP_ONLY = "#B9AEEA"
COL_NOT = "#D8D6E8"

COL_ORIG = "#5B4AA8"
COL_VAR = "#8F7FD0"
COL_ALT = "#B9AEEA"

COL_NEUTRAL = "#D8D6E8"
COL_SIGNALED = "#5B4AA8"


# ---------------------------
# Helpers
# ---------------------------
def to01(x):
    s = "" if x is None else str(x).strip()
    if s in ["1", "True", "true"]:
        return 1
    if s in ["0", "False", "false", "-", "", "nan", "None", "N/A"]:
        return 0
    try:
        return 1 if int(float(s)) == 1 else 0
    except Exception:
        return 0


def clean_caption_category(x):
    if pd.isna(x):
        return None
    s = str(x).strip().split(".")[0]
    if s == "1":
        return "orig"
    if s == "2":
        return "var"
    if s == "3":
        return "alt"
    return None


def format_k(value):
    if value >= 1000:
        return f"{value / 1000:.0f}k"
    return f"{value:.0f}"


# ---------------------------
# Figure 1
# Label-related vs non-related videos
# ---------------------------
def plot_label_related_structure(df: pd.DataFrame):
    vis_col = "video_identity_present_visual"
    cap_col = "caption_identity_involved"

    vis = df[vis_col].map(to01).to_numpy()
    cap = df[cap_col].map(to01).to_numpy()

    both = (vis == 1) & (cap == 1)
    vis_only = (vis == 1) & (cap == 0)
    cap_only = (vis == 0) & (cap == 1)
    neither = (vis == 0) & (cap == 0)

    n = len(df)

    cnt_vis_only = int(vis_only.sum())
    cnt_both = int(both.sum())
    cnt_cap_only = int(cap_only.sum())
    cnt_neither = int(neither.sum())

    pct = lambda k: 100.0 * (k / n)

    p_vis_only = pct(cnt_vis_only)
    p_both = pct(cnt_both)
    p_cap_only = pct(cnt_cap_only)
    p_neither = pct(cnt_neither)

    fig, ax = plt.subplots(figsize=(7.6, 2.15))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    y_related = 1
    y_not = 0

    left = 0
    ax.barh(y_related, p_cap_only, left=left, color=COL_CAP_ONLY, edgecolor="none", label="Caption only")
    left += p_cap_only
    ax.barh(y_related, p_both, left=left, color=COL_BOTH, edgecolor="none", label="Both video + caption")
    left += p_both
    ax.barh(y_related, p_vis_only, left=left, color=COL_VIDEO_ONLY, edgecolor="none", label="Video only")
    ax.barh(y_not, p_neither, color=COL_NOT, edgecolor="none", label="Not related")

    ax.set_xlim(0, 100)
    ax.set_yticks([y_related, y_not])
    ax.set_yticklabels(["Label-related", "Not related"], fontweight="bold")
    ax.set_xlabel("Percent of all videos (%)", fontweight="bold")

    for tick in ax.get_xticklabels():
        tick.set_fontweight("bold")

    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color("black")
    ax.spines["left"].set_linewidth(1.2)
    ax.spines["bottom"].set_visible(True)
    ax.spines["bottom"].set_color("black")
    ax.spines["bottom"].set_linewidth(1.0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

    def annotate_pct(y, left, width):
        if width >= 3:
            ax.text(
                left + width / 2,
                y,
                f"{width:.1f}%",
                ha="center",
                va="center",
                fontweight="bold",
                fontsize=9,
            )

    left = 0
    annotate_pct(y_related, left, p_cap_only)
    left += p_cap_only
    annotate_pct(y_related, left, p_both)
    left += p_both
    annotate_pct(y_related, left, p_vis_only)
    annotate_pct(y_not, 0, p_neither)

    fig.suptitle("Label-related vs Non-related Videos", y=1.06, fontweight="bold")

    ax.text(
        0.67,
        1.08,
        f"Total sample: n={n}",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontweight="bold",
        fontsize=10,
    )

    ax.legend(
        loc="lower left",
        bbox_to_anchor=(0.66, 0.02),
        frameon=False,
        prop={"weight": "bold"},
    )

    plt.tight_layout(pad=0.4)
    plt.savefig(
        "figure1_label_related_structure.png",
        transparent=True,
        bbox_inches="tight",
        pad_inches=0.01,
    )
    plt.show()

    print("Saved: figure1_label_related_structure.png")


# ---------------------------
# Figure 2
# Caption label category distribution
# ---------------------------
def plot_caption_label_distribution(df: pd.DataFrame):
    cap_col = "caption_identity_category"

    df = df.copy()
    df["cat_clean"] = df[cap_col].map(clean_caption_category)
    cap_df = df[df["cat_clean"].notna()].copy()

    cnt_orig = (cap_df["cat_clean"] == "orig").sum()
    cnt_var = (cap_df["cat_clean"] == "var").sum()
    cnt_alt = (cap_df["cat_clean"] == "alt").sum()

    sizes = [cnt_orig, cnt_var, cnt_alt]
    n_cap = len(cap_df)

    if n_cap == 0:
        print("No caption identity categories available for plotting.")
        return

    labels = ["Original T/P/H", "T/P/H Variants", "Alternative Labels"]

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    wedges, texts, autotexts = ax.pie(
        sizes,
        startangle=90,
        colors=[COL_ORIG, COL_VAR, COL_ALT],
        autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
        pctdistance=0.72,
        radius=1.3,
        center=(0.10, 0.0),
        textprops={"fontweight": "bold", "fontsize": 12},
        wedgeprops={"linewidth": 1.6, "edgecolor": "white"},
    )

    plt.setp(autotexts, size=11, weight="bold")

    fig.suptitle(
        "Caption Labeling: From T/P/H to Alternatives",
        y=1.02,
        fontweight="bold",
        fontsize=18,
    )

    fig.text(0.85, 0.82, f"Total sample: n={n_cap}", ha="center", fontweight="bold", fontsize=11)
    fig.text(0.85, 0.77, "(Captions with Identity Labels)", ha="center", fontweight="bold", fontsize=11)

    ax.legend(
        wedges,
        labels,
        loc="center left",
        bbox_to_anchor=(1.1, 0.5),
        frameon=False,
        prop={"weight": "bold", "size": 13},
    )

    ax.set_aspect("equal")

    plt.savefig(
        "figure2_caption_label_distribution.png",
        transparent=True,
        bbox_inches="tight",
        pad_inches=0.1,
    )
    plt.show()

    print("Saved: figure2_caption_label_distribution.png")


# ---------------------------
# Figure 3
# Audience engagement
# ---------------------------
def plot_engagement_comparison(df: pd.DataFrame):
    df = df.copy()

    for col in [
        "video_identity_present_visual",
        "caption_identity_involved",
        "digg_count",
        "comment_count",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["identity_group"] = np.where(
        (df["video_identity_present_visual"] == 1) | (df["caption_identity_involved"] == 1),
        "Identity Signaled\n(Label Present)",
        "Identity Neutral\n(No Label)",
    )

    group_names = [
        "Identity Neutral\n(No Label)",
        "Identity Signaled\n(Label Present)",
    ]

    stats = df.groupby("identity_group")[["digg_count", "comment_count"]].mean()
    likes = [stats.loc[name, "digg_count"] for name in group_names]
    comments = [stats.loc[name, "comment_count"] for name in group_names]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.2))
    fig.patch.set_alpha(0)
    ax1.set_facecolor("none")
    ax2.set_facecolor("none")

    bars1 = ax1.bar(group_names, likes, color=[COL_NEUTRAL, COL_SIGNALED], width=0.55, edgecolor="none")
    ax1.set_title("Average Likes", fontweight="bold", fontsize=14, pad=18)
    ax1.set_ylabel("Count", fontweight="bold", fontsize=13, labelpad=10)

    for bar in bars1:
        h = bar.get_height()
        if not np.isnan(h):
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                h * 1.02,
                format_k(h),
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=12,
            )

    bars2 = ax2.bar(group_names, comments, color=[COL_NEUTRAL, COL_SIGNALED], width=0.55, edgecolor="none")
    ax2.set_title("Average Comments", fontweight="bold", fontsize=14, pad=18)
    ax2.set_ylabel("Count", fontweight="bold", fontsize=13, labelpad=12)

    for bar in bars2:
        h = bar.get_height()
        if not np.isnan(h):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                h * 1.02,
                format_k(h),
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=12,
            )

    for ax in (ax1, ax2):
        ax.tick_params(axis="x", labelsize=12)
        ax.tick_params(axis="y", labelsize=12)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: format_k(x)))

        for t in ax.get_xticklabels():
            t.set_fontweight("bold")
        for t in ax.get_yticklabels():
            t.set_fontweight("bold")

        ax.spines["left"].set_visible(True)
        ax.spines["left"].set_color("black")
        ax.spines["left"].set_linewidth(1.2)
        ax.spines["bottom"].set_visible(True)
        ax.spines["bottom"].set_color("black")
        ax.spines["bottom"].set_linewidth(1.0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(False)

    fig.suptitle(
        "T/P/H-related Identity Labels and Audience Engagement",
        fontsize=18,
        fontweight="bold",
        y=1.1,
    )

    fig.text(
        0.68,
        1.0,
        f"Total videos analyzed (n={len(df)})",
        ha="left",
        va="top",
        fontweight="bold",
        fontsize=14,
    )

    plt.tight_layout(pad=0.6)
    plt.subplots_adjust(wspace=0.32)

    plt.savefig(
        "figure3_video_engagement_pattern.png",
        dpi=300,
        transparent=True,
        bbox_inches="tight",
        pad_inches=0.01,
    )
    plt.show()

    print("Saved: figure3_video_engagement_pattern.png")

    if likes[0] and comments[0]:
        print(f"Likes ratio (Label Present / No Label): {likes[1] / likes[0]:.2f}x")
        print(f"Comments ratio (Label Present / No Label): {comments[1] / comments[0]:.2f}x")


# ---------------------------
# Main
# ---------------------------
def main():
    df = pd.read_csv(INPUT_CSV, dtype=str)
    print("Loaded rows:", len(df))
    print("Columns:", list(df.columns))

    plot_label_related_structure(df)
    plot_caption_label_distribution(df)
    plot_engagement_comparison(df)


if __name__ == "__main__":
    main()
