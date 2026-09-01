import streamlit as st

st.set_page_config(page_title="謎解き", layout="wide")

CATEGORIES = ["容疑者", "凶器", "現場", "動機"]
SYMBOLS = ["", "〇", "×"]  # 0:空欄 1:〇 2:×

# ------------------------------------------------------------
# session_state 初期化
# ------------------------------------------------------------
if "items" not in st.session_state:
    st.session_state["items"] = {c: [] for c in CATEGORIES}
if "matrices" not in st.session_state:
    st.session_state["matrices"] = {}
if "word_input" not in st.session_state:
    st.session_state["word_input"] = ""


def matrix_key(cat1, cat2):
    return f"{cat1}__{cat2}"


def get_cell_state(cat1, cat2, i, j):
    key = matrix_key(cat1, cat2)
    return st.session_state["matrices"].get(key, {}).get((i, j), 0)


def cycle_cell(cat1, cat2, i, j):
    key = matrix_key(cat1, cat2)
    matrices = st.session_state["matrices"]
    matrices.setdefault(key, {})
    cur = matrices[key].get((i, j), 0)
    matrices[key][(i, j)] = (cur + 1) % 3
    st.session_state["matrices"] = matrices


def register_word():
    category = st.session_state.category_select
    val = st.session_state.word_input.strip()
    if category and val and val not in st.session_state["items"][category]:
        st.session_state["items"][category].append(val)
    st.session_state.word_input = ""


def remove_word(category, word):
    if word in st.session_state["items"][category]:
        st.session_state["items"][category].remove(word)
    # 関連するマトリクスのセル情報も削除（ズレ防止のため丸ごとクリア）
    for cat1, cat2 in [
        ("容疑者", "凶器"),
        ("容疑者", "現場"),
        ("容疑者", "動機"),
        ("凶器", "現場"),
        ("凶器", "動機"),
        ("現場", "動機"),
    ]:
        if category in (cat1, cat2):
            st.session_state["matrices"].pop(matrix_key(cat1, cat2), None)


def reset_all():
    st.session_state["items"] = {c: [] for c in CATEGORIES}
    st.session_state["matrices"] = {}
    st.session_state["word_input"] = ""


# ------------------------------------------------------------
# 見た目調整
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background-color: #a9b8e8;
    }
    div.stButton > button {
        width: 100%;
        height: 2.4em;
        border-radius: 4px;
        border: 1px solid #999;
        font-weight: 600;
    }
    .cell-header {
        background-color: #dfe6f7;
        text-align: center;
        font-weight: 700;
        padding: 6px 0;
        border: 1px solid #999;
    }
    .row-header {
        background-color: #dfe6f7;
        font-weight: 700;
        padding: 6px 4px;
        border: 1px solid #999;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# 左パネル（サイドバー）：登録エリア
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("## 謎解き")

    st.selectbox("選択してください...", CATEGORIES, key="category_select")

    # --- 音声入力（streamlit-mic-recorder が入っていれば利用） ---
    try:
        from streamlit_mic_recorder import speech_to_text

        voice_text = speech_to_text(
            language="ja",
            start_prompt="🎤 話す",
            stop_prompt="⏹ 停止",
            just_once=True,
            use_container_width=True,
            key="mic",
        )
        if voice_text:
            st.session_state.word_input = voice_text
    except ImportError:
        st.caption("※音声入力を使うには `pip install streamlit-mic-recorder` が必要です")

    col_in, col_btn = st.columns([3, 1])
    with col_in:
        st.text_input(
            "ワードを入力してEnter",
            key="word_input",
            on_change=register_word,
            label_visibility="collapsed",
            placeholder="ワードを入力してEnter",
        )
    with col_btn:
        st.button("✏️ 登録", on_click=register_word, use_container_width=True)

    st.divider()
    st.markdown("**登録済みワード**")
    for c in CATEGORIES:
        st.markdown(f"**{c}**")
        if st.session_state["items"][c]:
            for w in st.session_state["items"][c]:
                cols = st.columns([4, 1])
                cols[0].write(w)
                if cols[1].button("×", key=f"del_{c}_{w}"):
                    remove_word(c, w)
                    st.rerun()
        else:
            st.caption("（未登録）")

    st.divider()
    if st.button("🔄 リセット", type="primary", use_container_width=True):
        reset_all()
        st.rerun()

# ------------------------------------------------------------
# 右パネル：マトリクス表示
# ------------------------------------------------------------
st.markdown("### 対応表")

left_col, middle_col, right_col = st.columns([1, 1, 1])

left_pairs = [("凶器", "容疑者"), ("現場", "容疑者"), ("動機", "容疑者")]
middle_pairs = [("凶器", "動機"), ("現場", "動機")]
right_pairs = [("凶器", "現場")]


def render_matrix(cat1, cat2, container):
    items1 = st.session_state["items"][cat1]
    items2 = st.session_state["items"][cat2]
    if not items1 or not items2:
        return False

    with container:
        st.markdown(f"**{cat1} × {cat2}**")
        n_cols = len(items2) + 1
        header_cols = st.columns(n_cols)
        header_cols[0].markdown("<div class='cell-header'>&nbsp;</div>", unsafe_allow_html=True)
        for j, it2 in enumerate(items2):
            header_cols[j + 1].markdown(f"<div class='cell-header'>{it2}</div>", unsafe_allow_html=True)

        for i, it1 in enumerate(items1):
            row_cols = st.columns(n_cols)
            row_cols[0].markdown(f"<div class='row-header'>{it1}</div>", unsafe_allow_html=True)
            for j, it2 in enumerate(items2):
                state = get_cell_state(cat1, cat2, i, j)
                label = SYMBOLS[state] if SYMBOLS[state] else "　"
                if row_cols[j + 1].button(label, key=f"{cat1}_{cat2}_{i}_{j}"):
                    cycle_cell(cat1, cat2, i, j)
                    st.rerun()

        st.write("")
    return True


any_table_shown = False
for pair in left_pairs:
    if render_matrix(pair[0], pair[1], left_col):
        any_table_shown = True

for pair in middle_pairs:
    if render_matrix(pair[0], pair[1], middle_col):
        any_table_shown = True

for pair in right_pairs:
    if render_matrix(pair[0], pair[1], right_col):
        any_table_shown = True

if not any_table_shown:
    st.info("左側で「人物」「凶器」「犯行現場」「動機」を2種類以上登録すると、対応表が表示されます。")