# OMR Answer Sheet Correction System
A fully automated system to evaluate OMR (Optical Mark Recognition) answer sheets. The system detects marked answers from scanned OMR sheets, compares them with a predefined answer key, calculates scores, and highlights the selected options on the sheet. Users can upload multiple sheets at once and download results in an Excel file.

Template to create OMR Sheets: https://omr.netstudy.in/
Crop the to image to size 820*500 pixels before testing.

Steps to run the project:
1. python -m venv venv (creating a virtual environment)
2. venv\Scripts\activate (activating virtual environment)
3. pip install opencv-python numpy pandas streamlit openpyxl (install dependencies)
4. streamlit run app.py




