import streamlit as st
import pandas as pd
import random

# 1. 페이지 설정
st.set_page_config(page_title="나트랑 서바이벌 톡", page_icon="🌴")

# 2. 데이터 로드 함수
@st.cache_data
def load_data():
    # 저장해둔 sentences.txt 파일을 읽어옵니다. 
    # 데이터는 '상황|유형|상황설명|영어문장|영어발음|영어해석' 형식을 가정합니다.
    try:
        df = pd.read_csv('sentences.txt', sep='|')
        return df
    except FileNotFoundError:
        st.error("sentences.txt 파일을 찾을 수 없습니다.")
        return None

df = load_data()

# 3. 사이드바 - 상황 선택
st.sidebar.title("🌴 나트랑 여행 영어")
category = st.sidebar.selectbox("상황을 선택하세요", df['상황'].unique() if df is not None else [])
mode = st.sidebar.radio("모드 선택", ["학습 모드", "전체 보기", "현지 보여주기"])

st.title(f"📍 {category}")

if df is not None:
    filtered_df = df[df['상황'] == category]

    # --- 모드 1: 학습 모드 (퀴즈) ---
    if mode == "학습 모드":
        st.subheader("3초 타임어택 학습")
        
        if 'current_idx' not in st.session_state:
            st.session_state.current_idx = random.randint(0, len(filtered_df) - 1)
            st.session_state.show_answer = False

        row = filtered_df.iloc[st.session_state.current_idx]

        with st.container():
            st.info(f"**상황:** {row['상황설명']}")
            st.write(f"**유형:** {row['유형']}")
            
            if st.button("정답 확인"):
                st.session_state.show_answer = True

            if st.session_state.show_answer:
                st.success(f"🗣️ {row['영어문장']}")
                st.caption(f"발음: {row['영어발음']}")
                st.write(f"해석: {row['영어해석(일상적인해석)']}")
                
                if st.button("다음 문장"):
                    st.session_state.current_idx = random.randint(0, len(filtered_df) - 1)
                    st.session_state.show_answer = False
                    st.rerun()

    # --- 모드 2: 전체 보기 ---
    elif mode == "전체 보기":
        for _, row in filtered_df.iterrows():
            with st.expander(f"{row['영어해석(일상적인해석)']} ({row['유형']})"):
                st.write(f"**{row['영어문장']}**")
                st.write(f"발음: {row['영어발음']}")
                st.caption(f"설명: {row['상황설명']}")

    # --- 모드 3: 현지 보여주기 (큰 글씨) ---
    elif mode == "현지 보여주기":
        st.warning("말이 안 통할 때 현지인에게 화면을 보여주세요.")
        selected_msg = st.selectbox("전달할 내용을 선택하세요", filtered_df['영어해석(일상적인해석)'].tolist())
        msg_row = filtered_df[filtered_df['영어해석(일상적인해석)'] == selected_msg].iloc[0]
        
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
            <h1 style="color: #0e1117; font-size: 50px;">{msg_row['영어문장']}</h1>
            <p style="font-size: 20px;">{msg_row['영어해석(일상적인해석)']}</p>
        </div>
        """, unsafe_allow_html=True)

# 하단 푸터
st.sidebar.write("---")
st.sidebar.caption("5세 아이와 함께하는 나트랑 서바이벌 영어")