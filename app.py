import streamlit as st
import random

# 페이지 설정 (스마트폰 최적화)
st.set_page_config(page_title="나의 1000문장 단어장", page_icon="📖", layout="centered")

# CSS로 디자인 살짝 입히기
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #4CAF50; color: white; }
    .sentence-box { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #ddd; text-align: center; }
    .category-tag { color: #888; font-size: 0.8em; }
    .eng-text { font-size: 1.5em; font-weight: bold; color: #1E1E1E; margin: 10px 0; }
    .kor-text { font-size: 1.1em; color: #444; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로드 함수
@st.cache_data
def load_data():
    sentences = []
    try:
        with open("sentences.txt", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 4:
                    sentences.append({
                        "cat": parts[0],
                        "eng": parts[1],
                        "pron": parts[2],
                        "kor": parts[3]
                    })
    except FileNotFoundError:
        st.error("sentences.txt 파일을 찾을 수 없습니다.")
    return sentences

data = load_data()

# 세션 상태 초기화 (현재 인덱스 관리)
if 'idx' not in st.session_state:
    st.session_state.idx = 0

# 상단 타이틀
st.title("📖 나의 단어장")
st.write(f"현재 등록된 문장: {len(data)}개")

# 필터 및 검색
search_query = st.text_input("🔍 카테고리 또는 단어 검색", "")
filtered_data = [s for s in data if search_query.lower() in s['cat'].lower() or search_query.lower() in s['eng'].lower()]

if filtered_data:
    # 인덱스 범위 조절
    if st.session_state.idx >= len(filtered_data):
        st.session_state.idx = 0

    item = filtered_data[st.session_state.idx]

    # 문장 표시 카드
    st.markdown(f"""
        <div class="sentence-box">
            <div class="category-tag">[{item['cat']}]</div>
            <div class="eng-text">{item['eng']}</div>
            <div class="kor-text">{item['pron']}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 뜻 확인 버튼 (토글 방식)
    if st.button("뜻 확인하기"):
        st.success(f"📍 {item['kor']}")

    # 이동 버튼 (좌우 배치)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️"):
            st.session_state.idx = (st.session_state.idx - 1) % len(filtered_data)
            st.rerun()
    with col2:
        if st.button("랜덤 섞기 🎲"):
            st.session_state.idx = random.randint(0, len(filtered_data) - 1)
            st.rerun()
    with col3:
        if st.button("➡️"):
            st.session_state.idx = (st.session_state.idx + 1) % len(filtered_data)
            st.rerun()

else:
    st.warning("검색 결과가 없습니다.")

# 하단 진행률
if filtered_data:
    st.progress((st.session_state.idx + 1) / len(filtered_data))
    st.write(f"진행도: {st.session_state.idx + 1} / {len(filtered_data)}")