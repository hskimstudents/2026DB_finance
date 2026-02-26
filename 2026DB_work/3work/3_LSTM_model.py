import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tensorflow as tf
import random
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_percentage_error

# 1. 재현성을 위한 시드 고정
def set_seeds(seed=42):
    np.random.seed(seed)
    random.seed(seed)
    tf.random.set_seed(seed)
set_seeds(42)

def run_stepwise_model():
    # 2. 데이터 로드
    df = pd.read_csv("3_final_lstm_training_data.csv").dropna()
    df['날짜'] = pd.to_datetime(df['날짜'])
    
    feature_cols = ['Tech_Score', 'Market_Score', 'Risk_Score', '거래량']
    target_col = ['종가']
    
    scaler_x = MinMaxScaler()
    scaler_y = MinMaxScaler()
    
    scaled_x = scaler_x.fit_transform(df[feature_cols])
    scaled_y = scaler_y.fit_transform(df[target_col])
    
    # 3. 윈도우 시퀀스 생성
    window_size = 7
    full_data = np.hstack([scaled_x, scaled_y])
    
    X, y = [], []
    for i in range(len(full_data) - window_size):
        X.append(full_data[i:i+window_size])
        y.append(full_data[i+window_size, -1])
    X, y = np.array(X), np.array(y)
    
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    plot_dates = df['날짜'].iloc[window_size:].values

    # 4. 모델 설계 및 학습
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(100, return_sequences=True, input_shape=(window_size, 5)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(50),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    print("🔄 모델 학습 중... (4대 지표 산출 중)")
    model.fit(X_train, y_train, epochs=100, batch_size=4, verbose=0)

    # 5. 예측 수행
    test_preds = scaler_y.inverse_transform(model.predict(X_test))
    test_actuals = scaler_y.inverse_transform(y_test.reshape(-1, 1))
    
    train_preds = scaler_y.inverse_transform(model.predict(X_train))
    train_actuals = scaler_y.inverse_transform(y_train.reshape(-1, 1))

    # 6. [핵심] 4대 평가지표 계산 (Test 구간 기준)
    # (1) RMSE
    rmse = np.sqrt(mean_squared_error(test_actuals, test_preds))
    
    # (2) MAPE
    mape = mean_absolute_percentage_error(test_actuals, test_preds) * 100
    
    # (3) Accuracy (100 - MAPE)
    accuracy = 100 - mape
    
    # (4) R-Square
    r2 = r2_score(test_actuals, test_preds)

    # --- 그래프 출력 (기존과 동일) ---
    plt.figure(figsize=(10, 5))
    plt.plot(plot_dates[:split], train_actuals, label='Actual (Train)', color='gray', alpha=0.5)
    plt.plot(plot_dates[:split], train_preds, label='Predicted (Fit)', color='orange')
    plt.title('Step 1: Training Period Fit')
    plt.legend()
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.plot(plot_dates[split:], test_actuals, label='Actual Future', color='#1f77b4', linewidth=2)
    plt.plot(plot_dates[split:], test_preds, label='Model Prediction', color='#d62728', linestyle='--')
    plt.title(f'Step 2: Future Evaluation (Accuracy: {accuracy:.2f}%)')
    plt.legend()
    plt.show()

    # 7. 최종 결과 출력 (표 형식)
    print("\n" + "="*50)
    print(f"{'📊 모델 성능 평가 (4대 지표)':^45}")
    print("-" * 50)
    print(f" 1. Accuracy (예측 정확도) : {accuracy:.2f} %")
    print(f" 2. RMSE (평균 가격 오차)  : {rmse:,.0f} 원")
    print(f" 3. MAPE (평균 오차율)     : {mape:.2f} %")
    print(f" 4. R-Square (결정계수)    : {r2:.4f}")
    print("-" * 50)
    
    last_seq = full_data[-window_size:].reshape(1, window_size, 5)
    tomorrow_price = scaler_y.inverse_transform(model.predict(last_seq))
    print(f" 🔮 다음 거래일 예상 종가  : {tomorrow_price[0][0]:,.0f} 원")
    print("="*50)

if __name__ == "__main__":
    run_stepwise_model()