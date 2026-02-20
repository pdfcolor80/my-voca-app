import streamlit as st
import os

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 모바일 최적화 설정
st.set_page_config(page_title="영어 패턴 1000", layout="centered")

# CSS: 단계별 화면 제어 및 한 줄 최적화
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .study-card {
        background-color: #ffffff;
        padding: 30px 15px;
        border-radius: 30px;
        border: 1px solid #e9ecef;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        min-height: 420px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* 영어 및 발음 텍스트 스타일 */
    .eng-text { 
        color: #D32F2F; 
        font-size: calc(1.6rem + 1.2vw); 
        font-weight: bold; 
        line-height: 1.2; 
        margin-bottom: 10px;
        word-break: keep-all;
        min-height: 3.5em;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .sound-text { 
        color: #388E3C; 
        font-size: 1.3rem; 
        margin-top: 5px; 
        font-weight: 500; 
        opacity: 0.8;
        min-height: 1.5em;
    }
    
    /* 6~8회차에서 숨길 요소들 */
    .hidden-content {
        visibility: hidden;
    }
    
    .mean-box { 
        padding: 20px; 
        border-radius: 20px; 
        margin-top: 25px;
        background-color: #E3F2FD; 
        border: 1px solid #BBDEFB;
        width: 100%;
    }
    .mean-text { color: #1565C0; font-size: 1.9rem; font-weight: bold; }
    
    .label { color: #adb5bd; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
    
    .stButton>button { 
        width: 100%; 
        height: 4.8rem; 
        font-size: 1.5rem !important; 
        border-radius: 25px; 
        font-weight: bold;
        background: linear-gradient(135deg, #424242 0%, #212121 100%);
        color: white;
        border: none;
    }
    
    /* 하단 상태 바 */
    .status-info { 
        color: #FFFFFF; 
        font-weight: bold; 
        margin-top: 20px; 
        font-size: 1.1rem;
        background-color: #0288D1;
        padding: 12px;
        border-radius: 15px;
        transition: all 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

def load_sentences():
    if not os.path.exists(DATA_FILE): return []
    valid_sentences = []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 4: valid_sentences.append(parts[:4])
    return valid_sentences

def save_progress(index):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        f.write(str(index))

def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return int(content) if content else 0
        except: return 0
    return 0

sentences = load_sentences()

if "current_idx" not in st.session_state:
    st.session_state.current_idx = load_progress()

# --- 메인 학습 화면 ---
if sentences and st.session_state.current_idx < len(sentences):
    kind, eng, sound, mean = sentences[st.session_state.current_idx]
    
    st.progress(st.session_state.current_idx / len(sentences))
    
    # UI 구성 (ID 부여로 자바스크립트 제어)
    st.markdown(f"""
    <div class="study-card">
        <div class="label">{kind}</div>
        <div id="display-eng" class="eng-text">{eng}</div>
        <div id="display-sound" class="sound-text">[{sound}]</div>
        <div class="mean-box">
            <div class="mean-text">{mean}</div>
        </div>
        <div id="status-box" class="status-info">🔵 기본 학습: 보고 따라하기 (1/8)</div>
    </div>
    """, unsafe_allow_html=True)

    # 🔊 0.7배속 + 총 8회 반복 + 6회차부터 영어/발음 숨김
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
            msg.onend = function() {{
                count++;
                if (count < 8) {{
                    // 6회차(인덱스 5)부터 영어와 발음 숨김
                    if (count === 5) {{
                        engElement.classList.add('hidden-content');
                        soundElement.classList.add('hidden-content');
                        statusElement.innerText = "🟣 심화 학습: 소리만 듣고 쉐도잉 (" + (count+1) + "/8)";
                        statusElement.style.backgroundColor = "#8E24AA";
                    }} else if (count < 5) {{
                        statusElement.innerText = "🔵 기본 학습: 보고 따라하기 (" + (count+1) + "/8)";
                    }} else {{
                        statusElement.innerText = "🟣 심화 학습: 소리만 듣고 쉐도잉 (" + (count+1) + "/8)";
                    }}
                    
                    setTimeout(function() {{
                        window.speechSynthesis.speak(msg);
                    }}, 2000);
                }} else {{
                    statusElement.innerText = "✅ 8회 완료! 다음 문장으로 넘어가세요.";
                    statusElement.style.backgroundColor = "#43A047";
                }}
            }};
            
            // 초기화
            engElement.classList.remove('hidden-content');
            soundElement.classList.remove('hidden-content');
            window.speechSynthesis.speak(msg);
        }}
        shadowSpeaking();
        </script>
    """, height=0)

    if st.button("다음 문장으로 👉"):
        st.session_state.current_idx += 1
        save_progress(st.session_state.current_idx)
        st.rerun()

else:
    st.balloons()
    st.success("🎉 1,000문장 정복 완료!")
    if st.button("처음부터 다시 시작"):
        st.session_state.current_idx = 0
        save_progress(0)
        st.rerun()

with st.sidebar:
    st.write(f"진행도: {st.session_state.current_idx + 1} / {len(sentences)}")
    if st.button("🔄 기록 초기화"):
        st.session_state.current_idx = 0
        save_progress(0)
        st.rerun()