import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

#Fun Pertanyaan 1
def topProducts(df):
    total = df.groupby("product_id")["price"].sum().sort_values(ascending=False).reset_index()
    return total

#Fun Pertanyaan 2
def deliveryStatus(row):
    if row['order_delivered_customer_date'] < row['order_estimated_delivery_date']:
        return 'Lebih Cepat'
    elif row['order_delivered_customer_date'] == row['order_estimated_delivery_date']:
        return 'Tepat Waktu'
    else:
        return 'Terlambat'

def create_deliveryStatus(df):
    df['delivery_status'] = df.apply(deliveryStatus, axis=1)
    status_total = df.groupby('delivery_status')['order_id'].count().reset_index()
    return status_total

#Fun Pertanyaan 3
def freqLocation(df):
    topLoc = df['customer_city'].value_counts().sort_values(ascending=False).reset_index()
    topLoc.columns = ['Kota', 'Jumlah Transaksi']
    return topLoc

#Fun RFM
def create_rfm(df):
    df = df.copy()

    df["total_price"] = df["price"]
    df["order_date"] = pd.to_datetime(df["order_purchase_timestamp"], errors='coerce')

    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_date": "max",
        "order_id": "nunique",
        "total_price": "sum"
    })

    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # hitung recency
    recent_date = df["order_date"].max()
    rfm_df["recency"] = (recent_date - rfm_df["max_order_timestamp"]).dt.days

    # rapikan
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    rfm_df["customer_id"] = rfm_df["customer_id"].str[:8] + "..."

    return rfm_df
    
#Load Data
items_df = pd.read_csv("new_items_df.csv")
orders_df = pd.read_csv("new_orders_df.csv")
customers_df = pd.read_csv("new_customers_df.csv")

orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
orders_df['order_delivered_customer_date'] = pd.to_datetime(orders_df['order_delivered_customer_date'])
orders_df['order_estimated_delivery_date'] = pd.to_datetime(orders_df['order_estimated_delivery_date'])

all_df = pd.merge(orders_df, items_df, on="order_id")

#Sidebar
min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7a/Manchester_United_FC_crest.svg/960px-Manchester_United_FC_crest.svg.png")

    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# filter data
main_df = all_df[
    (all_df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) &
    (all_df['order_purchase_timestamp'] <= pd.to_datetime(end_date))
]
main_df = pd.merge(main_df, customers_df, on="customer_id")

#Jalankan fungsi
showProducts = topProducts(main_df)
showProducts["product_id"] = showProducts["product_id"].str[:8] + "..."
shipping_df = create_deliveryStatus(main_df)
showLocation = freqLocation(main_df)
rfm_df = create_rfm(main_df)

#Tampilan Dashboard
st.header('Dashboard')

#Pertanyaan 1
st.subheader("Produk dengan Pendapatan Terbesar")
fig, ax = plt.subplots(figsize=(12,6))
sns.barplot(
    x="product_id",
    y="price",
    data=showProducts.head(5),
    ax=ax
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
st.pyplot(fig)

#Pertanyaan 2
st.subheader("Delivery Status")
fig, ax = plt.subplots(figsize=(12,6))
sns.barplot(
    x="delivery_status",
    y="order_id",
    data=shipping_df,
    ax=ax
)
st.pyplot(fig)

#Pertanyaan 3
st.subheader("Lokasi pelanggan dengan frekuensi tertinggi")
fig, ax = plt.subplots(figsize=(12,6))
sns.barplot(
    x="Kota",
    y="Jumlah Transaksi",
    data=showLocation.head(5),
    ax=ax
)
st.pyplot(fig)

#RFM
st.subheader("Best Customer Based on RFM")

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30,6))

# Recency
sns.barplot(
    y="recency",
    x="customer_id",
    data=rfm_df.sort_values(by="recency", ascending=False).head(5),
    ax=ax[0]
)
ax[0].set_title("By Recency (days)")
ax[0].tick_params(axis='x', rotation=45)

# Frequency
sns.barplot(
    y="frequency",
    x="customer_id",
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
    ax=ax[1]
)
ax[1].set_title("By Frequency")
ax[1].tick_params(axis='x', rotation=45)

# Monetary
sns.barplot(
    y="monetary",
    x="customer_id",
    data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
    ax=ax[2]
)
ax[2].set_title("By Monetary")
ax[2].tick_params(axis='x', rotation=45)

st.pyplot(fig)