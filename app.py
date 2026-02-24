import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어 쉐도잉", layout="centered")

# --- CSS: 폰트 강제 적용 및 2열 그리드 레이아웃 고정 ---
st.markdown("""
    <style>
    /* 1. 폰트 강제 적용 (부드러운 고딕) */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    
    * {
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    header {visibility: hidden; height: 0px !important;}
    [data-testid="stHeader"] {display: none !important;}
    .main .block-container { padding-top: 0rem !important; margin-top: -60px !important; }

    /* 2. 2열 배치를 위한 카드 컨테이너 */
    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: space-between;
    }

    .card-wrapper {
        position: relative;
        width: 48%; /* 양옆 2개 배치 핵심 */
        min-height: 85px;
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 18px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        margin-bottom: 5px;
    }
    
    .card-wrapper:active {
        transform: scale(0.95);
        background-color: #f0f7ff;
    }

    /* 3. 텍스트 스타일 */
    .eng-txt { color: #007BFF; font-size: 1rem; font-weight: 800; margin-bottom: 2px; line-height: 1.2; }
    .acc-char { color: #E53935; font-weight: 900; text-decoration: underline; font-size: 0.95rem; }
    .base-char { color: #333333; font-weight: 600; font-size: 0.9rem; }

    /* 4. 스트림릿 기본 버튼을 투명하게 만들어 카드 전체를 덮음 */
    div.stButton > button {
        position: absolute !important;
        top: 0; left: 0; width: 100%; height: 100%;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        z-index: 100 !important;
        margin: 0 !important;
    }

    .context-box {
        background: #222;
        color: white;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        text-align: center;
        width: 100%;
    }

    .next-btn-area div.stButton > button {
        position: relative !important;
        background: #E53935 !important;
        color: white !important;
        height: 55px;
        border-radius: 30px;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        z-index: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 발음 HTML 생성 함수
def make_sound_html(sound_text, is_big=False):
    words = sound_text.split()
    b_size = "font-size: 1.6rem;" if is_big else ""
    a_size = "font-size: 1.9rem;" if is_big else ""
    html = '<div style="display:flex; justify-content:center; gap:2px; flex-wrap:wrap; line-height:1;">'
    for word in words:
        if len(word) > 0:
            html += f'<span><span class="acc-char" style="{a_size}">{word[0]}</span><span class="base-char" style="{b_size}">{word[1:]}</span></span>'
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

# 퀴즈 초기화 함수
def init_quiz(cat):
    pool = [r for r in all_data if r[0] != "패턴"] if cat == "💡 전체보기" else [r for r in all_data if r[0] == cat]
    if not pool: pool = all_data
    
    st.session_state.quiz_data = random.choice(pool)
    correct_eng = st.session_state.quiz_data[1]
    
    others = [r for r in all_data if r[1] != correct_eng]
    st.session_state.forest_items = random.sample(others, 5) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.forest_items)
    
    st.session_state.choice_items = random.sample(others, min(len(others), 2)) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.choice_items)
    
    patterns = [r for r in all_data if r[0] == "패턴"]
    st.session_state.bonus_pattern = random.choice(patterns) if patterns else None
    st.session_state.phase = "forest"

# 카테고리 선택
categories = sorted(list(set([r[0] for r in all_data if r[0] not in ["패턴", "숙어"]])))
categories = ["💡 전체보기"] + categories
selected_cat = st.selectbox("", categories, label_visibility="collapsed")

if "quiz_data" not in st.session_state or st.session_state.get("last_cat") != selected_cat:
    st.session_state.last_cat = selected_cat
    init_quiz(selected_cat)

# --- 팝업 다이얼로그 ---
@st.dialog("📚 필수 단어 복습")
def show_random_word():
    current_answer = st.session_state.quiz_data[1]
    words_pool = [r for r in all_data if r[0] in ["숙어", "패턴"] and r[1] != current_answer]
    if not words_pool: words_pool = all_data
    word = random.choice(words_pool)
    
    st.markdown(f"<h2 style='text-align:center; color:#007BFF; margin-bottom:0;'>{word[1]}</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; margin-bottom:15px;'>{make_sound_html(word[2], is_big=True)}</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; font-size:1.3rem; color:#333;'><b>뜻: {word[3]}</b></p>", unsafe_allow_html=True)
    st.info(f"**활용 상황:** {word[4]}")
    
    if st.button("다음 퀴즈 시작! 👉", key="pop_next"):
        init_quiz(selected_cat)
        st.rerun()

@st.dialog("💡 오답 확인")
def show_wrong_answer(item):
    st.markdown(f"### `{item[1]}`")
    st.markdown(f"**뜻:** {item[3]}")
    st.info(f"**상황:** {item[4]}")
    if st.button("다시 도전하기"): st.rerun()

# --- 메인 화면 렌더링 ---
curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

st.markdown(f"""
    <div class="context-box">
        <div style="font-size:0.8rem; color:#ffeb3b; font-weight:700;">{cat_name}</div>
        <div style="font-size:1.2rem; font-weight:500;">{target_context} ({target_mean})</div>
    </div>
""", unsafe_allow_html=True)

# 퀴즈 카드 렌더링 (2열 배치)
if st.session_state.phase in ["forest", "choices"]:
    items = st.session_state.forest_items if st.session_state.phase == "forest" else st.session_state.choice_items
    
    # st.columns 대신 직접 HTML과 버튼 매핑
    cols = st.columns(2)
    for i, item in enumerate(items):
        with cols[i % 2]:
            st.markdown(f"""
                <div class="card-wrapper">
                    <div class="eng-txt">{item[1]}</div>
                    <div class="snd-txt">{make_sound_html(item[2])}</div>
            """, unsafe_allow_html=True)
            if st.button(" ", key=f"q_btn_{i}"):
                if item[1] == target_eng:
                    st.session_state.phase = "solved"
                else:
                    st.session_state.phase = "choices"
                    show_wrong_answer(item)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.phase == "solved":
    st.markdown(f'<div style="text-align:center;"><div style="font-size:2.5rem; font-weight:900; color:#007BFF; line-height:1.1;">{target_eng}</div>', unsafe_allow_html=True)
    st.markdown(make_sound_html(target_sound, is_big=True), unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:1.4rem; font-weight:700; color:#444; margin:15px 0;">{target_mean}</div>', unsafe_allow_html=True)
    st.markdown('<div id="status" style="color:#E53935; font-weight:800; font-size:1.1rem;">🔊 쉐도잉 반복 중...</div></div>', unsafe_allow_html=True)

    if st.session_state.bonus_pattern:
        _, p_eng, p_sound, p_mean = st.session_state.bonus_pattern[:4]
        st.markdown(f'<div style="background-color:#f8fbff; border-left:5px solid #007BFF; border-radius:15px; padding:15px; margin-top:15px;"><div style="color:#007BFF; font-weight:800; font-size:0.9rem;">📍 연관 패턴</div><div style="font-size:1.2rem; font-weight:800;">{p_eng}</div><div style="font-size:1rem; color:#555;">{p_mean}</div></div>', unsafe_allow_html=True)

    # JS TTS
    js_target = target_eng.replace("'","")
    js_pattern = st.session_state.bonus_pattern[1].replace("'","").replace("(","").replace(")","") if st.session_state.bonus_pattern else ""
    st.components.v1.html(f"""
        <script>
        const status = window.parent.document.getElementById('status');
        window.speechSynthesis.cancel();
        let loop = 0;
        function play() {{
            let ut = new SpeechSynthesisUtterance("{js_target}");
            ut.lang = 'en-US'; ut.rate = 0.8;
            status.innerText = "🗣️ 따라하기 (" + (loop+1) + "/5)";
            ut.onend = () => {{
                loop++;
                if(loop < 5) setTimeout(play, 750);
                else if("{js_pattern}") {{
                    status.innerText = "✅ 패턴 예문 듣기...";
                    let put = new SpeechSynthesisUtterance("{js_pattern}");
                    put.lang = 'en-US';
                    window.speechSynthesis.speak(put);
                }}
            }};
            window.speechSynthesis.speak(ut);
        }}
        setTimeout(play, 300);
        </script>
    """, height=0)

    st.markdown('<div class="next-btn-area">', unsafe_allow_html=True)
    if st.button("다음 문제 👉", key="final_next"):
        show_random_word()
    st.markdown('</div>', unsafe_allow_html=True)