import streamlit as st
import os
import random

# 파일 경로 설정
DATA_FILE = "sentences.txt"

st.set_page_config(page_title="현실 영어 쉐도잉 퀴즈", layout="centered")

# --- CSS: 여백 완전 제거 및 버튼 내 발음 스타일 ---
st.markdown("""
    <style>
    /* 1. 상단 여백 및 헤더 완전 박멸 */
    [data-testid="stAppViewContainer"] { padding-top: 0px !important; }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .main .block-container { 
        padding-top: 0px !important; 
        margin-top: -100px !important; /* 위로 바짝 붙임 */
        padding-bottom: 0px !important;
    }
    
    .main { background-color: #ffffff; }

    /* 퀴즈 카드 */
    .quiz-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        min-height: 90vh;
    }

    /* 상황 설명 상자 */
    .context-box {
        background-color: #000000;
        color: #ffffff;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .context-text { font-size: 1.2rem; font-weight: 700; line-height: 1.4; word-break: keep-all; }

    /* 단어 숲 버튼 내부 스타일 */
    .btn-eng { color: #007BFF; font-size: 1.1rem; font-weight: 800; display: block; margin-bottom: 2px; }
    .btn-sound { color: #000000; font-size: 0.9rem; font-weight: 600; display: block; }
    .btn-accent { color: #E53935; text-decoration: underline; font-weight: 900; }

    /* 결과창 스타일 */
    .res-eng { font-size: 2.2rem; font-weight: 800; color: #007BFF; margin-bottom: 5px; }
    .res-sound-accent { color: #E53935; font-size: 1.8rem; font-weight: 900; text-decoration: underline; }
    .res-sound-norm { color: #000000; font-size: 1.6rem; font-weight: 700; }

    /* 패턴 박스 */
    .pattern-box {
        background-color: #f8f9fa;
        border: 2px dashed #007BFF;
        border-radius: 15px;
        padding: 12px;
        margin-top: 15px;
        text-align: left;
    }

    /* 버튼 공통 스타일 */
    .stButton>button { 
        border-radius: 12px; 
        padding: 8px 5px !important; 
        line-height: 1.2 !important;
        background-color: #ffffff;
        border: 1px solid #ddd;
    }
    /* 다음 문제 버튼 */
    .next-btn>div .stButton>button {
        height: 3.5rem;
        background-color: #E53935 !important;
        color: white !important;
        font-size: 1.2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

def get_styled_sound(sound_text, is_big=False):
    """한글 발음 첫 글자 강조 HTML 생성"""
    words = sound_text.split()
    html = '<div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 4px;">'
    for word in words:
        if len(word) > 0:
            accent_class = "res-sound-accent" if is_big else "btn-accent"
            norm_class = "res-sound-norm" if is_big else "btn-sound"
            html += f'<span><span class="{accent_class}">{word[0]}</span><span class="{norm_class}">{word[1:]}</span></span>'
    html += '</div>'
    return html

def load_data():
    idioms, patterns = [], []
    if not os.path.exists(DATA_FILE): return idioms, patterns
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            p = line.strip().split("|")
            if p[0] == "숙어" and len(p) >= 5: idioms.append(p)
            elif p[0] == "패턴" and len(p) >= 4: patterns.append(p)
    return idioms, patterns

idioms, patterns = load_data()

if idioms:
    if "quiz_idx" not in st.session_state:
        st.session_state.quiz_idx = random.randint(0, len(idioms) - 1)
        st.session_state.phase = "forest"
        correct_data = idioms[st.session_state.quiz_idx]
        others = [d for d in idioms if d[1] != correct_data[1]]
        
        # 12개 숲 데이터 구성 (표현, 발음 포함)
        forest_raw = random.sample(others, 11) + [correct_data]
        random.shuffle(forest_raw)
        st.session_state.forest_items = forest_raw
        
        # 4지선다 데이터 구성
        choice_raw = random.sample(others, 3) + [correct_data]
        random.shuffle(choice_raw)
        st.session_state.choice_items = choice_raw
        st.session_state.bonus_pattern = random.choice(patterns) if patterns else None

    curr = idioms[st.session_state.quiz_idx]
    _, eng, sound, mean, context = curr[:5]

    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="context-box"><div class="context-text">💡 {context}</div></div>', unsafe_allow_html=True)

    # --- 1단계: 단어 숲 ---
    if st.session_state.phase == "forest":
        st.write("🌳 **1단계: 알맞은 표현을 고르세요**")
        cols = st.columns(2) # 모바일 가독성을 위해 2열로 배치
        for i, item in enumerate(st.session_state.forest_items):
            i_eng, i_sound = item[1], item[2]
            # 버튼 내부에 HTML 주입
            btn_label = f"{i_eng}\n({i_sound})"
            if cols[i % 2].button(btn_label, key=f"f_{i}"):
                if i_eng == eng:
                    st.session_state.phase = "solved"
                else:
                    st.session_state.phase = "choices"
                st.rerun()
            # 버튼 바로 아래 스타일 적용된 텍스트 표시 (선택사항, 위 버튼 라벨이 안 예쁠 경우)
            cols[i % 2].markdown(f'<div style="text-align:center; margin-top:-10px; margin-bottom:10px;"><span class="btn-eng">{i_eng}</span>{get_styled_sound(i_sound)}</div>', unsafe_allow_html=True)

    # --- 2단계: 4지선다 ---
    elif st.session_state.phase == "choices":
        st.warning("⚠️ 틀렸습니다! 다시 한 번 찬스!")
        cols = st.columns(2)
        for i, item in enumerate(st.session_state.choice_items):
            i_eng, i_sound = item[1], item[2]
            if cols[i % 2].button(f"{i_eng} 선택", key=f"c_{i}"):
                st.session_state.phase = "solved"
                st.rerun()
            cols[i % 2].markdown(f'<div style="text-align:center; margin-top:-10px; margin-bottom:10px;"><span class="btn-eng">{i_eng}</span>{get_styled_sound(i_sound)}</div>', unsafe_allow_html=True)

    # --- 3단계: 정답 및 쉐도잉 ---
    elif st.session_state.phase == "solved":
        st.markdown(f"""
            <div style="margin-top:10px;">
                <div class="res-eng">{eng}</div>
                {get_accented_sound_html(sound) if 'get_accented_sound_html' in locals() else get_styled_sound(sound, True)}
                <div style="color:#666; font-size:1.3rem; font-weight:600; margin-top:5px;">{mean}</div>
                <div id="status-box" style="color:#E53935; font-weight:bold; margin-top:10px;">쉐도잉 준비...</div>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.bonus_pattern:
            _, p_eng, p_sound, p_mean = st.session_state.bonus_pattern[:4]
            st.markdown(f"""
                <div class="pattern-box">
                    <div style="color:#007BFF; font-weight:800; font-size:0.9rem;">📍 패턴으로 복습하기</div>
                    <div style="font-size:1.1rem; font-weight:700; margin:3px 0;">{p_eng}</div>
                    <div style="color:#666; font-size:0.85rem;">{p_sound} | {p_mean}</div>
                </div>
            """, unsafe_allow_html=True)

        # TTS 스크립트 (5회 반복)
        p_eng_js = st.session_state.bonus_pattern[1].replace("'", "").replace("(", "").replace(")", "") if st.session_state.bonus_pattern else ""
        st.components.v1.html(f"""
            <script>
            function start() {{
                const statusEl = window.parent.document.getElementById('status-box');
                window.speechSynthesis.cancel();
                let count = 0;
                function speak() {{
                    let msg = new SpeechSynthesisUtterance("{eng.replace("'","")}");
                    msg.lang = 'en-US'; msg.rate = 0.8;
                    statusEl.innerText = "🗣️ 따라하세요 (" + (count+1) + "/5)";
                    msg.onend = () => {{
                        count++;
                        if (count < 5) setTimeout(speak, 1000);
                        else if ("{p_eng_js}") {{
                            statusEl.innerText = "📍 패턴 문장 듣는 중...";
                            let p_msg = new SpeechSynthesisUtterance("{p_eng_js}");
                            p_msg.lang = 'en-US';
                            p_msg.onend = () => statusEl.innerText = "✅ 학습 완료!";
                            window.speechSynthesis.speak(p_msg);
                        }}
                    }};
                    window.speechSynthesis.speak(msg);
                }}
                setTimeout(speak, 500);
            }}
            start();
            </script>
        """, height=0)

        st.markdown('<div class="next-btn">', unsafe_allow_html=True)
        if st.button("다음 문제 👉"):
            for key in ["quiz_idx", "phase", "forest_items", "choice_items", "bonus_pattern"]:
                if key in st.session_state: del st.session_state[key]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)