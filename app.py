import streamlit as st
import os
import random

# 파일 경로 설정
DATA_FILE = "sentences.txt"

# 모바일 최적화 설정
st.set_page_config(page_title="영어 패턴 1000 AI", layout="centered")

# CSS: 단계별 화면 제어 및 가독성 최적화
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
    }
    .eng-text { 
        color: #D32F2F; 
        font-size: calc(1.7rem + 1.2vw); 
        font-weight: bold; 
        line-height: 1.2; 
        min-height: 4.5em;
        display: flex;
        align-items: center;
        justify-content: center;
        word-break: keep-all;
    }
    .sound-text { 
        color: #388E3C; 
        font-size: 1.3rem; 
        margin-top: 5px; 
        font-weight: 500; 
        opacity: 0.8;
        min-height: 1.5em;
    }
    .hidden-content { visibility: hidden !important; }
    .mean-box { 
        padding: 20px; 
        border-radius: 20px; 
        margin-top: 25px;
        background-color: #E3F2FD; 
        border: 1px solid #BBDEFB;
    }
    .mean-text { color: #1565C0; font-size: 1.9rem; font-weight: bold; }
    .status-info { 
        color: #FFFFFF; font-weight: bold; margin-top: 20px; font-size: 1.1rem;
        padding: 15px; border-radius: 15px; text-align: center;
        transition: background-color 0.5s ease;
    }
    .stButton>button { 
        width: 100%; height: 5rem; border-radius: 25px; font-weight: bold; font-size: 1.5rem !important; 
    }
    </style>
    """, unsafe_allow_html=True)

def load_sentences():
    if not os.path.exists(DATA_FILE): return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return [line.strip().split("|") for line in f if len(line.strip().split("|")) >= 4]

sentences = load_sentences()

if "current_idx" not in st.session_state:
    if sentences:
        st.session_state.current_idx = random.randint(0, len(sentences) - 1)
if "drive_mode" not in st.session_state:
    st.session_state.drive_mode = False

with st.sidebar:
    st.header("⚙️ 설정")
    st.session_state.drive_mode = st.toggle("🚗 운전 모드 (자동 넘기기)", value=st.session_state.drive_mode)
    if st.button("🎲 다른 문장 랜덤 추출"):
        st.session_state.current_idx = random.randint(0, len(sentences) - 1)
        st.rerun()

if sentences:
    idx = st.session_state.current_idx
    kind, eng, sound, mean = sentences[idx]
    
    st.markdown(f"""
    <div class="study-card">
        <div style="color:#adb5bd; font-weight:bold; font-size:0.9rem;">{kind}</div>
        <div id="display-eng" class="eng-text">{eng}</div>
        <div id="display-sound" class="sound-text">[{sound}]</div>
        <div class="mean-box">
            <div class="mean-text">{mean}</div>
        </div>
        <div id="status-box" class="status-info" style="background-color:#FF9800;">🐌 1단계: 초저속 연음 정복 (1/13)</div>
    </div>
    """, unsafe_allow_html=True)

    is_drive = "true" if st.session_state.drive_mode else "false"
    clean_eng = eng.replace('"', '').replace("'", "")
    
    st.components.v1.html(f"""
        <script>
        function startShadowing() {{
            const engEl = window.parent.document.getElementById('display-eng');
            const soundEl = window.parent.document.getElementById('display-sound');
            const statusEl = window.parent.document.getElementById('status-box');
            
            engEl.classList.remove('hidden-content');
            soundEl.classList.remove('hidden-content');
            
            window.speechSynthesis.cancel();
            
            let count = 0;
            const total = 13;
            const isDrive = {is_drive};

            function speak() {{
                let msg = new SpeechSynthesisUtterance("{clean_eng}");
                msg.lang = 'en-US';
                
                // [1단계: 1~5회] 초저속 (0.5배속)
                if (count < 5) {{
                    msg.rate = 0.5;
                    statusEl.innerText = "🐌 1단계: 초저속 연음 정복 (" + (count+1) + "/13)";
                    statusEl.style.backgroundColor = "#FF9800";
                }} 
                // [2단계: 6~10회] 기본속도 (0.8배속)
                else if (count < 10) {{
                    msg.rate = 0.8;
                    statusEl.innerText = "🔵 2단계: 표준 속도 반복 (" + (count+1) + "/13)";
                    statusEl.style.backgroundColor = "#0288D1";
                }} 
                // [3단계: 11~13회] 가리고 듣기 (0.8배속)
                else {{
                    msg.rate = 0.8;
                    engEl.classList.add('hidden-content');
                    soundEl.classList.add('hidden-content');
                    statusEl.innerText = "🟣 3단계: 소리만 집중 (" + (count+1) + "/13)";
                    statusEl.style.backgroundColor = "#8E24AA";
                }}

                msg.onend = function() {{
                    count++;
                    if (count < total) {{
                        setTimeout(speak, 2000);
                    }} else {{
                        statusEl.innerText = isDrive ? "🚗 3초 후 다음 문장으로..." : "✅ 13회 완료! 버튼을 누르세요.";
                        statusEl.style.backgroundColor = "#43A047";
                        if(isDrive) {{
                            setTimeout(() => {{
                                window.parent.document.querySelector('button[kind="primary"]').click();
                            }}, 3000);
                        }}
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