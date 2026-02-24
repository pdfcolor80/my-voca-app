import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어 쉐도잉", layout="centered")

# --- CSS: 최상급 UI 디자인 ---
st.markdown("""
    <style>
    /* 1. 상단 여백 및 툴바 완전 제거 */
    [data-testid="stAppViewContainer"] { padding-top: 0px !important; }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .main .block-container { padding-top: 0px !important; margin-top: -110px !important; }
    
    .main { background-color: #f7f9fc; }

    /* 퀴즈 카드 */
    .quiz-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 30px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        min-height: 90vh;
    }

    /* 상황 박스 (그라데이션) */
    .context-box {
        background: linear-gradient(135deg, #1a1a1a 0%, #434343 100%);
        color: #ffffff;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .cat-tag { font-size: 0.9rem; color: #ffeb3b; font-weight: 800; margin-bottom: 5px; text-transform: uppercase; }
    .context-text { font-size: 1.3rem; font-weight: 700; line-height: 1.4; word-break: keep-all; }

    /* 텍스트 스타일 */
    .eng-blue { color: #007BFF; font-size: 1.2rem; font-weight: 800; display: block; }
    .sound-black { color: #333333; font-size: 1rem; font-weight: 600; }
    .accent-red { color: #E53935; font-size: 1.1rem; font-weight: 900; text-decoration: underline; }

    /* 큰 결과용 텍스트 */
    .res-eng { font-size: 2.5rem; font-weight: 900; color: #007BFF; margin-bottom: 10px; }

    /* 버튼 스타일 */
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        border: 1px solid #eee;
        background-color: #ffffff;
        padding: 10px;
        transition: all 0.3s;
    }
    .stButton>button:hover { border-color: #007BFF; background-color: #f0f7ff; }

    /* 패턴 박스 */
    .pattern-box {
        background-color: #f0f7ff;
        border-left: 5px solid #007BFF;
        border-radius: 15px;
        padding: 15px;
        margin-top: 20px;
        text-align: left;
    }
    
    /* 다음 문제 버튼 */
    .next-btn>div .stButton>button {
        height: 4rem;
        background-color: #E53935 !important;
        color: white !important;
        font-size: 1.4rem !important;
        box-shadow: 0 4px 15px rgba(229, 57, 53, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 한글 강조 HTML 생성 함수
def get_accent_html(sound_text, is_big=False):
    words = sound_text.split()
    size_style = "font-size: 1.8rem;" if is_big else ""
    acc_size = "font-size: 2.2rem;" if is_big else ""
    
    html = '<div style="display:flex; justify-content:center; flex-wrap:wrap; gap:6px;">'
    for word in words:
        if len(word) > 0:
            html += f'<span><span class="accent-red" style="{acc_size}">{word[0]}</span><span class="sound-black" style="{size_style}">{word[1:]}</span></span>'
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

# 카테고리 추출
categories = sorted(list(set([r[0] for r in all_data if r[0] not in ["패턴", "숙어", "💡 기타 일상"]])))
categories = ["💡 전체보기"] + categories

# --- 사이드바 대신 상단 셀렉트 ---
selected_cat = st.selectbox("📚 학습할 상황을 선택하세요", categories)

# --- 퀴즈 세션 초기화 ---
def init_quiz(cat):
    if cat == "💡 전체보기":
        pool = [r for r in all_data if r[0] != "패턴"]
    else:
        pool = [r for r in all_data if r[0] == cat]
    
    if not pool: pool = [r for r in all_data if r[0] != "패턴"]
    
    st.session_state.quiz_data = random.choice(pool)
    correct_eng = st.session_state.quiz_data[1]
    
    # 오답 리스트
    others = [r for r in all_data if r[0] != "패턴" and r[1] != correct_eng]
    st.session_state.forest_items = random.sample(others, 11) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.forest_items)
    
    st.session_state.choice_items = random.sample(others, 3) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.choice_items)
    
    # 관련 패턴 1개
    patterns = [r for r in all_data if r[0] == "패턴"]
    st.session_state.bonus_pattern = random.choice(patterns) if patterns else None
    st.session_state.phase = "forest"

if "quiz_data" not in st.session_state or st.session_state.get("last_cat") != selected_cat:
    st.session_state.last_cat = selected_cat
    init_quiz(selected_cat)

# --- 화면 렌더링 ---
st.markdown('<div class="quiz-card">', unsafe_allow_html=True)

curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

# 상황 박스 표시
st.markdown(f"""
    <div class="context-box">
        <div class="cat-tag">{cat_name}</div>
        <div class="context-text">💡 {target_context}</div>
    </div>
""", unsafe_allow_html=True)

# 1단계: 12개 단어 숲
if st.session_state.phase == "forest":
    st.write("🌳 **1단계: 알맞은 카드를 찾으세요**")
    cols = st.columns(2)
    for i, item in enumerate(st.session_state.forest_items):
        with cols[i % 2]:
            st.markdown(f'<span class="eng-blue">{item[1]}</span>', unsafe_allow_html=True)
            st.markdown(get_accent_html(item[2]), unsafe_allow_html=True)
            if st.button("선택하기", key=f"f_btn_{i}"):
                if item[1] == target_eng: st.session_state.phase = "solved"
                else: st.session_state.phase = "choices"
                st.rerun()

# 2단계: 4지선다
elif st.session_state.phase == "choices":
    st.warning("⚠️ 조금 더 집중해 보세요! 4개 중에 정답이 있습니다.")
    cols = st.columns(2)
    for i, item in enumerate(st.session_state.choice_items):
        with cols[i % 2]:
            st.markdown(f'<span class="eng-blue">{item[1]}</span>', unsafe_allow_html=True)
            st.markdown(get_accent_html(item[2]), unsafe_allow_html=True)
            if st.button("정답!", key=f"c_btn_{i}"):
                st.session_state.phase = "solved"
                st.rerun()

# 3단계: 정답 및 무한 쉐도잉
elif st.session_state.phase == "solved":
    st.markdown(f'<div class="res-eng">{target_eng}</div>', unsafe_allow_html=True)
    st.markdown(get_accent_html(target_sound, is_big=True), unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:1.4rem; font-weight:600; margin-top:10px;">{target_mean}</div>', unsafe_allow_html=True)
    st.markdown('<div id="shadow-status" style="color:#E53935; font-weight:800; margin:15px 0;">🔊 원어민 발음 듣는 중...</div>', unsafe_allow_html=True)

    if st.session_state.bonus_pattern:
        _, p_eng, p_sound, p_mean = st.session_state.bonus_pattern[:4]
        st.markdown(f"""
            <div class="pattern-box">
                <div style="color:#007BFF; font-weight:800; font-size:0.9rem;">📍 패턴 활용하기</div>
                <div style="font-size:1.2rem; font-weight:800; margin:3px 0;">{p_eng}</div>
                <div style="color:#444; font-size:0.9rem;">{p_sound} | {p_mean}</div>
            </div>
        """, unsafe_allow_html=True)

    # JS TTS (5회 반복 + 패턴 1회)
    js_target = target_eng.replace("'","")
    js_pattern = st.session_state.bonus_pattern[1].replace("'","").replace("(","").replace(")","") if st.session_state.bonus_pattern else ""
    
    st.components.v1.html(f"""
        <script>
        const status = window.parent.document.getElementById('shadow-status');
        window.speechSynthesis.cancel();
        let loop = 0;
        function play() {{
            let utterance = new SpeechSynthesisUtterance("{js_target}");
            utterance.lang = 'en-US'; utterance.rate = 0.8;
            status.innerText = "🗣️ 소리내어 따라하세요 (" + (loop+1) + "/5)";
            utterance.onend = () => {{
                loop++;
                if(loop < 5) setTimeout(play, 1000);
                else {{
                    status.innerText = "📍 마지막으로 패턴 문장 듣기...";
                    let p_utter = new SpeechSynthesisUtterance("{js_pattern}");
                    p_utter.lang = 'en-US';
                    p_utter.onend = () => {{ status.innerText = "✅ 미션 완료! 다음으로 가시죠."; }};
                    setTimeout(() => window.speechSynthesis.speak(p_utter), 800);
                }}
            }};
            window.speechSynthesis.speak(utterance);
        }}
        setTimeout(play, 500);
        </script>
    """, height=0)

    st.markdown('<div class="next-btn">', unsafe_allow_html=True)
    if st.button("다음 문제 👉"):
        init_quiz(selected_cat)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)