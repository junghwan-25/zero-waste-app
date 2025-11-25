import streamlit as st
import pandas as pd
import os

# -------------------------
# 파일 업로드 UI
# -------------------------
st.title("🌿 제로웨이스트 소비 분석 앱")
st.write("엑셀 파일을 업로드하면 CO₂ 절감량과 친환경 소비 정보를 분석해드립니다!")

uploaded_file = st.file_uploader("📁 소비내역 엑셀 파일 업로드 (.xlsx)", type=["xlsx"])
sheet_name = st.text_input("📄 시트 이름 입력 (예: 1월)", value="1월")

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        st.success("엑셀 파일 불러오기 성공!")
        st.dataframe(df)

        # -------------------------
        # 분석 준비
        # -------------------------
        ITEM_COLUMN = "항목"
        ECO_COLUMN = "친환경 여부"
        CO2_COLUMN = "CO2 배출량(kg)"

        if ITEM_COLUMN not in df.columns or ECO_COLUMN not in df.columns or CO2_COLUMN not in df.columns:
            st.error("엑셀 파일에 필요한 컬럼(항목, 친환경 여부, CO2 배출량)이 없습니다.")
        else:
            # 전체 CO2
            total_actual_co2 = df[CO2_COLUMN].sum()

            # 친환경 제품 CO2
            eco_df = df[df[ECO_COLUMN] == True]
            eco_co2 = eco_df[CO2_COLUMN].sum()

            # 친환경 제품이 아니었을 경우 가정 (2배 계산 예시)
            total_conventional_co2 = eco_co2 * 2 + (total_actual_co2 - eco_co2)

            total_savings = total_conventional_co2 - total_actual_co2

            # -------------------------
            # 출력
            # -------------------------
            st.subheader("📊 환경 기여 분석 결과")
            st.write(f"✔️ 실제 CO2 배출량: **{total_actual_co2:.2f} kg**")
            st.write(f"✔️ 일반 제품 사용 시 가정 CO2: **{total_conventional_co2:.2f} kg**")
            st.write(f"🌍 CO2 절감량: **{total_savings:.2f} kg**")

            st.divider()

            st.subheader("🌱 친환경 소비한 항목")
            if len(eco_df) > 0:
                st.write(eco_df[ITEM_COLUMN].unique())
            else:
                st.write("친환경 소비 항목이 없습니다.")

    except Exception as e:
        st.error(f"파일 불러오기 오류: {e}")
else:
    st.info("엑셀 파일을 업로드해주세요!")
