import pandas as pd


INTERCODER_FILES = {
    "zx": "Evaluation/test_zx.csv",
    "yy": "Evaluation/test_yy.csv",
}

HUMAN_FILE = "Evaluation/test_together.csv"
AI_FILE = "evaluation_with_relevant_wlw.csv"


def cohens_kappa_manual(df, col1, col2):
    sub = df[[col1, col2]].copy()
    N = len(sub)

    if N == 0:
        return {"N": 0, "agreement_rate": None, "p_e": None, "kappa": None, "categories": []}

    p_o = (sub[col1] == sub[col2]).mean()
    categories = sorted(set(sub[col1]).union(set(sub[col2])))

    p_e = 0
    for k in categories:
        n_k1 = (sub[col1] == k).sum()
        n_k2 = (sub[col2] == k).sum()
        p_e += (n_k1 * n_k2) / (N ** 2)

    kappa = (p_o - p_e) / (1 - p_e) if p_e != 1 else 1.0

    return {
        "N": N,
        "agreement_rate": p_o,
        "p_e": p_e,
        "kappa": kappa,
        "categories": categories,
    }


def run_intercoder():
    zx = pd.read_csv(INTERCODER_FILES["zx"])
    yy = pd.read_csv(INTERCODER_FILES["yy"])

    zx.columns = zx.columns.str.strip()
    yy.columns = yy.columns.str.strip()

    cols = [
        "url",
        "relevant_wlw",
        "video_identity_present_visual",
        "caption_identity_involved",
    ]

    zx = zx[cols].copy()
    yy = yy[cols].copy()

    merged = pd.merge(
        zx,
        yy,
        on="url",
        suffixes=("_zx", "_yy"),
        how="inner",
    )

    merged["relevant_wlw_zx"] = pd.to_numeric(merged["relevant_wlw_zx"], errors="coerce")
    merged["relevant_wlw_yy"] = pd.to_numeric(merged["relevant_wlw_yy"], errors="coerce")

    print("\n========== INTER-CODER ==========")
    print("Matched rows:", len(merged))

    kappa_relevant = cohens_kappa_manual(
        merged,
        "relevant_wlw_zx",
        "relevant_wlw_yy",
    )

    both_relevant = merged[
        (merged["relevant_wlw_zx"] == 1) &
        (merged["relevant_wlw_yy"] == 1)
    ].copy()

    kappa_visual = cohens_kappa_manual(
        both_relevant,
        "video_identity_present_visual_zx",
        "video_identity_present_visual_yy",
    )

    kappa_caption = cohens_kappa_manual(
        both_relevant,
        "caption_identity_involved_zx",
        "caption_identity_involved_yy",
    )

    print("\n[INTER] Relevant WLW")
    print(kappa_relevant)
    print("\n[INTER] Video Identity Visual")
    print(kappa_visual)
    print("\n[INTER] Caption Identity Involved")
    print(kappa_caption)


def run_human_vs_ai():
    human = pd.read_csv(HUMAN_FILE)
    ai = pd.read_csv(AI_FILE)

    human.columns = human.columns.str.strip()
    ai.columns = ai.columns.str.strip()

    cols = [
        "url",
        "relevant_wlw",
        "video_identity_present_visual",
        "caption_identity_involved",
    ]

    human = human[cols].copy()
    ai = ai[cols].copy()

    merged = pd.merge(
        human,
        ai,
        on="url",
        suffixes=("_human", "_ai"),
        how="inner",
    )

    merged["relevant_wlw_human"] = pd.to_numeric(merged["relevant_wlw_human"], errors="coerce")
    merged["relevant_wlw_ai"] = pd.to_numeric(merged["relevant_wlw_ai"], errors="coerce")

    print("\n========== HUMAN vs AI ==========")
    print("Matched rows:", len(merged))

    kappa_relevant = cohens_kappa_manual(
        merged,
        "relevant_wlw_human",
        "relevant_wlw_ai",
    )

    both_relevant = merged[
        (merged["relevant_wlw_human"] == 1) &
        (merged["relevant_wlw_ai"] == 1)
    ].copy()

    kappa_visual = cohens_kappa_manual(
        both_relevant,
        "video_identity_present_visual_human",
        "video_identity_present_visual_ai",
    )

    kappa_caption = cohens_kappa_manual(
        both_relevant,
        "caption_identity_involved_human",
        "caption_identity_involved_ai",
    )

    print("\n[AI] Relevant WLW")
    print(kappa_relevant)
    print("\n[AI] Video Identity Visual")
    print(kappa_visual)
    print("\n[AI] Caption Identity Involved")
    print(kappa_caption)


def main():
    run_intercoder()
    run_human_vs_ai()


if __name__ == "__main__":
    main()
