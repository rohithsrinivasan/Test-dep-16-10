import pandas as pd

def check_excel_format(df, required_columns, additional_column):
  
  try:
    #df = pd.read_excel(excel_path)
    if set(required_columns) == set(df.columns):
      return True, df
    elif set(required_columns[:-1]) == set(df.columns):  
      df[f'{additional_column}'] = ' '
      #df.to_excel(excel_path, index=False)
      return True, df
    else:
      print("Incorrect extraction format.")
      return False, df
  except Exception as e:
    print(f"Error reading Excel file: {e}")
    return False, df     


def priority_order(row, df):
    value = row['Grouping']
    index = row.name  # Get the index from the row object
    
    # Power related cases
    if value == 'Power_Positive':
        return f"A_Power_Positive"
    elif value == 'Power_Negetive_Regulator_Capacitor':
        return f"Y_Power_Negetive"
    elif value == 'Power_Negetive':
        return f"Z_Power_Negetive"
    elif value == 'System':
        return f"B_System"
    elif value == 'No_Connect':
        return f"X_No_Connect"

    # Clock-related cases
    elif any(keyword in value for keyword in ('X1', 'X2')):
        return f"CA_Main_Clocks/Oscillators"
    elif 'XT' in value:
        return f"CB_External_Clocks/Oscillators"
    elif 'Clock_Capacitor' in value:
        return f"CC_External_Capacitive_Clocks/Oscillators"

    # I2C, Mode, Interrupts, Output cases
    elif value == 'I2C_Pins':
        return f"D_I2C_Pins"
    elif value == 'Mode':
        return f"E_ModePins"
    elif 'INT' in value:
        return f"I_Interrupts"
    elif 'Output' in value:
        return f"S_Output"
    elif 'Main_Clock' in value:
        return f"CA_Main_Clocks/Oscillators"

    # Port handling
    elif value.startswith("Port"):
        if row['Electrical Type'] == 'Input':

            if value.startswith("Port"):
                port_number = int(value.split(' ')[1])
                return f"P_Port {port_number:02d}"

            value_alternative = row['Pin Alternate Name']

            # Swap conditions for Input Electrical Type
            if any(keyword in value_alternative for keyword in ('X1', 'X2')):
                swap_pins_for_that_row(df, index)
                return f"CA_Main_Clocks/Oscillators"
            elif 'XT' in value_alternative:
                swap_pins_for_that_row(df, index)
                return f"CB_External_Clocks/Oscillators"
            elif 'MD' in value_alternative:
                swap_pins_for_that_row(df, index)
                return f"E_ModePins"
            elif 'NMI' in value_alternative:
                swap_pins_for_that_row(df, index)
                return f"I_Interrupts"
            elif 'VREF' in value_alternative:
                swap_pins_for_that_row(df, index)
                return f"A_Power_Ref_Positive"
            elif 'VRFF' in value_alternative:
                swap_pins_for_that_row(df, index)
                return f"A_Power_Ref_Positive"                
            else:

                return f"ZZ_Not_Assigned"

        else:
            # Handle non-input electrical type (like Output)
            port_number = int(value.split(' ')[1])
            return f"P_Port {port_number:02d}"

    # Default case for unhandled conditions
    else:
        return None

def swap_pins_for_that_row(df, index):
    df.loc[index, 'Pin Display Name'], df.loc[index, 'Pin Alternate Name'] = df.loc[index, 'Pin Alternate Name'], df.loc[index, 'Pin Display Name']
    return
    
def filter_and_sort_by_priority(df):
    sorted_df = df.sort_values(by='Priority', ascending=True).reset_index(drop=True)
    return sorted_df
       

def allocate_small_dataframe(row, df):
    grouped_indices = df.groupby('Priority').indices
    total_rows = len(df)
    left = []
    right = []
    left_limit = total_rows // 2

    last_side = 'Left'  # Start with the left side

    for group in grouped_indices.values():
        if last_side == 'Left' and len(left) + len(group) <= left_limit:
            left.extend(group)
        else:
            right.extend(group)
            last_side = 'Right'  # Switch to right side

    if row.name in left:
        return 'Left'
    else:
        return 'Right'


def side_allocation(row, df):
    total_rows = len(df)    
    if total_rows > 80:
        return allocate_large_dataframe(row, df)
    else:
        return allocate_small_dataframe(row, df)

def assigning_priority_for_group(df):
    df_copy = df.copy()  
    df_copy['Priority'] = df_copy.apply(lambda row: priority_order(row, df_copy), axis=1)
    return df_copy

def assigning_side_for_priority(df):
    df_copy = df.copy()
    df_new = filter_and_sort_by_priority(df_copy)
    df_new['Side'] = df_new.apply(lambda row: side_allocation(row, df_new), axis=1)
    
    # Apply sorting based on 'Side'
    ascending_order_df = df_new[df_new['Side'] == 'Left']
    ascending_order_df = assigning_ascending_order_for_similar_group(ascending_order_df)
    
    descending_order_df = df_new[df_new['Side'] == 'Right']
    descending_order_df = assigning_descending_order_for_similar_group(descending_order_df)
    
    # Concatenate the two sorted DataFrames back together
    final_df = pd.concat([ascending_order_df, descending_order_df]).reset_index(drop=True)
    
    return final_df

 
def assigning_ascending_order_for_similar_group(df):
    df_copy = df.copy()
    ascending_order_df = df_copy.groupby('Priority').apply(lambda group: group.sort_values('Pin Display Name'))
    ascending_order_df.reset_index(drop=True, inplace=True)
    return ascending_order_df 

def assigning_descending_order_for_similar_group(df):
    df_copy = df.copy()
    descending_order_df = df_copy.groupby('Priority').apply(lambda group: group.sort_values('Pin Display Name', ascending=False))
    descending_order_df.reset_index(drop=True, inplace=True)
    return descending_order_df


def Dual_in_line_as_per_Renesas(df): 
    df_copy = df.copy()
    df_copy['Changed Grouping'] = None

    # Function to get alphabetical inverse of the first letter
    def alphabetical_inverse(letter):
        if letter.isalpha() and letter.isupper():
            return chr(155 - ord(letter))  # A -> Z, B -> Y, etc.
        return letter

    # Function to get the alphabet corresponding to the reverse of a number (e.g., 01 -> Z, 05 -> V)
    def number_to_alphabet_inverse(number_str):
        if number_str.isdigit():
            num = int(number_str)
            if 1 <= num <= 26:
                return chr(91 - num)  # 1 -> Z, 2 -> Y, 3 -> X, ..., 26 -> A
        return number_str
    
    def assigning_descending_order_for_similar_group(group):
        return group.sort_values('Pin Display Name', ascending=False)

    for index, row in df_copy.iterrows():
        priority = row['Priority']
        
        # For 'Left' side, keep the priority unchanged
        if row['Side'] == 'Left':
            df_copy.at[index, 'Changed Grouping'] = priority

        # For 'Right' side, modify the priority
        elif row['Side'] == 'Right':

            # Sort the group by 'Pin Display Name' in descending order for 'Right' side
            right_side_group = df_copy[df_copy['Side'] == 'Right']
            sorted_right_group = right_side_group.groupby('Priority').apply(assigning_descending_order_for_similar_group)

            # Change the first letter of the 'Priority' value to its alphabetical inverse
            first_letter = priority[0]
            inverse_first_letter = alphabetical_inverse(first_letter)
            
            # Check if the priority ends with a number
            if priority[-2:].isdigit():  # Assuming numbers are two digits
                num_part = priority[-2:]  # The last two characters (numbers)
                inverse_num_part = number_to_alphabet_inverse(num_part)
                
                # Reconstruct the priority with the inverse number and inverse first letter
                df_copy.at[index, 'Changed Grouping'] = inverse_first_letter + priority[1:-2] + inverse_num_part + "_" + num_part
            else:
                # If no number at the end, just change the first letter
                df_copy.at[index, 'Changed Grouping'] = inverse_first_letter + priority[1:]

    return df_copy

def Dual_in_line_as_per_Renesas(df): 
    df_copy = df.copy()

    # Create a new column 'Changed Grouping'
    df_copy['Changed Grouping'] = None

    # Function to get alphabetical inverse of the first letter
    def alphabetical_inverse(letter):
        if letter.isalpha() and letter.isupper():
            return chr(155 - ord(letter))  # A -> Z, B -> Y, etc.
        return letter

    # Function to get the alphabet corresponding to the reverse of a number (e.g., 01 -> Z, 05 -> V)
    def number_to_alphabet_inverse(number_str):
        if number_str.isdigit():
            num = int(number_str)
            if 1 <= num <= 26:
                return chr(91 - num)  # 1 -> Z, 2 -> Y, 3 -> X, ..., 26 -> A
        return number_str

    # Function to sort groups by 'Pin Display Name' in descending order for 'Right' side
    def assigning_descending_order_for_similar_group(group):
        return group.sort_values('Pin Display Name', ascending=False)

    # Sort the right-side groups by 'Pin Display Name' in descending order
    right_side_group = df_copy[df_copy['Side'] == 'Right']
    sorted_right_group = right_side_group.groupby('Priority').apply(assigning_descending_order_for_similar_group)

    # Iterate over the rows
    for index, row in df_copy.iterrows():
        priority = row['Priority']

        # For 'Left' side, keep the priority unchanged
        if row['Side'] == 'Left':
            df_copy.at[index, 'Changed Grouping'] = priority

        # For 'Right' side, modify the priority using the sorted 'Pin Display Name'
        elif row['Side'] == 'Right':
            # Fetch the sorted row from the 'sorted_right_group'
            sorted_row = sorted_right_group.loc[(sorted_right_group['Priority'] == priority) & (sorted_right_group['Pin Display Name'] == row['Pin Display Name'])].iloc[0]

            # Change the first letter of the 'Priority' value to its alphabetical inverse
            first_letter = sorted_row['Priority'][0]
            inverse_first_letter = alphabetical_inverse(first_letter)

            # Check if the priority ends with a number
            if sorted_row['Priority'][-2:].isdigit():  # Assuming numbers are two digits
                num_part = sorted_row['Priority'][-2:]  # The last two characters (numbers)
                inverse_num_part = number_to_alphabet_inverse(num_part)
                
                # Reconstruct the priority with the inverse number and inverse first letter
                df_copy.at[index, 'Changed Grouping'] = inverse_first_letter + sorted_row['Priority'][1:-2] + inverse_num_part + "_" + num_part
            else:
                # If no number at the end, just change the first letter
                df_copy.at[index, 'Changed Grouping'] = inverse_first_letter + sorted_row['Priority'][1:]

    return df_copy


########    Partitioning   ###############

def allocate_large_dataframe(row, df):
    df['Priority'] = df['Priority'].fillna('')

    left_power_mask = df['Priority'].str.startswith('A')
    right_power_mask = df['Priority'].str.startswith('Z')

    # Create lists of indices for left and right power using the masks
    left_power = df.index[left_power_mask].tolist()
    right_power = df.index[right_power_mask].tolist()

    # Return based on the allocation
    if row.name in left_power:
        return 'Left_Power'
    elif row.name in right_power:
        return 'Right_Power'
    else:
        return None


def partitioning(df):
    df['Side'] = df.apply(allocate_large_dataframe, args=(df,), axis=1)
    power_df = df[(df['Side'] == 'Left_Power') | (df['Side'] == 'Right_Power')]
    unfilled_df = df[df['Side'].isna()]
    return power_df, unfilled_df

def filtering_out_all_power_pins_as_one_part(df):
    pass