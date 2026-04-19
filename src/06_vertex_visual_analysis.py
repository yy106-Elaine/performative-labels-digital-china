import os
import re
import pandas as pd
from vertexai.generative_models import GenerativeModel, Part

# ----------------------------
# Configuration
# ----------------------------
VIDEO_DIR = "Douyin Videos"
OUTPUT_CSV = "video_categorization.csv"

FIELDS = [
    "VIDEO_STYLE",
    "VIDEO_IDENTITY_PRESENT_VISUAL",
    "VIDEO_IDENTITY_VISUAL_TYPE",
]

# ----------------------------
# Collect local video paths
# ----------------------------
all_video_paths = [
    os.path.join(VIDEO_DIR, filename)
    for filename in os.listdir(VIDEO_DIR)
    if filename.lower().endswith(".mp4")
]

print("Number of video files being processed:", len(all_video_paths))

# ----------------------------
# Initialize model
# ----------------------------
model = GenerativeModel("gemini-2.5-pro")

# ----------------------------
# Prompt
# ----------------------------
prompt = """
You are conducting a structured sociological coding task for a research project on lesbian identity discourse (TPH culture) in Chinese short videos.

Return ONLY the following 3 lines in EXACT format, one per line.
Do NOT include extra lines.
Do NOT use markdown code blocks.
Do NOT add explanations.

VIDEO_STYLE: <1-8>
VIDEO_IDENTITY_PRESENT_VISUAL: <0 or 1>
VIDEO_IDENTITY_VISUAL_TYPE: <1-6 or N/A>

Important rules:
- VIDEO_STYLE must follow the defined category system.
- VIDEO_IDENTITY_PRESENT_VISUAL must be 0 or 1 only.
- If VIDEO_IDENTITY_PRESENT_VISUAL = 0, then VIDEO_IDENTITY_VISUAL_TYPE must be N/A.
- Keep responses concise and based only on observable evidence.

Coding:
1) VIDEO_STYLE (choose ONE number only):

1 = Romantic relationship  
(Primary focus is on a romantic couple or implied couple dynamic between two women. Indicators include affectionate interaction, couple-style framing, matching outfits, intimacy gestures, relationship storytelling, emotional bonding, or partner-centered narrative. The core content revolves around relational intimacy rather than identity debate or performance.)

2 = Identity discussion  
(Primary focus is explicit discussion of lesbian identity, T/P/H labels, or community norms. Must contain clear discursive cues such as asking viewers to comment, debating stereotypes, questioning roles, explaining identity categories, or statements like “leave your answer in the comments,” “what does your T always say,” “do you agree that…”. The video centers on reflective or argumentative discourse, not just appearance.)

3 = Appearance / visual performance  
(Primary focus is visual self-presentation: hand gestures, dance, aesthetic posing, fashion display, beauty shots, atmosphere-driven edits, transitions, or “帅照/美照” style content. Identity may be implied through styling, but there is no structured discussion. The emphasis is on looks, charisma, or visual appeal.)

4 = Comedy  
(Primary intent is humor. Includes parody, exaggerated stereotype performance, comedic skits, ironic reenactments, meme-style humor, or playful exaggeration. Laughter, comedic timing, or punchlines are central.)

5 = Vlog / daily life  
(Primary focus is documenting everyday activities such as cooking, studying, commuting, chatting casually, or daily routines. The tone is informal and diary-like. Identity may be present but is not the main organizing theme.)

7 = Drama / scripted short play  
(Clearly staged or scripted narrative involving characters and plot development. Includes role-playing, acted conflicts, structured storytelling, or episodic short dramas. Dialogue and narrative arc are central.)

8 = Other  
(Does not clearly fit into any of the above categories. Use only when none of the definitions apply.)

Decision rule:
Classify based on the PRIMARY organizing purpose of the video, not secondary elements. If multiple elements appear, choose the category that best represents the core communicative intent.

2) VIDEO_IDENTITY_PRESENT_VISUAL (0 or 1)

Definition:
Does the video contain a visually distinctive gender presentation style that is commonly recognizable within Chinese lesbian subcultural aesthetics?

Code as 1 if there is a clearly observable and culturally distinctive presentation pattern, such as:

- 鲻鱼头 (mullet haircut with short front/top and longer back)
- Very short cropped hair associated with masculine styling
- Deliberately androgynous or masculine-coded styling
- Visually emphasized short-hair presentation
- On-screen textual display of T, P, H, or related label variants (e.g., 长发T, 甜妹T, 姐P), even if not framed as a discussion

The decision should be based purely on observable visual presentation, not on spoken or textual identity discourse.

If no such distinctive presentation is present, code as 0.

2a) VIDEO_IDENTITY_VISUAL_TYPE

If VIDEO_IDENTITY_PRESENT_VISUAL = 1, specify the primary presentation category:

1 = Mullet haircut (鲻鱼头)
2 = Short cropped masculine hairstyle
3 = Androgynous short curly hair
4 = Other clearly masculine-coded styling
5 = Multiple distinctive features present, including 1-4
6 = Explicit TPH-related language displayed on screen (e.g., T/P/H labels or variants appearing as text overlay)

Be factual, do not speculate. Do not wrap output in ``` blocks.
""".strip()


# ----------------------------
# Parse model output
# ----------------------------
def parse_fixed_lines(text: str):
    cleaned = text.strip()
    cleaned = re.sub(r"^```.*?\n", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"\n```$", "", cleaned)

    parsed = {field: "" for field in FIELDS}

    # First attempt: KEY: VALUE parsing
    for line in cleaned.splitlines():
        line = line.strip()
        for field in FIELDS:
            prefix = f"{field}:"
            if line.startswith(prefix):
                parsed[field] = line[len(prefix):].strip()
                break

    # Fallback: positional parsing
    if parsed["VIDEO_STYLE"] == "":
        parts = cleaned.split()
        if len(parts) >= 3:
            parsed["VIDEO_STYLE"] = parts[0]
            parsed["VIDEO_IDENTITY_PRESENT_VISUAL"] = parts[1]
            parsed["VIDEO_IDENTITY_VISUAL_TYPE"] = parts[2]

    return parsed, cleaned


# ----------------------------
# Analyze one local video
# ----------------------------
def analyze_video(local_path: str) -> dict:
    with open(local_path, "rb") as f:
        video_bytes = f.read()

    video_part = Part.from_data(data=video_bytes, mime_type="video/mp4")

    response = model.generate_content(
        [video_part, prompt],
        generation_config={"temperature": 0.2},
    )

    parsed, cleaned = parse_fixed_lines(response.text)

    row = {
        "file_path": local_path,
        "raw_output": cleaned,
        "video_style": parsed["VIDEO_STYLE"],
        "video_identity_present_visual": parsed["VIDEO_IDENTITY_PRESENT_VISUAL"],
        "video_identity_visual_type": parsed["VIDEO_IDENTITY_VISUAL_TYPE"],
    }

    row["parse_ok"] = int(
        row["video_style"] != ""
        and row["video_identity_present_visual"] != ""
        and row["video_identity_visual_type"] != ""
    )

    return row


# ----------------------------
# Batch processing with resume
# ----------------------------
def main():
    if os.path.exists(OUTPUT_CSV):
        existing_df = pd.read_csv(OUTPUT_CSV)
        processed_paths = set(existing_df["file_path"].astype(str).tolist())
        all_rows = existing_df.to_dict("records")
    else:
        processed_paths = set()
        all_rows = []

    for i, path in enumerate(all_video_paths):
        if path in processed_paths:
            print(f"Skipping already processed video: {path}")
            continue

        try:
            row = analyze_video(path)

            print("\n---------------------------")
            print(f"[{i + 1}] Processing: {path}")
            print("Raw output:")
            print(row["raw_output"])
            print("---------------------------\n")

            all_rows.append(row)
            pd.DataFrame(all_rows).to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
            print(f"{len(all_rows)} row(s) saved to {OUTPUT_CSV} | parse_ok={row['parse_ok']}")

        except Exception as e:
            print(f"Error processing {path}: {e}")
            continue

    print(f"Success! {len(all_rows)} videos were processed and saved to {OUTPUT_CSV}.")


if __name__ == "__main__":
    main()
