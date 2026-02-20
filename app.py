import streamlit as st
import os

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 모바일 및 PC 최적화 레이아웃
st.set_page_config(page_title="영어 패턴 1000", layout="centered")

# CSS: 탭 위치 고정 및 디자인
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .study-card {
        background-color: #ffffff;
        padding: 30px 20px;
        border-radius: 25px;
        border: 1px solid #dee2e6;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        min-height: 320px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .eng-text { color: #D32F2F; font-size: 2.4rem; font-weight: bold; line-height: 1.2; }
    .sound-text { color: #2E7D32; font-size: 1.2rem; margin-top: 8px; font-weight: 500; }
    .mean-box { 
        padding: 15px; 
        border-radius: 15px; 
        margin-top: 15px;
        min-height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .mean-visible { background-color: #E3F2FD; border: 2px solid #2196F3; width: 100%; }
    .mean-text { color: #1565C0; font-size: 1.8rem; font-weight: bold; }
    
    /* 공통 버튼 스타일 */
    .stButton>button { 
        width: 100%; 
        height: 4.5rem; 
        font-size: 1.4rem !important; 
        border-radius: 20px; 
        font-weight: bold;
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
                return int(f.read().strip())
        except: return 0
    return 0

sentences = load_sentences()

if "current_idx" not in st.session_state:
    st.session_state.current_idx = load_progress()
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# --- 메인 화면 로직 ---
if sentences and st.session_state.current_idx < len(sentences):
    kind, eng, sound, mean = sentences[st.session_state.current_idx]
    
    st.progress(st.session_state.current_idx / len(sentences))

    # 카드 표시
    if not st.session_state.show_answer:
        st.markdown(f"""
        <div class="study-card">
            <div style="color:#adb5bd; font-weight:bold; font-size:0.8rem;">{kind}</div>
            <div class="eng-text">{eng}</div>
            <div class="sound-text">[{sound}]</div>
            <div class="mean-box" style="border: 2px dashed #eee;">
                <span style="color: #eee;">탭하여 확인</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 버튼을 누르면 '소리를 먼저 재생하고' 화면을 바꿉니다.
        if st.button("💡 뜻 확인 & 소리 듣기"):
            # 자바스크립트를 사용해 소리를 직접 실행
            js = f"""
            <script>
                function speak() {{
                    window.speechSynthesis.cancel();
                    var msg = new SpeechSynthesisUtterance("{eng.replace('"', '').replace("'", "")}");
                    msg.lang = 'en-US';
                    msg.rate = 0.9;
                    window.speechSynthesis.speak(msg);
                }}
                speak();
            </script>
            """
            st.components.v1.html(js, height=0)
            
            # 상태 변경
            st.session_state.show_answer = True
            st.rerun()
            
    else:
        st.markdown(f"""
        <div class="study-card">
            <div style="color:#adb5bd; font-weight:bold; font-size:0.8rem;">{kind}</div>
            <div class="eng-text">{eng}</div>
            <div class="sound-text">[{sound}]</div>
            <div class="mean-box mean-visible">
                <div class="mean-text">{mean}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("다음 문장으로 👉"):
            st.session_state.current_idx += 1
            st.session_state.show_answer = False
            save_progress(st.session_state.current_idx)
            st.rerun()

else:
    st.balloons()
    st.success("🎉 모든 문장을 완료했습니다!")
    if st.button("처음부터 다시 시작"):
        st.session_state.current_idx = 0
        save_progress(0)
        st.rerun()