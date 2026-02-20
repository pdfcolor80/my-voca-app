import streamlit as st
import os
import time

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 모바일 최적화 레이아웃
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
    .label { color: #adb5bd; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }
    
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
    if not os.path.exists(DATA_FILE):
        return []
    valid_sentences = []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")
            # 데이터가 4개 미만인 줄은 무시하거나 빈 값으로 채워 에러 방지
            if len(parts) >= 4:
                valid_sentences.append(parts[:4])
            elif len(parts) == 3: # 혹시 3개만 있다면 마지막을 빈 뜻으로 채움
                valid_sentences.append(parts + [""])
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
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# --- 메인 로직 ---
if not sentences:
    st.error("데이터 파일이 비어있거나 형식이 잘못되었습니다. '종류|영어|발음|뜻' 형식인지 확인하세요.")
elif st.session_state.current_idx < len(sentences):
    # 안전하게 데이터 가져오기
    current_data = sentences[st.session_state.current_idx]
    kind, eng, sound, mean = current_data
    
    st.progress(st.session_state.current_idx / len(sentences))

    if not st.session_state.show_answer:
        st.markdown(f"""
        <div class="study-card">
            <div class="label">{kind}</div>
            <div class="eng-text">{eng}</div>
            <div class="sound-text">[{sound}]</div>
            <div class="mean-box" style="border: 2px dashed #eee;">
                <span style="color: #eee;">탭하여 확인</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💡 뜻 확인 (소리 재생)", type="secondary", use_container_width=True):
            st.session_state.show_answer = True
            # 소리 재생 스크립트
            st.components.v1.html(f"""
                <script>
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{eng.replace('"', '')}");
                msg.lang = 'en-US';
                msg.rate = 0.8;
                window.speechSynthesis.speak(msg);
                </script>
            """, height=0)
            st.rerun()
    else:
        st.markdown(f"""
        <div class="study-card">
            <div class="label">{kind}</div>
            <div class="eng-text">{eng}</div>
            <div class="sound-text">[{sound}]</div>
            <div class="mean-box mean-visible">
                <div class="mean-text">{mean}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("다음 문장으로 👉", type="primary", use_container_width=True):
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

with st.sidebar:
    if st.button("🔄 기록 초기화"):
        st.session_state.current_idx = 0
        save_progress(0)
        st.rerun()