import streamlit as st
import pandas as pd
from io import BytesIO

# Function to handle file upload and initialize the DataFrame
def load_data():
    uploaded_file = st.sidebar.file_uploader("Upload an XLSX file", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        if "Inclusion" not in df.columns:
            df["Inclusion"] = ""
        if "Exclusion" not in df.columns:
            df["Exclusion"] = ""
        st.session_state.data = df
        return df
    return None

# Function to download the modified DataFrame
def download_data():
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        st.session_state.data.to_excel(writer, index=False, sheet_name="Sheet1")
    processed_data = output.getvalue()
    st.sidebar.download_button(
        label="Download Updated Excel",
        data=processed_data,
        file_name="updated_file.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# Function to handle row actions
def handle_action(action, reason=None):
    row = st.session_state.current_row
    # Update the DataFrame in the session state directly
    if action == "Include":
        st.session_state.data.at[row, "Inclusion"] = "Yes"
        st.session_state.data.at[row, "Exclusion"] = ""
    elif action == "To Discuss":
        st.session_state.data.at[row, "Inclusion"] = "Discuss"
        st.session_state.data.at[row, "Exclusion"] = ""
    else:
        st.session_state.data.at[row, "Inclusion"] = "Exclude"
        st.session_state.data.at[row, "Exclusion"] = reason

    # Increment the row for the next review
    st.session_state.current_row += 1

# Main script
data = load_data()

if data is not None:
    if "current_row" not in st.session_state:
        st.session_state.current_row = 0

    # Sidebar content (current row and download button)
    row = st.session_state.current_row
    if row < len(st.session_state.data):
        # Show the current row data in the main area
        st.write(f"You are reviewing row {row + 1} of {len(st.session_state.data)}")
        st.subheader(st.session_state.data.iloc[row].get("Title", "No Title"))
        st.write(f"**Publication Title:** {st.session_state.data.iloc[row].get('Publication Title', 'N/A')}")
        st.write(f"**Publication Year:** {st.session_state.data.iloc[row].get('Publication Year', 'N/A')}")
        st.write(f"**Abstract Note:** {st.session_state.data.iloc[row].get('Abstract Note', 'N/A')}")

        # Action buttons at the top, above the title
        with st.form(key=f"form_{row}"):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                include = st.form_submit_button("Include")
            with col2:
                discuss = st.form_submit_button("To Discuss")
            with col3:
                exclude_ethics = st.form_submit_button("Exclude - Not Ethics")
            with col4:
                exclude_board = st.form_submit_button("Exclude - Not Board")
            with col5:
                exclude_other = st.form_submit_button("Exclude - Other")

            if include:
                handle_action("Include")
                st.rerun()
            if discuss:
                handle_action("To Discuss")
                st.rerun()
            if exclude_ethics:
                handle_action("Exclude", "Not Ethics")
                st.rerun()
            if exclude_board:
                handle_action("Exclude", "Not Board")
                st.rerun()
            if exclude_other:
                handle_action("Exclude", "Other")
                st.rerun()

    else:
        st.write("All rows have been reviewed.")

    # Download the updated file button in the sidebar
    download_data()

else:
    st.write("Please upload an XLSX file to begin.")
