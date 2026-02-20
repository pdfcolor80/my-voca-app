import streamlit as st
import os
import random

# 파일 경로 설정
DATA_FILE = "sentences.txt"
# 점수 기반 데이터가 필요 없으므로 study_data.json 대신 간단한 진행도 기록만 유지 가능 (옵션)

st.set_page_config(page_title="영어 패턴 1000 랜덤 모드", layout="centered")

# CSS: 가독성 및 디자인 최적화
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; }
    .study-card {
        background-color: #ffffff;
        padding: 30px 15px;
        border-radius: 30px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        min-height: 450px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .eng-text { 
        color: #D32F2F; 
        font-size: calc(1.8rem + 1.5vw); 
        font-weight: bold; 
        line-height: 1.2; 
        min-height: 4em;
        display: flex;
        align-items: center;
        justify-content: center;
        word-break: keep-all;
    }
    .sound-text { color: #388E3C; font-size: 1.4rem; margin-top: 5px; font-weight: 500; opacity: 0.8; }
    .hidden-content { visibility: hidden; }
    .mean-box { 
        padding: 20px; 
        border-radius: 20px; 
        margin-top: 25px;
        background-color: #E3F2FD; 
        border: 1px solid #BBDEFB;
    }
    .mean-text { color: #1565C0; font-size: 2.0rem; font-weight: bold; }
    .status-info { 
        color: #FFFFFF; font-weight: bold; margin-top: 20px; font-size: 1.2rem;
        padding: 15px; border-radius: 15px; text-align: center;
    }
    .stButton>button { width: 100%; height: 5rem; border-radius: 25px; font-weight: bold; font-size: 1.6rem !important; }
    </style>
    """, unsafe_allow_html=True)

def load_sentences():
    if not os.path.exists(DATA_FILE): return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return [line.strip().split("|") for line in f if len(line.strip().split("|")) >= 4]

sentences = load_sentences()

# 세션 상태 초기화
if "current_idx" not in st.session_state:
    if sentences:
        st.session_state.current_idx = random.randint(0, len(sentences) - 1)
if "drive_mode" not in st.session_state:
    st.session_state.drive_mode = False

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 학습 설정")
    st.session_state.drive_mode = st.toggle("🚗 운전 모드 (자동 넘기기)", value=st.session_state.drive_mode)
    st.info("운전 모드 활성화 시 8번 반복 후 3초 뒤 자동으로 다음 랜덤 문장으로 이동합니다.")
    
    if st.button("🎲 다른 문장 랜덤 추출"):
        st.session_state.current_idx = random.randint(0, len(sentences) - 1)
        st.rerun()

# --- 메인 학습 화면 ---
if sentences:
    idx = st.session_state.current_idx
    kind, eng, sound, mean = sentences[idx]
    
    st.markdown(f"""
    <div class="study-card">
        <div style="color:#adb5bd; font-weight:bold;">{kind}</div>
        <div id="display-eng" class="eng-text">{eng}</div>
        <div id="display-sound" class="sound-text">[{sound}]</div>
        <div class="mean-box">
            <div class="mean-text">{mean}</div>
        </div>
        <div id="status-box" class="status-info" style="background-color:#0288D1;">🔵 랜덤 학습 시작 (1/8)</div>
    </div>
    """, unsafe_allow_html=True)

    # 🔊 8회 반복 및 자동 넘기기 자바스크립트
    is_drive = "true" if st.session_state.drive_mode else "false"
    clean_eng = eng.replace('"', '').replace("'", "")
    
    st.components.v1.html(f"""
        <script>
        function shadowSpeaking() {{
            const engElement = window.parent.document.getElementById('display-eng');
            const soundElement = window.parent.document.getElementById('display-sound');
            const statusElement = window.parent.document.getElementById('status-box');
            
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{clean_eng}");
            msg.lang = 'en-US';
            msg.rate = 0.7; 
            
            var count = 0;
            var isDriveMode = {is_drive};

            msg.onend = function() {{
                count++;
                if (count < 8) {{
                    if (count === 5) {{
                        engElement.classList.add('hidden-content');
                        soundElement.classList.add('hidden-content');
                        statusElement.innerText = "🟣 심화 학습: 소리만 듣기 (" + (count+1) + "/8)";
                        statusElement.style.backgroundColor = "#8E24AA";
                    }} else if (count < 5) {{
                        statusElement.innerText = "🔵 기본 학습: 보고 읽기 (" + (count+1) + "/8)";
                    }}
                    
                    setTimeout(function() {{ 
                        window.speechSynthesis.speak(msg); 
                    }}, 2000);
                }} else {{
                    if(isDriveMode) {{
                        statusElement.innerText = "🚗 운전모드: 3초 후 다음 랜덤 문장 이동";
                        statusElement.style.backgroundColor = "#43A047";
                        setTimeout(function() {{
                            window.parent.document.querySelector('button[kind="primary"]').click();
                        }}, 3000);
                    }} else {{
                        statusElement.innerText = "✅ 8회 완료! 다음 버튼을 누르세요.";
                        statusElement.style.backgroundColor = "#43A047";
                    }}
                }}
            }};
            window.speechSynthesis.speak(msg);
        }}
        shadowSpeaking();
        </script>
    """, height=0)

    # 하단 버튼: 클릭 시 무조건 다음 랜덤 문장으로 이동
    if st.button("다음 랜덤 문장 👉", type="primary"):
        st.session_state.current_idx = random.randint(0, len(sentences) - 1)
        st.rerun()

else:
    st.error("sentences.txt 파일을 찾을 수 없거나 데이터가 비어있습니다.")