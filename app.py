import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어 쉐도잉", layout="centered")

# --- CSS: 디자인 및 레이아웃 최적화 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif !important; }
    header { visibility: hidden; height: 0px !important; }
    [data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 10px !important; margin-top: -60px !important; }

    .context-box {
        background: #1e1e1e; color: white; border-radius: 12px;
        padding: 8px 12px; margin-bottom: 10px; text-align: center; font-size: 0.9rem;
    }

    /* 보기 레이아웃: 문장 버튼과 발음 버튼 한 줄 배치 */
    .option-row {
        display: flex; align-items: center; gap: 5px; margin-bottom: 8px;
    }
    
    /* 실제 정답 체크용 버튼 스타일 */
    div.stButton > button {
        width: 100% !important; background-color: #ffffff !important;
        border: 1px solid #ddd !important; border-radius: 10px !important;
        padding: 10px !important; font-size: 0.95rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        height: 50px !important;
    }

    /* 다음 문제 버튼 전용 */
    .next-area div.stButton > button {
        background-color: #E53935 !important; color: white !important;
        height: 55px !important; border-radius: 28px !important; font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    all_rows = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 5: all_rows.append(p)
    return all_rows

all_data = load_data()

def init_quiz(cat):
    quiz_pool = [r for r in all_data if r[0] not in ["패턴", "숙어", "단어"]] if cat == "💡 전체보기" else [r for r in all_data if r[0] == cat]
    if not quiz_pool: quiz_pool = [r for r in all_data if r[0] not in ["패턴", "숙어", "단어"]]
    st.session_state.quiz_data = random.choice(quiz_pool)
    correct_eng = st.session_state.quiz_data[1]
    distractor_pool = [r for r in all_data if r[0] == "단어" and r[1] != correct_eng]
    if len(distractor_pool) < 5: distractor_pool = [r for r in all_data if r[1] != correct_eng]
    st.session_state.forest_items = random.sample(distractor_pool, 5) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.forest_items)
    st.session_state.phase = "forest"

categories = sorted(list(set([r[0] for r in all_data if r[0] not in ["패턴", "숙어", "단어"]])))
categories = ["💡 전체보기"] + categories
selected_cat = st.selectbox("", categories, label_visibility="collapsed")

if "quiz_data" not in st.session_state or st.session_state.get("last_cat") != selected_cat:
    st.session_state.last_cat = selected_cat
    init_quiz(selected_cat)

# --- 메인 화면 ---
curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

st.markdown(f'<div class="context-box"><b>{cat_name}</b><br>{target_context} ({target_mean})</div>', unsafe_allow_html=True)

if st.session_state.phase == "forest":
    for i, item in enumerate(st.session_state.forest_items):
        col1, col2 = st.columns([0.85, 0.15])
        
        with col1:
            # 텍스트 버튼 (정답 체크용)
            if st.button(f"{item[1]} / {item[2]}", key=f"ans_{i}"):
                if item[1] == target_eng:
                    st.session_state.phase = "solved"
                    st.rerun()
                else:
                    # 😈 비웃음 + 얄미운 경고창
                    st.components.v1.html(f"""
                        <script>
                        const ctx = new (window.AudioContext || window.webkitAudioContext)();
                        function beep(f, d, s) {{
                            const o = ctx.createOscillator(); const g = ctx.createGain();
                            o.type = 'sawtooth'; o.frequency.value = f;
                            g.gain.setValueAtTime(0.1, ctx.currentTime);
                            o.connect(g); g.connect(ctx.destination);
                            o.start(ctx.currentTime + s); o.stop(ctx.currentTime + s + d);
                        }}
                        beep(880, 0.1, 0); beep(1100, 0.2, 0.15);
                        alert("풉! 🤣\\n[{item[1]}]은 '{item[3]}'이라는 뜻이에요.\\n정신 차리세요! 😜");
                        </script>
                    """, height=0)

        with col2:
            # 개별 발음 버튼 (🔊 아이콘)
            if st.button("🔊", key=f"spk_{i}"):
                st.components.v1.html(f"""
                    <script>
                    window.speechSynthesis.cancel();
                    let ut = new SpeechSynthesisUtterance("{item[1].replace("'","")}");
                    ut.lang = 'en-US'; ut.rate = 0.9;
                    window.speechSynthesis.speak(ut);
                    </script>
                """, height=0)

elif st.session_state.phase == "solved":
    st.balloons()
    st.markdown(f"""
        <div style="text-align:center;">
            <h2 style="color:#007BFF; margin-bottom:0;">{target_eng}</h2>
            <p style="font-size:1.2rem; color:#E53935; font-weight:700;">{target_sound}</p>
            <h4 style="color:#444;">{target_mean}</h4>
            <hr>
            <p style="font-weight:800; color:#333;">🔊 자동 반복 쉐도잉 중...</p>
        </div>
    """, unsafe_allow_html=True)

    st.components.v1.html(f"""
        <script>
        window.speechSynthesis.cancel();
        let loop = 0;
        function play() {{
            let ut = new SpeechSynthesisUtterance("{target_eng.replace("'","")}");
            ut.lang = 'en-US'; ut.rate = 0.85;
            ut.onend = () => {{ loop++; if(loop < 5) setTimeout(play, 700); }};
            window.speechSynthesis.speak(ut);
        }}
        play();
        </script>
    """, height=0)

    st.markdown('<div class="next-area">', unsafe_allow_html=True)
    if st.button("다음 문제 👉", key="next"):
        review_pool = [r for r in all_data if r[0] == "단어"]
        if review_pool:
            w = random.choice(review_pool)
            st.components.v1.html(f"""
                <script>alert("📚 단어 복습!\\n\\n{w[1]} ({w[2]})\\n뜻: {w[3]}"); window.parent.location.reload();</script>
            """, height=0)
            init_quiz(selected_cat)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)