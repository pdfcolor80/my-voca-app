import streamlit as st
import os
import time
import random

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 페이지 설정
st.set_page_config(page_title="영어 패턴 1000 부수기", page_icon="📖", layout="centered")

# 스타일 설정
st.markdown("""
    <style>
    .main-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #e1e4e8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .label { color: #586069; font-size: 0.9rem; margin-top: 10px; }
    .content-mean { color: #1f77b4; font-size: 1.5rem; font-weight: bold; }
    .content-eng { color: #d62728; font-size: 1.3rem; font-weight: bold; margin-top: 5px; }
    .content-sound { color: #2ca02c; font-size: 1.1rem; margin-top: 5px; }
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

# --- 사이드바 ---
with st.sidebar:
    st.header("⚙️ 설정")
    goal = st.number_input("🎯 오늘 목표량", min_value=1, value=20)
    auto_mode = st.toggle("🤖 자동 넘김 모드", value=False)
    auto_delay = st.slider("⏳ 넘김 간격(초)", 2, 15, 5)
    
    st.divider()
    if st.button("🔄 처음부터 다시하기"):
        st.session_state.current_idx = 0
        st.session_state.count = 0
        save_progress(0)
        st.rerun()

# --- 메인 화면 ---
st.title("📖 영어 패턴 1000 부수기")

if st.session_state.current_idx < len(sentences):
    kind, eng, sound, mean = sentences[st.session_state.current_idx]
    
    # 상단 진도표
    total_len = len(sentences)
    st.progress(st.session_state.current_idx / total_len)
    st.caption(f"진도: {st.session_state.current_idx}/{total_len} | 오늘 학습: {st.session_state.count}/{goal}")

    # 1. 정보 상시 노출 카드
    st.markdown(f"""
    <div class="main-card">
        <div class="label">뜻 (Meaning)</div>
        <div class="content-mean">{mean}</div>
        <div class="label">영어 문장 (English)</div>
        <div class="content-eng">{eng}</div>
        <div class="label">발음 (Pronunciation)</div>
        <div class="content-sound">{sound}</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 이미지 출력 로직 개선
    # 한글 뜻에서 핵심 명사만 추출 (조사 제거 등 간단한 전처리)
    clean_keyword = mean.split('(')[0].replace("해요", "").replace("있어요", "").strip()
    
    # 캐시 방지를 위해 랜덤 쿼리 파라미터(lock) 추가
    # 검색어를 영어 키워드와 한글 키워드 조합으로 시도
    img_url = f"https://loremflickr.com/800/450/{clean_keyword},people/all?lock={st.session_state.current_idx}"
    
    st.image(img_url, caption=f"상황 연상: {clean_keyword}", use_container_width=True)

    st.divider()

    # 3. 제어 로직
    if not auto_mode:
        if st.button("다음 문장으로 👉", use_container_width=True):
            st.session_state.current_idx += 1
            st.session_state.count += 1
            save_progress(st.session_state.current_idx)
            st.rerun()
    else:
        if st.session_state.count < goal:
            st.info(f"💡 {auto_delay}초 후 자동으로 다음 문장으로 넘어갑니다.")
            time.sleep(auto_delay)
            st.session_state.current_idx += 1
            st.session_state.count += 1
            save_progress(st.session_state.current_idx)
            st.rerun()
        else:
            st.success("🎉 오늘 목표를 달성했습니다! 목표를 늘려 더 학습해보세요.")
            st.balloons()
else:
    st.balloons()
    st.header("🏆 1,000문장 정복 완료!")
    st.write("축하합니다! 모든 문장을 완수하셨습니다.")

st.caption("진도는 자동으로 저장되어 브라우저를 껐다 켜도 유지됩니다.")