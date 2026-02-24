import streamlit as st
import os
import random

# 파일 경로 설정
DATA_FILE = "sentences.txt"

st.set_page_config(page_title="영어 시네마 쉐도잉", layout="centered")

# --- CSS: 다크 모드 시네마틱 UI ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    
    .study-card {
        background-color: #1c1e21;
        padding: 15px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        border: 1px solid #333;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 85vh; 
    }
    
    .video-container {
        width: 100%;
        border-radius: 15px;
        margin-bottom: 15px;
        overflow: hidden;
        border: 2px solid #444;
    }
    
    .eng-text-container { 
        display: flex; flex-wrap: wrap; align-items: center; justify-content: center; 
        gap: 5px; margin-bottom: 10px; 
    }
    .char-normal { color: #eee; font-size: 1.5rem; font-weight: 500; }
    .char-accent { color: #FFD700; font-size: 1.8rem; font-weight: 800; text-decoration: underline; }
    
    .sound-text { color: #aaa; font-size: 1rem; margin-bottom: 10px; font-style: italic; }
    
    .mean-box { 
        padding: 15px; 
        background-color: #2c2f33; 
        border-radius: 15px;
        margin-bottom: 15px;
    }
    .mean-text { color: #4dabf7; font-size: 1.4rem; font-weight: bold; }
    
    .status-info { font-size: 1rem; color: #ff6b6b; font-weight: bold; margin-bottom: 10px; }
    
    .stButton>button { 
        width: 100%; height: 4.5rem; border-radius: 12px; font-weight: bold; font-size: 1.2rem !important;
        background-color: #f03e3e !important; color: white !important; border: none;
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
        # 마지막 항목이 유튜브 ID라고 가정 (없으면 기본 검색어 활용)
        return [line.strip().split("|") for line in f if len(line.strip().split("|")) >= 4]

all_sentences = load_sentences()

with st.sidebar:
    st.header("🎬 쉐도잉 설정")
    study_mode = st.radio("단계", ["1단계: 숙어", "2단계: 패턴"])
    st.session_state.drive_mode = st.toggle("🚗 운전 모드", value=st.session_state.get('drive_mode', False))
    target_cat = "숙어" if "숙어" in study_mode else "패턴"
    filtered_data = [s for s in all_sentences if s[0] == target_cat]

if filtered_data:
    if "current_idx" not in st.session_state or st.session_state.get('last_cat') != target_cat:
        st.session_state.current_idx = random.randint(0, len(filtered_data) - 1)
        st.session_state.last_cat = target_cat

    idx = st.session_state.current_idx
    row = filtered_data[idx]
    
    # 데이터 구조: 카테고리|영어|발음|뜻|유튜브ID(선택)
    cat, eng, sound, mean = row[0], row[1], row[2], row[3]
    yt_id = row[4] if len(row) > 4 else None

    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    
    # --- 미디어 영역: 오직 유튜브 영상만 ---
    st.markdown('<div class="video-container">', unsafe_allow_html=True)
    if yt_id:
        # 특정 영상 ID가 있는 경우 해당 영상 재생
        st.video(f"https://www.youtube.com/watch?v={yt_id}")
    else:
        # ID가 없는 경우 유튜브에서 해당 숙어의 영화 장면을 검색하여 보여줌
        search_url = f"https://www.youtube.com/results?search_query={eng.replace(' ', '+')}+movie+scene"
        st.info(f"📺 '{eng}' 관련 영상을 검색 중입니다...")
        st.video(f"https://www.youtube.com/embed?listType=search&list={eng}+movie+scene")
    st.markdown('</div>', unsafe_allow_html=True)

    # 텍스트 정보 영역
    st.markdown(f"""
        <div>
            <div id="display-eng" class="eng-text-container">{get_accented_html(eng)}</div>
            <div id="display-sound" class="sound-text">[{sound}]</div>
            <div class="mean-box"><div class="mean-text">{mean}</div></div>
            <div id="status-box" class="status-info">준비 완료</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # JS 학습 로직 (음성 반복 및 가림 효과)
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
                
                if (count < 5) {{ 
                    msg.rate = 0.6; 
                    statusEl.innerText = "Step 1: 저속 반복 (" + (count+1) + "/13)"; 
                }} else if (count < 10) {{ 
                    msg.rate = 0.9; 
                    statusEl.innerText = "Step 2: 정상 반복 (" + (count+1) + "/13)"; 
                }} else {{ 
                    msg.rate = 0.9; 
                    engEl.classList.add('hidden-content'); 
                    soundEl.classList.add('hidden-content'); 
                    statusEl.innerText = "Step 3: 장면 연상 쉐도잉 (" + (count+1) + "/13)"; 
                }}

                msg.onend = function() {{
                    count++;
                    if (count < 13) {{ 
                        setTimeout(speak, 1500); 
                    }} else {{
                        statusEl.innerText = isDrive ? "🚗 3초 후 다음 장면..." : "✅ 학습 완료";
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
            if (btn.innerText.includes("다음")) {{ 
                btn.onclick = () => {{ setTimeout(start, 500); }}; 
            }}
        }});
        </script>
    """, height=0)

    if st.button("다음 랜덤 장면 👉", type="primary"):
        st.session_state.current_idx = random.randint(0, len(filtered_data) - 1)
        st.rerun()