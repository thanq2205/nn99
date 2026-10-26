import random
import time

import streamlit as st

st.set_page_config(page_title="Verity Escape", page_icon="👾")

TIME_LIMIT = 120      # 2 phút mỗi màn
MAX_WRONG = 3         # sai quá 3 lần thì mất 1 tim
MAX_HEARTS = 3

# (tên màn, gợi ý bằng emoji, từ khóa)
LEVELS = [
    ("Sân trường", "✏️ viết chữ", "BUT"),
    ("Hành lang", "📖 đọc, học bài", "SACH"),
    ("Lớp học", "📏 đo độ dài", "THUOC"),
    ("Thư viện", "🏫 nơi bạn học mỗi ngày", "LOPHOC"),
    ("Phòng tin học", "🖍️ thầy cô viết lên đây", "BANGDEN"),
    ("Phòng hiệu trưởng", "👩‍🏫 người dạy bạn", "GIAOVIEN"),
]


def new_game():
    st.session_state.level = 0
    st.session_state.hearts = MAX_HEARTS
    st.session_state.wrong = 0
    st.session_state.msg = ""
    start_level()


def start_level():
    st.session_state.start = time.time()
    st.session_state.wrong = 0
    word = LEVELS[st.session_state.level][2]
    letters = list(word)
    random.shuffle(letters)
    st.session_state.pieces = letters


def lose_heart(reason):
    st.session_state.hearts -= 1
    st.session_state.wrong = 0
    if st.session_state.hearts <= 0:
        st.session_state.msg = "💀 Verity bắt được bạn! Quay lại màn 1."
        new_game()
    else:
        st.session_state.msg = f"💔 {reason} Mất 1 tim."
        start_level()


if "level" not in st.session_state:
    new_game()

st.title("👾 Verity Escape")

# Kết thúc game
if st.session_state.level >= len(LEVELS):
    st.balloons()
    st.success("🎉 Bạn đã thoát khỏi trường học và cắt đuôi Verity!")
    st.button("Chơi lại", on_click=new_game)
    st.stop()

name, hint, answer = LEVELS[st.session_state.level]
st.subheader(f"Màn {st.session_state.level + 1}/{len(LEVELS)} – {name}")
st.write("❤️" * st.session_state.hearts + "🖤" * (MAX_HEARTS - st.session_state.hearts))

if st.session_state.msg:
    st.warning(st.session_state.msg)


# Đồng hồ đếm ngược, tự cập nhật mỗi giây
@st.fragment(run_every=1)
def timer():
    left = TIME_LIMIT - int(time.time() - st.session_state.start)
    if left <= 0:
        lose_heart("Hết giờ, Verity đuổi kịp bạn!")
        st.rerun()
    st.progress(left / TIME_LIMIT, text=f"⏱️ Còn {left} giây – Verity đang đuổi theo!")


timer()

st.write(f"**Gợi ý:** {hint}")
st.write("**Các mảnh ghép:** " + " ".join(f"`{c}`" for c in st.session_state.pieces))
st.write("**Từ khóa:** " + " ".join("⬜" for _ in answer) + f"  ({len(answer)} ô)")

with st.form("answer", clear_on_submit=True):
    guess = st.text_input("Ghép các mảnh lại thành từ khóa:")
    ok = st.form_submit_button("Mở khóa 🔓")

if ok:
    if guess.strip().upper().replace(" ", "") == answer:
        st.session_state.level += 1
        st.session_state.msg = ""
        if st.session_state.level < len(LEVELS):
            start_level()
        st.rerun()
    else:
        st.session_state.wrong += 1
        if st.session_state.wrong > MAX_WRONG:
            lose_heart("Sai quá 3 lần!")
        else:
            st.session_state.msg = (
                f"❌ Sai rồi! ({st.session_state.wrong}/{MAX_WRONG} lần sai)"
            )
        st.rerun()
