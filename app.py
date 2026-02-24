import streamlit as st
import os
import random

DATA_FILE = "sentences.txt"

# --- UI 스타일 ---
st.markdown("""
    <style>
    .quiz-card { background-color: #ffffff; padding: 20px; border-radius: 25px; box-shadow: 0 4px 30px rgba(0,0,0,0.1); border: 1px solid #f0f0f0; text-align: center; }
    .context-box { background-color: #000000; color: #ffffff; border-radius: 20px; padding: 20px; margin-bottom: 20px; font-weight: 700; }
    .eng-text { font-size: 2.2rem; font-weight: 800; color: #000000; }
    .sound-accent { color: #E53935; font-size: 1.8rem; font-weight: 900; text-decoration: underline; }
    .pattern-box { background-color: #fef2f2; border: 2px dashed #E53935; border-radius: 15px; padding: 15px; margin-top: 20px; text-align: left; }
    .status-info { color: #E53935; font-weight: bold; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

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
        st.session_state.phase = "quiz"
        st.session_state.bonus_pattern = random.choice(patterns) if patterns else None

    curr = idioms[st.session_state.quiz_idx]
    _, eng, sound, mean, context = curr[:5]

    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="context-box">💡 {context}</div>', unsafe_allow_html=True)

    if st.session_state.phase == "quiz":
        # 퀴즈 로직 (간략화)
        if st.button(f"정답 확인: {eng}"):
            st.session_state.phase = "solved"
            st.rerun()

    elif st.session_state.phase == "solved":
        st.markdown(f'<div class="eng-text">{eng}</div>', unsafe_allow_html=True)
        st.write(f" 뜻: {mean}")
        st.markdown('<div id="status-box" class="status-info">쉐도잉 시작...</div>', unsafe_allow_html=True)

        # 보너스 패턴 출력
        if st.session_state.bonus_pattern:
            _, p_eng, p_sound, p_mean = st.session_state.bonus_pattern
            st.markdown(f"""
                <div class="pattern-box">
                    <div style="color:#E53935; font-weight:800;">📍 함께 공부할 패턴 영어</div>
                    <div style="font-size:1.2rem; font-weight:700;">{p_eng}</div>
                    <div style="color:#666;">{p_sound} ({p_mean})</div>
                </div>
            """, unsafe_allow_html=True)

        # TTS 로직 (숙어 5회 + 패턴 1회)
        p_eng_clean = st.session_state.bonus_pattern[1].replace("(", "").replace(")", "")
        st.components.v1.html(f"""
            <script>
            let count = 0;
            function speak() {{
                let msg = new SpeechSynthesisUtterance("{eng}");
                msg.lang = 'en-US';
                msg.onend = () => {{
                    count++;
                    if(count < 5) setTimeout(speak, 1000);
                    else {{
                        let p_msg = new SpeechSynthesisUtterance("{p_eng_clean}");
                        p_msg.lang = 'en-US';
                        window.speechSynthesis.speak(p_msg);
                    }}
                }};
                window.speechSynthesis.speak(msg);
            }}
            speak();
            </script>
        """, height=0)

        if st.button("다음 문제 👉"):
            del st.session_state.quiz_idx
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)