import random
import time

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# =========================
# 0. 재현성 확보를 위한 시드 고정
# =========================
SEED = 42
np.random.seed(SEED)
tf.random.set_seed(SEED)
random.seed(SEED)

# =========================
# 1. 데이터 로드 & 기본 전처리
# =========================

DATA_PATH = r"C:\\Users\\qazyo\\Desktop\\workspace_DB\\2026DB_work\\3_final_lstm_training_data.csv"
df = pd.read_csv(DATA_PATH, encoding="utf-8")

# 날짜 변환 + 정렬
df["날짜"] = pd.to_datetime(df["날짜"])
df = df.sort_values("날짜").reset_index(drop=True)

# 주가변동이 비어있는(첫 날 등) 행 제거
df = df.dropna(subset=["주가변동"]).reset_index(drop=True)

print("데이터 개수:", len(df))

# =========================
# 2. Feature / Target 선택
# =========================

feature_cols = ["Tech_Score", "Market_Score", "Risk_Score", "종가", "거래량"]
target_col = "주가변동"  # 일별 수익률

features = df[feature_cols].values                  # (N, 5)
target = df[target_col].values.reshape(-1, 1)       # (N, 1)

# =========================
# 3. 스케일링 (Train 구간 기준)
# =========================

# Train/Test 나누기 비율 (시퀀스 만들기 전, row 기준)
train_ratio_rows = 0.8
train_size_rows = int(len(df) * train_ratio_rows)

features_train = features[:train_size_rows]
target_train = target[:train_size_rows]

feature_scaler = MinMaxScaler()
target_scaler = MinMaxScaler()

feature_scaler.fit(features_train)
target_scaler.fit(target_train)

features_scaled = feature_scaler.transform(features)
target_scaled = target_scaler.transform(target)

# =========================
# 4. 시계열 윈도우 생성
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
        y.append(target_array[i])                   # 현재 시점의 타깃 (주가변동)
    return np.array(X), np.array(y)

WINDOW_SIZE = 20

X_all, y_all = create_sequences(features_scaled, target_scaled, window_size=WINDOW_SIZE)

print("전체 시퀀스 개수:", len(X_all))

# 시퀀스 기준 Train/Test 분할
train_ratio_seq = 0.8
sequence_train_size = int(train_ratio_seq * len(X_all))

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

start_time = time.time()

history = model.fit(
    X_train, y_train,
    epochs=100,
    batch_size=16,
    validation_split=0.2,   # train의 마지막 20%를 검증용으로 사용 (시계열 유지)
    shuffle=False,          # 시계열이므로 섞지 않음
    callbacks=[early_stop, checkpoint],
    verbose=1
)

train_time = time.time() - start_time
print(f"학습 시간: {train_time:.2f} 초")

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
mape = np.mean(np.abs((y_test_inv - y_pred_inv) / y_test_inv)) * 100
r2 = r2_score(y_test_inv, y_pred_inv)

# 방향성 정확도 (수익률 > 0 을 상승으로 정의)
direction_true = (y_test_inv.flatten() > 0).astype(int)
direction_pred = (y_pred_inv.flatten() > 0).astype(int)
direction_acc = np.mean(direction_true == direction_pred) * 100

print("========== Test 성능 ==========")
print(f"MSE  : {mse:.6f}")
print(f"RMSE : {rmse:.6f}")
print(f"MAE  : {mae:.6f}")
print(f"MAPE : {mape:.2f}%")
print(f"R^2  : {r2:.4f}")
print(f"방향성 정확도 : {direction_acc:.2f}%")

# =========================
# 9. 모델 & 가중치 저장
# =========================

model_save_path = r"C:\\Users\\qazyo\\Desktop\\workspace_DB\\2026DB_work\\lstm_stock_full_model.h5"
model.save(model_save_path)
print(f"전체 모델 저장: {model_save_path}")

# =========================
# 10. 전체 구간 가격 그래프 (Full Period)
# =========================

# 전체 시퀀스에 대해 예측 (Train + Test 모두 포함)
y_all_pred_scaled = model.predict(X_all)
y_all_pred_inv = target_scaler.inverse_transform(y_all_pred_scaled)

pred_returns_full = y_all_pred_inv.flatten()              # 길이: len(X_all)

# 누적수익률 기반으로 예측 종가 복원
# 첫 예측 대상 시점의 직전 가격을 기준으로 시작
prices_full = df["종가"].values
dates_full = df["날짜"].values

start_price_full = prices_full[WINDOW_SIZE - 1]            # P_{t-1}
cum_returns_full = np.cumprod(1 + pred_returns_full)       # (1+r1)*(1+r2)*...
predicted_prices_full = start_price_full * cum_returns_full

# 실제 종가 (예측 가능한 구간만: WINDOW_SIZE 이후)
actual_prices_full = prices_full[WINDOW_SIZE:]             # 길이: len(X_all)
dates_for_plot_full = dates_full[WINDOW_SIZE:]

plt.figure(figsize=(12, 5))
plt.plot(dates_for_plot_full, actual_prices_full, label="Actual Price (종가)", linewidth=2)
plt.plot(dates_for_plot_full, predicted_prices_full,
         label="Predicted Price (Full Period)", linestyle="--")

plt.title("Actual vs Predicted Stock Price (Full Period)")
plt.xlabel("Date")
plt.ylabel("Price")

ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gcf().autofmt_xdate()

plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# =========================
# 11. Test 구간만 확대해서 가격 그래프
# =========================

# 테스트 구간 시작 인덱스 (df 기준)
test_start_idx = WINDOW_SIZE + sequence_train_size

actual_prices_test = df["종가"].values[test_start_idx:]
test_dates = df["날짜"].values[test_start_idx:]

print("actual_prices_test len:", len(actual_prices_test))
print("y_pred_inv len        :", len(y_pred_inv))

# 예측 수익률 (Test 구간)
pred_returns_test = y_pred_inv.flatten()

# 누적수익률 계산
cum_returns_test = np.cumprod(1 + pred_returns_test)

# 테스트 구간 첫 날 실제 종가를 기준으로 예측 종가 복원
start_price_test = actual_prices_test[0]
predicted_prices_test = start_price_test * cum_returns_test

plt.figure(figsize=(12, 5))
plt.plot(test_dates, actual_prices_test, label="Actual Price (Test)", linewidth=2)
plt.plot(test_dates, predicted_prices_test,
         label="Predicted Price (Test From Returns)", linestyle="--")

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