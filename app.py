import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

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
    'All (1920-2022)' : ('All (1920-2022)', 1920, 2022),
    'Silent Generation (1928 - 1945)': ('Silent Generation (1928 - 1945)', 1928, 1945), #17
    'Baby Boomer (1946 - 1964)': ('Baby Boomer (1946 - 1964)', 1946, 1964), #18
    'Gen X (1965 - 1980)': ('Gen X (1965 - 1980)', 1965, 1980), #15
    'Millennials (1981 - 1996)': ('Millennials (1981 - 1996)', 1981, 1996), #15
    'Gen Z (1997 - 2009)': ('Gen Z (1997 - 2009)', 1997, 2009), #12
    'Gen Alpha (2010 - 2022)': ('Gen Alpha (2010 - 2022)', 2010, 2022)
}

def get_generation(genName):
    
    df = load_data()
    gen = df[(df['birthdate'].dt.year >= generation_ranges[genName][1]) & (df['birthdate'].dt.year <= generation_ranges[genName][2])]
    return gen

def get_range(start, end):
    
    df = load_data()
    gen = df[(df['birthdate'].dt.year >= start) & (df['birthdate'].dt.year <= end)]
    return gen
 
### BIRTHDAY RANK
def numOfdays(year):
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return 366
    else:
        return 365

def currentAge(date):
    
    age = datetime.now() - datetime.strptime(str(date), '%Y-%m-%d')
    years = age.days // 365
    remaining_days = age.days % 365
    months = remaining_days // 30
    remaining_days = remaining_days % 30
    days = remaining_days
    st.write("You are {} years, {} months, {} days old".format(years, months, days))
    

def bdayRank(date):
    inputYr = date.year
    df_yr = get_range(inputYr, inputYr)
    df_yr = df_yr.sort_values(by='births', ascending=False).reset_index(drop=True)
    ranking = df_yr.index[df_yr['birthdate'] == pd.to_datetime(date)].tolist()
    
    currentAge(date)
    
    txt = f'''In <b style="font-size:larger">{inputYr}</b>, 
    this birthday ranked as the 
    <b style="font-size:larger">{ranking[0]}{"th" if 11 <= ranking[0] <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(ranking[0] % 10, "th")}</b> 
    most popular birthday out of the {numOfdays(inputYr)} potential dates'''
    st.markdown(txt, unsafe_allow_html=True)
    
    st.write(' dd MM is ')
 
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

### MOST COMMON BIRTHDAYS ###
def commonBday(start, end, N):
    gen = get_range(start, end)
    birthdates = gen.sort_values(by='births', ascending=False).head(N).reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(birthdates['date'].astype(str) + ' ' + birthdates['month'].map(month_names), birthdates['births'], color='purple')
    ax.invert_yaxis()
    ax.set_xlim(birthdates['births'].min() - 30, birthdates['births'].max() + 30)

    for bar in bars:
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}', ha='left', va='center', fontsize=12)
   
    if (start == end):
        ax.set_title(f'Most Common Birthday dates (' + str(start) + ')')
    else:
        ax.set_title(f'Most Common Birthday dates (' + str(start) + ' - ' +  str(end) + ')')
    ax.set_xlabel('Total Births')
    ax.set_ylabel('Birthday Date')
    st.pyplot(fig)
    
### RAREST BIRTHDAY ###
def rareBday(start, end, N):
    gen = get_range(start, end)
    birthdates = gen.sort_values(by='births', ascending=True).head(N).reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(birthdates['date'].astype(str) + ' ' + birthdates['month'].map(month_names), birthdates['births'], color='lightblue')
    ax.invert_yaxis()
    ax.set_xlim(birthdates['births'].min() - 30, birthdates['births'].max() + 30)
    
    for bar in bars:
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}', ha='left', va='center', fontsize=12)
   
    if (start == end):
        ax.set_title(f'Rarest Birthday dates (' + str(start) + ')')
    else:
        ax.set_title(f'Rarest Birthday dates (' + str(start) + ' - ' +  str(end) + ')')
    ax.set_xlabel('Total Births')
    ax.set_ylabel('Birthday Date')
    st.pyplot(fig)
    


### METHOD CREATING HEATMAP ###
def generate_heatmap(start, end):
    # gen = get_generation(genName)
    gen = get_range(start, end)
   
    pivot_table = gen.pivot_table(index='month', columns='date', values='births', aggfunc='sum')
    pivot_table.index = pivot_table.index.map(month_names)
    pivot_table.columns = pivot_table.columns.map(str)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(pivot_table, cmap='BuPu', annot=False, linewidths=2, robust=True, ax=ax)

    # ax.set_title(f'Heatmap of Most Common Birthdays for {generation_ranges[genName][0]}')
    ax.set_title('Heatmap of Most Common Birthdays for (' + str(start) + ' - ' +  str(end) + ')')
    ax.set_xlabel('Date')
    ax.set_ylabel('Month')
    st.pyplot(fig)
    

st.subheader('Birthday Rank')
birthday = st.date_input("Your birthday")
tabA, tabB, tabC = st.tabs(["Summary", "Popular Birthday Date", "Rarest Birthday Date"])
with tabA:
    bdayRank(birthday)

with tabB:
    inputYr = birthday.year
    st.write('The top most common birthdays in ', inputYr,  ' are:')
    commonBday(inputYr, inputYr, 10)
    
with tabC:
    inputYr = birthday.year
    st.write('The top rarest birthdays in ', inputYr,  ' are:')
    rareBday(inputYr, inputYr, 10)


st.subheader('Birthday HeatMap')
tab1, tab2 = st.tabs(["Generations", "Custom Range"])

with tab1:
    generation_options = list(generation_ranges.keys())
    selected_generation = st.radio("Select Generation", generation_options)
    start, end = generation_ranges[selected_generation][1], generation_ranges[selected_generation][2]
    generate_heatmap(start, end)


with tab2:
    start, end = st.slider('Select range', value=[1920,2022], min_value=1920, max_value=2022 )
    st.write("Selected Year Range: From ", start, 'To ', end)
    generate_heatmap(start, end)
