import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from datetime import datetime
import plotly.express as px


st.set_page_config(
    page_title="Bike Sharing Analysis",
    page_icon="🚴",
    layout="wide"
)

warnings.filterwarnings('ignore')

st.title("Bike Sharing Analysis")
st.write("""
Explaratory Data Analysis untuk Penyewaan Sepeda di tahun 2011 hingga 2012""")

with st.sidebar:
    st.markdown("""
        <style>
            div {
                text-align: center;
            }
        </style>
    """, unsafe_allow_html=True)
    st.header("""
              Tugas ini merupakan tugas project yang diberikan oleh [dicoding](https://www.dicoding.com/)
               """)


@st.cache_data
def load_data():
    day = pd.read_csv('day.csv', sep=',')
    return day

day = load_data()


day['dteday'] = pd.to_datetime(day['dteday'], format ='%Y-%m-%d' ).dt.date

def ubah_year(x):
    return 2011 if x == 0 else 2012

day['yr'] = day['yr'].apply(ubah_year).astype(int)

day['mnth'] = pd.Categorical(
    day['mnth'].map(lambda x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][x - 1]), 
    categories=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 
    ordered=True
)

def ubah_season(x):
    if x == 1:
        return 'Musim Semi'
    elif x == 2:
        return 'Musim Panas'
    elif x == 3:
        return 'Musim Gugur'
    else:
        return 'Musim Dingin'

day['season'] = day['season'].apply(ubah_season)

def working(x):
    return 'Hari Libur' if x == 1 else 'Bukan Hari Libur'

day['workingday'] = day['workingday'].apply(working)

def situasi_cuaca(x):
    if x == 1:
        return 'Cuaca Cerah'
    elif x == 2:
        return 'Cuaca Berkabut'
    elif x == 3:
        return 'Cuaca Hujan'
    else:
        return 'Cuaca Ekstrem'

day['weathersit'] = day['weathersit'].apply(situasi_cuaca)
day = day.drop(["instant", "holiday", "weekday"], axis=1)

if st.checkbox("Perlihatkan 5 Baris Data"):
    st.write(day.head())

if st.checkbox('Perlihatkan Informasi Awal Data'):
    list_item = [] 
    for col in day.columns: 
        unique_samples = day[col].unique()
        if len(unique_samples) > 30:
            unique_samples = unique_samples[:30]
        list_item.append([col, day[col].dtype, 
                          day[col].isna().sum(), 
                          100 * day[col].isna().sum() / len(day[col]), 
                          day[col].nunique(), 
                          ', '.join(map(str, unique_samples))])  
    desc_df = pd.DataFrame(data=list_item, columns=['Feature', 'Data Type', 'Null', 'Null (%)', 'Unique', 'Unique Sample'])
    st.write(desc_df)



st.subheader("Visualizations")

def season_rent(day):
    seasonal_rentals = day.groupby('season')['cnt'].sum().reset_index()
    fig = px.bar(seasonal_rentals, x='season', y='cnt', color='season',
                 title='Jumlah penyewa Sepeda berdasarkan Musim tahun 2011-2012',
                 color_discrete_map={
                     'Musim Semi': '#4A90E2',
                     'Musim Panas': '#007AFF',
                     'Musim Gugur': '#1C8CBA',
                     'Musim Dingin': '#A4D65E'
                 })
    fig.update_xaxes(title_text='Musim')
    fig.update_yaxes(title_text='Jumlah penyewa Sepeda')
    fig.update_layout(showlegend=False, width=600, height=600)
    for i in range(len(seasonal_rentals)):
        fig.add_annotation(
            x=seasonal_rentals['season'][i],
            y=seasonal_rentals['cnt'][i],
            text=str(int(seasonal_rentals['cnt'][i])),
            showarrow=False,
            font=dict(size=12)
        )
    return fig

def season_workingday(day):
    workingday_rentals = day.groupby(['workingday', 'yr','season'])['cnt'].sum().reset_index()
    fig = px.bar(workingday_rentals, x='season', y='cnt', color='workingday',
                 title='Perbandingan Jumlah penyewa Sepeda Berdasarkan Musim',
                 color_discrete_map={
                     'Hari Libur': '#5B99C2',  
                     'Bukan Hari Libur': '#134B70'  
                 })
    fig.update_xaxes(title_text='Musim')
    fig.update_yaxes(title_text='Jumlah penyewa Sepeda')
    fig.update_layout(showlegend=True, width=600, height=600,
                       barmode='stack',  
                       bargap=0.2,  
                       bargroupgap=0.1,  
                       )
    return fig

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(season_rent(day))
with col2:
    st.plotly_chart(season_workingday(day))


st.write("### Jumlah Total Sepeda yang Disewakan Berdasarkan Cuaca dan Tahun")
import plotly.express as px

def weather_rent(day):
    weather_rentals = day.groupby('weathersit')['cnt'].sum().reset_index()
    fig = px.bar(weather_rentals, x='weathersit', y='cnt', color='weathersit',
                 title='Jumlah penyewa Sepeda Berdasarkan Tahun dan Cuaca',
                 color_discrete_map={
                    'Cuaca Cerah': 'blue',   
                    'Cuaca Berkabut': 'green',  
                    'Cuaca Hujan': 'red'    
                 })

    # Memperbarui label sumbu
    fig.update_xaxes(title_text='Tahun')
    fig.update_yaxes(title_text='Jumlah Penyewaan Sepeda')
    # Mengatur layout
    fig.update_layout(showlegend=True, width=600, height=600)
    for i in range(len(weather_rentals)):
        fig.add_annotation(
            x=weather_rentals['weathersit'][i],
            y=weather_rentals['cnt'][i],
            text=str(int(weather_rentals['cnt'][i])),
            showarrow=False,
            font=dict(size=12)
        )
    return fig

def monthly_rentals(day):
    monthly_counts = day.groupby(by=["mnth", "yr", "weathersit"]).agg({"cnt": "sum"}).reset_index()
    total_counts = monthly_counts.groupby(['yr', 'weathersit'])['cnt'].sum().reset_index()

    fig = px.line(monthly_counts, 
                  x="mnth", 
                  y="cnt", 
                  color="weathersit", 
                  line_dash="yr", 
                  title="Jumlah total sepeda yang disewakan berdasarkan Bulan dan Tahun",
                  markers=True,
                  labels={"mnth": "Bulan", "cnt": "Jumlah penyewa Sepeda", "weathersit": "Cuaca"})
    
    total_legend_labels = []
    for weather in total_counts['weathersit'].unique():
        for index, row in total_counts[total_counts['weathersit'] == weather].iterrows():
            total_legend_labels.append(f"{weather} di Tahun {row['yr']}: {row['cnt']} penyewa")
    
    # Menggabungkan semua label menjadi satu string dengan baris baru
    annotations_text = "<br>".join(total_legend_labels)

    # Menambahkan anotasi ke grafik dengan latar belakang putih dan teks hitam
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0, y=1,
        text=annotations_text,
        showarrow=False,
        font=dict(size=14, color="black"),
        align="left",
        bgcolor="white",  
        bordercolor="black",  
        borderwidth=1,
        xanchor="left",
        yanchor="top"
    )

    # Memperbarui sumbu dan layout
    fig.update_xaxes(title_text='Bulan')
    fig.update_yaxes(title_text='Jumlah penyewa Sepeda', range=[0, 175000], tickvals=[0, 25000, 50000, 75000, 100000, 125000, 150000, 175000])
    fig.update_layout(
        showlegend=True, 
        plot_bgcolor='rgba(0,0,0,0)', 
        width=1000, 
        height=600,
        legend_title_text="Tipe Cuaca",
        legend=dict(x=1, 
                    y=1,
                    font=dict(size=15))  # Menempatkan legend di sudut kanan atas
    )
    fig.update_traces(marker=dict(size=10), line=dict(width=4))

    return fig

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(weather_rent(day), use_container_width=True)

with col2:
     st.plotly_chart(monthly_rentals(day), use_container_width=True)


st.write("### Jumlah total sepeda yang disewakan berdasarkan Bulan dan tahun")
monthly_counts = day.groupby(by=["mnth", "yr"]).agg({"cnt": "sum"}).reset_index()
average_counts1 = monthly_counts.groupby("yr")["cnt"].mean().reset_index()
average_counts1.rename(columns={"cnt": "avg_cnt"}, inplace=True)
# Menghitung jumlah total berdasarkan tahun
total_counts = monthly_counts.groupby('yr')['cnt'].sum().reset_index()

plt.figure(figsize=(10, 4))

sns.lineplot(data=monthly_counts, 
             x="mnth", 
             y="cnt", 
             hue="yr", 
             palette=["#000000", "#FF0000"], 
             marker="o")

for index, row in average_counts1.iterrows():
    plt.axhline(y=row['avg_cnt'], color='black' if row['yr'] == 2011 else 'red', linestyle='--', label=f'Rata-rata di tahun {int(row["yr"])}')

total_legend_labels = []
for index, row in total_counts.iterrows():
    total_legend_labels.append(f"Jumlah penyewa di Tahun {row['yr']}: {row['cnt']}")

# Menampilkan legend jumlah total dengan latar belakang
plt.text(0.02, 0.95, "\n".join(total_legend_labels), 
         transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

plt.title("Jumlah total sepeda yang disewakan berdasarkan Bulan dan tahun")
plt.xlabel('Bulan')
plt.ylabel('Jumlah penyewa sepeda')
plt.xticks(rotation=45)
plt.grid(True)  # Menambahkan grid untuk membantu visualisasi
plt.legend(title="Tahun", loc="upper right")
plt.tight_layout()
st.pyplot(plt)



st.write("### Jumlah total sepeda yang disewakan dari kategori casual dan registered")
# Menghitung jumlah total berdasarkan bulan dan tahun
monthly_counts = day.groupby(by=["mnth", "yr"]).agg({"casual": "sum", "registered": "sum"}).reset_index()

# Menghitung jumlah total berdasarkan tahun
total_counts = monthly_counts.groupby('yr')[['casual', 'registered']].sum().reset_index()

# Membuat grafik garis
plt.figure(figsize=(10, 4))

# Menggambar garis untuk penyewa kategori casual tahun 2011 dan 2012
sns.lineplot(data=monthly_counts[monthly_counts['yr'] == 2011], 
             x="mnth", 
             y="casual", 
             label="Casual 2011", 
             color='blue',
             marker="o")

sns.lineplot(data=monthly_counts[monthly_counts['yr'] == 2012], 
             x="mnth", 
             y="casual", 
             label="Casual 2012", 
             color='orange', 
             marker="o")

# Menggambar garis untuk penyewa registered tahun 2011 dan 2012
sns.lineplot(data=monthly_counts[monthly_counts['yr'] == 2011], 
             x="mnth", 
             y="registered", 
             label="Registered 2011", 
             color='red',
             marker="o")

sns.lineplot(data=monthly_counts[monthly_counts['yr'] == 2012], 
             x="mnth", 
             y="registered", 
             label="Registered 2012", 
             color='green',
             marker="o")

# Menampilkan legend untuk garis di sudut kanan atas
plt.legend(title="Tipe Penyewa", loc="upper right")

total_legend_labels = []
for index, row in total_counts.iterrows():
    total_legend_labels.append(f"Total Casual {row['yr']}: {row['casual']}")
    total_legend_labels.append(f"Total Registered {row['yr']}: {row['registered']}")
    if index == 0:  # Menambahkan spasi setelah tahun 2011
        total_legend_labels.append("")  # Menambahkan baris kosong

# Menampilkan legend jumlah total dengan latar belakang
plt.text(0.02, 0.95, "\n".join(total_legend_labels), 
         transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

plt.title("Jumlah total sepeda yang disewakan dari kategori casual dan registered")
plt.xlabel('Bulan')
plt.ylabel('Jumlah penyewa Sepeda')
plt.xticks(rotation=45)
plt.grid(True)  # Menambahkan grid untuk membantu visualisasi
plt.tight_layout()
st.pyplot(plt)


st.write("### Heatmap Korelasi antara Temp, Atemp, Windspeed, dan Cnt")
# Membuat heatmap
correlation_matrix = day[['temp', 'atemp', 'windspeed', 'cnt']].corr()
plt.figure(figsize=(5, 3))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Heatmap Korelasi antara Temp, Atemp, Windspeed, dan Cnt')
st.pyplot(plt)
