import streamlit as st
import os
import json
import random

# 파일 경로 설정
DATA_FILE = "sentences.txt"
PROGRESS_FILE = "study_data.json"

st.set_page_config(page_title="영어 패턴 1000 운전모드", layout="centered")

# CSS: 일반 모드와 운전 모드 대응 디자인
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; } /* 운전 시 눈부심 방지 다크모드 배경 */
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
        font-size: calc(2rem + 1.5vw); /* 운전 중 잘 보이게 더 크게 */
        font-weight: bold; 
        line-height: 1.2; 
        min-height: 4em;
        display: flex;
        align-items: center;
        justify-content: center;
        word-break: keep-all;
    }
    .sound-text { color: #388E3C; font-size: 1.5rem; margin-top: 5px; font-weight: 500; opacity: 0.8; }
    .hidden-content { visibility: hidden; }
    .mean-box { 
        padding: 20px; 
        border-radius: 20px; 
        margin-top: 25px;
        background-color: #E3F2FD; 
        border: 1px solid #BBDEFB;
    }
    .mean-text { color: #1565C0; font-size: 2.2rem; font-weight: bold; }
    .status-info { 
        color: #FFFFFF; font-weight: bold; margin-top: 20px; font-size: 1.2rem;
        padding: 15px; border-radius: 15px; text-align: center;
    }
    /* 버튼들 */
    .stButton>button { width: 100%; height: 5rem; border-radius: 25px; font-weight: bold; font-size: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 함수들
def load_sentences():
    if not os.path.exists(DATA_FILE): return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return [line.strip().split("|") for line in f if len(line.strip().split("|")) >= 4]

def load_study_data():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_study_data(data):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_all_ascii=False, indent=4)

def get_next_sentence(sentences, study_data):
    unseen = [i for i in range(len(sentences)) if str(i) not in study_data]
    if unseen: return unseen[0]
    sorted_items = sorted(study_data.items(), key=lambda x: x[1])
    candidates = [int(k) for k, v in sorted_items[:min(20, len(sorted_items))]]
    return random.choice(candidates)

sentences = load_sentences()
study_data = load_study_data()

# 세션 상태 초기화
if "current_idx" not in st.session_state:
    st.session_state.current_idx = get_next_sentence(sentences, study_data)
if "drive_mode" not in st.session_state:
    st.session_state.drive_mode = False

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    st.session_state.drive_mode = st.toggle("🚗 운전 모드 (자동 넘기기)", value=st.session_state.drive_mode)
    st.write("운전 모드에서는 8번 반복 후 3초 뒤 다음 문장으로 자동 이동합니다.")
    if st.button("🔄 기록 초기화"):
        if os.path.exists(PROGRESS_FILE): os.remove(PROGRESS_FILE)
        st.rerun()

# --- 메인 화면 ---
if sentences:
    idx = st.session_state.current_idx
    kind, eng, sound, mean = sentences[idx]
    
    st.progress(idx / len(sentences))
    
    st.markdown(f"""
    <div class="study-card">
        <div style="color:#adb5bd; font-weight:bold;">{kind}</div>
        <div id="display-eng" class="eng-text">{eng}</div>
        <div id="display-sound" class="sound-text">[{sound}]</div>
        <div class="mean-box">
            <div class="mean-text">{mean}</div>
        </div>
        <div id="status-box" class="status-info" style="background-color:#0288D1;">🔵 학습 시작</div>
    </div>
    """, unsafe_allow_html=True)

    # 🔊 자동 넘기기 로직이 포함된 자바스크립트
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
                        statusElement.innerText = "🟣 심화 학습 (" + (count+1) + "/8)";
                        statusElement.style.backgroundColor = "#8E24AA";
                    }} else if (count < 5) {{
                        statusElement.innerText = "🔵 기본 학습 (" + (count+1) + "/8)";
                    }}
                    setTimeout(function() {{ window.speechSynthesis.speak(msg); }}, 2000);
                }} else {{
                    statusElement.innerText = isDriveMode ? "🚗 운전모드: 3초 후 다음 문장 이동" : "✅ 완료! 난이도를 선택하세요.";
                    statusElement.style.backgroundColor = "#43A047";
                    
                    if(isDriveMode) {{
                        setTimeout(function() {{
                            // Streamlit의 hidden button을 클릭하여 다음 문장으로 이동
                            window.parent.document.querySelector('button[kind="primary"]').click();
                        }}, 3000);
                    }}
                }}
            }};
            window.speechSynthesis.speak(msg);
        }}
        shadowSpeaking();
        </script>
    """, height=0)

    # 하단 컨트롤
    if st.session_state.drive_mode:
        # 운전 모드일 때 자동으로 클릭될 보이지 않는 버튼
        if st.button("Next (Auto)", type="primary", key="auto_next"):
            # 운전 모드에서는 자동으로 '쉬움' 점수를 주고 넘어감
            study_data[str(idx)] = study_data.get(str(idx), 0) + 1
            save_study_data(study_data)
            st.session_state.current_idx = get_next_sentence(sentences, study_data)
            st.rerun()
    else:
        # 일반 모드: 난이도 선택 버튼
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔴 어려워요"):
                study_data[str(idx)] = study_data.get(str(idx), 0) - 1
                save_study_data(study_data)
                st.session_state.current_idx = get_next_sentence(sentences, study_data)
                st.rerun()
        with col2:
            if st.button("🟢 쉬워요"):
                study_data[str(idx)] = study_data.get(str(idx), 0) + 1
                save_study_data(study_data)
                st.session_state.current_idx = get_next_sentence(sentences, study_data)
                st.rerun()