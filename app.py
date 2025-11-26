import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="친환경 소비 분석 대시보드", layout="wide")

def load_and_analyze_data(df):
    """
    업로드된 엑셀의 DataFrame을 받아 친환경 소비 분석 대시보드를 출력
    """

    # --- 1. 상수 정의 ---

    GREEN_KEYWORDS = [
        '리필', 'refill', '재활용', '업사이클', '대나무', '천연수세미',
        '제로웨이스트', '친환경', '에코백', '고체비누', '소프넛',
        '스테인리스 빨대', '다회용', '용기내'
    ]

    CO2_SAVINGS_MAP = {
        '리필': 0.2, 'refill': 0.2, '용기내': 0.2,
        '재활용': 0.1, '업사이클': 0.15,
        '고체비누': 0.15, '소프넛': 0.1,
        '천연수세미': 0.05, '대나무': 0.05,
        '에코백': 0.5, '스테인리스 빨대': 0.05
    }

    BASE_EMISSION_MAP = {
        '리필': 0.7, 'refill': 0.7, '용기내': 0.7,
        '재활용': 0.4, '업사이클': 0.4,
        '고체비누': 0.7, '소프넛': 0.7,
        '천연수세미': 0.15, '대나무': 0.1,
        '에코백': 0.5, '스테인리스 빨대': 0.05
    }
    DEFAULT_BASE_EMISSION = 0.4

    ITEM_COLUMN = '구매 품목'
    COST_COLUMN = '금액'
    QUANTITY_COLUMN = '수량'
    CO2_EMISSION_COLUMN = '탄소 배출량(kg)'

    # --- 2. 전처리 ---

    df[COST_COLUMN] = df[COST_COLUMN].astype(str).str.replace(r'[^\d.]', '', regex=True).replace('', 0).astype(float)
    df[ITEM_COLUMN] = df[ITEM_COLUMN].fillna('').astype(str).str.lower()

    # 수량이 없으면 1로 처리
    if QUANTITY_COLUMN not in df.columns:
        df[QUANTITY_COLUMN] = 1
        st.warning(f"'{QUANTITY_COLUMN}' 컬럼이 없어 수량을 1로 가정합니다.")
    else:
        df[QUANTITY_COLUMN] = df[QUANTITY_COLUMN].astype(str).str.replace(r'[^\d]', '', regex=True).replace('', 0).astype(int)

    # 친환경 여부 판단
    df['친환경 여부'] = False
    for keyword in GREEN_KEYWORDS:
        df.loc[df[ITEM_COLUMN].str.contains(keyword), '친환경 여부'] = True

    # --- 3. CO2 계산 ---
    df['CO2_절감량(kg)'] = 0.0
    for keyword, savings in CO2_SAVINGS_MAP.items():
        df.loc[df[ITEM_COLUMN].str.contains(keyword) & (df['친환경 여부']), 'CO2_절감량(kg)'] = df[QUANTITY_COLUMN] * savings

    total_co2_savings = df['CO2_절감량(kg)'].sum()

    # CO2 배출량 계산
    if CO2_EMISSION_COLUMN in df.columns:
        df[CO2_EMISSION_COLUMN] = df[CO2_EMISSION_COLUMN].astype(str).str.replace(r'[^\d.]', '', regex=True).replace('', 0).astype(float)

        total_actual_co2 = df[CO2_EMISSION_COLUMN].sum()
        total_conventional_co2 = total_actual_co2 + total_co2_savings
        co2_method = "실제 배출량 사용"

    else:
        st.warning(f"'{CO2_EMISSION_COLUMN}' 컬럼이 없어 CO₂ 배출량을 추정합니다.")
        df['CO2_기준배출량(kg)'] = df[QUANTITY_COLUMN] * DEFAULT_BASE_EMISSION
        for keyword, emission in BASE_EMISSION_MAP.items():
            df.loc[df[ITEM_COLUMN].str.contains(keyword), 'CO2_기준배출량(kg)'] = df[QUANTITY_COLUMN] * emission

        total_conventional_co2 = df['CO2_기준배출량(kg)'].sum()
        total_actual_co2 = total_conventional_co2 - total_co2_savings
        co2_method = "추정치 기반 계산"

    # --- 4. 금액 계산 ---
    total_cost = df[COST_COLUMN].sum()
    eco_cost = df.loc[df['친환경 여부'], COST_COLUMN].sum()
    eco_ratio = (eco_cost / total_cost * 100) if total_cost > 0 else 0

    # --- 5. 결과 출력 ---
    st.header("🌿 제로 웨이스트 소비 분석 대시보드")

    st.subheader("💰 소비 금액 분석")
    st.write(f"**총 소비 금액:** {total_cost:,.0f} 원")
    st.write(f"**친환경 소비 금액:** {eco_cost:,.0f} 원")
    st.write(f"**친환경 소비 비율:** {eco_ratio:.1f}%")

    st.markdown("---")

    st.subheader("🌲 환경 기여 지표")
    st.write(f"**CO₂ 계산 방식:** {co2_method}")
    st.write(f"**총 CO₂ 기준 배출량:** {total_conventional_co2:.2f} kg")
    st.write(f"**총 CO₂ 실제 배출량:** {total_actual_co2:.2f} kg")
    st.write(f"**총 CO₂ 절감량:** {total_co2_savings:.2f} kg")

    if total_co2_savings > 0:
        st.info(f"🚗 승용차 약 **{total_co2_savings / 0.17:.0f} km** 주행 절감 효과")

    st.markdown("---")

    st.subheader("♻ 친환경 제품 목록 (최대 10개)")
    eco_items = df[df['친환경 여부']][ITEM_COLUMN].unique()
    if len(eco_items) > 0:
        for item in eco_items[:10]:
            st.write(f"- {item}")
    else:
        st.write("등록된 친환경 품목이 없습니다.")

    return df


# 📌 --- Streamlit UI --- #

st.title("📊 친환경 소비 데이터 분석기 (Streamlit 버전)")

uploaded_file = st.file_uploader("엑셀 파일 업로드", type=['xlsx'])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = st.selectbox("시트 선택", xls.sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

    st.success(f"'{sheet_name}' 시트를 불러왔습니다.")

    if st.button("분석 시작하기 🚀"):
    if uploaded_file is not None:
        st.success("📊 분석을 시작합니다!")
        load_and_analyze_data(uploaded_file)
    else:
        st.warning("엑셀 파일을 먼저 업로드해주세요.")


