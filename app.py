import streamlit as st
import os

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 모바일 최적화 설정
st.set_page_config(page_title="영어 패턴 1000", layout="centered")

# CSS: 단계별 화면 변화 및 글자 최적화
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
        min-height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* 영어 텍스트 스타일 */
    .eng-text { 
        color: #D32F2F; 
        font-size: calc(1.6rem + 1.2vw); 
        font-weight: bold; 
        line-height: 1.2; 
        margin-bottom: 10px;
        word-break: keep-all;
        min-height: 4em; /* 높이 고정으로 화면 흔들림 방지 */
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* 3~5회차에서 영어를 숨길 때 사용할 클래스 */
    .hidden-text {
        visibility: hidden;
    }
    
    .sound-text { color: #388E3C; font-size: 1.2rem; margin-top: 5px; font-weight: 500; opacity: 0.8; }
    
    .mean-box { 
        padding: 20px; 
        border-radius: 20px; 
        margin-top: 25px;
        background-color: #E3F2FD; 
        border: 1px solid #BBDEFB;
        width: 100%;
    }
    .mean-text { color: #1565C0; font-size: 1.8rem; font-weight: bold; }
    
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
    
    /* 현재 상태 안내 박스 */
    .status-info { 
        color: #FFFFFF; 
        font-weight: bold; 
        margin-top: 15px; 
        font-size: 1.1rem;
        background-color: #FF5722;
        padding: 10px;
        border-radius: 15px;
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
    
    # 💡 JavaScript에서 화면의 텍스트를 직접 제어하기 위해 ID를 부여함
    st.markdown(f"""
    <div class="study-card">
        <div class="label">{kind}</div>
        <div id="display-eng" class="eng-text">{eng}</div>
        <div class="sound-text">[{sound}]</div>
        <div class="mean-box">
            <div class="mean-text">{mean}</div>
        </div>
        <div id="status-box" class="status-info">🎧 1단계: 보고 따라하기 (1/5)</div>
    </div>
    """, unsafe_allow_html=True)

    # 🔊 0.7배속 연음 + 5회 반복 + 단계별 가리기 스크립트
    clean_eng = eng.replace('"', '').replace("'", "")
    
    st.components.v1.html(f"""
        <script>
        function shadowSpeaking() {{
            const engElement = window.parent.document.getElementById('display-eng');
            const statusElement = window.parent.document.getElementById('status-box');
            
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{clean_eng}");
            msg.lang = 'en-US';
            msg.rate = 0.7; 
            
            var count = 0;
            msg.onend = function() {{
                count++;
                if (count < 5) {{
                    // 단계별 화면 제어 로직
                    if (count === 2) {{
                        // 3회차부터 영어 숨김
                        engElement.classList.add('hidden-text');
                        statusElement.innerText = "🔇 2단계: 소리만 듣고 맞추기 (" + (count+1) + "/5)";
                        statusElement.style.backgroundColor = "#9C27B0";
                    }} else {{
                        statusElement.innerText = (count < 2 ? "🎧 1단계: 보고 따라하기 (" : "🔇 2단계: 소리만 듣고 맞추기 (") + (count+1) + "/5)";
                    }}
                    
                    setTimeout(function() {{
                        window.speechSynthesis.speak(msg);
                    }}, 2000);
                }} else {{
                    statusElement.innerText = "✅ 학습 완료! 다음 버튼을 누르세요.";
                    statusElement.style.backgroundColor = "#4CAF50";
                }}
            }};
            
            // 시작 상태 설정
            engElement.classList.remove('hidden-text');
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