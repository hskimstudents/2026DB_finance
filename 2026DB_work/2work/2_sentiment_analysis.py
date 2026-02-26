import pandas as pd

def run_absa_analysis():
    # 1. 수집한 데이터 불러오기
    try:
        df = pd.read_csv("C:\\Users\\qazyo\\Desktop\\workspace_DB\\2026DB_work\\google_news_30days_0225.csv")
        print("✅ 수집된 뉴스 데이터를 불러왔습니다.")
    except FileNotFoundError:
        print("❌ 'naver_news_simple.csv' 파일이 없습니다. 먼저 수집 코드를 실행해주세요.")
        return

    # 2. 산공과 프로젝트용 ABSA 사전 정의 (잘린 단어도 매칭되도록 어근 위주)
    aspect_map = {
        'Tech': [
            # 메모리/공정/기술
            'HBM', 'HBM3', 'HBM3E', 'D램', 'DRAM', '낸드', 'NAND', 
            '미세공정', '3나노', '2나노', '공정', '수율', '양산', '라인',
            '패키징', 'TSV', '파운드리', '파운드리사업', 
            # AI/서버/고부가
            'AI', 'AI서버', '가속기', 'GPU', '데이터센터', '클라우드',
            # 공학/산공 느낌
            '시뮬레이션', '모델링', '최적화', 'P5', '제빙'
        ],

        'Market': [
            # 가격/지수/목표가
            '목표가', '목표주가', '상향조정', '하향조정',
            '최고가', '신고가', '저가', '돌파', '탈환',
            '6000', '7000', '8000', '코스피', '코스닥', '시총',
            # 수급/투자의견/뷰
            '매수', '매도', '비중확대', '비중축소', '중립',
            '강세', '약세', '랠리', '숨고르기', '조정',
            '순매수', '순매도', '외국인', '기관', '개인',
            # 주주환원/배당
            '배당', '자사주', '소각', '주주환원', '배당성향'
        ],

        'Risk': [
            # 법적/규제 리스크
            '노사', '파업', '갈등', '임단협',
            '준감위', '금감원', '규제', '제재', '조사', '압수수색',
            '유출', '기밀', '보안사고', '해킹',
            '유죄', '무죄', '재판', '상고', '파기환송',
            # 경영/산업 리스크
            '긴장', '불확실', '부담', '열세',
            '리스크', '위험', '경고', '주의보',
            '감산', '감원', '구조조정', '적자', '적자전환',
            '수요둔화', '침체', '역성장'
        ]
    }

    pos_words = [
        # 실적/펀더멘털 긍정
        '호실적', '깜짝실적', '어닝서프라이즈', '개선', '반등', '회복',
        '호조', '모멘텀', '확대', '상승세', '강세', '견조',

        # 주가/평가 긍정
        '상향', '상향조정', '돌파', '탈환', '신고가', '최고가', '강세장',
        '급등', '랠리', '강세', '견인', '호평', '긍정적', '우호적',

        # 지위/경쟁력
        '1위', '선도', '우위', '경쟁력', '압도', '지배력', '확보', '성공'
    ]

    neg_words = [
        # 실적/펀더멘털 부정
        '부진', '악화', '둔화', '감소', '감익', '감소세', '축소',
        '어닝쇼크', '쇼크', '실망', '실망스러운',

        # 주가/시장 부정
        '하락', '급락', '추락', '약세', '약세장', '매도세', '손실',
        '우려', '악재', '부담', '냉각', '침체', '경고',

        # 리스크/사건
        '유출', '갈등', '긴장', '공방', '분쟁',
        '유죄', '패소', '리콜', '사고', '차질', '중단'
    ]
    def get_absa_score(title):
        title = str(title)
        clean_title = title.replace("...", "") # 잘린 부분 제거
        scores = {'Tech_Score': 0, 'Market_Score': 0, 'Risk_Score': 0}
        
        for aspect, keywords in aspect_map.items():
            if any(kw in clean_title for kw in keywords):
                p_score = sum(1 for pw in pos_words if pw in clean_title)
                n_score = sum(1 for nw in neg_words if nw in clean_title)
                
                # 가중치: '속보'나 '사상 첫' 같은 단어는 영향력 1.5배
                multiplier = 1.5 if any(x in clean_title for x in ['사상 첫', '속보', '낙점']) else 1.0
                scores[f'{aspect}_Score'] = (p_score - n_score) * multiplier
                
        return pd.Series(scores)

    # 3. 분석 실행
    print("🚀 기사 제목 분석 및 수치화 진행 중...")
    analysis_df = df['기사 제목'].apply(get_absa_score)
    final_df = pd.concat([df, analysis_df], axis=1)

    # 4. 날짜별 평균 점수 산출 (LSTM 입력용 X값)
    daily_data = final_df.groupby('날짜').agg({
        'Tech_Score': 'mean',
        'Market_Score': 'mean',
        'Risk_Score': 'mean'
    }).reset_index()

    # 5. 결과 저장
    final_df.to_csv("C:\\Users\\qazyo\\Desktop\\workspace_DB\\2026DB_work\\samsung_absa_detail.csv", index=False, encoding='utf-8-sig')
    daily_data.to_csv("C:\\Users\\qazyo\\Desktop\\workspace_DB\\2026DB_work\\daily_input_for_lstm.csv", index=False, encoding='utf-8-sig')

    print("\n" + "="*40)
    print("🎉 분석 완료!")
    print(f"1. 상세 분석 결과: samsung_absa_detail.csv")
    print(f"2. LSTM 입력용 파일: daily_input_for_lstm.csv")
    print("="*40)
    print(daily_data.head())

if __name__ == "__main__":
    run_absa_analysis()