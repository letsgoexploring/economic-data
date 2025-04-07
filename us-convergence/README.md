# `us-convergence`

Programs for creating a dataset of US state- and regional-level income per capita from 1929 to present.

1. US state income per capita dataset
  - Instructions: Run either **state_income_data.ipynb** or **state_income_data.py**
  - Ouput:
    - stateIncomeData.csv in the ../csv directory
  - Dependencies: numpy, pandas, json

2. US state income per capita animated gif.
  - Instructions: Run **us_convergence_map.ipynb** or **us_convergence_map.py**. *You must have ImageMagick (http://www.imagemagick.org/) installed on your system to run this.*
  - Output: 
    - us_state_convergence.gif in the ../gif directory
  - Dependencies: bs4 (BeautifulSoup), simplemapplot, runProcs.py
