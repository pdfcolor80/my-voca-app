import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어 쉐도잉", layout="centered")

# --- CSS: 레이아웃 및 폰트 설정 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif !important; }

    header {visibility: hidden; height: 0px !important;}
    [data-testid="stHeader"] {display: none !important;}
    .main .block-container { padding-top: 0rem !important; margin-top: -65px !important; }

    .card-wrapper {
        position: relative; width: 100%; min-height: 80px; margin-bottom: 6px;
        background: #ffffff; border: 1px solid #f0f0f0; border-radius: 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex;
        flex-direction: column; justify-content: center; align-items: center;
        text-align: center; transition: all 0.2s;
    }
    .card-wrapper:hover { border-color: #007BFF; background-color: #f8fbff; }
    .eng-txt { color: #007BFF; font-size: 1.05rem; font-weight: 800; margin-bottom: 2px; pointer-events: none; }
    .acc-char { color: #E53935; font-weight: 900; text-decoration: underline; font-size: 0.95rem; }
    .base-char { color: #333333; font-weight: 600; font-size: 0.9rem; }

    .stButton > button {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: transparent !important; border: none !important;
        color: transparent !important; z-index: 10; margin: 0 !important; padding: 0 !important;
    }

    .context-box {
        background: #1a1a1a; color: white; border-radius: 18px;
        padding: 12px; margin-bottom: 8px; text-align: center;
    }

    .next-btn-area .stButton > button {
        position: relative; background: #E53935 !important; color: white !important;
        height: 50px; border-radius: 25px; font-size: 1.1rem !important; font-weight: 800 !important;
    }
    [data-testid="column"] { padding: 0 3px !important; }
    </style>
    """, unsafe_allow_html=True)

def make_sound_html(sound_text, is_big=False):
    words = sound_text.split()
    b_size = "font-size: 1.6rem;" if is_big else ""
    a_size = "font-size: 1.9rem;" if is_big else ""
    html = '<div style="display:flex; justify-content:center; gap:2px; flex-wrap:wrap;">'
    for word in words:
        if len(word) > 0:
            html += f'<span><span class="acc-char" style="{a_size}">{word[0]}</span><span class="base-char" style="{b_size}">{word[1:]}</span></span>'
    html += '</div>'
    return html

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
categories = sorted(list(set([r[0] for r in all_data if r[0] not in ["패턴", "숙어"]])))
categories = ["💡 전체보기"] + categories
selected_cat = st.selectbox("", categories, label_visibility="collapsed")

def init_quiz(cat):
    pool = [r for r in all_data if r[0] != "패턴"] if cat == "💡 전체보기" else [r for r in all_data if r[0] == cat]
    if not pool: pool = [r for r in all_data if r[0] != "패턴"]
    
    # 정답 선정
    st.session_state.quiz_data = random.choice(pool)
    correct_eng = st.session_state.quiz_data[1]
    
    # 후보군 선정
    others = [r for r in all_data if r[0] != "패턴" and r[1] != correct_eng]
    st.session_state.forest_items = random.sample(others, 5) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.forest_items)
    st.session_state.choice_items = random.sample(others, min(len(others), 2)) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.choice_items)
    
    patterns = [r for r in all_data if r[0] == "패턴"]
    st.session_state.bonus_pattern = random.choice(patterns) if patterns else None
    st.session_state.phase = "forest"

if "quiz_data" not in st.session_state or st.session_state.get("last_cat") != selected_cat:
    st.session_state.last_cat = selected_cat
    init_quiz(selected_cat)

# --- 팝업 다이얼로그 ---

@st.dialog("📚 필수 단어 복습")
def show_random_word():
    # 힌트 방지 로직: 현재 퀴즈 정답(quiz_data)과 다음에 나올 수 있는 풀에서 제외
    current_answer = st.session_state.quiz_data[1]
    
    # 숙어/패턴 중 현재 정답이 아닌 것들만 필터링
    words_pool = [r for r in all_data if r[0] in ["숙어", "패턴"] and r[1] != current_answer]
    
    if not words_pool: words_pool = all_data
    word = random.choice(words_pool)
    
    # 팝업을 닫고 다음 퀴즈를 로드하기 위한 준비
    st.markdown(f"<h2 style='text-align:center; color:#007BFF; margin-bottom:0;'>{word[1]}</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; margin-bottom:15px;'>{make_sound_html(word[2], is_big=True)}</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; font-size:1.3rem; color:#333;'><b>뜻: {word[3]}</b></p>", unsafe_allow_html=True)
    st.info(f"**활용 상황:** {word[4]}")
    
    if st.button("다음 퀴즈 시작! 👉", use_container_width=True):
        init_quiz(selected_cat)
        st.rerun()

@st.dialog("💡 오답 확인")
def show_wrong_answer(item):
    st.markdown(f"### `{item[1]}`")
    st.markdown(f"**뜻:** {item[3]}")
    st.info(f"**상황:** {item[4]}")
    if st.button("다시 도전하기"): st.rerun()

# --- 화면 렌더링 ---
curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

st.markdown(f"""
    <div class="context-box">
        <div style="font-size:0.75rem; color:#ffeb3b; font-weight:800;">{cat_name}</div>
        <div style="font-size:1.15rem; font-weight:500;">{target_context} ({target_mean})</div>
    </div>
""", unsafe_allow_html=True)

def draw_cards(items):
    cols = st.columns(2)
    for i, item in enumerate(items):
        with cols[i % 2]:
            st.markdown(f"""<div class="card-wrapper"><div class="eng-txt">{item[1]}</div><div class="snd-txt">{make_sound_html(item[2])}</div>""", unsafe_allow_html=True)
            if st.button("", key=f"q_{i}"):
                if item[1] == target_eng: st.session_state.phase = "solved"
                else: show_wrong_answer(item); st.session_state.phase = "choices"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.phase == "forest":
    draw_cards(st.session_state.forest_items)
elif st.session_state.phase == "choices":
    st.write("<p style='text-align:center; color:#E53935; font-weight:700; margin:0;'>🎯 정답을 찾아보세요!</p>", unsafe_allow_html=True)
    draw_cards(st.session_state.choice_items)
elif st.session_state.phase == "solved":
    st.markdown(f'<div style="text-align:center;"><div style="font-size:2.5rem; font-weight:900; color:#007BFF; line-height:1.1;">{target_eng}</div>', unsafe_allow_html=True)
    st.markdown(make_sound_html(target_sound, is_big=True), unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:1.3rem; font-weight:700; color:#444; margin:10px 0;">{target_mean}</div>', unsafe_allow_html=True)
    st.markdown('<div id="status" style="color:#E53935; font-weight:800;">🔊 쉐도잉 반복 중...</div></div>', unsafe_allow_html=True)

    if st.session_state.bonus_pattern:
        _, p_eng, p_sound, p_mean = st.session_state.bonus_pattern[:4]
        st.markdown(f'<div style="background-color:#f8fbff; border-left:5px solid #007BFF; border-radius:15px; padding:12px; margin-top:10px;"><div style="color:#007BFF; font-weight:800; font-size:0.8rem;">📍 연관 패턴</div><div style="font-size:1.1rem; font-weight:800;">{p_eng}</div><div style="font-size:0.9rem; color:#555;">{p_mean}</div></div>', unsafe_allow_html=True)

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
    if st.button("다음 문제 👉", key="next_q"):
        show_random_word()
    st.markdown('</div>', unsafe_allow_html=True)