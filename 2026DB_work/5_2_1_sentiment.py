import pandas as pd
import glob
import os

def run_absa_analysis():
    # 1. RSS로 수집한 최신 파일 자동 찾기
    # 2026DB_finance\2026DB_work\google_news_latest_120days_0226.csv
    try:
        df = pd.read_csv("C:\\Users\\qazyo\\Desktop\\workspace_DB\\2026DB_finance\\2026DB_work\\google_news_latest_120days_0226.csv")
        print("✅ 수집된 뉴스 데이터를 불러왔습니다.")
    except FileNotFoundError:
        print("❌  파일이 없습니다. 먼저 수집 코드를 실행해주세요.")
        return

    # 2. 통합 Aspect Map (기술/시장/리스크 보강)
    aspect_map = {
        'Tech': [
            'HBM', 'HBM3', 'HBM3E', 'HBM4', 'D램', 'DRAM', '낸드', 'NAND', 
            '미세공정', '3나노', '2나노', '공정', '수율', '양산', '라인',
            '패키징', 'TSV', '파운드리', '파운드리사업', '하이브리드 본딩',
            'AI', 'AI서버', '가속기', 'GPU', '데이터센터', '클라우드', 'NPU',
            '시뮬레이션', '모델링', '최적화', 'P5', '제빙', '반도체연구소', '기술기획'
        ],
        'Market': [
            '목표가', '목표주가', '상향조정', '하향조정', '전망',
            '최고가', '신고가', '저가', '돌파', '탈환', '반등',
            '6000', '7000', '8000', '코스피', '코스닥', '시총',
            '매수', '매도', '비중확대', '비중축소', '중립', '수혜',
            '강세', '약세', '랠리', '숨고르기', '조정', '수주', '납품',
            '순매수', '순매도', '외국인', '기관', '개인', '엔비디아', 'AMD',
            '배당', '자사주', '소각', '주주환원', '배당성향'
        ],
        'Risk': [
            '노사', '파업', '갈등', '임단협', '임금협상',
            '준감위', '금감원', '규제', '제재', '조사', '압수수색',
            '유출', '기밀', '보안사고', '해킹', '산업스파이',
            '유죄', '무죄', '재판', '상고', '파기환송', '표창', '유공',
            '긴장', '불확실', '부담', '열세', '밀렸다', '격차',
            '리스크', '위험', '경고', '주의보', '비상경영',
            '감산', '감원', '구조조정', '적자', '적자전환',
            '수요둔화', '침체', '역성장', '공급과잉'
        ]
    }

    # 긍정 단어 보강
    pos_words = [
        '호실적', '깜짝실적', '어닝서프라이즈', '개선', '반등', '회복',
        '호조', '모멘텀', '확대', '상승세', '강세', '견조', '수혜',
        '상향', '상향조정', '돌파', '탈환', '신고가', '최고가', '강세장',
        '급등', '랠리', '호평', '긍정적', '우호적', '웃는다', '훈풍',
        '1위', '선도', '우위', '경쟁력', '압도', '지배력', '확보', '성공',
        '최초', '독점', '양산 개시', '채택', '낙점', '초격차'
    ]

    # 부정 단어 보강
    neg_words = [
        '부진', '악화', '둔화', '감소', '감익', '감소세', '축소',
        '어닝쇼크', '쇼크', '실망', '실망스러운', '하회', '정체',
        '하락', '급락', '추락', '약세', '약세장', '매도세', '손실',
        '우려', '악재', '부담', '냉각', '침체', '경고', '불안',
        '유출', '갈등', '긴장', '공방', '분쟁', '이탈', '밀렸다',
        '유죄', '패소', '리콜', '사고', '차질', '중단', '위기'
    ]

    def get_absa_score(title):
        title = str(title)
        clean_title = title.replace("[", "").replace("]", "") 
        scores = {'Tech_Score': 0.0, 'Market_Score': 0.0, 'Risk_Score': 0.0}
        
        for aspect, keywords in aspect_map.items():
            # 1. 해당 Aspect 키워드 포함 여부 확인
            if any(kw in clean_title for kw in keywords):
                # 2. 감성 점수 계산
                p_count = sum(1 for pw in pos_words if pw in clean_title)
                n_count = sum(1 for nw in neg_words if nw in clean_title)
                sentiment_net = p_count - n_count
                
                # 3. [개선된 로직] 키워드만 있어도 기본점수 부여하여 0점 방지
                if sentiment_net > 0:
                    final_score = sentiment_net
                elif sentiment_net < 0:
                    final_score = sentiment_net
                else:
                    # 감성 단어가 없어도 키워드가 있다면 기본값 부여
                    # Risk는 키워드 존재만으로 부정(-0.5), 나머지는 긍정(0.5)
                    final_score = -0.5 if aspect == 'Risk' else 0.5
                
                # 4. 가중치 적용 (중요 키워드 포함 시 영향력 증폭)
                multiplier = 1.5 if any(x in clean_title for x in ['사상 첫', '속보', '단독', '양산', '초격차']) else 1.0
                scores[f'{aspect}_Score'] = float(final_score * multiplier)
                
        return pd.Series(scores)

    # 3. 분석 실행
    print("🚀 기사 제목 분석 및 수치화 진행 중...")
    analysis_df = df['기사 제목'].apply(get_absa_score)
    final_df = pd.concat([df, analysis_df], axis=1)

    # 4. 날짜별 평균 점수 산출
    daily_data = final_df.groupby('날짜').agg({
        'Tech_Score': 'mean',
        'Market_Score': 'mean',
        'Risk_Score': 'mean'
    }).reset_index()

    # 5. 결과 저장
    final_df.to_csv("C:\\Users\\qazyo\\Desktop\\workspace_DB\\2026DB_finance\\2026DB_work\\5_samsung_absa_detail.csv", index=False, encoding='utf-8-sig')
    daily_data.to_csv("C:\\Users\\qazyo\\Desktop\\workspace_DB\\2026DB_finance\\2026DB_work\\5_daily_input_for_lstm.csv", index=False, encoding='utf-8-sig')

    print("\n" + "="*40)
    print("🎉 분석 및 보정 완료!")
    print(f"1. 상세 분석 결과: samsung_absa_detail.csv")
    print(f"2. LSTM 입력용 파일: daily_input_for_lstm.csv")
    print("="*40)
    print(daily_data)

if __name__ == "__main__":
    run_absa_analysis()