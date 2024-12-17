import pandas as pd
import streamlit as st
from io import BytesIO
import re
from datetime import datetime

# Define keywords for highlighting
HIGHLIGHT_KEYWORDS = ["board", "director", "governance", "ethic", "moral", "virtue", "virtuous", "integrity", "utilitarian", "values", "decision-making"]

# Streamlit configuration
st.set_page_config(layout="wide")

with st.sidebar:
    file_path = st.file_uploader("Upload your spreadsheet", type=["csv", "xlsx"])

# Helper function to save DataFrame back to the uploaded file format
def save_to_file(df, original_file):
    output = BytesIO()
    if original_file.name.endswith(".csv"):
        df.to_csv(output, index=False)
    else:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def highlight_keywords(text):
    if not isinstance(text, str):
        return ""
    for keyword in HIGHLIGHT_KEYWORDS:
        text = re.sub(
            fr"(?i)({keyword})",  # Case-insensitive match
            r"<mark style='background-color: yellow;'>\1</mark>",
            text
        )
    return text

if file_path:
    # Load the uploaded file into a DataFrame
    if file_path.name.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # Ensure the DataFrame is sorted
    df = df.sort_values(by="Publication Title", ascending=True).reset_index(drop=True)

    # Find the first unprocessed row
    row_index = next((i for i, row in df.iterrows() if pd.isna(row['Inclusion'])), 0)

    # Calculate progress
    total_rows = len(df)
    handled_rows = df['Inclusion'].notna().sum()
    progress_message = f"Progress: {handled_rows} of {total_rows} rows handled."
    st.sidebar.markdown(f"### {progress_message}")

    # If all rows are processed
    if row_index >= len(df):
        st.write("No more rows to review!")
    else:
        # Display current row details
        current_row = df.iloc[row_index]
        st.markdown(f"## {current_row['Title']}")
        st.markdown(f"**{current_row['Publication Year']}** | *{current_row['Publication Title']}* | Row in Excel: *{row_index + 1}*")

        # Highlight abstract note keywords
        abstract_note = current_row.get('Abstract Note', '')
        highlighted_abstract = highlight_keywords(abstract_note)
        st.markdown("**Abstract Note:**", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:1.2em;'>{highlighted_abstract}</div>", unsafe_allow_html=True)

        # Define action functions
        def update_row(inclusion_value, exclusion_value=None):
            df.loc[row_index, 'Inclusion'] = inclusion_value
            if exclusion_value:
                df.loc[row_index, 'Exclusion'] = exclusion_value

            # Save changes directly to the file
            updated_data = save_to_file(df, file_path)
            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            file_name = f"{timestamp}-litreview-boardethics.{file_path.name.split('.')[-1]}"
            st.sidebar.download_button(
                label="Download Updated File",
                data=updated_data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if file_path.name.endswith(".xlsx") else "text/csv"
            )

            # Move to the next row
            return next((i for i, row in df.iterrows() if pd.isna(row['Inclusion'])), len(df))

        # Action buttons
        col1, col2, col3, col4, col5 = st.columns(5)
        if col1.button("Include"):
            row_index = update_row("Yes")
        if col2.button("Exclude - Not Board"):
            row_index = update_row("No", "Not Board")
        if col3.button("Exclude - Not Ethics"):
            row_index = update_row("No", "Not Ethics")
        if col4.button("Exclude - Other"):
            row_index = update_row("No", "Other")
        if col5.button("To Discuss"):
            row_index = update_row("Discuss")
