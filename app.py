import streamlit as st
import os
import random

# 파일 및 이미지 경로 설정
DATA_FILE = "sentences.txt"
IMAGE_DIR = "images" 

st.set_page_config(page_title="영어 이미지 연상", layout="centered")

# --- CSS: 스마트폰 한 화면(No Scroll) 최적화 ---
st.markdown("""
    <style>
    /* 전체 배경 및 여백 제거 */
    .main { background-color: #fdfdfd; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    
    .study-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        /* 화면 높이에 맞게 유연하게 조절 */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 80vh; 
    }
    
    /* 이미지 크기 고정 및 최적화 */
    .image-box {
        width: 100%;
        height: 180px; 
        background-color: #f9f9f9;
        border-radius: 15px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .image-box img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
    
    /* 텍스트 크기 조절 (한 화면에 들어오도록) */
    .eng-text-container { 
        display: flex; flex-wrap: wrap; align-items: center; justify-content: center; 
        gap: 5px; margin-bottom: 5px; 
    }
    .char-normal { color: #333; font-size: 1.4rem; font-weight: 500; }
    .char-accent { color: #E53935; font-size: 1.7rem; font-weight: 800; text-decoration: underline; }
    
    .sound-text { color: #888; font-size: 0.9rem; margin-bottom: 10px; font-style: italic; }
    
    .mean-box { 
        padding: 12px; 
        background-color: #f8faff; 
        border-radius: 15px;
        margin-bottom: 10px;
    }
    .mean-text { color: #1a73e8; font-size: 1.3rem; font-weight: bold; }
    
    .status-info { font-size: 0.9rem; color: #d32f2f; font-weight: bold; margin-bottom: 10px; }
    
    /* 하단 버튼 고정 */
    .stButton>button { 
        width: 100%; height: 4rem; border-radius: 12px; font-weight: bold; font-size: 1.1rem !important;
        background-color: #333 !important; color: white !important; 
    }
    
    .hidden-content { display: none !important; }
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

all_sentences = load_sentences()

# 사이드바 설정 (모바일에서는 접혀있음)
with st.sidebar:
    st.header("🎯 설정")
    study_mode = st.radio("단계", ["1단계: 숙어", "2단계: 패턴"])
    st.session_state.drive_mode = st.toggle("🚗 운전 모드", value=st.session_state.get('drive_mode', False))
    target_cat = "숙어" if "숙어" in study_mode else "패턴"
    filtered_data = [s for s in all_sentences if s[0] == target_cat]

if filtered_data:
    if "current_idx" not in st.session_state or st.session_state.get('last_cat') != target_cat:
        st.session_state.current_idx = random.randint(0, len(filtered_data) - 1)
        st.session_state.last_cat = target_cat

    idx = st.session_state.current_idx
    _, eng, sound, mean = filtered_data[idx]
    
    img_filename = eng.lower().replace(" ", "_").replace("'", "") + ".jpg"
    img_path = os.path.join(IMAGE_DIR, img_filename)
    
    # 카드 레이아웃 시작
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    
    # 1. 이미지 영역
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.markdown(f'<div class="image-box" style="color:#ccc; font-size:0.8rem;">이미지 준비 중<br>({img_filename})</div>', unsafe_allow_html=True)

    # 2. 영어/발음/뜻/상태 영역
    st.markdown(f"""
        <div>
            <div id="display-eng" class="eng-text-container">{get_accented_html(eng)}</div>
            <div id="display-sound" class="sound-text">[{sound}]</div>
            <div class="mean-box"><div class="mean-text">{mean}</div></div>
            <div id="status-box" class="status-info">준비 완료</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 카드 레이아웃 끝
    st.markdown('</div>', unsafe_allow_html=True)

    # JS 로직 (중괄호 에러 수정 완료)
    is_drive = "true" if st.session_state.drive_mode else "false"
    clean_eng = eng.replace('"', '').replace("'", "")
    
    st.components.v1.html(f"""
        <script>
        function start() {{
            const engEl = window.parent.document.getElementById('display-eng');
            const soundEl = window.parent.document.getElementById('display-sound');
            const statusEl = window.parent.document.getElementById('status-box');
            engEl.classList.remove('hidden-content');
            soundEl.classList.remove('hidden-content');
            window.speechSynthesis.cancel();
            let count = 0;
            const isDrive = {is_drive};
            function speak() {{
                let msg = new SpeechSynthesisUtterance("{clean_eng}");
                msg.lang = 'en-US';
                if (count < 5) {{ msg.rate = 0.5; statusEl.innerText = "Step 1: 느리게 (" + (count+1) + "/13)"; }}
                else if (count < 10) {{ msg.rate = 0.8; statusEl.innerText = "Step 2: 반복 (" + (count+1) + "/13)"; }}
                else {{ 
                    msg.rate = 0.8; engEl.classList.add('hidden-content'); soundEl.classList.add('hidden-content'); 
                    statusEl.innerText = "Step 3: 쉐도잉 (" + (count+1) + "/13)"; 
                }}
                msg.onend = function() {{
                    count++;
                    if (count < 13) {{ setTimeout(speak, 1200); }}
                    else {{
                        statusEl.innerText = isDrive ? "🚗 다음으로..." : "✅ 완료";
                        if(isDrive) {{
                            setTimeout(() => {{
                                const buttons = window.parent.document.querySelectorAll('button');
                                for (let btn of buttons) {{ if (btn.innerText.includes("다음")) {{ btn.click(); break; }} }}
                            }}, 2000);
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

    # 3. 하단 버튼
    if st.button("다음 랜덤 문장 👉", type="primary"):
        st.session_state.current_idx = random.randint(0, len(filtered_data) - 1)
        st.rerun()