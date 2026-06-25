
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "core"))
from rag_engine import engine

st.set_page_config(page_title="사내 지식 베이스 챗봇", page_icon="🤖")

st.title("🏢 사내 지식 베이스 챗봇")
st.markdown("사내 매뉴얼과 문서를 기반으로 정확한 답변을 제공합니다.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("질문을 입력하세요 (예: 휴가 규정이 어떻게 되나요?)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("사내 문서를 검색 중입니다..."):
            # RAG 엔진 호출
            response = engine.query(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
