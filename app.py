import pandas as pd
import streamlit as st

st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)
        
st.set_page_config(layout="wide")
import pandas as pd
import streamlit as st

st.title("CSV Comparison by Amrut")
st.write("""
Upload two CSV files to compare differences.
Changed cells will show old value (strikethrough, red) and new value (green) with highlighted background.
Only relevant columns and context will be shown.
""")

col1, col2 , col3= st.columns([10,10, 2])
with col1:
    file1 = st.file_uploader("Upload first CSV (Old)", type=["csv"])
with col2: 
    file2 = st.file_uploader("Upload second CSV (New)", type=["csv"])
with col3:
    show_all_rows = st.checkbox("Show all rows", value=False)
    
if file1 and file2:
    df_old = pd.read_csv(file1)
    df_new = pd.read_csv(file2)

    if df_old.shape != df_new.shape:
        st.error("CSV files have different shapes. Please upload files with the same structure.")
    else:
        comparison_df = df_new.copy().astype('object')
        changed_rows = []
        changed_cols = set()

        # Detect changes and format cells
        for i in range(len(df_new)):
            row_changed = False
            for col in df_new.columns:
                old_val = str(df_old.at[i, col]) if pd.notna(df_old.at[i, col]) else ""
                new_val = str(df_new.at[i, col]) if pd.notna(df_new.at[i, col]) else ""

                # Ignore None vs empty string changes
                if old_val != new_val and not (old_val == "" and new_val == ""):
                    row_changed = True
                    changed_cols.add(col)
                    comparison_df.at[i, col] = (
                        f'<div style="background-color:#ccffcc; padding:2px; white-space:nowrap;">'
                        f'<span style="text-decoration: line-through; color:red;">{old_val}</span> → '
                        f'<span style="color:green;">{new_val}</span></div>'
                    )
            if row_changed:
                changed_rows.append(i)

        # Determine columns to display: changed columns + one before and one after
        all_cols = list(df_new.columns)
        if not show_all_rows:
            cols_to_display = set()
            for col in changed_cols:
                idx = all_cols.index(col)
                cols_to_display.add(col)
                if idx - 1 >= 0:
                    cols_to_display.add(all_cols[idx - 1])
                if idx + 1 < len(all_cols):
                    cols_to_display.add(all_cols[idx + 1])
            cols_to_display = [c for c in all_cols if c in cols_to_display]
        else:
            cols_to_display = all_cols

        # Build final display with context rows and continuity breaks
        rows_to_display = []
        last_displayed = -1
        print('--')
        for idx in changed_rows:
            # print (idx, last_displayed, idx >  last_displayed + 1)
            if  idx >  last_displayed + 2:
                rows_to_display.append("..." ) #+ str(last_displayed))
            if idx - 1 >= 0:
                rows_to_display.append(idx - 1)
            rows_to_display.append(idx)
            if idx + 1 < len(df_new):
                rows_to_display.append(idx + 1)
            last_displayed = idx + 1
        
        # Remove duplicates while preserving order
        # final_rows = rows_to_display
        final_rows  = [ ]
        for r in rows_to_display:
            if ( r not in final_rows and type(r) == int ) or type(r) == str :
                final_rows.append(r)
        # for row in rows_to_display:
            # print (row)
            
        # Create display DataFrame
        display_data = []
        for r in final_rows:
            # print (r)
            if not type(r)==int:
                display_data.append(["..." for _ in cols_to_display])
            else:
                display_data.append([comparison_df.iloc[r][c] for c in cols_to_display])

        display_df = pd.DataFrame(display_data, columns=cols_to_display)
        # Add line numbers
        line_numbers = ["..." if r == "..." else str(r + 1) for r in final_rows]
        display_df.insert(0, "Line # ", line_numbers)

        st.write("### Highlighted Differences with Context and Compact Columns")
        st.write(display_df.to_html(index=False, escape=False), unsafe_allow_html=True)
        # st.dataframe(display_df, hide_index=True)

