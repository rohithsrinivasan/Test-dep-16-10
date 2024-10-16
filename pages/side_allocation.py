import os
import streamlit as st
import pandas as pd
from tabula import read_pdf
import SideAllocation_functions
from dotenv import load_dotenv
import google.generativeai as genai
import functions as f

f.header_intro()
f.header_intro_2()

st.subheader("Side Allocation Page")

if 'grouped_pin_table' in st.session_state:
    grouped_pin_table = st.session_state['grouped_pin_table']

    st.write("Grouped Pin Table:")
    st.dataframe(grouped_pin_table)

    required_columns = ['Pin Designator', 'Pin Display Name', 'Electrical Type', 'Pin Alternate Name', 'Grouping','Priority']
    additional_column = 'Priority'
    before_priority_flag, added_empty_priority_column = SideAllocation_functions.check_excel_format(grouped_pin_table,required_columns, additional_column)
    #st.text(f"Before Side Allocation Flag :{before_priority_flag}")
    #st.dataframe(added_empty_priority_column)
    priority_added = SideAllocation_functions.assigning_priority_for_group(added_empty_priority_column)
    #st.text(f"Priority Column Added")
    #st.dataframe(priority_added)

    required_columns = ['Pin Designator', 'Pin Display Name', 'Electrical Type', 'Pin Alternate Name', 'Grouping','Priority', 'Side']
    additional_column = 'Side'
    before_side_flag, added_empty_side_column = SideAllocation_functions.check_excel_format(priority_added,required_columns, additional_column)
    #st.text(f"Before Side Allocation Flag :{before_side_flag}")
    #st.dataframe(added_empty_side_column)

    if len(added_empty_side_column) < 80:
        side_added = SideAllocation_functions.assigning_side_for_priority(added_empty_side_column)
        st.text(f"Side Column Added")
        st.dataframe(side_added)
    else:
        st.text(f"Executing Partioning")
        power_df, unfilled_df = SideAllocation_functions.partitioning(added_empty_side_column)
        st.dataframe(power_df)




    changing_as_per_style_guide = st.checkbox("Dual-in-line with Last Pin to Bottom right")

    if changing_as_per_style_guide:

        required_columns = ['Pin Designator', 'Pin Display Name', 'Electrical Type', 'Pin Alternate Name', 'Grouping','Priority', 'Side', 'Changed Grouping']
        additional_column = 'Changed Grouping'
        before_new_grouping_flag, added_empty_new_grouping_column = SideAllocation_functions.check_excel_format(side_added,required_columns, additional_column)        

        #st.text(f"Before New grouping Allocation Flag :{before_new_grouping_flag}")
        #st.dataframe(added_empty_new_grouping_column)

        side_added = SideAllocation_functions.Dual_in_line_as_per_Renesas(added_empty_new_grouping_column)
        st.text(f"DIL template as per Renesas")
        st.dataframe(side_added)      

else:
    st.write("No Grouped Pin table available.")  
