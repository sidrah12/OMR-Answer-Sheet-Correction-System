import streamlit as st
import pandas as pd
import os
import cv2
import numpy as np
from main import detect_answers, score_answers, BUBBLE_COORDS, OPTIONS

# ---------- UI Colors ----------
BACKGROUND_COLOR = "#FFF8E7"
HEADER_COLOR = "#1F4E79"
HEADER_TEXT_COLOR = "#FFFFFF"
SUCCESS_COLOR = "#3AAFA9"
ERROR_COLOR = "#F28C8C"

st.set_page_config(page_title="OMR Correction System", layout="wide")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BACKGROUND_COLOR};
    }}
    .stHeader, h1 {{
        color: {HEADER_COLOR};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("OMR Answer Sheet Correction System")

# ------------------ FUNCTIONS ------------------
def highlight_detected(img_path):
    """Detect answers and draw rectangles around marked bubbles."""
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detected_answers = []

    for q_num, bubbles in BUBBLE_COORDS.items():
        bubble_darkness = []

        for (x, y, w, h) in bubbles:
            roi = gray[y:y+h, x:x+w]
            mean_val = cv2.mean(roi)[0]
            bubble_darkness.append(mean_val)

        # Darkest bubble = marked
        marked_idx = int(np.argmin(bubble_darkness))
        detected_answers.append(OPTIONS[marked_idx])

        # Highlight the detected bubble
        x, y, w, h = bubbles[marked_idx]
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Green rectangle

    # Save temporarily
    temp_path = f"temp_highlight.png"
    cv2.imwrite(temp_path, img)
    return detected_answers, temp_path

# ------------------ UPLOAD ANSWER KEY ------------------
st.header("Step 1: Upload Answer Key")
answer_key_file = st.file_uploader("Upload answer key (.txt)", type=["txt"])
answer_key = None

if answer_key_file:
    answer_key = [line.decode("utf-8").strip().upper() for line in answer_key_file.readlines()]
    st.success(f"Answer key loaded with {len(answer_key)} questions")

# ------------------ UPLOAD OMR SHEETS ------------------
st.header("Step 2: Upload OMR Sheets")
uploaded_files = st.file_uploader(
    "Upload OMR sheets (images)", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

results = []

if uploaded_files and answer_key:
    for file in uploaded_files:
        st.subheader(f"Processing: {file.name}")

        # Save uploaded image temporarily
        temp_path = f"temp_{file.name}"
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())

        # Detect answers and get highlighted image
        detected, highlighted_path = highlight_detected(temp_path)
        score = score_answers(detected, answer_key)

        results.append({
            "Student": file.name,
            "Detected": " ".join(detected),
            "Score": f"{score}/{len(answer_key)}"
        })

        # Display highlighted image
        st.image(highlighted_path, caption="OMR Sheet with Detected Answers", use_container_width=True)
        st.success(f"Processed {file.name}")

# ------------------ DISPLAY RESULTS ------------------
if results:
    st.subheader("Results")
    df = pd.DataFrame(results)
    st.dataframe(df)

    # Save to Excel
    os.makedirs("result", exist_ok=True)
    out_path = "result/scores.xlsx"
    df.to_excel(out_path, index=False)

    # Download button
    with open(out_path, "rb") as f:
        st.download_button("Download Results (Excel)", f, "scores.xlsx")
