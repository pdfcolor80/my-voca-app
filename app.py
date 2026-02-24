import streamlit as st
import os
import random

# 파일 경로 설정
DATA_FILE = "sentences.txt"

st.set_page_config(page_title="현실 영어 쉐도잉", layout="centered")

# --- CSS: 상단 여백 제거 및 현실 텍스트 UI ---
st.markdown("""
    <style>
    /* 상단 여백 및 헤더 제거 */
    [data-testid="stAppViewContainer"] { padding-top: 0px !important; }
    [data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 0px !important; margin-top: -75px !important; }
    
    .main { background-color: #ffffff; }

    .study-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 25px rgba(0,0,0,0.06);
        border: 1px solid #f0f0f0;
        min-height: 85vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* 상황 설명 (현실 버전 강조) */
    .context-box {
        background-color: #fdf2f2; /* 연한 레드 배경 */
        border-radius: 15px;
        padding: 18px;
        margin-bottom: 30px;
        text-align: left;
        border-left: 6px solid #E53935;
    }
    .context-tag { 
        color: #E53935; 
        font-weight: 800; 
        font-size: 0.85rem; 
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .context-text { 
        color: #1a1a1a; 
        font-size: 1.15rem; 
        line-height: 1.5; 
        font-weight: 600;
        word-break: keep-all;
    }

    /* 영어 문장 및 발음 */
    .eng-text-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-bottom: 5px; }
    .char-normal { color: #000000; font-size: 2rem; font-weight: 700; }
    .char-accent { color: #E53935; font-size: 2.3rem; font-weight: 900; text-decoration: underline; }
    
    .sound-text { color: #999; font-size: 1.2rem; margin-bottom: 25px; font-style: italic; }

    /* 뜻 설명 박스 */
    .mean-box { 
        padding: 15px; 
        background-color: #000000; 
        border-radius: 12px; 
        margin-bottom: 25px;
    }
    .mean-text { color: #ffffff; font-size: 1.6rem; font-weight: 800; }
    
    .status-info { font-size: 1.2rem; color: #E53935; font-weight: bold; margin-bottom: 20px; }
    
    /* 버튼 스타일 */
    .stButton>button { 
        width: 100%; height: 5rem; border-radius: 15px; font-weight: bold; font-size: 1.4rem !important;
        background-color: #E53935 !important; color: white !important; border: none;
        box-shadow: 0 4px 15px rgba(229, 57, 53, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

def get_accented_html(text):
    words = text.split()
    vowels = "aeiouAEIOU"
    html_output = ""
    for word in words:
        html_output += '<div style="display: flex; align-items: flex-end;">'
        accented = False
        for char in word:
            if not accented and char in vowels and len(word) > 2:
                html_output += f'<span class="char-accent">{char}</span>'
                accented = True
            else:
                html_output += f'<span class="char-normal">{char}</span>'
        html_output += '</div>&nbsp;'
    return html_output

def load_sentences():
    if not os.path.exists(DATA_FILE): return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = []
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 4:
                # 상황 설명이 없으면 기본값
                if len(parts) < 5: parts.append("원어민이 이 말을 할 때의 표정을 떠올려보세요!")
                data.append(parts)
        return data

all_sentences = load_sentences()

with st.sidebar:
    st.header("⚙️ 앱 설정")
    study_mode = st.radio("학습 모드", ["1단계: 숙어", "2단계: 패턴"])
    st.session_state.drive_mode = st.toggle("🚗 운전 모드", False)
    target_cat = "숙어" if "숙어" in study_mode else "패턴"
    filtered_data = [s for s in all_sentences if s[0] == target_cat]

if filtered_data:
    if "current_idx" not in st.session_state or st.session_state.get('last_cat') != target_cat:
        st.session_state.current_idx = random.randint(0, len(filtered_data) - 1)
        st.session_state.last_cat = target_cat

    idx = st.session_state.current_idx
    _, eng, sound, mean, context = filtered_data[idx]

    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    
    # --- 현실적 상황 설명 영역 ---
    st.markdown(f"""
        <div class="context-box">
            <div class="context-tag">Real Context</div>
            <div class="context-text">{context}</div>
        </div>
    """, unsafe_allow_html=True)

    # 뜻 박스 (블랙 배경에 화이트 텍스트로 강조)
    st.markdown(f'<div class="mean-box"><div class="mean-text">{mean}</div></div>', unsafe_allow_html=True)

    # 영어 텍스트
    st.markdown(f"""
        <div>
            <div id="display-eng" class="eng-text-container">{get_accented_html(eng)}</div>
            <div id="display-sound" class="sound-text">[{sound}]</div>
            <div id="status-box" class="status-info">쉐도잉 시작하기</div>
        </div>
    """, unsafe_allow_html=True)

    # JS 쉐도잉 로직
    is_drive = "true" if st.session_state.drive_mode else "false"
    clean_eng = eng.replace('"', '').replace("'", "")
    
    st.components.v1.html(f"""
        <script>
        function start() {{
            const engEl = window.parent.document.getElementById('display-eng');
            const soundEl = window.parent.document.getElementById('display-sound');
            const statusEl = window.parent.document.getElementById('status-box');
            
            engEl.style.opacity = "1";
            soundEl.style.opacity = "1";
            window.speechSynthesis.cancel();
            
            let count = 0;
            const isDrive = {is_drive};
            function speak() {{
                let msg = new SpeechSynthesisUtterance("{clean_eng}");
                msg.lang = 'en-US';
                
                if (count < 5) {{ 
                    msg.rate = 0.6; 
                    statusEl.innerText = "Step 1: 듣기 👂 (" + (count+1) + "/13)"; 
                }}
                else if (count < 10) {{ 
                    msg.rate = 0.9; 
                    statusEl.innerText = "Step 2: 따라하기 🗣️ (" + (count+1) + "/13)"; 
                }}
                else {{ 
                    msg.rate = 1.0; 
                    engEl.style.opacity = "0"; 
                    soundEl.style.opacity = "0"; 
                    statusEl.innerText = "Step 3: 안보고 말하기 🔥 (" + (count+1) + "/13)"; 
                }}
                
                msg.onend = function() {{
                    count++;
                    if (count < 13) {{ setTimeout(speak, 1500); }}
                    else {{
                        statusEl.innerText = isDrive ? "🚗 3초 뒤 다음 문장..." : "✅ 오늘 한 문장 마스터!";
                        if(isDrive) {{
                            setTimeout(() => {{
                                const buttons = window.parent.document.querySelectorAll('button');
                                for (let btn of buttons) {{ if (btn.innerText.includes("다음")) {{ btn.click(); break; }} }}
                            }}, 3000);
                        }}
                    }}
                }};
                window.speechSynthesis.speak(msg);
            }}
            speak();
        }}
        window.parent.document.querySelectorAll('button').forEach(btn => {{
            if (btn.innerText.includes("다음")) {{ btn.onclick = () => {{ setTimeout(start, 500); }}; }}
        }});
        </script>
    """, height=0)

    if st.button("다음 랜덤 문장 👉", type="primary"):
        st.session_state.current_idx = random.randint(0, len(filtered_data) - 1)
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)