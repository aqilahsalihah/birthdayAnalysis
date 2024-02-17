import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title='Birthday Annalysis', page_icon=':birthday_cake:', layout='wide')
st.title("How Rare is Your Birthday")

### DEFINING DATAFRAME ###
def load_data(): 
    URL_DATA = 'https://storage.data.gov.my/demography/births.parquet'
    df = pd.read_parquet(URL_DATA)
    if 'date' in df.columns: df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df = df.drop('state', axis=1 )
    df = df.rename(columns={'date': 'birthdate'})
    df['year'] = df['birthdate'].dt.year
    df['month'] = df['birthdate'].dt.month
    df['date'] = df['birthdate'].dt.day
    df = df[['birthdate', 'year', 'month', 'date', 'births']]
    return df
    

### DEFINING GENERATION ###
generation_ranges = {
    'all' : ('All (1920-2022)', 1920, 2022),
    'older' : ('Older Generation (1920 - 1980)', 1920, 1980),
    'younger' : ('Younger Generation (1981 - 2022)', 1981, 2022),
    'silent': ('Silent Generation (1928 - 1945)', 1928, 1945), #17
    'boomer': ('Baby Boomer (1946 - 1964)', 1946, 1964), #18
    'genX': ('Gen X (1965 - 1980)', 1965, 1980), #15
    'genY': ('Millennials (1981 - 1996)', 1981, 1996), #15
    'genZ': ('Gen Z (1997 - 2009)', 1997, 2009), #12
    'genAlpha': ('Gen Alpha (2010 - 2022)', 2010, 2022)
}

def get_generation(genName):
    
    df = load_data()
    gen = df[(df['birthdate'].dt.year >= generation_ranges[genName][1]) & (df['birthdate'].dt.year <= generation_ranges[genName][2])]
    # st.write(gen)
    return gen
 
 
### MONTH NAMES DICTIONARY ###   
month_names = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sept',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec'
}


### METHOD CREATING HEATMAP ###
def generate_heatmap(genName):
    gen = get_generation(genName)
   
    pivot_table = gen.pivot_table(index='month', columns='date', values='births', aggfunc='sum')
    pivot_table.index = pivot_table.index.map(month_names)
    pivot_table.columns = pivot_table.columns.map(str)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(pivot_table, cmap='BuPu', annot=False, linewidths=2, robust=True, ax=ax)

    ax.set_title(f'Heatmap of Most Common Birthdays for {generation_ranges[genName][0]}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Month')
    st.pyplot(fig)
    
generation_options = list(generation_ranges.keys())
selected_generation = st.selectbox("Select Generation", generation_options)
generate_heatmap(selected_generation)