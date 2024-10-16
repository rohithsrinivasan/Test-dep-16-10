import os
import streamlit as st
import pandas as pd
from tabula import read_pdf
import grouping_functions
from dotenv import load_dotenv
import google.generativeai as genai
import functions as f

f.header_intro()
f.header_intro_2()

st.subheader("Grouping 2.0 Page")

if 'pin_table' in st.session_state:
    pin_table = st.session_state['pin_table']

    st.write("Pin Table:")
    st.dataframe(pin_table)
    before_grouping_flag, added_empty_grouping_column = grouping_functions.check_excel_format(pin_table)
    #st.text(f"Before Pin Grouping Flag :{before_grouping_flag}")
    #st.dataframe(added_empty_grouping_column)

    mcu = st.checkbox("Use Algorithm (MCU) for grouping")
    power = st.checkbox("Use database for grouping")
    llm_model = st.checkbox("Use hugging face model (trained)")

    if not any([mcu, power, llm_model]):
        st.info("Make a selection")
        pin_grouping_table = pd.DataFrame()

    elif sum([mcu, power, llm_model]) > 1:
        st.info("Please only make a single selection")
        pin_grouping_table = pd.DataFrame()

    else:
        # Perform grouping based on the selected method
        if mcu:
            pin_grouping_table = grouping_functions.assigning_grouping_as_per_algorithm(added_empty_grouping_column)
            st.text("After Grouping from Algorithm:")
        
        elif power:
            json_file = "Database.json"
            pin_grouping_table = grouping_functions.assigning_grouping_as_per_database(added_empty_grouping_column, json_file)
            st.text("After Grouping from Database:")
        
        elif llm_model:
            st.text("Executing LLM")
            response, pin_grouping_table = grouping_functions.assigning_grouping_as_per_LLM(added_empty_grouping_column)
            st.text("Step 1-")
            st.markdown(f'Type of device :red[{response.text}]')
       
        # Common operations after grouping
        st.dataframe(pin_grouping_table)
        no_grouping_assigned = grouping_functions.check_empty_groupings(pin_grouping_table)
        
        if no_grouping_assigned.empty:
            st.info("All grouping values are filled.") 

        else:
            st.info("Please fill in group values for these:")
            edited_df = st.data_editor(no_grouping_assigned)

            if edited_df['Grouping'].isnull().any():
                st.info("Please enter group names for all.")
            else:
                pin_grouping_table.update(edited_df)
                st.text("Final Grouping Table")
                st.dataframe(pin_grouping_table) 

        st.success("Done!")
        st.session_state["page"] = "SideAlloc" 
        st.session_state['grouped_pin_table'] = pin_grouping_table

        # Check if redirection to "SideAlloc" page is needed
        if "page" in st.session_state and st.session_state["page"] == "SideAlloc":
            st.page_link("pages/side_allocation.py", label="SideAlloc")
        else:
            st.write("Grouped Pin table displayed")            

else:
    st.write("No pin table available.")                  

