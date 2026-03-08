import pandas as pd
import plotly.graph_objects as go

# ===== 1️⃣ 讀取 Excel =====
file_path = './plot_1.xlsx'
df = pd.read_excel(file_path)

# ===== 2️⃣ 確保日期是 datetime 格式 =====
df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])

# ===== 3️⃣ 處理小於0.1的值 =====
df_processed = df.copy()

# 對每個數值欄位做處理
for col in df_processed.columns[1:]:
    df_processed[col] = df_processed[col].apply(lambda x: x if x >= 0.1 else None)

# ===== 4️⃣ 建立圖表 =====
fig = go.Figure()
for col in df_processed.columns[2:]:
    fig.add_trace(go.Scatter(
        x=df_processed.iloc[:, 0],
        y=df_processed[col],
        mode='lines',
        name=col,
        connectgaps=True
    ))

fig.update_layout(
    title="Multiple Columns Log Y Axis",
    xaxis_title="Date",
    yaxis_title="Value",
    yaxis_type="log",
    hovermode="x unified",
    template="plotly_white"
)

fig.show()