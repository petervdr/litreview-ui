import pandas as pd
import streamlit as st
from io import BytesIO
import re
from datetime import datetime

# Define keywords for highlighting
HIGHLIGHT_KEYWORDS = ["board", "director", "governance", "ethic", "moral", "virtue", "virtuous", "integrity", "utilitarian", "values", "decision-making"]

# Load the spreadsheet
st.set_page_config(layout="wide")

with st.sidebar:
    file_path = st.file_uploader("Upload your spreadsheet", type=["csv", "xlsx"])

    # Option to download updated file
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        processed_data = output.getvalue()
        return processed_data

    if 'df' in st.session_state:
        xlsx_data = to_excel(st.session_state.df)
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        file_name = f"{timestamp}-litreview-boardethics.xlsx"
        st.download_button(
            label="Download as XLSX",
            data=xlsx_data,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if file_path:
    # Load the data into a DataFrame
    if file_path.name.endswith(".csv"):
        df = pd.read_csv(file_path)  # Use the uploaded file object directly
    else:
        df = pd.read_excel(file_path)  # Use the uploaded file object directly

    # Ensure the DataFrame is saved in session state for reuse
    if 'df' not in st.session_state:
        st.session_state.df = df.copy()

    # Sort the entire DataFrame by 'Publication Title'
    st.session_state.df = st.session_state.df.sort_values(by="Publication Title", ascending=True).reset_index(drop=True)

    # Initialize the row index if not already set
    if 'row_index' not in st.session_state:
        st.session_state.row_index = 0

    # Ensure row_index does not exceed the DataFrame length
    while st.session_state.row_index < len(st.session_state.df):
        current_row = st.session_state.df.iloc[st.session_state.row_index]
        if pd.isna(current_row['Inclusion']):
            break
        st.session_state.row_index += 1

    # If all rows have been processed
    if st.session_state.row_index >= len(st.session_state.df):
        st.write("No more rows to review!")
    else:
        # Display the current row
        current_row = st.session_state.df.iloc[st.session_state.row_index]
        st.markdown(f"## {current_row['Title']}")
        st.markdown(
            f"**{current_row['Publication Year']}** | *{current_row['Publication Title']}*")

        # Highlight keywords in Abstract Note
        abstract_note = current_row.get('Abstract Note', '')
        abstract_note_highlighted = abstract_note if isinstance(abstract_note, str) else ''  # Ensure the value is a string
        for keyword in HIGHLIGHT_KEYWORDS:
            abstract_note_highlighted = re.sub(
                fr"(?i)({keyword})",  # Case-insensitive match for the keyword
                r"<mark style='background-color: yellow;'>\1</mark>",  # Highlight the matched word
                abstract_note_highlighted
            )
        st.markdown(f"**Abstract Note:**", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:1.2em;'>{abstract_note_highlighted}</div>", unsafe_allow_html=True)

        # Define actions
        def update_row(inclusion_value, exclusion_value=None):
            st.session_state.df.loc[st.session_state.row_index, 'Inclusion'] = inclusion_value
            if exclusion_value:
                st.session_state.df.loc[st.session_state.row_index, 'Exclusion'] = exclusion_value
            st.session_state.row_index += 1

        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Include"):
            update_row("Yes")
        if col2.button("Exclude - Not Board"):
            update_row("No", "Not Board")
        if col3.button("Exclude - Not Ethics"):
            update_row("No", "Not Ethics")
        if col4.button("Exclude - Other"):
            update_row("No", "Other")
        if st.button("To Discuss"):
            update_row("Discuss")
