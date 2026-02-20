import streamlit as st
import os
import random
import re

# 파일 경로 설정
DATA_FILE = "sentences.txt"

st.set_page_config(page_title="영어 패턴 1000 AI", layout="centered")

# CSS: 강조 단어와 일반 단어의 차이를 극대화
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
        min-height: 480px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 5px solid #eee;
    }
    
    .border-step1 { border-color: #FF9800 !important; }
    .border-step2 { border-color: #0288D1 !important; }
    .border-step3 { border-color: #9C27B0 !important; }
    .border-done { border-color: #4CAF50 !important; }

    /* 전체 문장 컨테이너 */
    .eng-text-container { 
        min-height: 5em;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 10px;
    }
    
    /* 일반 단어 (기능어: to, the, is 등) */
    .word-normal {
        color: #888;
        font-size: 1.6rem;
        font-weight: 400;
    }
    
    /* ⬆️ 강세 단어 (내용어: 강조해서 높게 읽는 단어) */
    .word-stress {
        color: #D32F2F;
        font-size: 2.2rem;
        font-weight: 900;
        text-decoration: underline; /* 시각적으로 한 번 더 강조 */
    }

    /* 실시간 읽기 강조 (JS용) */
    .word-active {
        background-color: yellow;
        transform: scale(1.2);
    }
    
    .sound-text { color: #388E3C; font-size: 1.3rem; margin-top: 5px; opacity: 0.8; }
    .hidden-content { visibility: hidden !important; }
    .mean-box { padding: 20px; border-radius: 20px; margin-top: 25px; background-color: #E3F2FD; }
    .mean-text { color: #1565C0; font-size: 1.9rem; font-weight: bold; }
    .status-info { color: #FFFFFF; font-weight: bold; margin-top: 20px; font-size: 1.1rem; padding: 15px; border-radius: 15px; text-align: center; }
    .stButton>button { width: 100%; height: 5rem; border-radius: 25px; font-weight: bold; font-size: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 강세 단어 판별 함수 (간단한 내용어 추출 로직)
def highlight_stress(text):
    # 강세를 주지 않는 기능어 목록 (소문자로 유지될 단어들)
    function_words = {'a', 'an', 'the', 'is', 'am', 'are', 'was', 'were', 'to', 'at', 'in', 'on', 'of', 'for', 'and', 'but', 'or', 'it', 'its', 'my', 'your', 'his', 'her'}
    words = text.split()
    html_output = ""
    
    for word in words:
        clean_word = re.sub(r'[^\w]', '', word).lower()
        if clean_word in function_words:
            html_output += f'<span class="word-normal">{word}</span>'
        else:
            # 강세 단어는 대문자로 바꾸고 강조 클래스 적용
            html_output += f'<span class="word-stress">{word.upper()}</span>'
            
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
    
    # 강세 표시가 적용된 HTML 생성
    stressed_html = highlight_stress(eng)
    
    st.markdown(f"""
    <div id="main-card" class="study-card border-step1">
        <div style="color:#adb5bd; font-weight:bold;">{kind}</div>
        <div id="display-eng" class="eng-text-container">
            {stressed_html}
        </div>
        <div id="display-sound" class="sound-text">[{sound}]</div>
        <div class="mean-box">
            <div class="mean-text">{mean}</div>
        </div>
        <div id="status-box" class="status-info" style="background-color:#FF9800;">🐌 1단계: 초저속 (표시된 단어 강조!)</div>
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
            const wordElements = engContainer.querySelectorAll('span');
            
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
                    statusEl.innerText = "🐌 1단계: 강조 단어에 힘주어 읽기 (" + (count+1) + "/13)";
                    statusEl.style.backgroundColor = "#FF9800";
                }} else if (count < 10) {{
                    msg.rate = 0.8;
                    card.className = "study-card border-step2";
                    statusEl.innerText = "🔵 2단계: 리듬 타며 연결하기 (" + (count+1) + "/13)";
                    statusEl.style.backgroundColor = "#0288D1";
                }} else {{
                    msg.rate = 0.8;
                    engContainer.classList.add('hidden-content');
                    soundEl.classList.add('hidden-content');
                    card.className = "study-card border-step3";
                    statusEl.innerText = "🟣 3단계: 소리만 듣고 복기 (" + (count+1) + "/13)";
                    statusEl.style.backgroundColor = "#9C27B0";
                }}

                msg.onboundary = function(event) {{
                    if (event.name === 'word') {{
                        wordElements.forEach(el => el.classList.remove('word-active'));
                        const wordIdx = getWordIndex("{clean_eng}", event.charIndex);
                        if (wordElements[wordIdx]) wordElements[wordIdx].classList.add('word-active');
                    }}
                }};

                msg.onend = function() {{
                    wordElements.forEach(el => el.classList.remove('word-active'));
                    count++;
                    if (count < total) setTimeout(speak, 2000);
                    else {{
                        card.className = "study-card border-done";
                        statusEl.innerText = isDrive ? "🚗 자동 이동 중..." : "✅ 완료!";
                        statusEl.style.backgroundColor = "#43A047";
                        if(isDrive) setTimeout(() => {{ window.parent.document.querySelector('button[kind="primary"]').click(); }}, 3000);
                    }}
                }};
                window.speechSynthesis.speak(msg);
            }}

            function getWordIndex(text, offset) {{
                const beforeText = text.substring(0, offset).trim();
                return beforeText === "" ? 0 : beforeText.split(/\s+/).length;
            }}

            speak();
        }}
        setTimeout(startShadowing, 500);
        </script>
    """, height=0)

    if st.button("다음 랜덤 문장 👉", type="primary"):
        st.session_state.current_idx = random.randint(0, len(sentences) - 1)
        st.rerun()