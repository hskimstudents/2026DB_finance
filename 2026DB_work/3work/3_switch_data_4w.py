import yfinance as yf
import pandas as pd

def merge_absa_with_stock():
    # 1. ABSA 분석 결과 불러오기
    try:
        absa_data = pd.read_csv("C:\\Users\\qazyo\\Desktop\\workspace_DB\\2026DB_work\\3_daily_input_for_lstm.csv")
        # 날짜 형식을 주가 데이터와 맞추기 위해 변환
        absa_data['날짜'] = pd.to_datetime(absa_data['날짜']).dt.strftime('%Y-%m-%d')
        print("✅ ABSA 데이터를 불러왔습니다.")
    except:
        print("❌ 'daily_input_for_lstm.csv'가 없습니다.")
        return

    # 2. 삼성전자 주가 데이터 수집 (최근 1개월치)
    print("🚀 삼성전자 주가 데이터를 가져오는 중...")
    samsung = yf.Ticker("005930.KS")
    stock_df = samsung.history(period="4mo")
    stock_df = stock_df.reset_index()
    stock_df['Date'] = stock_df['Date'].dt.strftime('%Y-%m-%d')
    
    # 필요한 컬럼만 추출 (날짜, 종가, 거래량)
    stock_df = stock_df[['Date', 'Close', 'Volume']]
    stock_df.columns = ['날짜', '종가', '거래량']

    # 3. 두 데이터 결합 (Merge)
    # 기사가 있는 날짜에 주가 데이터를 붙입니다.
    final_dataset = pd.merge(absa_data, stock_df, on='날짜', how='inner')

    # 4. 등락률 계산 (LSTM이 학습하기 더 좋은 지표)
    final_dataset['주가변동'] = final_dataset['종가'].pct_change()
    
    # 5. 최종 저장
    final_dataset.to_csv("C:\\Users\\qazyo\\Desktop\\workspace_DB\\2026DB_work\\3_final_lstm_training_data.csv", index=False, encoding='utf-8-sig')
    
    print("\n" + "="*40)
    print("🎉 LSTM 학습용 최종 데이터셋 완성!")
    print(f"저장된 파일: final_lstm_training_data.csv")
    print("="*40)
    print(final_dataset.head())

if __name__ == "__main__":
    # pip install yfinance 필수
    merge_absa_with_stock()