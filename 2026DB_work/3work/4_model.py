import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# =========================
# 1. 데이터 로드 & 기본 전처리
# =========================

# CSV 경로만 본인 환경에 맞게 수정
DATA_PATH = "C:\\Users\\qazyo\\Desktop\\workspace_DB\\2026DB_work\\3_final_lstm_training_data.csv"

# 한글 인코딩 이슈 있을 수 있어서 encoding 옵션도 추가
df = pd.read_csv(DATA_PATH, encoding="utf-8")

# 날짜를 datetime으로 변환 + 정렬
df["날짜"] = pd.to_datetime(df["날짜"])
df = df.sort_values("날짜").reset_index(drop=True)

# 주가변동이 비어있는(첫 날) 행 제거
df = df.dropna(subset=["주가변동"]).reset_index(drop=True)

# =========================
# 2. Feature / Target 선택
# =========================

feature_cols = ["Tech_Score", "Market_Score", "Risk_Score", "종가", "거래량"]
target_col = "주가변동"

features = df[feature_cols].values          # (N, 5)
target = df[target_col].values.reshape(-1, 1)  # (N, 1)

# =========================
# 3. 스케일링 (Train 기준)
# =========================

# Train/Test 나누기 비율
train_ratio = 0.8
train_size = int(len(df) * train_ratio)

# Train 구간 기준으로 스케일러 fit
features_train = features[:train_size]
target_train = target[:train_size]

feature_scaler = MinMaxScaler()
target_scaler = MinMaxScaler()

feature_scaler.fit(features_train)
target_scaler.fit(target_train)

features_scaled = feature_scaler.transform(features)
target_scaled = target_scaler.transform(target)

# =========================
# 4. 시계열 윈도우 생성 함수
# =========================

def create_sequences(feature_array, target_array, window_size=20):
    """
    feature_array: (N, num_features)
    target_array:  (N, 1)
    window_size:   과거 몇 일 데이터를 볼지
    """
    X, y = [], []
    for i in range(window_size, len(feature_array)):
        X.append(feature_array[i - window_size:i])  # 과거 window_size일
        y.append(target_array[i])                   # 현재 시점의 타깃
    return np.array(X), np.array(y)

WINDOW_SIZE = 20

X_all, y_all = create_sequences(features_scaled, target_scaled, window_size=WINDOW_SIZE)

# 시퀀스를 만든 뒤 다시 Train/Test 분할
sequence_train_size = int(train_ratio * len(X_all))

X_train = X_all[:sequence_train_size]
y_train = y_all[:sequence_train_size]

X_test = X_all[sequence_train_size:]
y_test = y_all[sequence_train_size:]

print("X_train shape:", X_train.shape)  # (N_train, window, num_features)
print("y_train shape:", y_train.shape)  # (N_train, 1)
print("X_test shape:", X_test.shape)
print("y_test shape:", y_test.shape)

# =========================
# 5. LSTM 모델 정의
# =========================

num_features = X_train.shape[2]

model = Sequential([
    LSTM(64, input_shape=(WINDOW_SIZE, num_features), return_sequences=False),
    Dropout(0.2),
    Dense(32, activation="relu"),
    Dense(1)  # 타깃: 스케일된 주가변동 (1차원)
])

model.compile(
    loss="mse",
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    metrics=["mae"]
)

model.summary()

# =========================
# 6. 콜백 정의 (조기 종료, 베스트 모델 저장)
# =========================

checkpoint_path = "lstm_stock_best_model.h5"

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=10,
    restore_best_weights=True
)

checkpoint = ModelCheckpoint(
    filepath=checkpoint_path,
    monitor="val_loss",
    save_best_only=True,
    verbose=1
)

# =========================
# 7. 모델 학습
# =========================

history = model.fit(
    X_train, y_train,
    epochs=100,
    batch_size=16,
    validation_split=0.2,
    callbacks=[early_stop, checkpoint],
    verbose=1
)

# =========================
# 8. Test 데이터 성능 평가
# =========================

# 스케일된 값으로 예측
y_pred_scaled = model.predict(X_test)

# 원래 스케일로 역변환 (주가변동 실제 값 단위로)
y_test_inv = target_scaler.inverse_transform(y_test)
y_pred_inv = target_scaler.inverse_transform(y_pred_scaled)

mse = mean_squared_error(y_test_inv, y_pred_inv)
mae = mean_absolute_error(y_test_inv, y_pred_inv)
rmse = np.sqrt(mse)
r2 = r2_score(y_test_inv, y_pred_inv)

print("========== Test 성능 ==========")
print(f"MSE  : {mse:.6f}")
print(f"RMSE : {rmse:.6f}")
print(f"MAE  : {mae:.6f}")
print(f"R^2  : {r2:.4f}")

# =========================
# 9. 모델 & 가중치 저장
# =========================

model.save("C:\\Users\\qazyo\\Desktop\\workspace_DB\\2026DB_work\\lstm_stock_full_model.h5")
print("전체 모델 저장: lstm_stock_full_model.h5")

# =========================
# 10. 테스트 구간 종가 그래프
# =========================

# 시퀀스 만들면서 앞에 WINDOW_SIZE만큼 잘렸으니까
test_start_idx = WINDOW_SIZE + sequence_train_size

# 테스트 구간의 실제 종가 & 날짜
actual_prices = df["종가"].values[test_start_idx:]   # shape: (len(y_test),)
test_dates    = df["날짜"].values[test_start_idx:]

print("actual_prices len:", len(actual_prices))
print("y_pred_inv len   :", len(y_pred_inv))

# 예측 수익률 (역스케일 완료된 상태)
pred_returns = y_pred_inv.flatten()                  # shape: (len(y_test),)

# 누적수익률 계산: (1 + r1) * (1 + r2) * ...
cum_returns = np.cumprod(1 + pred_returns)

# 테스트 구간 첫 날 실제 종가를 기준으로 예측 종가 재구성
start_price = actual_prices[0]
predicted_prices = start_price * cum_returns

# 그래프 그리기
plt.figure(figsize=(12, 5))

plt.plot(test_dates, actual_prices, label="Actual Price (closed price)", linewidth=2)
plt.plot(test_dates, predicted_prices,
         label="Predicted Price (From LSTM Returns)", linestyle="--")

plt.title("Actual vs Predicted Stock Price (Test Period)")
plt.xlabel("Date")
plt.ylabel("Price")

ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gcf().autofmt_xdate()

plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()