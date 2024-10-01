import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Fungsi untuk menghapus outlier menggunakan IQR
def remove_outliers_iqr(df, column):
    while True:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Deteksi outlier
        initial_size = df.shape[0]
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        final_size = df.shape[0]
        
        # Jika tidak ada lagi data yang dihapus, hentikan loop
        if initial_size == final_size:
            break
    return df

day_df = pd.read_csv("main_data.csv")

# Menghapus outlier untuk kolom 'hum', 'windspeed', dan 'casual'
day_df_clean = remove_outliers_iqr(day_df, 'hum')
day_df_clean = remove_outliers_iqr(day_df_clean, 'windspeed')
day_df_clean = remove_outliers_iqr(day_df_clean, 'casual')

# Sidebar untuk memilih analisis
st.sidebar.header('Navigation')
option = st.sidebar.selectbox('Pilih Kategori Analisis', 
                              ['Ringkasan', 'Working Day vs Weekend', 
                               'Sewa Sepeda dalam Seminggu', 'Pengaruh Kecepatan Angin',
                               'Total Maksimum', 'Sewa Sepeda Perbulan'])

# Visualisasi dan Analisis sesuai dengan pilihan sidebar
if option == 'Ringkasan':
    st.subheader("Ringkasan Data")
    st.write(day_df_clean.describe())

elif option == 'Working Day vs Weekend':
    st.subheader("Working Day vs Weekend Bike Rentals")
    
    total_sewa_workingday = day_df_clean.groupby(by='workingday')['cnt'].sum()
    hari = ['Weekend', 'Working Day']

    fig, ax = plt.subplots()
    ax.bar(hari, total_sewa_workingday)
    ax.set_title('Perbandingan Sewa Sepeda Working Day dan Weekend')
    ax.set_ylabel('Total Sewa Sepeda')
    ax.set_xlabel('Jenis Hari')

    st.pyplot(fig)

elif option == 'Sewa Sepeda dalam Seminggu':
    st.subheader("Sewa Sepeda dalam Seminggu")

    total_sewa_weekday = day_df_clean.groupby(by='weekday')['cnt'].sum()
    hari = ('Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu')
    nilai = total_sewa_weekday.values
    colors = ('red', 'yellow', '#6495ED', 'pink', '#BDB76B', 'green', 'orange')

    fig, ax = plt.subplots()
    ax.pie(nilai, labels=hari, autopct='%1.1f%%', colors=colors)
    ax.set_title('Persentase Jumlah Sewa Setiap Hari dalam Seminggu')

    st.pyplot(fig)

elif option == 'Pengaruh Kecepatan Angin':
    st.subheader("Pengaruh Kecepatan Angin Terhadap Penyewaan Sepeda")

    total_sewa = day_df_clean["cnt"]
    angin = day_df_clean["windspeed"]

    fig, ax = plt.subplots()
    ax.scatter(angin, total_sewa)
    sns.regplot(x=angin, y=total_sewa, scatter=False, color="red", ax=ax)
    ax.set_xlabel('Kecepatan Angin')
    ax.set_ylabel('Total Sewa Sepeda')
    
    st.pyplot(fig)

elif option == 'Total Maksimum':
    st.subheader("Total Maksimum Penyewaan Sepeda")

    max_cnt_row = day_df_clean.loc[day_df_clean['cnt'].idxmax()]
    tabel_max = pd.DataFrame({
        'Tanggal': [max_cnt_row['dteday']],
        'Registered User': [max_cnt_row['registered']],
        'Casual User': [max_cnt_row['casual']],
        'Total sepeda disewa': [max_cnt_row['cnt']],     
    })

    st.table(tabel_max)

elif option == 'Sewa Sepeda Perbulan':
    st.subheader("Sewa Sepeda Perbulan dalam 2 Tahun")

    day_df_clean['dteday'] = pd.to_datetime(day_df_clean['dteday'])
    monthly_df = day_df_clean.resample(rule='M', on='dteday').agg({"cnt": "sum"})
    monthly_df.index = monthly_df.index.strftime('%Y-%m')
    monthly_df = monthly_df.reset_index()
    monthly_df.rename(columns={"cnt": "Total Sewa", "dteday": "Bulan"}, inplace=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=monthly_df, x='Bulan', y='Total Sewa', marker='o', ax=ax)
    ax.set_title('Total Penyewaan Sepeda per Bulan')
    ax.set_xlabel('Bulan')
    ax.set_ylabel('Total Sewa')
    ax.set_xticks(range(len(monthly_df['Bulan'])))
    ax.set_xticklabels(monthly_df['Bulan'], rotation=45)

    st.pyplot(fig)

