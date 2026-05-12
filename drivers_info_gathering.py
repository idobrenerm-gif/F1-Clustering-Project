import pandas as pd
import os

# dictionary containing all the drivers non-race data
drivers_data = [
    {
        'driver_number':1, 'name':'Max Verstappen', 'team':'Red Bull Racing',
        'age_in_2023':26, 'years_of_experience':9, 'years_in_current_team':8,'contract_years_remaining':5,
        'country':'Netherlands', 'marital_status':'in a relationship', 'has_kids':False,
        'world_championships':2, 'height_cm':181, 'weight_kg':72,'driver_status':1            
    },
    {   
        'driver_number': 11, 'name': 'Sergio Perez', 'team': 'Red Bull Racing', 
        'age_in_2023': 33, 'years_of_experience': 13, 'years_in_current_team': 3, 'contract_years_remaining':1,
        'country': 'Mexico', 'marital_status': 'Married', 'has_kids': True, 
        'world_championships': 0, 'height_cm': 173, 'weight_kg': 63, 'driver_status': 2
    },
    {
        'driver_number': 44, 'name': 'Lewis Hamilton', 'team': 'Mercedes', 
        'age_in_2023': 38, 'years_of_experience': 17, 'years_in_current_team': 11,'contract_years_remaining':0, 
        'country': 'United Kingdom', 'marital_status': 'Single', 'has_kids': False, 
        'world_championships': 7, 'height_cm': 174, 'weight_kg': 73, 'driver_status': 1
    },
    {
        'driver_number': 63, 'name': 'George Russell', 'team': 'Mercedes', 
        'age_in_2023': 25, 'years_of_experience': 5, 'years_in_current_team': 2,'contract_years_remaining':2,
        'country': 'United Kingdom', 'marital_status': 'In a Relationship', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 185, 'weight_kg': 70, 'driver_status': 2
    },
    {
        'driver_number': 16, 'name': 'Charles Leclerc', 'team': 'Ferrari', 
        'age_in_2023': 26, 'years_of_experience': 6, 'years_in_current_team': 5,'contract_years_remaining':1, 
        'country': 'Monaco', 'marital_status': 'In a Relationship', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 180, 'weight_kg': 69, 'driver_status': 1
    },
    {
        'driver_number': 55, 'name': 'Carlos Sainz', 'team': 'Ferrari', 
        'age_in_2023': 29, 'years_of_experience': 9, 'years_in_current_team': 3,'contract_years_remaining':1, 
        'country': 'Spain', 'marital_status': 'In a Relationship', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 178, 'weight_kg': 66, 'driver_status': 2
    },
    {
        'driver_number': 4, 'name': 'Lando Norris', 'team': 'McLaren', 
        'age_in_2023': 24, 'years_of_experience': 5, 'years_in_current_team': 5,'contract_years_remaining':2, 
        'country': 'United Kingdom', 'marital_status': 'Single', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 170, 'weight_kg': 68, 'driver_status': 1
    },
    {
        'driver_number': 81, 'name': 'Oscar Piastri', 'team': 'McLaren', 
        'age_in_2023': 22, 'years_of_experience': 1, 'years_in_current_team': 1,'contract_years_remaining':3, 
        'country': 'Australia', 'marital_status': 'In a Relationship', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 178, 'weight_kg': 68, 'driver_status': 2
    },
    {
        'driver_number': 14, 'name': 'Fernando Alonso', 'team': 'Aston Martin', 
        'age_in_2023': 42, 'years_of_experience': 20, 'years_in_current_team': 1,'contract_years_remaining':1, 
        'country': 'Spain', 'marital_status': 'In a Relationship', 'has_kids': False, 
        'world_championships': 2, 'height_cm': 171, 'weight_kg': 68, 'driver_status': 1
    },
    {
        'driver_number': 18, 'name': 'Lance Stroll', 'team': 'Aston Martin', 
        'age_in_2023': 25, 'years_of_experience': 7, 'years_in_current_team': 5,'contract_years_remaining':3, 
        'country': 'Canada', 'marital_status': 'In a Relationship', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 182, 'weight_kg': 70, 'driver_status': 2
    },
    {
        'driver_number': 10, 'name': 'Pierre Gasly', 'team': 'Alpine', 
        'age_in_2023': 27, 'years_of_experience': 7, 'years_in_current_team': 1,'contract_years_remaining':1, 
        'country': 'France', 'marital_status': 'In a Relationship', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 177, 'weight_kg': 70, 'driver_status': 2
    },
    {
        'driver_number': 31, 'name': 'Esteban Ocon', 'team': 'Alpine', 
        'age_in_2023': 27, 'years_of_experience': 7, 'years_in_current_team': 4,'contract_years_remaining':1, 
        'country': 'France', 'marital_status': 'In a Relationship', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 186, 'weight_kg': 66, 'driver_status': 1
    },
    {
        'driver_number': 23, 'name': 'Alex Albon', 'team': 'Williams', 
        'age_in_2023': 27, 'years_of_experience': 4, 'years_in_current_team': 2,'contract_years_remaining':1, 
        'country': 'Thailand', 'marital_status': 'In a Relationship', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 186, 'weight_kg': 73, 'driver_status': 1
    },
    {
        'driver_number': 2, 'name': 'Logan Sargeant', 'team': 'Williams', 
        'age_in_2023': 23, 'years_of_experience': 1, 'years_in_current_team': 1,'contract_years_remaining':0, 
        'country': 'United States', 'marital_status': 'Single', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 181, 'weight_kg': 71, 'driver_status': 2
    },
    {
        'driver_number': 22, 'name': 'Yuki Tsunoda', 'team': 'AlphaTauri', 
        'age_in_2023': 23, 'years_of_experience': 3, 'years_in_current_team': 3,'contract_years_remaining':0, 
        'country': 'Japan', 'marital_status': 'Single', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 159, 'weight_kg': 54, 'driver_status': 1
    },
    {
        'driver_number': 77, 'name': 'Valtteri Bottas', 'team': 'Alfa Romeo', 
        'age_in_2023': 34, 'years_of_experience': 11, 'years_in_current_team': 2,'contract_years_remaining':1, 
        'country': 'Finland', 'marital_status': 'In a Relationship', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 173, 'weight_kg': 69, 'driver_status': 1
    },
    {
        'driver_number': 24, 'name': 'Zhou Guanyu', 'team': 'Alfa Romeo', 
        'age_in_2023': 24, 'years_of_experience': 2, 'years_in_current_team': 2,'contract_years_remaining':0, 
        'country': 'China', 'marital_status': 'Single', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 175, 'weight_kg': 63, 'driver_status': 2
    },
    {
        'driver_number': 20, 'name': 'Kevin Magnussen', 'team': 'Haas', 
        'age_in_2023': 31, 'years_of_experience': 9, 'years_in_current_team': 6,'contract_years_remaining':0, 
        'country': 'Denmark', 'marital_status': 'Married', 'has_kids': True, 
        'world_championships': 0, 'height_cm': 174, 'weight_kg': 68, 'driver_status': 1
    },
    {
        'driver_number': 27, 'name': 'Nico Hulkenberg', 'team': 'Haas', 
        'age_in_2023': 36, 'years_of_experience': 12, 'years_in_current_team': 1,'contract_years_remaining':0, 
        'country': 'Germany', 'marital_status': 'Married', 'has_kids': True, 
        'world_championships': 0, 'height_cm': 184, 'weight_kg': 78, 'driver_status': 2
    },
    {
        'driver_number': 3, 'name': 'Daniel Ricciardo', 'team': 'AlphaTauri', 
        'age_in_2023': 34, 'years_of_experience': 13, 'years_in_current_team': 1,'contract_years_remaining':0, 
        'country': 'Australia', 'marital_status': 'In a Relationship', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 180, 'weight_kg': 66, 'driver_status': 2
    },
    {
        'driver_number': 40, 'name': 'Liam Lawson', 'team': 'AlphaTauri', 
        'age_in_2023': 21, 'years_of_experience': 1, 'years_in_current_team': 1,'contract_years_remaining':0, 
        'country': 'New Zealand', 'marital_status': 'In a Relationship', 'has_kids': False, 
        'world_championships': 0, 'height_cm': 174, 'weight_kg': 68, 'driver_status': 2
    }
]

df_drivers_data = pd.DataFrame(drivers_data)
 
# savaing data into csv file
#os.makedirs('processed_data', exist_ok=True)
#df_drivers_data.to_csv('processed_data/f1_drivers_data_2023.csv', index=False, encoding='utf-8-sig')
#print('data saved to processed_data/f1_drivers_data_2023.csv')
 
# add new column - contract_years_remaining to the csv file and updtate the values based on the contract information of each driver 
file_path = 'processed_data/f1_drivers_data_2023.csv'
df = pd.read_csv(file_path)

contract_mapping = {1:5,11:2,44:0,63:2,16:1,55:1,4:2,81:3,14:1,18:3,10:1,31:1,23:1,2:0,22:0,77:1,24:0,20:0,27:0,3:0,40:0}
df['contract_years_remaining'] = df['driver_number'].map(contract_mapping)
df.to_csv(file_path, index=False, encoding='utf-8-sig')
print('contract years remaining updated in the csv file')