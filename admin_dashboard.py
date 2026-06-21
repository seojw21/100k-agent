
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Admin Dashboard | Knowledge Base", layout="wide")

st.title("📊 관리자 운영 대시보드")
st.subheader("시스템 모니터링 및 데이터 분석")

# 샘플 데이터 (실제 구현 시 DB 연동)
data = {
    "질문": ["휴가 규정", "비품 신청", "복리후생", "재택근무 정책", "연차 계산", "신규 입사자 교육"],
    "빈도": [45, 32, 18, 29, 12, 5],
    "정확도": [0.98, 0.95, 0.92, 0.97, 0.89, 0.95]
}
df = pd.DataFrame(data)

col1, col2 = st.columns(2)

with col1:
    st.write("### 🔍 주요 질문 분석")
    st.bar_chart(df.set_index("질문")["빈도"])
    st.caption("사용자들이 가장 많이 묻는 질문을 파악하여 사내 지식 베이스를 강화하십시오.")

with col2:
    st.write("### ✅ 답변 정확도 현황")
    st.line_chart(df.set_index("질문")["정확도"])
    st.caption("정확도가 낮은 항목은 RAG 파이프라인의 프롬프트나 데이터를 재검토해야 합니다.")

st.divider()
st.write("### 📝 최근 피드백 및 로그")
st.table(df)
