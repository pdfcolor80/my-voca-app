import streamlit as st
import os
import time

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 페이지 설정
st.set_page_config(page_title="영어 패턴 1000 부수기", page_icon="📖", layout="wide")

# 스타일 설정
st.markdown("""
    <style>
    .main-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e1e4e8;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .mean-text { color: #1f77b4; font-size: 1.8rem; font-weight: bold; margin-bottom: 10px; }
    .eng-text { color: #d62728; font-size: 1.5rem; font-weight: bold; margin-bottom: 5px; }
    .sound-text { color: #2ca02c; font-size: 1.2rem; }
    .label { font-size: 0.85rem; color: #6c757d; font-weight: bold; text-transform: uppercase; }
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

sentences = load_sentences()

if "current_idx" not in st.session_state:
    st.session_state.current_idx = load_progress()
if "count" not in st.session_state:
    st.session_state.count = 0

# --- 사이드바 ---
with st.sidebar:
    st.header("⚙️ Settings")
    goal = st.number_input("🎯 오늘 목표", min_value=1, value=20)
    auto_mode = st.toggle("🤖 자동 넘김 모드", value=False)
    auto_delay = st.slider("⏳ 넘김 간격(초)", 3, 20, 7)
    
    st.divider()
    if st.button("🔄 처음부터 다시 시작"):
        st.session_state.current_idx = 0
        st.session_state.count = 0
        save_progress(0)
        st.rerun()

# --- 메인 학습 화면 ---
st.title("📖 영어 패턴 1000 부수기")

if st.session_state.current_idx < len(sentences):
    kind, eng, sound, mean = sentences[st.session_state.current_idx]
    
    col1, col2 = st.columns([1, 1.2]) # 왼쪽은 텍스트, 오른쪽은 이미지

    with col1:
        # 진도 표시
        st.progress(st.session_state.current_idx / len(sentences))
        st.write(f"**진도:** {st.session_state.current_idx}/1000 | **오늘 학습:** {st.session_state.count}/{goal}")
        
        # 텍스트 정보 상시 노출
        st.markdown(f"""
        <div class="main-card">
            <div class="label">한국어 뜻</div>
            <div class="mean-text">{mean}</div>
            <hr>
            <div class="label">영어 문장</div>
            <div class="content-box">
                <div class="eng-text">{eng}</div>
                <div class="sound-text">{sound}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 제어 버튼
        if not auto_mode:
            if st.button("다음 문장으로 👉", use_container_width=True):
                st.session_state.current_idx += 1
                st.session_state.count += 1
                save_progress(st.session_state.current_idx)
                st.rerun()
        else:
            if st.session_state.count < goal:
                st.info(f"💡 {auto_delay}초 후 자동으로 넘어갑니다.")
                time.sleep(auto_delay)
                st.session_state.current_idx += 1
                st.session_state.count += 1
                save_progress(st.session_state.current_idx)
                st.rerun()

    with col2:
        # 가장 정확한 방법: 구글 이미지 검색 결과를 iframe으로 삽입
        # 괄호를 제거한 영어 문장으로 검색
        search_query = eng.replace("(", "").replace(")", "").replace("'", "")
        # 구글 이미지 검색 URL (안전 모드 적용)
        google_url = f"https://www.google.com/search?q={search_query}+meaning&tbm=isch&safe=active"
        
        st.write(f"🔍 **'{search_query}'** 상황 검색 결과")
        # iframe을 사용하여 구글 검색 페이지를 작게 보여줌 (높이 조절 가능)
        st.markdown(f'<iframe src="{google_url}" width="100%" height="600" style="border:1px solid #eee; border-radius:10px;"></iframe>', unsafe_allow_html=True)

else:
    st.balloons()
    st.header("🏆 1,000문장 정복 완료!")
    save_progress(0)

st.caption("공부한 기록은 자동으로 저장되어 언제든 이어서 할 수 있습니다.")