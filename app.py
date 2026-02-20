import streamlit as st
import os
import random
import re

# 파일 경로 설정
DATA_FILE = "sentences.txt"

st.set_page_config(page_title="영어 패턴 1000 AI", layout="centered")

# CSS: 알파벳 단위 강조 스타일
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .study-card {
        background-color: #ffffff;
        padding: 30px 15px;
        border-radius: 30px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        min-height: 500px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 5px solid #eee;
    }
    
    .border-step1 { border-color: #FF9800 !important; }
    .border-step2 { border-color: #0288D1 !important; }
    .border-step3 { border-color: #9C27B0 !important; }
    
    .eng-text-container { 
        min-height: 6em;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 10px;
        font-family: 'Arial', sans-serif;
    }
    
    /* 개별 단어 박스 */
    .word-box { display: flex; align-items: flex-end; }

    /* 일반 알파벳 */
    .char-normal {
        color: #444;
        font-size: 2rem;
        font-weight: 500;
    }
    
    /* 📍 엑센트 알파벳 강조 (높게 읽는 부분) */
    .char-accent {
        color: #D32F2F;
        font-size: 2.6rem;
        font-weight: 900;
        position: relative;
        bottom: 5px; /* 시각적으로 위로 띄움 */
    }
    .char-accent::after {
        content: '↑';
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1rem;
        font-weight: bold;
    }

    .sound-text { color: #388E3C; font-size: 1.3rem; margin-top: 10px; opacity: 0.7; }
    .hidden-content { visibility: hidden !important; }
    .mean-box { padding: 20px; border-radius: 20px; margin-top: 25px; background-color: #E3F2FD; }
    .mean-text { color: #1565C0; font-size: 2rem; font-weight: bold; }
    .status-info { color: #FFFFFF; font-weight: bold; margin-top: 20px; font-size: 1.1rem; padding: 15px; border-radius: 15px; text-align: center; }
    .stButton>button { width: 100%; height: 5rem; border-radius: 25px; font-weight: bold; font-size: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 텍스트 내 단어별 엑센트 알파벳 처리 로직
def get_accented_html(text):
    words = text.split()
    vowels = "aeiouAEIOU"
    html_output = ""
    
    for word in words:
        html_output += '<div class="word-box">'
        # 간단한 강세 규칙: 2음절 이상 단어는 첫 번째 모음에 강세 (학습용 단순화)
        # 실제 사전 API 연동 없이 규칙 기반으로 시각화
        accent_done = False
        for i, char in enumerate(word):
            if not accent_done and char in vowels and len(word) > 2:
                html_output += f'<span class="char-accent">{char}</span>'
                accent_done = True
            else:
                html_output += f'<span class="char-normal">{char}</span>'
        html_output += '</div>'
        
    return html_output

def load_sentences():
    if not os.path.exists(DATA_FILE): return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return [line.strip().split("|") for line in f if len(line.strip().split("|")) >= 4]

sentences = load_sentences()

if "current_idx" not in st.session_state:
    if sentences: st.session_state.current_idx = random.randint(0, len(sentences) - 1)
if "drive_mode" not in st.session_state: st.session_state.drive_mode = False

with st.sidebar:
    st.header("⚙️ 설정")
    st.session_state.drive_mode = st.toggle("🚗 운전 모드", value=st.session_state.drive_mode)
    if st.button("🎲 랜덤 추출"):
        st.session_state.current_idx = random.randint(0, len(sentences) - 1)
        st.rerun()

if sentences:
    idx = st.session_state.current_idx
    kind, eng, sound, mean = sentences[idx]
    
    # 알파벳 단위 강조 HTML 생성
    accented_html = get_accented_html(eng)
    
    st.markdown(f"""
    <div id="main-card" class="study-card border-step1">
        <div style="color:#adb5bd; font-weight:bold;">{kind}</div>
        <div id="display-eng" class="eng-text-container">
            {accented_html}
        </div>
        <div id="display-sound" class="sound-text">[{sound}]</div>
        <div class="mean-box">
            <div class="mean-text">{mean}</div>
        </div>
        <div id="status-box" class="status-info" style="background-color:#FF9800;">🐌 1단계: ↑ 표시된 알파벳을 높게! (1/13)</div>
    </div>
    """, unsafe_allow_html=True)

    is_drive = "true" if st.session_state.drive_mode else "false"
    clean_eng = eng.replace('"', '').replace("'", "")
    
    st.components.v1.html(f"""
        <script>
        function startShadowing() {{
            const card = window.parent.document.getElementById('main-card');
            const engContainer = window.parent.document.getElementById('display-eng');
            const soundEl = window.parent.document.getElementById('display-sound');
            const statusEl = window.parent.document.getElementById('status-box');
            
            engContainer.classList.remove('hidden-content');
            soundEl.classList.remove('hidden-content');
            window.speechSynthesis.cancel();
            
            let count = 0;
            const total = 13;
            const isDrive = {is_drive};

            function speak() {{
                let msg = new SpeechSynthesisUtterance("{clean_eng}");
                msg.lang = 'en-US';
                
                if (count < 5) {{
                    msg.rate = 0.5;
                    card.className = "study-card border-step1";
                    statusEl.innerText = "🐌 1단계: 강세 알파벳 높이기 (" + (count+1) + "/13)";
                    statusEl.style.backgroundColor = "#FF9800";
                }} else if (count < 10) {{
                    msg.rate = 0.8;
                    card.className = "study-card border-step2";
                    statusEl.innerText = "🔵 2단계: 표준 리듬 반복 (" + (count+1) + "/13)";
                    statusEl.style.backgroundColor = "#0288D1";
                }} else {{
                    msg.rate = 0.8;
                    engContainer.classList.add('hidden-content');
                    soundEl.classList.add('hidden-content');
                    card.className = "study-card border-step3";
                    statusEl.innerText = "🟣 3단계: 가리고 말하기 (" + (count+1) + "/13)";
                    statusEl.style.backgroundColor = "#9C27B0";
                }}

                msg.onend = function() {{
                    count++;
                    if (count < total) setTimeout(speak, 2000);
                    else {{
                        if(isDrive) setTimeout(() => {{ window.parent.document.querySelector('button[kind="primary"]').click(); }}, 3000);
                    }}
                }};
                window.speechSynthesis.speak(msg);
            }}
            speak();
        }}
        setTimeout(startShadowing, 500);
        </script>
    """, height=0)

    if st.button("다음 랜덤 문장 👉", type="primary"):
        st.session_state.current_idx = random.randint(0, len(sentences) - 1)
        st.rerun()