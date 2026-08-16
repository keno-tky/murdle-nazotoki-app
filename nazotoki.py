import streamlit as st
import pandas as pd

st.set_page_config(page_title="なぞときメモアプリ", layout="wide")
st.title("📝 なぞときメモアプリ")

# ============================
# CSS（正方形セル＋色付き）
# ============================
st.markdown("""
<style>
.square-btn {
    width: 50px !important;
    height: 50px !important;
    font-size: 24px !important;
    text-align: center !important;
    padding: 0 !important;
}
.green-btn {
    background-color: #c8f7c5 !important;
    color: #008000 !important;
}
.red-btn {
    background-color: #f7c5c5 !important;
    color: #b00000 !important;
}
.empty-btn {
    background-color: #f0f0f0 !important;
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================
# 入力フォーム
# ============================
with st.form("input_form"):
    suspects = st.text_area("容疑者（改行区切り）", "A\nB\nC")
    weapons = st.text_area("凶器（改行区切り）", "ナイフ\nロープ\n毒")
    places = st.text_area("犯行現場（改行区切り）", "キッチン\n庭\n書斎")
    submitted = st.form_submit_button("マトリクス作成")

# ============================
# 初期化は「作成ボタンを押した時だけ」
# ============================
if submitted:
    st.session_state["matrix_ready"] = True
    st.session_state["suspects_list"] = [s.strip() for s in suspects.split("\n") if s.strip()]
    st.session_state["weapons_list"] = [w.strip() for w in weapons.split("\n") if w.strip()]
    st.session_state["places_list"] = [p.strip() for p in places.split("\n") if p.strip()]

    # セル状態を初期化（作成時のみ）
    for r in st.session_state["weapons_list"] + st.session_state["places_list"]:
        for c in st.session_state["suspects_list"] + st.session_state["places_list"]:
            st.session_state[f"cell_{r}_{c}"] = ""

# ============================
# マトリクス表示（session_state を参照）
# ============================
if st.session_state.get("matrix_ready", False):

    suspects_list = st.session_state["suspects_list"]
    weapons_list = st.session_state["weapons_list"]
    places_list = st.session_state["places_list"]

    block_A_rows = weapons_list
    block_A_cols = suspects_list

    block_B_rows = places_list
    block_B_cols = suspects_list

    block_C_rows = weapons_list
    block_C_cols = places_list

    def state_key(r, c):
        return f"cell_{r}_{c}"

    def btn_key(r, c):
        return f"btn_{r}_{c}"

    # ============================
    # レイアウト：左にマトリクス、右に確認表
    # ============================
    left_area, right_area = st.columns([3, 2])

    # ============================
    # 左側：マトリクス（L字）
    # ============================
    with left_area:
        st.write("### 🔍 推理マトリクス")

        # Block A（容疑者 × 凶器）
        st.write("#### 🔷 Block A：容疑者 × 凶器")
        for r in block_A_rows:
            cols = st.columns(len(block_A_cols))
            for i, c in enumerate(block_A_cols):

                sk = state_key(r, c)
                bk = btn_key(r, c)
                val = st.session_state.get(sk, "")

                if cols[i].button(val if val else "　", key=bk):
                    if val == "":
                        st.session_state[sk] = "〇"
                    elif val == "〇":
                        st.session_state[sk] = "×"
                    else:
                        st.session_state[sk] = ""
                    st.session_state["updated"] = True

        # Block B（容疑者 × 犯行現場）
        st.write("#### 🔷 Block B：容疑者 × 犯行現場")
        for r in block_B_rows:
            cols = st.columns(len(block_B_cols))
            for i, c in enumerate(block_B_cols):

                sk = state_key(r, c)
                bk = btn_key(r, c)
                val = st.session_state.get(sk, "")

                if cols[i].button(val if val else "　", key=bk):
                    if val == "":
                        st.session_state[sk] = "〇"
                    elif val == "〇":
                        st.session_state[sk] = "×"
                    else:
                        st.session_state[sk] = ""
                    st.session_state["updated"] = True

        # Block C（凶器 × 犯行現場）
        st.write("#### 🔷 Block C：凶器 × 犯行現場")
        for r in block_C_rows:
            cols = st.columns(len(block_C_cols))
            for i, c in enumerate(block_C_cols):

                sk = state_key(r, c)
                bk = btn_key(r, c)
                val = st.session_state.get(sk, "")

                if cols[i].button(val if val else "　", key=bk):
                    if val == "":
                        st.session_state[sk] = "〇"
                    elif val == "〇":
                        st.session_state[sk] = "×"
                    else:
                        st.session_state[sk] = ""
                    st.session_state["updated"] = True

    # ============================
    # 右側：確認表
    # ============================
    with right_area:
        st.write("### 📄 確認表（全体一覧）")

        all_rows = weapons_list + places_list
        all_cols = suspects_list + places_list

        df = pd.DataFrame("", index=all_rows, columns=all_cols)

        for r in all_rows:
            for c in all_cols:
                df.loc[r, c] = st.session_state.get(state_key(r, c), "")

        st.dataframe(df, use_container_width=True)

# ============================
# 再描画（updated フラグ）
# ============================
if st.session_state.get("updated", False):
    st.session_state["updated"] = False
    st.rerun()
