import streamlit as st
import os
import time

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 페이지 설정
st.set_page_config(page_title="영어 패턴 1000 부수기", page_icon="💡", layout="centered")

# 핵심 단어별 아이콘 매칭 사전
ICON_MAP = {
    "happy": "😊", "sad": "😢", "think": "🤔", "go": "🏃", "eat": "🍴",
    "drink": "☕", "call": "📞", "see": "👁️", "dance": "💃", "sing": "🎤",
    "time": "⏰", "money": "💰", "car": "🚗", "home": "🏠", "work": "💼",
    "sorry": "🙏", "thank": "💖", "question": "❓", "idea": "💡", "love": "😍",
    "expensive": "💎", "cheap": "🏷️", "fast": "⚡", "slow": "🐢", "hot": "🔥",
    "cold": "❄️", "help": "🤝", "look": "👀", "listen": "🎧", "speak": "🗣️"
}

def get_context_icon(eng, mean):
    combined = (eng + " " + mean).lower()
    for word, icon in ICON_MAP.items():
        if word in combined:
            return icon
    return "📖"

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

# 스타일 설정: 영어를 가장 크고 위로 배치
st.markdown("""
    <style>
    .main-card {
        background-color: #ffffff;
        padding: 35px;
        border-radius: 25px;
        border: 2px solid #f0f2f6;
        text-align: center;
        box-shadow: 0 12px 30px rgba(0,0,0,0.08);
        margin-top: 20px;
    }
    .icon-box { font-size: 80px; margin-bottom: 15px; }
    .eng-text { color: #E53935; font-size: 2.5rem; font-weight: bold; margin-bottom: 5px; line-height: 1.2; }
    .sound-text { color: #43A047; font-size: 1.3rem; margin-bottom: 25px; }
    .mean-text { color: #1E88E5; font-size: 1.8rem; font-weight: bold; margin-top: 10px; }
    .info-label { color: #bdbdbd; font-size: 0.85rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
    hr { border: 0; border-top: 1px solid #eee; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

sentences = load_sentences()
if "current_idx" not in st.session_state:
    st.session_state.current_idx = load_progress()
if "count" not in st.session_state:
    st.session_state.count = 0

# --- 사이드바 ---
with st.sidebar:
    st.header("⚙️ 학습 설정")
    goal = st.number_input("🎯 오늘 목표", min_value=1, value=20)
    auto_mode = st.toggle("🤖 자동 넘김 모드", value=False)
    auto_delay = st.slider("⏳ 넘김 간격(초)", 2, 15, 5)
    if st.button("🔄 처음부터 다시 시작"):
        st.session_state.current_idx = 0
        st.session_state.count = 0
        save_progress(0)
        st.rerun()

# --- 메인 학습화면 ---
if st.session_state.current_idx < len(sentences):
    kind, eng, sound, mean = sentences[st.session_state.current_idx]
    current_icon = get_context_icon(eng, mean)
    
    # 상단 진도표
    st.progress(st.session_state.current_idx / len(sentences))
    st.write(f"📊 진도: {st.session_state.current_idx}/1000 | 오늘 학습: {st.session_state.count}/{goal}")

    # 중앙 카드: 영어(위/크게) -> 발음 -> 뜻(아래)
    st.markdown(f"""
    <div class="main-card">
        <div class="icon-box">{current_icon}</div>
        <div class="info-label">English</div>
        <div class="eng-text">{eng}</div>
        <div class="sound-text">[{sound}]</div>
        <hr>
        <div class="info-label">Meaning</div>
        <div class="mean-text">{mean}</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("") 

    # 제어 버튼
    if not auto_mode:
        if st.button("다음 문장으로 넘어가기 👉", use_container_width=True):
            st.session_state.current_idx += 1
            st.session_state.count += 1
            save_progress(st.session_state.current_idx)
            st.rerun()
    else:
        if st.session_state.count < goal:
            st.info(f"⏳ {auto_delay}초 후 자동으로 다음으로 넘어갑니다.")
            time.sleep(auto_delay)
            st.session_state.current_idx += 1
            st.session_state.count += 1
            save_progress(st.session_state.current_idx)
            st.rerun()
        else:
            st.success("🎉 오늘 목표 달성! 수고하셨습니다.")
            st.balloons()
else:
    st.balloons()
    st.header("🏆 1,000문장 마스터 완료!")