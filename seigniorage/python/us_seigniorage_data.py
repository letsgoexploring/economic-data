#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import fredpy as fp
import numpy as np


# # US Seigniorage Data
# 
# Seigniorage is the real value of the change in the monetary base:
# 
# \begin{align}
# \frac{M_{t}-M_{t-1}}{P_t} & = \Delta m_t + \frac{\pi_t}{1+\pi_t}m_{t-1}
# \end{align}
# 
# where $\Delta m_t = m_t - m_{t-1}$ and $\pi_t = P_t/ P_{t-1} - 1$. The first term on the right-hand side is the revenue from increasing the real monetary base while the seond term is the inflation tax on the existing monetary base.
# 
# This program downloads from FRED the following data for the US economy:
# 
# * monetary base (BOGMBASE)
# * GDP deflator data (A191RD3A086NBEA)
# 
# The program returns a CSV file with columns containing:
# 
# * average annual real monetary base (trillions of $)
# * average annual GDP deflator inflation
# * change in real monetary base from preceding year for 1960 only
# * inflation tax from preceding year for 1960 only
# * total seigniorage for 1960 only
# 
# The purpose behind providing incomplete columns is to give students a starting point for completing the columns using Excel or a comparable tool.
# 
# ## Download and manage data

# In[2]:


# Download monetary base and GDP deflator data
m_base = fp.series('BOGMBASE')
gdp_deflator = fp.series('A191RD3A086NBEA')

# Convert monetary base data to annual frequency
m_base = m_base.as_frequency('A')

# Equalize data ranges for monetary base and GDP deflator data
m_base, gdp_deflator = fp.window_equalize([m_base, gdp_deflator])

# GDP deflator base year
base_year = gdp_deflator.units.split(' ')[-1].split('=')[0]


# In[3]:


# Construct real monetary base
real_m_base = m_base.data/gdp_deflator.data*100/1000/1000

# Construct inflation data
inflation = (gdp_deflator.data/gdp_deflator.data.shift(1))-1


# ## Save data to csv

# In[4]:


real_m_base_col_name = 'real monetary base [billions of '+base_year+' dollars]'
inflation_col_name = 'GDP deflator inflation'
delta_m_base_col_name = 'change in real monetary base [billions of '+base_year+' dollars]'
inflation_tax_col_name = 'inflation tax revenue [billions of '+base_year+' dollars]'
total_col_name = 'total seigniorage [billions of '+base_year+' dollars]'


# Put data into DataFrame
df = pd.DataFrame({real_m_base_col_name:real_m_base,inflation_col_name:inflation})

# Add single value to second row of the change in real monetary base column
df.loc[df.index[1],delta_m_base_col_name] = df.loc[df.index[1],real_m_base_col_name] - df.loc[df.index[0],real_m_base_col_name]

# Add single value to second row of the inflation tax revenue column
df.loc[df.index[1],inflation_tax_col_name] = 1/(1+1/df.loc[df.index[1],inflation_col_name]) * df.loc[df.index[0],real_m_base_col_name]

# Add single value to second row of total seigniorage column
df.loc[df.index[1],total_col_name] = df.loc[df.index[1],delta_m_base_col_name] + df.loc[df.index[1],inflation_tax_col_name]

# Save to csv
df.to_csv('../csv/us_seigniorage_data.csv',index=True)

