import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어 쉐도잉", layout="centered")

# --- CSS: 한 화면 최적화 및 레이아웃 ---
st.markdown("""
    <style>
    /* 1. 상단 여백 및 헤더 제거 */
    [data-testid="stAppViewContainer"] { padding-top: 0px !important; }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .main .block-container { 
        padding-top: 0px !important; 
        margin-top: -110px !important; 
        max-height: 100vh;
        overflow: hidden;
    }
    
    .main { background-color: #ffffff; }

    /* 전체 카드 컨테이너 */
    .quiz-card {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 20px;
        text-align: center;
        height: 98vh;
        display: flex;
        flex-direction: column;
    }

    /* 상황 박스 슬림화 */
    .context-box {
        background: linear-gradient(135deg, #1e1e1e 0%, #444 100%);
        color: #ffffff;
        border-radius: 15px;
        padding: 12px;
        margin-bottom: 5px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .cat-tag { font-size: 0.7rem; color: #ffeb3b; font-weight: 800; margin-bottom: 2px; }
    .context-text { font-size: 1.1rem; font-weight: 700; line-height: 1.2; }

    /* 퀴즈 버튼 최적화 */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #eee;
        background-color: #fcfcfc;
        padding: 2px !important;
        min-height: 42px;
        margin-bottom: 0px;
    }
    .eng-blue { color: #007BFF; font-size: 0.95rem; font-weight: 800; display: block; }
    .sound-black { color: #333; font-size: 0.8rem; font-weight: 600; }
    .accent-red { color: #E53935; font-size: 0.9rem; font-weight: 900; text-decoration: underline; }

    /* 결과창 디자인 */
    .res-eng { font-size: 2.2rem; font-weight: 900; color: #007BFF; margin-bottom: 2px; }
    .res-mean { font-size: 1.2rem; font-weight: 700; color: #444; }

    /* 패턴 박스 슬림화 */
    .pattern-box {
        background-color: #f0f7ff;
        border-left: 4px solid #007BFF;
        border-radius: 10px;
        padding: 8px;
        margin-top: 5px;
        text-align: left;
    }
    .pattern-eng { font-size: 1rem; font-weight: 800; color: #222; }

    /* 다음 문제 버튼 */
    .next-btn>div .stButton>button {
        height: 3.5rem;
        background-color: #E53935 !important;
        color: white !important;
        font-size: 1.3rem !important;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 발음 강조 함수
def get_accent_html(sound_text, is_big=False):
    words = sound_text.split()
    e_size = "font-size: 1.6rem;" if is_big else ""
    a_size = "font-size: 1.9rem;" if is_big else ""
    html = '<div style="display:flex; justify-content:center; flex-wrap:wrap; gap:3px;">'
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

# 상단 선택바 (레이아웃 공간 확보를 위해 콤팩트하게)
selected_cat = st.selectbox("", categories, label_visibility="collapsed")

# 퀴즈 초기화 함수
def init_quiz(cat):
    pool = [r for r in all_data if r[0] != "패턴"] if cat == "💡 전체보기" else [r for r in all_data if r[0] == cat]
    if not pool: pool = [r for r in all_data if r[0] != "패턴"]
    
    st.session_state.quiz_data = random.choice(pool)
    correct_eng = st.session_state.quiz_data[1]
    
    # 오답 데이터 (에러 방지를 위해 충분한 데이터 확보)
    others = [r for r in all_data if r[0] != "패턴" and r[1] != correct_eng]
    st.session_state.forest_items = random.sample(others, 11) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.forest_items)
    
    st.session_state.choice_items = random.sample(others, min(len(others), 3)) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.choice_items)
    
    patterns = [r for r in all_data if r[0] == "패턴"]
    st.session_state.bonus_pattern = random.choice(patterns) if patterns else None
    st.session_state.phase = "forest"

# 세션 상태 관리
if "quiz_data" not in st.session_state or st.session_state.get("last_cat") != selected_cat:
    st.session_state.last_cat = selected_cat
    init_quiz(selected_cat)

# --- 메인 화면 시작 ---
st.markdown('<div class="quiz-card">', unsafe_allow_html=True)

curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

st.markdown(f"""
    <div class="context-box">
        <div class="cat-tag">{cat_name}</div>
        <div class="context-text">{target_context}</div>
    </div>
""", unsafe_allow_html=True)

# 1단계: 단어 숲 (12개 버튼)
if st.session_state.phase == "forest":
    cols = st.columns(2)
    for i, item in enumerate(st.session_state.forest_items):
        with cols[i % 2]:
            st.markdown(f'<span class="eng-blue">{item[1]}</span>', unsafe_allow_html=True)
            st.markdown(get_accent_html(item[2]), unsafe_allow_html=True)
            if st.button("선택", key=f"f_btn_{i}"):
                if item[1] == target_eng:
                    st.session_state.phase = "solved"
                else:
                    st.session_state.phase = "choices"
                st.rerun()

# 2단계: 4지선다
elif st.session_state.phase == "choices":
    st.error("틀렸습니다! 다시 기회를 드릴게요.")
    cols = st.columns(2)
    for i, item in enumerate(st.session_state.choice_items):
        with cols[i % 2]:
            st.markdown(f'<span class="eng-blue">{item[1]}</span>', unsafe_allow_html=True)
            st.markdown(get_accent_html(item[2]), unsafe_allow_html=True)
            if st.button("정답!", key=f"c_btn_{i}"):
                st.session_state.phase = "solved"
                st.rerun()

# 3단계: 정답 확인 및 쉐도잉
elif st.session_state.phase == "solved":
    st.markdown(f'<div class="res-eng">{target_eng}</div>', unsafe_allow_html=True)
    st.markdown(get_accent_html(target_sound, is_big=True), unsafe_allow_html=True)
    st.markdown(f'<div class="res-mean">뜻: {target_mean}</div>', unsafe_allow_html=True)
    st.markdown('<div id="status-txt" style="color:#E53935; font-weight:800; font-size:0.9rem; margin:10px 0;">🔊 쉐도잉 5회 반복 중...</div>', unsafe_allow_html=True)

    if st.session_state.bonus_pattern:
        _, p_eng, p_sound, p_mean = st.session_state.bonus_pattern[:4]
        st.markdown(f"""
            <div class="pattern-box">
                <div style="color:#007BFF; font-weight:800; font-size:0.7rem;">📍 보너스 패턴</div>
                <div class="pattern-eng">{p_eng}</div>
                <div style="font-size:0.8rem; color:#666;">{p_sound} | {p_mean}</div>
            </div>
        """, unsafe_allow_html=True)

    # JS TTS 로직
    clean_target = target_eng.replace("'","")
    clean_pattern = st.session_state.bonus_pattern[1].replace("'","").replace("(","").replace(")","") if st.session_state.bonus_pattern else ""
    st.components.v1.html(f"""
        <script>
        const status = window.parent.document.getElementById('status-txt');
        window.speechSynthesis.cancel();
        let i = 0;
        function speak() {{
            let ut = new SpeechSynthesisUtterance("{clean_target}");
            ut.lang = 'en-US'; ut.rate = 0.85;
            status.innerText = "🗣️ 따라하기 (" + (i+1) + "/5)";
            ut.onend = () => {{
                i++;
                if(i < 5) setTimeout(speak, 800);
                else if("{clean_pattern}") {{
                    status.innerText = "📍 패턴 예문 듣기...";
                    let put = new SpeechSynthesisUtterance("{clean_pattern}");
                    put.lang = 'en-US';
                    put.onend = () => status.innerText = "✅ 미션 완료!";
                    window.speechSynthesis.speak(put);
                }}
            }};
            window.speechSynthesis.speak(ut);
        }}
        setTimeout(speak, 300);
        </script>
    """, height=0)

    st.markdown('<div class="next-btn">', unsafe_allow_html=True)
    if st.button("다음 문제 👉"):
        init_quiz(selected_cat)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)