import pandas as pd
import json
from pandas import *
from dotenv import load_dotenv
import google.generativeai as genai
import os

def check_excel_format(df):
  
  try:
    required_columns = ['Pin Designator', 'Pin Display Name', 'Electrical Type', 'Pin Alternate Name', 'Grouping']

    if set(required_columns) == set(df.columns):
      return True, df
    elif set(required_columns[:-1]) == set(df.columns):  # Check for missing 'Grouping' column
      df['Grouping'] = ' '
      #df.to_excel(excel_path, index=False)
      return True, df
    else:
      print("Incorrect extraction format.")
      return False, df
  except Exception as e:
    print(f"Error reading Excel file: {e}")
    return False, df 
  

def assigning_grouping_as_per_database(old_df, json_path):
  df = old_df.copy()
  try:
    with open(json_path, 'r') as f:
      label_map = json.load(f) 

    def get_label(name):
        name = name.strip()
        for label, names in label_map.items():
            if name in [item.strip() for item in names]:
                return label
        print(f"Warning: Could not find a matching label for {name}. Assigning 'Unknown'.")    
        return None

    df['Grouping'] = df['Pin Display Name'].apply(get_label)
    print("Labels assigned to Grouping column successfully.")

  except Exception as e:
    print(f"Error processing files: {e}")    
  return df  

def group_port_pins(value):
    if value.startswith('P'):
        if len(value) == 3:
            if value[1] in '0123456789':
                return f'Port {value[1]}'
            elif value[1] in 'ABCDEFGH':
                return f'Port {value[1]}'
            
        elif len(value) in (4, 5) and value[1] in '0123456789ABCDEFGH' and value[2] == '_':
            return f'Port {value[1:2]}'

        elif value[1:3] in '101112131415':
            return f'Port {value[1:3]}'
    return None 

def group_other_io_pins(row):
   
    i2c_prefixes = ['SDA','SCL','\SDA']
    main_clock_prefixes = ['XOUT', 'XIN']

    if row['Electrical Type'] == 'I/O' and row['Pin Display Name'].startswith(tuple(i2c_prefixes)):
      return f"I2C_Pins"
   
    elif row['Electrical Type'] == 'I/O' and row['Pin Display Name'].startswith(tuple(main_clock_prefixes)):
      return f"Main_Clock"

# grouping i/o Pins - GPIO's together- I/o
# SDA and SCL have to be placed together

def group_power_pins(row):
    
    power_prefixes = ['EVS', 'VSS', 'VCC', 'EVD', 'REG', 'Epa', 'AVS', 'AVC', 'CVC', 'VDD','EPA', 'A1VREFH', 'A2VREFH']
    power_positive_prefixes = ['VDD','EVD','AVD','CVD', 'VCC']
    power_negetive_prefixes = ['VSS','EVS','AVS','CVS','Epa','EPA']
    power_negetive_regulator_capacitance_prefix = ['REG']

    power_suffixes = ['REFL', 'REFH']
    power_suffixes_ref_positive = ['REFH', 'A1VREFH', 'A2VREFH']
    power_suffixes_ref_negetive = ['REFL']

    vcc_pins = ['VCC']
    vss_pins = ['VSS']

    audio_data_lines = ["AUD"]
    control_pins = ["RDC"]
    cutoff_pins = ["DCUT", "\DCUT"]


    if row['Electrical Type'] == 'Power' and row['Pin Display Name'].startswith(tuple(power_prefixes)):
        prefix = row['Pin Display Name'][:3]
        suffix = row['Pin Display Name'][3:7]
        if prefix in power_positive_prefixes:
            return f'Power_Positive'  # Handle positive power prefixes
        elif prefix in power_negetive_prefixes:
            return f'Power_Negetive'  # Handle negetive power prefixes 
        elif suffix in power_suffixes_ref_positive:
            return f'Power_Ref_Positive'  
        elif suffix in power_suffixes_ref_negetive:
            return f'Power_Ref_Negetive' 
    
        else:
            ######   Handling special cases   ######
            if prefix in power_negetive_regulator_capacitance_prefix:
                return f'Power_Negetive_Regulator_Capacitor'  
            else:
                return f'P{prefix[1]}'  

    elif row['Electrical Type'] == 'Power' and any(prefix in row['Pin Display Name'] for prefix in vcc_pins): 
        return f'Power_Positive'    
    elif row['Electrical Type'] == 'Power' and any(prefix in row['Pin Display Name'] for prefix in vss_pins): 
        return f'Power_Negetive'  

    elif any(row['Pin Display Name'].startswith(prefix) for prefix in audio_data_lines) and row['Electrical Type'] in ['Input', 'I/O']:
        return f"Audio_data_lines"    
    elif any(row['Pin Display Name'].startswith(prefix) for prefix in control_pins) and row['Electrical Type'] in ['Input', 'I/O']:
        return f"Control"
    elif any(row['Pin Display Name'].startswith(prefix) for prefix in cutoff_pins) and row['Electrical Type'] in ['Input', 'I/O']:
        return f"Cutoff"    
  
           
    return None  


def group_output_pins(row):

    common_output_prefixes = ['COM']
    system_prefixes = ['RES']
    main_clock_prefixes = ['XOUT']
    External_Clock_Capacitor_prefixes = ['XCOUT']

    if row['Electrical Type'] == 'Output' and row['Pin Display Name'].startswith(tuple(common_output_prefixes)):
        return 'Common_Output'    
    elif row['Electrical Type'] == 'Output' and row['Pin Display Name'].startswith(tuple(system_prefixes)):
        return 'System'
    elif row['Electrical Type'] == 'Output' and row['Pin Display Name'].startswith(tuple(main_clock_prefixes)):
      return f"Main_Clock"  
    elif row['Electrical Type'] == 'Output' and row['Pin Display Name'].startswith(tuple(External_Clock_Capacitor_prefixes)):
      return f"External_Clock_Capacitor"        
    elif row['Electrical Type'] == 'Output':
        return 'System_Output'    
    else:
        return None


def group_input_pins(row):

    input_prefixes = ["XT", "\R", "EX", "\S", "MD", "NM", "Vr", "FW", "OS", "X1", "X2", "XI", "MO","XC"]
    adc_prefixes = ['ADCC']
    mode_pins = ['MODE']

    if row['Electrical Type'] == "Input":
        if row['Pin Display Name'].startswith(tuple(input_prefixes)):
            return {
                "XT": "External_Clock",
                "\R": "System",
                "EX": "Clock1",
                "\S": "System",
                "MD": "Mode",
                "MO" : "Mode",
                "NM": "Interrupt",
                "Vr": "P+ Analog",
                "FW": "System",
                "OS": "Clock2",
                "X1": "Main_Clock",
                "X2": "Main_Clock",
                "XI" : "Main_Clock",
                "XC" : "External_Clock_Capacitor"
            }[row['Pin Display Name'][:2]]
        

        elif row['Electrical Type'] == 'Input' and any(prefix in row['Pin Display Name'] for prefix in adc_prefixes): 
            return "ADC_Pins"
        elif row['Electrical Type'] == 'Input' and any(prefix in row['Pin Display Name'] for prefix in mode_pins): 
            return "Mode"        
        

    return None
# Chipseclect will always be input CS - Input 

def group_passsive_pins(row):
   
    passive_prefixes = ['NC']
    if row['Electrical Type'] == 'Passive' and row['Pin Display Name'].startswith(tuple(passive_prefixes)):
        return f'No_Connect'

def assigning_grouping_as_per_algorithm(df):
    df['Grouping'] = df['Pin Display Name'].apply(group_port_pins)
    #df['Grouping'] = df.apply(group_power_pin, axis=1)
    mask = df['Grouping'].isna()  # Create a mask for NaN values in 'Grouping'
    df.loc[mask, 'Grouping'] = df[mask].apply(group_other_io_pins, axis=1)
    mask = df['Grouping'].isna()  # Create a mask for NaN values in 'Grouping'
    df.loc[mask, 'Grouping'] = df[mask].apply(group_power_pins, axis=1)  # Apply group_power_pin only to NaN rows
    mask = df['Grouping'].isna()
    df.loc[mask, 'Grouping'] = df[mask].apply(group_output_pins, axis=1)
    mask = df['Grouping'].isna()
    df.loc[mask, 'Grouping'] = df[mask].apply(group_input_pins, axis=1)
    mask = df['Grouping'].isna()
    df.loc[mask, 'Grouping'] = df[mask].apply(group_passsive_pins, axis=1)    

    return df

def assigning_grouping_as_per_LLM(pin_table):

    load_dotenv()
    model = genai.GenerativeModel("gemini-pro")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)

    # Prompt to LLM
    input = f"Guess what category this device can be just by referring to the pin table. Here is your pin table {pin_table}"
    response = model.generate_content(input)
    print(response.text)
    pin_grouping_table = pin_table

    # Return the response and an empty DataFrame (uniform with other functions)
    return response, pin_table


def check_empty_groupings(df):
    empty_groupings = df[df['Grouping'].isna()]
    return empty_groupings

   