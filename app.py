import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어 쉐도잉", layout="centered")

# --- CSS: 팝업 스타일 및 기존 레이아웃 유지 ---
st.markdown("""
    <style>
    header {visibility: hidden; height: 0px !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    .main .block-container {
        padding-top: 0rem !important;
        margin-top: -50px !important;
    }

    /* 카드형 버튼 디자인 */
    div.stButton > button {
        background-color: #ffffff !important;
        border: 1px solid #eee !important;
        border-radius: 12px !important;
        padding: 8px 5px !important;
        width: 100% !important;
        min-height: 75px !important;
        transition: all 0.2s;
        display: block !important;
    }
    div.stButton > button:hover {
        border-color: #007BFF !important;
        background-color: #f8fbff !important;
    }

    /* 버튼 내 텍스트 스타일 */
    .btn-eng { color: #007BFF; font-size: 1.05rem; font-weight: 800; display: block; margin-bottom: 2px; }
    
    /* 상황 박스 */
    .context-box {
        background: linear-gradient(135deg, #1e1e1e 0%, #444 100%);
        color: white;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        text-align: center;
    }

    /* 다음 버튼 전용 */
    .next-btn-style > div > button {
        background-color: #E53935 !important;
        color: white !important;
        font-size: 1.4rem !important;
        height: 60px !important;
        font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 발음 강조 HTML 생성
def get_accent_html(sound_text, is_big=False):
    words = sound_text.split()
    b_size = "font-size: 1.6rem;" if is_big else "font-size: 0.9rem;"
    a_size = "font-size: 1.9rem;" if is_big else "font-size: 1rem;"
    html = '<div style="display:flex; justify-content:center; gap:3px; flex-wrap:wrap;">'
    for word in words:
        if len(word) > 0:
            html += f'<span><span style="color:#E53935; font-weight:900; text-decoration:underline; {a_size}">{word[0]}</span><span style="color:#333; font-weight:600; {b_size}">{word[1:]}</span></span>'
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

selected_cat = st.selectbox("", categories, label_visibility="collapsed")

# 퀴즈 초기화
def init_quiz(cat):
    pool = [r for r in all_data if r[0] != "패턴"] if cat == "💡 전체보기" else [r for r in all_data if r[0] == cat]
    if not pool: pool = [r for r in all_data if r[0] != "패턴"]
    
    st.session_state.quiz_data = random.choice(pool)
    correct_eng = st.session_state.quiz_data[1]
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

# --- 오답 팝업 처리 (@st.dialog 사용) ---
@st.dialog("💡 오답 확인")
def show_wrong_answer(item):
    st.markdown(f"### `{item[1]}`")
    st.markdown(f"**발음:** {item[2]}")
    st.markdown(f"**뜻:** {item[3]}")
    st.info(f"**상황:** {item[4]}")
    if st.button("다시 도전하기"):
        st.rerun()

# --- 렌더링 ---
curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

st.markdown(f"""
    <div class="context-box">
        <div style="font-size:0.75rem; color:#ffeb3b; font-weight:800; margin-bottom:2px;">{cat_name}</div>
        <div style="font-size:1.15rem; font-weight:700; line-height:1.2;">{target_context}</div>
    </div>
""", unsafe_allow_html=True)

# 퀴즈 카드 그리기 함수
def draw_cards(items):
    cols = st.columns(2)
    for i, item in enumerate(items):
        with cols[i % 2]:
            st.markdown(f'<div style="text-align:center; margin-bottom:-35px; position:relative; z-index:1; pointer-events:none;">'
                        f'<span class="btn-eng">{item[1]}</span>'
                        f'{get_accent_html(item[2])}'
                        f'</div>', unsafe_allow_html=True)
            if st.button("", key=f"btn_{i}"):
                if item[1] == target_eng:
                    st.session_state.phase = "solved"
                    st.rerun()
                else:
                    st.session_state.phase = "choices"
                    show_wrong_answer(item) # 오답 시 팝업 띄우기

if st.session_state.phase == "forest":
    st.write("🌳 **정답 문장을 클릭하세요 (6개 후보)**")
    draw_cards(st.session_state.forest_items)

elif st.session_state.phase == "choices":
    st.error("아쉬워요! 3개 중에서 다시 골라보세요.")
    draw_cards(st.session_state.choice_items)

elif st.session_state.phase == "solved":
    st.markdown(f'<div style="text-align:center;"><div style="font-size:2.4rem; font-weight:900; color:#007BFF; margin-bottom:5px;">{target_eng}</div>', unsafe_allow_html=True)
    st.markdown(get_accent_html(target_sound, is_big=True), unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:1.4rem; font-weight:700; color:#444; margin-top:8px;">{target_mean}</div>', unsafe_allow_html=True)
    st.markdown('<div id="shadow-status" style="color:#E53935; font-weight:800; margin-top:10px;">🔊 5회 반복 쉐도잉 중...</div></div>', unsafe_allow_html=True)

    if st.session_state.bonus_pattern:
        _, p_eng, p_sound, p_mean = st.session_state.bonus_pattern[:4]
        st.markdown(f"""
            <div style="background-color:#f0f7ff; border-left:5px solid #007BFF; border-radius:12px; padding:12px; margin-top:15px; text-align:left;">
                <div style="color:#007BFF; font-weight:800; font-size:0.8rem;">📍 연관 패턴</div>
                <div style="font-size:1.1rem; font-weight:800; color:#222;">{p_eng}</div>
                <div style="font-size:0.9rem; color:#555;">{p_sound} | {p_mean}</div>
            </div>
        """, unsafe_allow_html=True)

    # TTS 로직
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
                    status.innerText = "📍 패턴 문장 듣기...";
                    let put = new SpeechSynthesisUtterance("{js_pattern}");
                    put.lang = 'en-US';
                    put.onend = () => status.innerText = "✅ 미션 완료!";
                    window.speechSynthesis.speak(put);
                }}
            }};
            window.speechSynthesis.speak(ut);
        }}
        setTimeout(play, 300);
        </script>
    """, height=0)

    st.markdown('<div class="next-btn-style">', unsafe_allow_html=True)
    if st.button("다음 문제 👉"):
        init_quiz(selected_cat)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)