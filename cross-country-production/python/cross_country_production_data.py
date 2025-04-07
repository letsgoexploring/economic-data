#!/usr/bin/env python
# coding: utf-8

# In[1]:


from urllib.request import urlopen
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
plt.style.use('classic')
plt.rcParams['figure.facecolor'] = 'white'


# In[2]:


# Export path: Set to empty string '' if you want to export data to current directory
csv_export_path = '../csv/'

# Most recent PWT version verified manually
manual_pwt_version = '10.01'

# Download link for PWT Excel file
pwt_excel_url = 'https://dataverse.nl/api/access/datafile/354095'


# # Cross Country Production Data
# 
# This program extracts particular series from the Penn World Tables (PWT). Data and documentation for the PWT are available at https://pwt.sas.upenn.edu/. For additional reference see the article "The Next Generation of the Penn World Table" by Feenstra, Inklaar, and Timmer in the October 2015 issue of the *American Economic Review* (https://www.aeaweb.org/articles?id=10.1257/aer.20130954)
# 
# ## Try to find the current version of PWT

# In[3]:


# Get HTML for PWT homepage
html = urlopen("https://www.rug.nl/ggdc/productivity/pwt/?lang=en").read()

# Parse HTML
soup = BeautifulSoup(html, 'html.parser')

# Find title string
title = soup.find('title').string


try:
    float(title.string.split(' ')[1])
    pwt_version = title.string.split(' ')[1]
except:
    print('Automatic PWT version identification failed.')
    pwt_version = manual_pwt_version


# ## Import data and manage

# In[4]:


# Set the current value of the PWT data file
current_pwt_file = 'pwt'+pwt_version.replace('.','')+'.xlsx'


# In[5]:


# Import data from local source or download if not present
if os.path.exists('../xslx/'+current_pwt_file):
    info = pd.read_excel('../xslx/'+current_pwt_file,sheet_name='Info',header=None)
    legend = pd.read_excel('../xslx/'+current_pwt_file,sheet_name='Legend',index_col=0)
    pwt = pd.read_excel('../xslx/'+current_pwt_file,sheet_name='Data',index_col=3,parse_dates=True)

else:
    info = pd.read_excel(pwt_excel_url,sheet_name='Info',header=None)
    legend = pd.read_excel(pwt_excel_url,sheet_name='Legend',index_col=0)
    pwt = pd.read_excel(pwt_excel_url,sheet_name='Data',index_col=3,parse_dates=True)


# In[6]:


# Find PWT version
version = info.iloc[0][0].split(' ')[-1]

# Find base year for real variables
base_year = legend.loc['rgdpe']['Variable definition'].split(' ')[-1].split('US')[0]

# Most recent year
final_year = pwt[pwt['countrycode']=='USA'].sort_index().index[-1].year

metadata = pd.Series(dtype=str,name='Values')
metadata['version'] = version
metadata['base_year'] = base_year
metadata['final_year'] = final_year
metadata['gdp_per_capita_units'] = base_year+' dollars per person'

metadata.to_csv(csv_export_path+'/pwt_metadata.csv')


# In[7]:


# Replace Côte d'Ivoire with Cote d'Ivoire
pwt['country'] = pwt['country'].str.replace(u"Côte d'Ivoire",u"Cote d'Ivoire")

# Merge country name and code
pwt['country'] = pwt['country']+' - '+pwt['countrycode']

# Create hierarchical index
pwt = pwt.set_index(['country',pwt.index])

# Display new DataFrame
pwt


# ## Construct data sets

# In[8]:


# Define a function that constructs data sets
def create_data_set(year0,pwtCode,per_capita,per_worker):
    
    year0 = str(year0)
    
    if per_capita:
        data = pwt[pwtCode]/pwt['pop']
        
    elif per_worker:
        data = pwt[pwtCode]/pwt['emp']
        
    else:
        data = pwt[pwtCode]
        
    data = data.unstack(level='country').loc[year0:].dropna(axis=1)
    
    return data


# ### Individual time series

# In[9]:


# Create data sets
gdp_pc = create_data_set(year0=1960,pwtCode='cgdpo',per_capita=True,per_worker=False)
consumption_pc = create_data_set(year0=1960,pwtCode='ccon',per_capita=True,per_worker=False)
physical_capital_pc = create_data_set(year0=1960,pwtCode='cn',per_capita=True,per_worker=False)
human_capital_pc = create_data_set(year0=1960,pwtCode='hc',per_capita=False,per_worker=False)
price_level = create_data_set(year0=1960,pwtCode='pl_gdpo',per_capita=False,per_worker=False)

# Find intsection of countries with data from 1960
intersection = gdp_pc.columns.intersection(consumption_pc.columns).intersection(physical_capital_pc.columns).intersection(human_capital_pc.columns).intersection(price_level.columns)

# Adjust data
gdp_pc = gdp_pc[intersection]
consumption_pc = consumption_pc[intersection]
physical_capital_pc = physical_capital_pc[intersection]
human_capital_pc = human_capital_pc[intersection]
price_level = price_level[intersection]

# Export to csv
gdp_pc.to_csv(csv_export_path+'/cross_country_gdp_per_capita.csv')
consumption_pc.to_csv(csv_export_path+'/cross_country_consumption_per_capita.csv')
physical_capital_pc.to_csv(csv_export_path+'/cross_country_physical_capital_per_capita.csv')
human_capital_pc.to_csv(csv_export_path+'/cross_country_human_capital_per_capita.csv')
price_level.to_csv(csv_export_path+'/cross_country_price_level.csv')


# ### Multiple series for last year available

# In[10]:


# Restrict data to final year
df = pwt.swaplevel(0, 1).sort_index().loc[(str(final_year),slice(None))].reset_index()

# Select columns: 'countrycode','country','cgdpo','emp','hc','cn','pl_gdpo'
df = df[['countrycode','country','cgdpo','emp','hc','cn','pl_gdpo']]

# Rename columns
df.columns = ['country_code','country','gdp','labor','human_capital','physical_capital','price_level']

# Remove country codes from country column
df['country'] = df['country'].str.split(' - ',expand=True)[0]

# Drop countries with missing observations
df = df.dropna()


# 3. Export data
df[['country_code','country','gdp','labor','human_capital','physical_capital','price_level']].to_csv(csv_export_path+'/cross_country_production.csv',index=False)


# ## Plot for website

# In[11]:


# Load data
df = pd.read_csv('../csv/cross_country_gdp_per_capita.csv',index_col='year',parse_dates=True)
income60 = df.iloc[0]/1000
growth = 100*((df.iloc[-1]/df.iloc[0])**(1/(len(df.index)-1))-1)

# Construct plot
fig = plt.figure(figsize=(10, 6)) 
ax = fig.add_subplot(1,1,1)
colors = ['red','blue','magenta','green']

plt.scatter(income60,growth,s=0.0001)
for i, txt in enumerate(df.columns):
    
    ax.annotate(txt[-3:], (income60[i],growth[i]),fontsize=10,color = colors[np.mod(i,4)])
ax.grid()

ax.set_xlabel('GDP per capita in 1960\n (thousands of 2011 $ PPP)')
ax.set_ylabel('Real GDP per capita growth\nfrom 1970 to '+str(df.index[0].year)+ ' (%)')
xlim = ax.get_xlim()
ax.set_xlim([0,xlim[1]])

fig.tight_layout()

# Save image
plt.savefig('../png/fig_GDP_GDP_Growth_site.png',bbox_inches='tight')

