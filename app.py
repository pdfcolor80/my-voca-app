import streamlit as st
import os
import random

# 파일 경로 설정
DATA_FILE = "sentences.txt"

# 모바일 최적화 설정
st.set_page_config(page_title="영어 패턴 1000 AI", layout="centered")

# CSS: 강조 효과 및 애니메이션 레이아웃
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
        transition: all 0.5s ease;
        border: 5px solid #eee;
    }
    
    /* 강조 테두리 */
    .border-step1 { border-color: #FF9800 !important; }
    .border-step2 { border-color: #0288D1 !important; }
    .border-step3 { border-color: #9C27B0 !important; }
    .border-done { border-color: #4CAF50 !important; }

    /* 단어별 강조를 위한 컨테이너 */
    .eng-text-container { 
        min-height: 5em;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 10px;
    }
    
    /* 기본 단어 스타일 */
    .word-span {
        color: #555;
        font-size: 1.8rem;
        font-weight: bold;
        transition: all 0.2s ease;
        display: inline-block;
    }
    
    /* 🔊 강조 시 (높낮이 강조) */
    .word-active {
        color: #D32F2F !important;
        font-size: 2.6rem !important;
        transform: translateY(-10px) scale(1.1);
        text-shadow: 0 4px 10px rgba(211,47,47,0.3);
    }
    
    .sound-text { 
        color: #388E3C; 
        font-size: 1.3rem; 
        margin-top: 5px; 
        font-weight: 500; 
        opacity: 0.8;
    }
    .hidden-content { visibility: hidden !important; }
    
    .mean-box { 
        padding: 20px; 
        border-radius: 20px; 
        margin-top: 25px;
        background-color: #E3F2FD; 
        width: 100%;
    }
    .mean-text { color: #1565C0; font-size: 1.9rem; font-weight: bold; }
    
    .status-info { 
        color: #FFFFFF; font-weight: bold; margin-top: 20px; font-size: 1.1rem;
        padding: 15px; border-radius: 15px; text-align: center;
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
    st.header("⚙️ 학습 설정")
    st.session_state.drive_mode = st.toggle("🚗 운전 모드 (자동 넘기기)", value=st.session_state.drive_mode)
    if st.button("🎲 다른 문장 랜덤"):
        st.session_state.current_idx = random.randint(0, len(sentences) - 1)
        st.rerun()

if sentences:
    idx = st.session_state.current_idx
    kind, eng, sound, mean = sentences[idx]
    
    # 단어별로 분리하여 HTML 생성 (높낮이 강조용)
    words_html = "".join([f'<span class="word-span">{w}</span>' for w in eng.split()])
    
    st.markdown(f"""
    <div id="main-card" class="study-card border-step1">
        <div style="color:#adb5bd; font-weight:bold; font-size:0.9rem;">{kind}</div>
        <div id="display-eng" class="eng-text-container">
            {words_html}
        </div>
        <div id="display-sound" class="sound-text">[{sound}]</div>
        <div class="mean-box">
            <div class="mean-text">{mean}</div>
        </div>
        <div id="status-box" class="status-info" style="background-color:#FF9800;">🐌 1단계: 초저속 (1/13)</div>
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
            const wordSpans = engContainer.getElementsByClassName('word-span');
            
            engContainer.classList.remove('hidden-content');
            soundEl.classList.remove('hidden-content');
            
            window.speechSynthesis.cancel();
            
            let count = 0;
            const total = 13;
            const isDrive = {is_drive};

            function speak() {{
                let msg = new SpeechSynthesisUtterance("{clean_eng}");
                msg.lang = 'en-US';
                
                // 속도 설정
                if (count < 5) {{
                    msg.rate = 0.5;
                    card.className = "study-card border-step1";
                    statusEl.innerText = "🐌 1단계: 초저속 강조 (" + (count+1) + "/13)";
                    statusEl.style.backgroundColor = "#FF9800";
                }} else if (count < 10) {{
                    msg.rate = 0.8;
                    card.className = "study-card border-step2";
                    statusEl.innerText = "🔵 2단계: 표준 강조 (" + (count+1) + "/13)";
                    statusEl.style.backgroundColor = "#0288D1";
                }} else {{
                    msg.rate = 0.8;
                    engContainer.classList.add('hidden-content');
                    soundEl.classList.add('hidden-content');
                    card.className = "study-card border-step3";
                    statusEl.innerText = "🟣 3단계: 소리 집중 (" + (count+1) + "/13)";
                    statusEl.style.backgroundColor = "#9C27B0";
                }}

                // 🔊 단어별 강조 (높낮이 시뮬레이션) 애니메이션
                msg.onboundary = function(event) {{
                    if (event.name === 'word') {{
                        // 모든 단어 초기화
                        for (let s of wordSpans) s.classList.remove('word-active');
                        
                        // 현재 읽는 단어 찾기
                        const wordIdx = getWordIndexAtOffset("{clean_eng}", event.charIndex);
                        if (wordSpans[wordIdx]) {{
                            wordSpans[wordIdx].classList.add('word-active');
                        }}
                    }}
                }};

                msg.onend = function() {{
                    for (let s of wordSpans) s.classList.remove('word-active');
                    count++;
                    if (count < total) {{
                        setTimeout(speak, 2000);
                    }} else {{
                        card.className = "study-card border-done";
                        statusEl.innerText = isDrive ? "🚗 3초 후 이동" : "✅ 13회 완료!";
                        statusEl.style.backgroundColor = "#43A047";
                        if(isDrive) setTimeout(() => {{ window.parent.document.querySelector('button[kind="primary"]').click(); }}, 3000);
                    }}
                }};
                window.speechSynthesis.speak(msg);
            }}

            // 텍스트 오프셋으로 몇 번째 단어인지 계산하는 함수
            function getWordIndexAtOffset(text, offset) {{
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