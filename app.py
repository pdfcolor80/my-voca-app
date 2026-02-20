import streamlit as st
import os
import time
import requests

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 페이지 설정
st.set_page_config(page_title="영어 패턴 1000 부수기", page_icon="📖")

# CSS로 UI 깔끔하게 다듬기
st.markdown("""
    <style>
    .stButton>button { width: 100%; }
    .mean-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

def load_sentences():
    if not os.path.exists(DATA_FILE):
        st.error(f"'{DATA_FILE}' 파일이 없습니다.")
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return [line.strip().split("|") for line in f if "|" in line]

def save_progress(index):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        f.write(str(index))

def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return int(content) if content else 0
        except:
            return 0
    return 0

# 데이터 로드
sentences = load_sentences()

# 세션 상태 초기화
if "current_idx" not in st.session_state:
    st.session_state.current_idx = load_progress()
if "count" not in st.session_state:
    st.session_state.count = 0
if "show_english" not in st.session_state:
    st.session_state.show_english = False

# --- 사이드바 ---
with st.sidebar:
    st.title("⚙️ 학습 설정")
    goal = st.number_input("🎯 오늘 목표 학습량", min_value=1, value=20)
    auto_mode = st.toggle("🤖 자동 넘김 모드")
    auto_delay = st.slider("⏳ 넘김 간격(초)", 2, 10, 4)
    
    st.divider()
    if st.button("🔄 처음부터 다시 시작"):
        st.session_state.current_idx = 0
        st.session_state.count = 0
        save_progress(0)
        st.rerun()

# --- 메인 화면 ---
st.title("📖 영어 패턴 1000 부수기")

if st.session_state.current_idx < len(sentences):
    kind, eng, sound, mean = sentences[st.session_state.current_idx]
    
    # 진도바
    progress_val = min(st.session_state.current_idx / len(sentences), 1.0)
    st.progress(progress_val, text=f"전체 진도: {st.session_state.current_idx}/{len(sentences)}")
    st.write(f"오늘 학습 목표: {st.session_state.count} / {goal}")

    # 1. 뜻 상시 노출
    st.markdown(f"<div class='mean-box'><h3>뜻: {mean}</h3></div>", unsafe_allow_html=True)

    # 2. 상황 이미지 (Unsplash 무료 이미지 API 사용)
    # 문장의 핵심 키워드로 사진 한 장 가져오기
    search_query = eng.replace("(", "").replace(")", "").replace("I'm", "").replace("I", "")
    image_url = f"https://loremflickr.com/800/400/{search_query.split()[0]}" 
    st.image(image_url, caption="상황 예시 이미지", use_container_width=True)

    st.divider()

    # 3. 학습 로직
    if not auto_mode:
        # 수동 모드
        if not st.session_state.show_english:
            if st.button("👉 영어 문장 보기"):
                st.session_state.show_english = True
                st.rerun()
        else:
            st.success(f"### 영어: {eng}")
            st.info(f"발음: {sound}")
            if st.button("✅ 다음 문장으로"):
                st.session_state.current_idx += 1
                st.session_state.count += 1
                st.session_state.show_english = False
                save_progress(st.session_state.current_idx)
                st.rerun()
    else:
        # 자동 모드
        if st.session_state.count < goal:
            st.success(f"### 영어: {eng}")
            st.info(f"발음: {sound}")
            st.caption(f"{auto_delay}초 후 다음 문장으로 넘어갑니다...")
            
            time.sleep(auto_delay)
            
            st.session_state.current_idx += 1
            st.session_state.count += 1
            save_progress(st.session_state.current_idx)
            st.rerun()
        else:
            st.balloons()
            st.success("🎉 오늘 목표를 달성했습니다! 더 공부하시려면 사이드바에서 목표를 늘려주세요.")

else:
    st.balloons()
    st.header("🏆 1,000문장 정복 완료!")
    st.write("대단한 끈기입니다! 모든 문장을 마스터하셨습니다.")

# 하단 정보
st.caption("공부한 진도는 자동으로 저장(progress.txt)되어 언제든 이어서 할 수 있습니다.")