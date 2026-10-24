#essential library for data analysis
import pandas as pd
#module to work with databases
import sqlite3
#a library which allows the creation of graphs
import matplotlib.pyplot as plt
#auxiliar one to help with visualization
import matplotlib.ticker as ticker

#local path to the CSV file
file_path= "dly2275.csv"

#an "automatic" way to filter through the file and get rid of any possible inconvenient
header_line = 0
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    for line_number, line in enumerate(f):
        if 'date' in line.lower() and ('maxtp' in line.lower() or 'rain' in line.lower()):
            header_line = line_number
            break

#the Pandas function will read the local file
df_raw = pd.read_csv(file_path, skiprows=header_line, low_memory=False)

#to clean hidden spaces
df_raw.columns = df_raw.columns.str.strip().str.lower()

#here we select the "only" columns that really matter for us, ignoring the rest of the data
#.copy will create a copy of this data to avoid warnings related to the original table
#HERE WE TREAT THE DATA AND SELECT EXACTLY WHAT WE WANT FROM IT
df = df_raw[['date', 'maxtp', 'rain']].copy()

#here we filter the data and convert then to float using a Pandas function
#errors='coerce' guarantees that the program won't fail in case there invalid data there
df['maxtp'] = pd.to_numeric(df['maxtp'], errors='coerce')
df['rain'] = pd.to_numeric(df['rain'], errors='coerce')

#we enter into date and extract only the year from there
#the column year will be created after that
df['date'] = pd.to_datetime(df['date'], format='mixed')
df['year'] = df['date'].dt.year

#Vital step opening/creating a connection with the database
conn = sqlite3.connect('ireland_climate.sqlite')

#df.to_sql takes the table and converts it to a SQLite database directly
#it replaces the table in case it already exists, thus making repeated tests more intuitive
#it also avoid that Panda's relative column lines get saved into the database
df.to_sql('valentia_weather', conn, if_exists='replace', index=False)

#we will group the data by year
#we want the maxtp inside every year
#.mean will calculate the average considering 365 days per year
annual_temp = df.groupby('year')['maxtp'].mean()

#it shows the last 10 years
print(annual_temp.tail(10))

#CREATING THE GRAPH AND TELLING ITS WIDTH AND HEIGHT IN INCHES
plt.figure(figsize=(12, 6))

#HERE IS WHERE THE MAGIC BECOMES VISIBLE
#first_arg = x-axis, second_arg= y-axis
#the rest are details and parameters for the graph
plt.plot(annual_temp.index, annual_temp.values, color='darkred', linewidth=1.5, label='Average Max Temperature')

#Here we add more details such as title, names for the axis, grid for visibility and legend
plt.title('Average Max Temperature Across Years in Ireland', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Temperature (°C)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

#setting to display the graph by decade
ax = plt.gca()
ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
plt.xticks(rotation=0)

#to display the graph
plt.legend()
plt.show()

#A way to export DATA directly through Excel to help with PowerBI
df.to_excel('ireland_climate.xlsx', index=False)