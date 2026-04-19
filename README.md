# Performative Labels Under Censorship  
### T/P/H Labeling Culture and Lesbian Identity in Digital China

This project investigates how lesbian identity labeling practices (T/P/H culture) are performed, transformed, and negotiated on Chinese short-video platforms, particularly Douyin.

It combines computational social media analysis with cultural studies approaches to examine how identity is signaled through captions, visual presentation, and platform interaction patterns.

---

## Overview

The project builds a full data pipeline to:

- Collect Douyin video URLs based on identity-related keywords  
- Extract video metadata and captions  
- Filter relevant lesbian content using rule-based and multimodal methods  
- Code identity signals in both visual and textual dimensions  
- Merge coding results with engagement data (likes, comments)  
- Construct a final analytical dataset  
- Evaluate coding reliability using human annotation and Cohen’s kappa  

The analysis focuses on how labeling practices shift from traditional T/P/H categories toward more flexible and performative identity expressions.

---

## Repository Structure

```text
src/
├── 01_search_scraper.py              # Collect video URLs from Douyin search
├── 02_extract_metadata.py           # Extract captions and hashtag metadata
├── 03_filter_keyword.py             # Rule-based keyword filtering
├── 04_filter_multimodal.py          # Multimodal refinement (video-level filtering)
├── 05_collect_interactions.py       # Collect engagement metrics (likes/comments)
├── 06_vertex_visual_analysis.py     # Visual coding via Vertex AI (video-level)
├── 07_caption_textual_coding.py     # Caption-level identity coding
├── 08_merge_coding_and_interactions.py  # Merge coding results with engagement data
├── 09_build_final_dataset.py        # Construct final dataset for analysis
├── 10_visualization.py              # Generate figures for analysis
├── 11_prepare_evaluation_files.py   # Prepare human evaluation datasets
├── 12_compute_kappa_main.py         # Cohen’s kappa for main variables
└── 13_compute_kappa_caption_category.py # Kappa for caption label categories

data/
├── sample_input/                    # Example input files
├── sample_output/                   # Example intermediate outputs
└── README.md

results/
├── figures/                         # Final visualizations
└── tables/                          # Summary tables

archive/
└── notes_on_private_or_omitted_material.md
