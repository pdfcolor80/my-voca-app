import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어", layout="centered")

# --- CSS: 한 화면(One-Screen) 레이아웃 최적화 ---
st.markdown("""
    <style>
    /* 1. 상단 여백 제거 및 전체 높이 고정 */
    [data-testid="stAppViewContainer"] { padding-top: 0px !important; }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .main .block-container { 
        padding-top: 0px !important; 
        margin-top: -115px !important; 
        padding-bottom: 0px !important;
        max-height: 100vh;
        overflow: hidden;
    }
    
    .main { background-color: #ffffff; }

    /* 퀴즈 카드: 내부 여백 최소화 */
    .quiz-card {
        background-color: #ffffff;
        padding: 10px 15px;
        border-radius: 25px;
        text-align: center;
        border: 1px solid #f0f0f0;
        height: 98vh; /* 화면 높이에 맞춤 */
        display: flex;
        flex-direction: column;
    }

    /* 상황 박스: 크기 축소 */
    .context-box {
        background: linear-gradient(135deg, #222 0%, #444 100%);
        color: #ffffff;
        border-radius: 15px;
        padding: 12px;
        margin-bottom: 8px;
    }
    .cat-tag { font-size: 0.75rem; color: #ffeb3b; font-weight: 800; }
    .context-text { font-size: 1.1rem; font-weight: 700; line-height: 1.3; }

    /* 퀴즈 버튼 레이아웃: 간격 조밀하게 */
    .btn-container { margin-bottom: 5px; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid #eee;
        background-color: #fcfcfc;
        padding: 4px 2px !important; /* 버튼 높이 축소 */
        min-height: 45px;
    }
    .eng-blue { color: #007BFF; font-size: 1rem; font-weight: 800; display: block; line-height: 1.1; }
    .sound-black { color: #333; font-size: 0.85rem; font-weight: 600; }
    .accent-red { color: #E53935; font-size: 0.95rem; font-weight: 900; text-decoration: underline; }

    /* 결과창 텍스트 */
    .res-eng { font-size: 2rem; font-weight: 900; color: #007BFF; line-height: 1.2; }
    .res-mean { font-size: 1.1rem; color: #555; font-weight: 600; margin-bottom: 5px; }

    /* 패턴 박스: 하단 고정 느낌 */
    .pattern-box {
        background-color: #f0f7ff;
        border-left: 4px solid #007BFF;
        border-radius: 12px;
        padding: 10px;
        margin-top: 5px;
        text-align: left;
    }
    .pattern-label { color: #007BFF; font-weight: 800; font-size: 0.75rem; }
    .pattern-eng { font-size: 1.05rem; font-weight: 800; color: #222; }

    /* 다음 버튼 */
    .next-btn>div .stButton>button {
        height: 3.5rem;
        background-color: #E53935 !important;
        color: white !important;
        font-size: 1.3rem !important;
        margin-top: 10px;
    }
    
    /* 선택 박스 위치 조정 */
    .stSelectbox { margin-bottom: 5px !important; }
    </style>
    """, unsafe_allow_html=True)

# 한글 강조 함수
def get_accent_html(sound_text, is_big=False):
    words = sound_text.split()
    e_size = "font-size: 1.5rem;" if is_big else ""
    a_size = "font-size: 1.8rem;" if is_big else ""
    html = '<div style="display:flex; justify-content:center; flex-wrap:wrap; gap:4px;">'
    for word in words:
        if len(word) > 0:
            html += f'<span><span class="accent-red" style="{a_size}">{word[0]}</span><span class="sound-black" style="{e_size}">{word[1:]}</span></span>'
    html += '</div>'
    return html

# 데이터 로딩
@st.cache_data
def load_data():
    all_rows = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 4: all_rows.append(p)
    return all_rows

all_data = load_data()
categories = sorted(list(set([r[0] for r in all_data if r[0] not in ["패턴", "숙어", "💡 기타 일상"]])))
categories = ["💡 전체보기"] + categories

# 상단 선택바
selected_cat = st.selectbox("", categories, label_visibility="collapsed")

# 퀴즈 초기화
def init_quiz(cat):
    pool = [r for r in all_data if r[0] != "패턴"] if cat == "💡 전체보기" else [r for r in all_data if r[0] == cat]
    if not pool: pool = [r for r in all_data if r[0] != "패턴"]
    st.session_state.quiz_data = random.choice(pool)
    correct_eng = st.session_state.quiz_data[1]
    others = [r for r in all_data if r[0] != "패턴" and r[1] != correct_eng]
    st.session_state.forest_items = random.sample(others, 11) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.forest_items)
    st.session_state.choice_items = random.sample(others, 3) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.choice_items)
    patterns = [r for r in all_data if r[0] == "패턴"]
    st.session_state.bonus_pattern = random.choice(patterns) if patterns else None
    st.session_state.phase = "forest"

if "quiz_data" not in st.session_state or st.session_state.get("last_cat") != selected_cat:
    st.session_state.last_cat = selected_cat
    init_quiz(selected_cat)

# --- 메인 렌더링 ---
st.markdown('<div class="quiz-card">', unsafe_allow_html=True)

curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

st.markdown(f'<div class="context-box"><div class="cat-tag">{cat_name}</div><div class="context-text">{target_context}</div></div>', unsafe_allow_html=True)

if st.session_state.phase == "forest":
    cols = st.columns(2)
    for i, item in enumerate(st.session_state.forest_items):
        with cols[i % 2]:
            st.markdown(f'<span class="eng-blue">{item[1]}</span>', unsafe_allow_html=True)
            st.markdown(get_accent_html(item[2]), unsafe_allow_html=True)
            if st.button("선택", key=f"f_{i}"):
                st.session_state.phase = "solved" if item[1] == target_eng else "choices"
                st.rerun()

elif st.session_state.phase == "choices":
    st.error("틀렸습니다! 4개 중 정답은?")
    cols = st.columns(2)
    for i, item in enumerate(st.session_state.choice_items):
        with cols[i % 2]:
            st.markdown(f'<span class="eng-blue">{item[1]}</span>', unsafe_allow_html=True)
            st.markdown(get_accent_html(item[2]), unsafe_allow_html=True)
            if st.button("확인", key=f"c_{i}"):
                st.session_state.phase = "solved"
                st.rerun()

elif st.session_state.phase == "solved":
    st.markdown(f'<div class="res-eng">{target_eng}</div>', unsafe_allow_html=True)
    st.markdown(get_accent_html(target_sound, is_big=True), unsafe_allow_html=True)
    st.markdown(f'<div class="res-mean">뜻: {target_mean}</div>', unsafe_allow_html=True)
    st.markdown('<div id="shadow-status" style="color:#E53935; font-weight:800; font-size:0.9rem;">🔊 쉐도잉 중...</div>', unsafe_allow_html=True)

    if st.session_state.bonus_pattern:
        _, p_eng, p_sound, p_mean = st.session_state.bonus_pattern[:4]
        st.markdown(f'<div class="pattern-box"><div class="pattern-label">📍 패턴 문장</div><div class="pattern-eng">{p_eng}</div><div style="font-size:0.85rem; color:#444;">{p_sound} | {p_mean}</div></div>', unsafe_allow_html=True)

    # TTS (축소된 스크립트)
    js_target = target_eng.replace("'","")
    js_pattern = st.session_state.bonus_pattern[1].replace("'","").replace("(","").replace(")","") if st.session_state.bonus_pattern else ""
    st.components.v1.html(f"""
        <script>
        const status = window.parent.document.getElementById('shadow-status');
        window.speechSynthesis.cancel();
        let loop = 0;
        function play() {{
            let ut = new SpeechSynthesisUtterance("{js_target}");
            ut.lang = 'en-US'; ut.rate = 0.85;
            status.innerText = "🗣️ 따라하기 (" + (loop+1) + "/5)";
            ut.onend = () => {{
                loop++;
                if(loop < 5) setTimeout(play, 800);
                else if("{js_pattern}") {{
                    let put = new SpeechSynthesisUtterance("{js_pattern}");
                    put.lang = 'en-US'; 
                    put.onend = () => status.innerText = "✅ 완료!";
                    window.speechSynthesis.speak(put);
                }}
            }};
            window.speechSynthesis.speak(ut);
        }}
        setTimeout(play, 300);
        </script>
    """, height=0)

    st.markdown('<div class="next-btn">', unsafe_allow_html=True)
    if st.button("다음 문제 👉"):
        init_quiz(selected_cat)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)