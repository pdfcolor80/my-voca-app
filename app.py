import streamlit as st
import os
import time

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 페이지 설정 (모바일 최적화: 레이아웃을 centered로 고정)
st.set_page_config(page_title="영어 1000", page_icon="🚀", layout="centered")

# CSS: 모바일 화면에서 텍스트가 잘 보이고 여백을 줄이도록 설정
st.markdown("""
    <style>
    /* 전체 배경 및 폰트 설정 */
    .main { background-color: #f9f9f9; }
    
    /* 카드 디자인: 여백 최소화 */
    .mobile-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #eee;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* 영어를 가장 크고 위에 배치 */
    .eng-title { color: #d32f2f; font-size: 1.8rem; font-weight: bold; margin-bottom: 2px; line-height: 1.2; }
    .sound-sub { color: #388e3c; font-size: 1.1rem; margin-bottom: 10px; }
    
    /* 뜻은 아래에 중간 크기로 */
    .mean-box { background-color: #f1f3f4; padding: 10px; border-radius: 10px; }
    .mean-text { color: #1976d2; font-size: 1.4rem; font-weight: bold; }
    
    .label { font-size: 0.7rem; color: #aaa; text-transform: uppercase; margin-bottom: 2px; }
    
    /* 구글 이미지 iframe 크기 조절 */
    .img-container { width: 100%; height: 350px; border-radius: 10px; overflow: hidden; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

def load_sentences():
    if not os.path.exists(DATA_FILE):
        st.error("파일 없음")
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
                return int(f.read().strip())
        except: return 0
    return 0

sentences = load_sentences()
if "current_idx" not in st.session_state:
    st.session_state.current_idx = load_progress()
if "count" not in st.session_state:
    st.session_state.count = 0

# --- 사이드바 (모바일에서는 메뉴 아이콘으로 숨겨짐) ---
with st.sidebar:
    st.header("⚙️ 설정")
    goal = st.number_input("🎯 오늘 목표", min_value=1, value=20)
    auto_mode = st.toggle("🤖 자동 넘김")
    auto_delay = st.slider("⏳ 시간(초)", 3, 15, 5)
    if st.button("🔄 리셋"):
        st.session_state.current_idx = 0
        save_progress(0)
        st.rerun()

# --- 메인 학습 화면 ---
if st.session_state.current_idx < len(sentences):
    kind, eng, sound, mean = sentences[st.session_state.current_idx]
    
    # 1. 텍스트 영역 (카드)
    st.markdown(f"""
    <div class="mobile-card">
        <div class="label">English</div>
        <div class="eng-title">{eng}</div>
        <div class="sound-sub">[{sound}]</div>
        <div class="mean-box">
            <div class="mean-text">{mean}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. 제어 버튼 (크게 배치)
    if not auto_mode:
        if st.button("다음 문장 👉", use_container_width=True):
            st.session_state.current_idx += 1
            st.session_state.count += 1
            save_progress(st.session_state.current_idx)
            st.rerun()
    else:
        st.caption(f"⏱ {auto_delay}초 후 자동 넘김...")
        time.sleep(auto_delay)
        st.session_state.current_idx += 1
        st.session_state.count += 1
        save_progress(st.session_state.current_idx)
        st.rerun()

    # 3. 이미지 영역 (하단 배치, 모바일 최적화 높이)
    search_query = eng.replace("(", "").replace(")", "").strip()
    google_img_url = f"https://www.google.com/search?q={search_query}+meaning&tbm=isch&safe=active"
    
    st.markdown(f"""
        <div class="img-container">
            <iframe src="{google_img_url}" width="100%" height="350" style="border:none;"></iframe>
        </div>
    """, unsafe_allow_html=True)
    
    # 하단 진행률
    st.progress(st.session_state.current_idx / len(sentences))
    st.caption(f"진도: {st.session_state.current_idx}/1000 | 오늘: {st.session_state.count}/{goal}")

else:
    st.balloons()
    st.success("1,000문장 정복!")