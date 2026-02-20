import streamlit as st
import os
import random

# 파일 경로 설정
DATA_FILE = "sentences.txt"

st.set_page_config(page_title="영어 패턴 1000", layout="centered")

# CSS: 정신없던 효과들을 제거하고 깔끔한 UI로 변경
st.markdown("""
    <style>
    .main { background-color: #fdfdfd; }
    .study-card {
        background-color: #ffffff;
        padding: 40px 20px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid #eee;
    }
    
    /* 영어 텍스트 영역 */
    .eng-text-container { 
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin-bottom: 20px;
    }
    
    .word-box { display: flex; align-items: baseline; }

    /* 일반 글자 */
    .char-normal {
        color: #333;
        font-size: 1.8rem;
        font-weight: 500;
    }
    
    /* 적당한 강조 (빨간색 화살표 제거, 대신 굵기만 조절) */
    .char-accent {
        color: #E53935;
        font-size: 2.1rem;
        font-weight: 800;
        text-decoration: underline;
    }

    .sound-text { color: #666; font-size: 1.1rem; margin-top: 5px; font-style: italic; }
    .hidden-content { display: none !important; }
    
    /* 한글 뜻 영역 */
    .mean-box { 
        margin-top: 30px;
        padding: 15px;
        border-top: 1px solid #f0f0f0;
    }
    .mean-text { color: #1a73e8; font-size: 1.7rem; font-weight: bold; }
    
    /* 하단 상태바 (심플하게) */
    .status-info { 
        margin-top: 20px;
        font-size: 1rem;
        color: #777;
        font-weight: 500;
    }
    
    .stButton>button { 
        width: 100%; height: 4rem; border-radius: 12px; font-weight: bold; 
        background-color: #333; color: white; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

def get_accented_html(text):
    words = text.split()
    vowels = "aeiouAEIOU"
    html_output = ""
    for word in words:
        html_output += '<div class="word-box">'
        accent_done = False
        for char in word:
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
    st.header("설정")
    st.session_state.drive_mode = st.toggle("🚗 운전 모드 (자동 넘기기)", value=st.session_state.drive_mode)

if sentences:
    idx = st.session_state.current_idx
    kind, eng, sound, mean = sentences[idx]
    accented_html = get_accented_html(eng)
    
    st.markdown(f"""
    <div class="study-card">
        <div style="color:#999; font-size:0.8rem; margin-bottom:10px;">{kind}</div>
        <div id="display-eng" class="eng-text-container">{accented_html}</div>
        <div id="display-sound" class="sound-text">[{sound}]</div>
        <div class="mean-box">
            <div class="mean-text">{mean}</div>
        </div>
        <div id="status-box" class="status-info">진행 중...</div>
    </div>
    """, unsafe_allow_html=True)

    is_drive = "true" if st.session_state.drive_mode else "false"
    clean_eng = eng.replace('"', '').replace("'", "")
    
    st.components.v1.html(f"""
        <script>
        function start() {{
            const engEl = window.parent.document.getElementById('display-eng');
            const soundEl = window.parent.document.getElementById('display-sound');
            const statusEl = window.parent.document.getElementById('status-box');
            
            window.speechSynthesis.cancel();
            let count = 0;
            const isDrive = {is_drive};

            function speak() {{
                let msg = new SpeechSynthesisUtterance("{clean_eng}");
                msg.lang = 'en-US';
                
                // 1~5회: 0.5배속 | 6~10회: 0.8배속 | 11~13회: 0.8배속 + 숨김
                if (count < 5) {{
                    msg.rate = 0.5;
                    statusEl.innerText = "Step 1: 연음 파악 중 (" + (count+1) + "/13)";
                }} else if (count < 10) {{
                    msg.rate = 0.8;
                    statusEl.innerText = "Step 2: 정상 속도 훈련 (" + (count+1) + "/13)";
                }} else {{
                    msg.rate = 0.8;
                    engEl.classList.add('hidden-content');
                    soundEl.classList.add('hidden-content');
                    statusEl.innerText = "Step 3: 쉐도잉 완성 (" + (count+1) + "/13)";
                }}

                msg.onend = function() {{
                    count++;
                    if (count < 13) {{
                        setTimeout(speak, 1500);
                    }} else {{
                        statusEl.innerText = "학습 완료";
                        if(isDrive) setTimeout(() => {{ 
                            window.parent.document.querySelector('button[kind="primary"]').click(); 
                        }}, 2000);
                    }}
                }};
                window.speechSynthesis.speak(msg);
            }}
            speak();
        }}
        setTimeout(start, 500);
        </script>
    """, height=0)

    if st.button("다음 랜덤 문장 👉", type="primary"):
        st.session_state.current_idx = random.randint(0, len(sentences) - 1)
        st.rerun()