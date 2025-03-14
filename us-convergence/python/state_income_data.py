#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import json
from urllib.request import urlopen
import os


# # State Income Data
# 
# Constructs a data set of real income per capita for the continental United States from 1840 to the present.
# 
# Nominal income per capita for 1840, 1880, a 1900 were found in Appendix A in "Interregional Differences in Per Capita Income, Population, and Total Income, 1840-1950" by Richard Easterlin in <ins>Trends in the American Economy in the Nineteenth Century</ins> (https://www.nber.org/books-and-chapters/trends-american-economy-nineteenth-century).
# 
# The CPI for 1840, 1880, and 1900 was taken from "<ins>Bicentennial Edition: Historical Statistics of the United States, Colonial Times to 1970</ins> (https://www.census.gov/library/publications/1975/compendia/hist_stats_colonial-1970.html)
# 
# 
# Income data from 1929 are obtained from the BEA.
# 
# ## Preliminaries

# In[2]:


# Import BEA API key or set manually to variable api_key
try:
    items = os.getcwd().split('/')[:3]
    items.append('bea_api_key.txt')
    path = '/'.join(items)
    with open(path,'r') as api_key_file:
        api_key = api_key_file.readline()

except:
    api_key = None


# In[3]:


# Dictionary of state abbreviations
stateAbbr = {
u'Alabama':u'AL',
u'Alaska *':u'AK',
u'Arizona':u'AZ',
u'Arkansas':u'AR',
u'California':u'CA',
u'Colorado':u'CO',
u'Connecticut':u'CT',
u'Delaware':u'DE',
u'District of Columbia':u'DC',
u'Florida':u'FL',
u'Georgia':u'GA',
u'Hawaii *':u'HI',
u'Idaho':u'ID',
u'Illinois':u'IL',
u'Indiana':u'IN',
u'Iowa':u'IA',
u'Kansas':u'KS',
u'Kentucky':u'KY',
u'Louisiana':u'LA',
u'Maine':u'ME',
u'Maryland':u'MD',
u'Massachusetts':u'MA',
u'Michigan':u'MI',
u'Minnesota':u'MN',
u'Mississippi':u'MS',
u'Missouri':u'MO',
u'Montana':u'MT',
u'Nebraska':u'NE',
u'Nevada':u'NV',
u'New Hampshire':u'NH',
u'New Jersey':u'NJ',
u'New Mexico':u'NM',
u'New York':u'NY',
u'North Carolina':u'NC',
u'North Dakota':u'ND',
u'Ohio':u'OH',
u'Oklahoma':u'OK',
u'Oregon':u'OR',
u'Pennsylvania':u'PA',
u'Rhode Island':u'RI',
u'South Carolina':u'SC',
u'South Dakota':u'SD',
u'Tennessee':u'TN',
u'Texas':u'TX',
u'Utah':u'UT',
u'Vermont':u'VT',
u'Virginia':u'VA',
u'Washington':u'WA',
u'West Virginia':u'WV',
u'Wisconsin':u'WI',
u'Wyoming':u'WY'
}

# List of states in the US
stateList = [s for s in stateAbbr]


# ## Deflator data

# In[4]:


# Obtain data from BEA
gdp_deflator = urlopen('http://apps.bea.gov/api/data/?UserID='+api_key+'&method=GetData&datasetname=NIPA&TableName=T10109&TableID=13&Frequency=A&Year=X&ResultFormat=JSON&')

# Parse result
result = gdp_deflator.read().decode('utf-8')
json_response = json.loads(result)

# Import to DataFrame and organize
df = pd.DataFrame(json_response['BEAAPI']['Results']['Data'])
df['DataValue'] = df['DataValue'].astype(float)
df = df.set_index(['LineDescription',pd.to_datetime(df['TimePeriod'])])
df.index.names = ['line description','Year']

# Extract price level data
data_p = df['DataValue'].loc['Gross domestic product']/100
data_p.name = 'price level'
data_p = data_p.sort_index()
data_p


# In[5]:


base_year = json_response['BEAAPI']['Results']['Notes'][0]['NoteText'].split('Index numbers, ')[-1].split('=')[0]

with open('../csv/state_income_metadata.csv','w') as newfile:
    newfile.write(',Values\n'+'base_year,'+base_year)


# ## Per capita income data

# In[6]:


# Obtain data from BEA
state_y_pc = urlopen('http://apps.bea.gov/api/data/?UserID='+api_key+'&method=GetData&DataSetName=Regional&TableName=SAINC1&LineCode=3&Year=ALL&GeoFips=STATE&ResultFormat=JSON')

# Parse result
result = state_y_pc.read().decode('utf-8')
json_response = json.loads(result)

# Import to DataFrame and organize
df = pd.DataFrame(json_response['BEAAPI']['Results']['Data'])
df.GeoName = df.GeoName.replace(stateAbbr)
df = df.set_index(['GeoName',pd.DatetimeIndex(df['TimePeriod'])])
df.index.names = ['State','Year']
df['DataValue'] = df['DataValue'].replace('(NA)',np.nan)


# # Extract income data
data_y = df['DataValue'].str.replace(',','').astype(float)
data_y.name = 'income'
data_y = data_y.unstack('State')
data_y = data_y.sort_index()
data_y = data_y.divide(data_p,axis=0)
data_y = data_y.dropna(how='all')


# # Load Easterlin's data

# In[7]:


# Import Easterlin's income data
easterlin_data = pd.read_csv('../historic_data/Historical Statistics of the US - Easterlin State Income Data.csv',index_col=0)

# Import historic CPI data
historic_cpi_data=pd.read_csv('../historic_data/Historical Statistics of the US - cpi.csv',index_col=0)
historic_cpi_data = historic_cpi_data/historic_cpi_data.loc[1929]*data_p.loc['1929'].iloc[0]


# In[8]:


# Construct series for real incomes in 1840, 1880, and 1900
df_1840 = easterlin_data['Income per capita - 1840 - A [cur dollars]']/historic_cpi_data.loc[1840].iloc[0]
df_1880 = easterlin_data['Income per capita - 1880 [cur dollars]']/historic_cpi_data.loc[1890].iloc[0]
df_1900 = easterlin_data['Income per capita - 1900 [cur dollars]']/historic_cpi_data.loc[1900].iloc[0]

# Put into a DataFrame and concatenate with previous data beginning in 1929
df = pd.DataFrame({pd.to_datetime('1840'):df_1840,pd.to_datetime('1880'):df_1880,pd.to_datetime('1900'):df_1900}).transpose()
df = pd.concat([data_y,df]).sort_index()

# Replace 0s for Alaska and Hawaii with NaN. 
df.loc[df['AK']==0,'AK']=np.nan
df.loc[df['HI']==0,'HI']=np.nan


# In[9]:


# Export data to csv
series = df.sort_index()
# dropCols = [u'AK', u'HI', u'New England', u'Mideast', u'Great Lakes', u'Plains', u'Southeast', u'Southwest', u'Rocky Mountain', u'Far West','Far West *']
dropCols = [u'New England', u'Mideast', u'Great Lakes', u'Plains', u'Southeast', u'Southwest', u'Rocky Mountain', u'Far West','Far West *']
for c in dropCols:
    series = series.drop([c],axis=1)

series.to_csv('../csv/state_income_data.csv',na_rep='NaN')

