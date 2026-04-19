# Data Dictionary

This document describes the variables used in the anonymized sample datasets.  
All data are simplified and anonymized for privacy and ethical considerations.

---

## Common Field

### sample_id
- Description: An anonymized identifier for each video sample.
- Note: Does not correspond to real Douyin video IDs.

---

## sample_raw_like/sample_existing_metadata.csv

### caption_text
- Description: Generalized or rewritten version of the original video caption.

### hashtags
- Description: Simplified representation of hashtags extracted from the original content.

### status_note
- Description: Status of metadata extraction.
- Values:
  - `ok`: metadata successfully retrieved
  - `missing_json`: metadata not available or failed to extract

---

## sample_filtered/sample_metadata_keep.csv

### description
- Description: Generalized summary of the caption content used for classification.

### hashtags
- Description: Simplified hashtag features used for identifying content themes.

### relevant_wlw
- Description: Indicator of whether the video is classified as relevant to women-loving-women (WLW) content.
- Values:
  - `1`: relevant
- Note: This dataset only includes videos classified as relevant.

---

## sample_enriched/sample_video_interaction.csv

### digg_count
- Description: Number of likes on the video.

### comment_count
- Description: Number of comments on the video.

### collect_count
- Description: Number of times the video was saved/bookmarked.

### share_count
- Description: Number of times the video was shared.

### status_note
- Description: Status of interaction data collection.

### source
- Description: Source of the interaction data (e.g., `detail_json`).

---

## sample_ai_analysis/sample_video_categorization.csv

### relevant_wlw
- Description: Binary indicator of WLW relevance.

### video_style
- Description: Categorical variable representing video format or style (e.g., performance, daily life, aesthetic content).

### video_identity_present_visual
- Description: Whether identity-related signals are visually present in the video.
- Values:
  - `1`: present
  - `0`: not present

### video_identity_visual_type
- Description: Type of visual identity signal (if present).
- Values:
  - categorical codes or `N/A`

### label_culture_effect
- Description: Indicator of whether labeling practices influence the video's presentation or interpretation.
- Values:
  - categorical codes or `N/A`

### caption_identity_involved
- Description: Whether identity labeling appears in the caption text.
- Values:
  - `1`: present
  - `0`: not present

### caption_identity_category
- Description: Type of identity label used in the caption.
- Values:
  - `1`: traditional T/P/H labels
  - `2`: variants or modified forms
  - `3`: alternative or emerging labels
  - `N/A`: no label present

### digg_count
- Description: Number of likes (merged from interaction data).

### comment_count
- Description: Number of comments (merged from interaction data).

---

## evaluation_sample/

### relevant_wlw
- Description: WLW relevance label assigned by human coders or AI.

### video_identity_present_visual
- Description: Visual presence of identity-related signals.

### caption_identity_involved
- Description: Whether caption contains identity-related elements.

### caption_identity_category
- Description: Category of identity labeling in caption.

- Note:
  - Human coding is performed independently by two coders.
  - A reconciled agreement dataset is created after discussion.
  - AI results are compared with human labels for Cohen’s kappa evaluation.
