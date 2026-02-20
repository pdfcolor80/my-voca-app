import streamlit as st
import os
import time

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 페이지 설정
st.set_page_config(page_title="영어 패턴 1000 부수기", page_icon="📖", layout="centered")

# 스타일 설정: 뜻, 영어, 발음을 한 카드 안에 깔끔하게 상시 노출
st.markdown("""
    <style>
    .main-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #1f77b4;
        margin-bottom: 20px;
    }
    .mean-text { color: #1f77b4; font-size: 1.6rem; font-weight: bold; margin-bottom: 10px; }
    .eng-text { color: #d62728; font-size: 1.4rem; font-weight: bold; margin-bottom: 5px; }
    .sound-text { color: #2ca02c; font-size: 1.1rem; font-style: italic; }
    .label { font-size: 0.8rem; color: #6c757d; font-weight: normal; }
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

# --- 사이드바 설정 ---
with st.sidebar:
    st.header("⚙️ Study Setup")
    goal = st.number_input("🎯 오늘 목표량", min_value=1, value=20)
    auto_mode = st.toggle("🤖 자동 넘김 모드", value=False)
    auto_delay = st.slider("⏳ 넘김 간격(초)", 2, 15, 5)
    
    st.divider()
    if st.button("🔄 처음부터 다시하기"):
        st.session_state.current_idx = 0
        st.session_state.count = 0
        save_progress(0)
        st.rerun()

# --- 메인 학습 화면 ---
st.title("📖 영어 패턴 1000 부수기")

if st.session_state.current_idx < len(sentences):
    kind, eng, sound, mean = sentences[st.session_state.current_idx]
    
    # 진도 표시
    total_len = len(sentences)
    st.progress(st.session_state.current_idx / total_len)
    st.caption(f"진도: {st.session_state.current_idx}/{total_len} | 오늘 목표: {st.session_state.count}/{goal}")

    # 1. 정보 상시 노출 (뜻 + 영어 + 발음)
    st.markdown(f"""
    <div class="main-card">
        <div class="label">뜻 (Meaning)</div>
        <div class="mean-text">{mean}</div>
        <div class="label">영어 (English)</div>
        <div class="eng-text">{eng}</div>
        <div class="label">발음 (Pronunciation)</div>
        <div class="sound-text">{sound}</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 이미지 출력 로직 (가장 안정적인 웹 이미지 소스 사용)
    # 영어 문장의 첫 단어와 주요 키워드를 조합하여 검색 신뢰도를 높임
    clean_query = eng.replace("(", "").replace(")", "").replace("'", "").strip()
    # 문장마다 고유한 이미지가 나오도록 seed 값을 문장 인덱스로 설정
    image_url = f"https://loremflickr.com/800/450/{clean_query.split()[0]},people/all?lock={st.session_state.current_idx}"
    
    # 이미지 표시
    st.image(image_url, caption=f"상황 연상 이미지: {mean}", use_container_width=True)

    st.divider()

    # 3. 제어 버튼 및 자동화
    if not auto_mode:
        if st.button("다음 문장으로 넘어가기 👉", use_container_width=True):
            st.session_state.current_idx += 1
            st.session_state.count += 1
            save_progress(st.session_state.current_idx)
            st.rerun()
    else:
        if st.session_state.count < goal:
            st.info(f"💡 {auto_delay}초 후 자동으로 다음으로 넘어갑니다.")
            time.sleep(auto_delay)
            st.session_state.current_idx += 1
            st.session_state.count += 1
            save_progress(st.session_state.current_idx)
            st.rerun()
        else:
            st.success("🎉 오늘 목표를 달성했습니다! 목표를 더 늘려보세요.")
            st.balloons()
else:
    st.balloons()
    st.header("🏆 1,000문장 정복 완료!")
    st.write("모든 문장을 학습하셨습니다. 정말 대단합니다!")

st.caption("공부한 기록은 자동으로 저장되어 언제든 이어서 할 수 있습니다.")