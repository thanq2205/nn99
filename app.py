"""
VERITY ESCAPE – Game kinh dị góc nhìn thứ nhất: bị cô giáo ma Verity truy đuổi trong trường học, vừa chạy vừa trả lời câu hỏi bài tập
Chạy:  streamlit run app.py
Đặt file nhạc "doors-roblox-ost-elevator-jam-made-with-Voicemod.mp3" cùng thư mục với app.py.
Game 3D chạy bằng Three.js, nhúng vào Streamlit qua components.html.
"""
import base64
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="VERITY ESCAPE", layout="wide")


# ---------------------------------------------------------------------------
# DỮ LIỆU CÂU ĐỐ TRẮC NGHIỆM (sửa tại đây)
# Mỗi cửa có 3 câu. Chọn đúng -> nhận 1 chữ số. Ghép theo "order" để ra mật mã.
#   q: câu hỏi | a: đáp án ĐÚNG | w: 3 đáp án SAI | digit: chữ số | hint: gợi ý
# Vị trí A/B/C/D được xáo ngẫu nhiên mỗi lần mở câu hỏi.
# ---------------------------------------------------------------------------
# Ngân hàng câu hỏi NHÌN HÌNH ĐOÁN (15 câu = 5 khu x 3 câu). e = emoji làm hình; muốn dùng ảnh của bạn thì thêm "img": "ten_file.png" (đặt cùng thư mục app.py).
# (cũ: Ngân hàng câu hỏi môn học Mỗi ván game xáo trộn vị trí đáp án A/B/C/D và chữ số chìa khóa.
#   q: câu hỏi | a: đáp án ĐÚNG | w: 3 đáp án SAI | hint: gợi ý
# Muốn thêm câu hỏi: thêm dict cùng dạng vào SCHOOL_QS (nên giữ tổng số = 15, hoặc sửa FIXED/BONUS bên dưới).
SCHOOL_QS = [
    {"e": "🐘", "q": "Đây là con vật nào?",
     "a": "Con voi", "w": ["Con tê giác", "Con hà mã", "Con lạc đà"], "digit": 4, "hint": "Có chiếc vòi dài và đôi ngà."},
    {"e": "🌋", "q": "Hình này thể hiện hiện tượng thiên nhiên nào?",
     "a": "Núi lửa phun trào", "w": ["Sóng thần", "Lốc xoáy", "Động đất"], "digit": 7, "hint": "Có dung nham nóng chảy trào ra."},
    {"e": "🦋", "q": "Đây là loài côn trùng nào?",
     "a": "Con bướm", "w": ["Con ong", "Con chuồn chuồn", "Con dơi"], "digit": 1, "hint": "Đôi cánh nhiều màu sắc, bay từ hoa này sang hoa khác."},
    {"e": "🍎", "q": "Đây là loại quả nào?",
     "a": "Quả táo", "w": ["Quả lê", "Quả đào", "Quả cà chua"], "digit": 3, "hint": "Câu chuyện quả táo rơi của Newton."},
    {"e": "⚽", "q": "Đây là quả bóng của môn thể thao nào?",
     "a": "Bóng đá", "w": ["Bóng rổ", "Bóng chuyền", "Bóng bầu dục"], "digit": 8, "hint": "Môn thể thao vua."},
    {"e": "🚲", "q": "Đây là phương tiện nào?",
     "a": "Xe đạp", "w": ["Xe máy", "Xe lăn", "Xe ba gác"], "digit": 5, "hint": "Chạy bằng sức đạp của chân."},
    {"e": "🌈", "q": "Đây là hiện tượng gì sau cơn mưa?",
     "a": "Cầu vồng", "w": ["Mưa đá", "Sấm sét", "Sương mù"], "digit": 9, "hint": "Có 7 sắc màu."},
    {"e": "🔭", "q": "Đây là dụng cụ gì?",
     "a": "Kính thiên văn", "w": ["Kính hiển vi", "Ống nhòm", "Máy ảnh"], "digit": 6, "hint": "Dùng để quan sát các vì sao."},
    {"e": "🐢", "q": "Đây là con vật nào?",
     "a": "Con rùa", "w": ["Con ốc sên", "Con cua", "Con thằn lằn"], "digit": 0, "hint": "Mang trên lưng một chiếc mai cứng."},
    {"e": "🌙", "q": "Đây là thiên thể nào?",
     "a": "Mặt trăng", "w": ["Mặt trời", "Ngôi sao", "Sao Hỏa"], "digit": 2, "hint": "Xuất hiện trên bầu trời đêm."},
    {"e": "🎹", "q": "Đây là nhạc cụ nào?",
     "a": "Đàn piano", "w": ["Đàn ghi-ta", "Đàn violin", "Trống"], "digit": 3, "hint": "Có các phím đen và phím trắng."},
    {"e": "🧲", "q": "Đây là vật gì?",
     "a": "Nam châm", "w": ["Chìa khóa", "Móng ngựa", "Cái kẹp giấy"], "digit": 7, "hint": "Hút được sắt."},
    {"e": "🍉", "q": "Đây là loại quả nào?",
     "a": "Dưa hấu", "w": ["Quả bí", "Quả dừa", "Quả bưởi"], "digit": 1, "hint": "Vỏ xanh, ruột đỏ, ngọt mát ngày hè."},
    {"e": "⏰", "q": "Đây là vật dụng gì?",
     "a": "Đồng hồ báo thức", "w": ["Cái chuông", "La bàn", "Cái cân"], "digit": 9, "hint": "Kêu vào buổi sáng để đánh thức bạn."},
    {"e": "🐧", "q": "Đây là con vật nào?",
     "a": "Chim cánh cụt", "w": ["Con vịt", "Con hải cẩu", "Con mòng biển"], "digit": 4, "hint": "Sống ở vùng cực lạnh giá, không biết bay."},
]

# Bức tranh bí ẩn: mỗi ván bốc 1 bức. e = emoji làm tranh (hoặc "img": "file.png" cùng thư mục app.py); a = từ khóa phải điền vào ô trống.
PUZZLES = [
    {"e": "🦁", "a": "SƯ TỬ"},
    {"e": "🚀", "a": "TÊN LỬA"},
    {"e": "🏰", "a": "LÂU ĐÀI"},
    {"e": "🌻", "a": "HOA HƯỚNG DƯƠNG"},
    {"e": "🐙", "a": "BẠCH TUỘC"},
    {"e": "🎸", "a": "ĐÀN GHI TA"},
    {"e": "🚁", "a": "MÁY BAY TRỰC THĂNG"},
]

_ROOMS = [   # thứ tự = kiểu khu 3D: 0 sân cờ, 1 dãy lớp học, 2 sân bóng, 3 vườn cây phượng, 4 cổng trường
    ("Sân cờ", "Cột cờ lặng gió giữa đêm. Các dãy lớp học xung quanh tối om, cửa sổ đen kịt..."),
    ("Dãy lớp học", "Cửa lớp khép chặt, ghế đá ướt mưa dưới hành lang. Có tiếng thì thầm: 'Trả lời đi...'"),
    ("Sân bóng", "Sân bóng giữa đêm, hai khung thành trống trơn. Verity đang ở đâu đó gần đây..."),
    ("Vườn cây phượng", "Hàng cây đung đưa trong bóng tối. Có thứ gì đó đang di chuyển..."),
    ("Cổng trường", "Cổng sắt đã khóa. Verity đang đứng đợi ngay bên cạnh..."),
]
DOORS = [
    {"name": n, "intro": t, "order": [0, 1, 2], "order_text": "Ghép chìa 1 → chìa 2 → chìa 3.",
     "questions": SCHOOL_QS[i * 3:(i + 1) * 3]}
    for i, (n, t) in enumerate(_ROOMS)
]

MUSIC_FILE = "doors-roblox-ost-elevator-jam-made-with-Voicemod.mp3"
PLAY_MUSIC_FILE = "05. In The House.mp3"   # nhạc nền khi đang chơi

# Âm thanh bão: sấm cắt từ file "tiengsamset.mp3" (đã xử lý) + tiếng mưa lặp liền mạch.
# Đặt 2 file này cùng thư mục với app.py. Thiếu file thì game tự dùng âm thanh tổng hợp như cũ.
# Tiếng bước chân: file "tiengchan.mp3" (đặt cùng thư mục với app.py). Game cắt từng bước chân theo bảng STEP_CLIPS
# [giây bắt đầu, độ to] rồi phát lần lượt; chạy thì phát nhanh hơn + cao hơn một chút. Thiếu file -> dùng tiếng tổng hợp cũ.
CATCH_FILE = "faaahhhh.mp3"     # tiếng khi ma bắt được người chơi (đặt cùng thư mục với app.py; thiếu file -> dùng tiếng gào tổng hợp)
GHOST_FILE = "tiengma.mp3"      # tiếng ma: phát khi ma xuất hiện (đặt cùng thư mục với app.py; thiếu file -> dùng tiếng tổng hợp)
STEP_FILE = "tiengchan.mp3"
SIREN_FILE = "siren-head-sounds-new.mp3"   # tiếng còi kinh dị: thỉnh thoảng vang lên từ xa trong lúc chơi (đặt cùng thư mục với app.py; thiếu file -> bỏ qua)
STEP_CLIPS = [[0.357, 0.126], [1.009, 0.144], [1.609, 0.085], [2.236, 0.152], [2.852, 0.159], [3.477, 0.216], [4.102, 0.09], [4.775, 0.137], [5.373, 0.078], [6.027, 0.132], [6.624, 0.088], [7.266, 0.21], [7.871, 0.219], [8.504, 0.177], [9.101, 0.236], [9.732, 0.196], [10.365, 0.212], [11.021, 0.115], [11.64, 0.086], [12.267, 0.153], [12.883, 0.157], [13.508, 0.215], [14.133, 0.089], [14.806, 0.137], [15.404, 0.078], [16.058, 0.132], [16.655, 0.142], [17.322, 0.126], [17.959, 0.136], [18.628, 0.115], [19.278, 0.116], [19.922, 0.21], [20.53, 0.253], [21.179, 0.152], [21.823, 0.087], [22.482, 0.154], [23.096, 0.083], [23.784, 0.121], [25.072, 0.092], [25.708, 0.107], [26.407, 0.112]]
THUNDER_FILE = "thunder_fx.mp3"
RAIN_FILE = "rain_loop.wav"

# ---- ĐỔI ÂM THANH: đặt 1 file nhạc/âm thanh mới (cùng thư mục với app.py) rồi sửa tên ở đây. ----
# Nếu file tồn tại, nó thay cho: nhạc menu, nhạc nền khi chơi, tiếng ma, tiếng bị bắt và tiếng còi.
# Không tìm thấy file thì game giữ nguyên các file cũ.
SOUND_FILE = "sound.mp3"


def _snd(default: str) -> str:
    return SOUND_FILE if (Path(__file__).resolve().parent / SOUND_FILE).exists() else default


MUSIC_FILE = _snd(MUSIC_FILE)
PLAY_MUSIC_FILE = _snd(PLAY_MUSIC_FILE)
CATCH_FILE = _snd(CATCH_FILE)
GHOST_FILE = _snd(GHOST_FILE)
SIREN_FILE = _snd(SIREN_FILE)
# Bảng cắt của THUNDER_FILE: s = giây bắt đầu clip trong file, d = độ dài, c = thời điểm TIẾNG NỔ trong clip
# (game căn c đúng vào lúc tia chớp + độ trễ), k = 'crack' (nổ gắt, dùng cho sét gần) / 'roll' (sấm cuộn, sét xa).
THUNDER_CLIPS = [
    {"n": "A", "k": "crack", "s": 0.0, "d": 3.07, "c": 0.08},
    {"n": "B", "k": "crack", "s": 3.47, "d": 1.866, "c": 0.08},
    {"n": "C", "k": "crack", "s": 5.736, "d": 1.81, "c": 0.08},
    {"n": "D", "k": "crack", "s": 7.946, "d": 7.108, "c": 0.08},
    {"n": "E", "k": "crack", "s": 15.454, "d": 8.08, "c": 0.08},
    {"n": "F", "k": "crack", "s": 23.934, "d": 3.082, "c": 0.08},
    {"n": "G", "k": "crack", "s": 27.416, "d": 2.428, "c": 0.08},
    {"n": "I", "k": "crack", "s": 30.244, "d": 5.47, "c": 0.08},
    {"n": "L1", "k": "crack", "s": 36.114, "d": 1.766, "c": 0.08},
    {"n": "M", "k": "crack", "s": 38.28, "d": 4.31, "c": 0.08},
    {"n": "N", "k": "crack", "s": 42.99, "d": 2.514, "c": 0.08},
    {"n": "O", "k": "crack", "s": 45.904, "d": 3.952, "c": 0.08},
    {"n": "J", "k": "roll", "s": 50.256, "d": 6.35, "c": 0.3},
    {"n": "L2", "k": "roll", "s": 57.006, "d": 5.15, "c": 0.3},
    {"n": "intro", "k": "roll", "s": 62.556, "d": 2.85, "c": 0.3}
]


def _norm(s: str) -> str:
    """So khớp tên file không phân biệt hoa/thường, dấu cách, gạch dưới, dấu chấm."""
    return "".join(ch for ch in s.lower() if ch.isalnum())


@st.cache_data(show_spinner=False)
def load_mp3(name: str, skip: str = "", fallback: bool = False) -> str:
    """Đọc file mp3 (cùng thư mục với app.py) và nhúng vào game dạng data-URI."""
    base = Path(__file__).resolve().parent
    p = base / name
    if not p.exists():
        want = _norm(Path(name).stem)
        files = sorted(base.glob("*.mp3"))
        same = [f for f in files if _norm(f.stem) == want]
        if same:
            p = same[0]
        elif fallback:
            other = [f for f in files if _norm(f.stem) != _norm(Path(skip).stem)]
            if not other:
                return ""
            p = other[0]
        else:
            return ""
    return "data:audio/mpeg;base64," + base64.b64encode(p.read_bytes()).decode()


@st.cache_data(show_spinner=False)
def load_asset(name: str, mime: str) -> str:
    """Đọc file âm thanh cùng thư mục với app.py -> data-URI (rỗng nếu không có)."""
    p = Path(__file__).resolve().parent / name
    if not p.exists():
        return ""
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


# Kho câu hỏi bổ sung: mỗi ván game bốc ngẫu nhiên 15 câu từ (kho gốc + kho này) rồi chia ngẫu nhiên vào các phòng.
EXTRA_QUESTIONS = []                      # kho dự phòng (để trống)
FIXED_QUESTIONS = SCHOOL_QS[:5]           # mỗi phòng luôn có 1 câu trong 5 câu này
BONUS_QUESTIONS = SCHOOL_QS[5:]           # mỗi phòng nhận thêm 2 câu trong 10 câu này


def _pic(q) -> str:
    """Hình của câu hỏi: file ảnh (nếu có 'img' và file tồn tại) hoặc emoji 'e'."""
    f = q.get("img")
    if f:
        ext = Path(f).suffix.lower().lstrip(".")
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp", "gif": "image/gif"}.get(ext, "image/png")
        d = load_asset(f, mime)
        if d:
            return d
    return q.get("e", "")


def _qd(q) -> dict:
    return {"q": q["q"], "o": [q["a"]] + q["w"], "hint": q["hint"], "p": _pic(q)}


def build_fixed() -> str:
    return json.dumps([_qd(q) for q in FIXED_QUESTIONS], ensure_ascii=False)


def build_bonus() -> str:
    return json.dumps([_qd(q) for q in BONUS_QUESTIONS], ensure_ascii=False)


def build_pool() -> str:
    return json.dumps([_qd(q) for q in EXTRA_QUESTIONS], ensure_ascii=False)


def build_puz() -> str:
    return json.dumps([{"p": _pic(x), "a": x["a"]} for x in PUZZLES], ensure_ascii=False)


def build_data() -> str:
    out = []
    for d in DOORS:
        out.append({
            "name": d["name"], "intro": d["intro"], "order": d["order"], "order_text": d["order_text"],
            # o[0] luôn là đáp án đúng; phía JS sẽ xáo thứ tự A/B/C/D
            "questions": [
                {**_qd(q), "digit": q["digit"]}
                for q in d["questions"]
            ],
        })
    return json.dumps(out, ensure_ascii=False)


# ---------------------------------------------------------------------------
# GAME 3D (HTML + Three.js)
# ---------------------------------------------------------------------------
GAME_HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<style>
  html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#000;font-family:'Times New Roman','Noto Serif',Georgia,serif;color:#eee;user-select:none}
  /* Khung 16:9: #stage luôn giữ tỉ lệ 16:9 (letterbox), #ui là lớp giao diện thiết kế ở 1280x720 rồi scale theo khung */
  #stage{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);overflow:hidden;background:#000}
  #c{position:absolute;inset:0}
  #c canvas{display:block}
  #ui{position:absolute;left:0;top:0;width:1280px;height:720px;transform-origin:0 0;overflow:hidden;pointer-events:none}
  .ov,#modal,#sl,#fs,button,input{pointer-events:auto}
  #fs{position:absolute;top:8px;right:10px;z-index:30;padding:5px 10px;font-size:13px;margin:0;opacity:.75}
  #fs:hover,#mu:hover,#pz:hover{opacity:1}
  #pz{position:absolute;top:8px;right:132px;z-index:30;padding:5px 9px;font-size:13px;margin:0;opacity:.75;display:none}
  .touch #pz{padding:10px 14px;font-size:18px;right:170px}
  #pbl{display:none;flex-wrap:wrap;justify-content:center;gap:5px;margin:6px 0}
  .pc{display:inline-block;width:30px;height:38px;border-bottom:4px solid #16130f;font-size:26px;font-weight:900;line-height:38px;color:#8a0f0f}
  .pg{display:inline-block;width:16px}
  #box.pz #mpic{height:auto;line-height:0;font-size:0}
  #box.pz #mpic canvas{width:400px;height:240px;border:3px solid #16130f;background:#120d09}
  #box.pz #mi{font-size:20px;padding:6px;width:70%}
  #mu{position:absolute;top:8px;right:74px;z-index:30;padding:5px 9px;font-size:13px;margin:0;opacity:.75}
  #lockbtn{position:absolute;right:16px;bottom:16px;z-index:7;width:56px;height:56px;padding:0;margin:0;border-radius:50%;
           font-size:18px;font-weight:bold;background:rgba(0,0,0,.55);border:2px solid #9a2a2a;display:none}
  #lockbtn.on{background:rgba(120,90,10,.75);border-color:#ffd86b;box-shadow:0 0 14px #a80}
  #cross.lk{box-sizing:border-box;width:22px;height:22px;margin:-11px;background:transparent;border:2px solid rgba(255,255,255,.85);box-shadow:0 0 6px #000}
  #cross.lk:after{content:'';position:absolute;left:50%;top:50%;width:4px;height:4px;margin:-2px;border-radius:50%;background:#fff}
  #musichint{display:none;margin-top:14px;font-size:14px;color:#8a8070;animation:mh 1.6s infinite}
  @keyframes mh{0%,100%{opacity:.35}50%{opacity:1}}
  .row{display:flex;align-items:center;justify-content:center;gap:10px;margin:8px 0}
  .row input[type=range]{width:320px;accent-color:#b3141a}
  .sq{width:42px;padding:6px 0;font-size:20px}
  #settings .hw{text-align:center;width:600px}
  #ql{color:#ffd86b;font-size:19px;margin:4px 0}
  #qd{font-size:13px;color:#9a9080;margin:4px auto;max-width:520px}
  #opts{display:none;flex-direction:column;gap:8px;margin-bottom:8px}
  .opt{display:flex;align-items:center;gap:12px;width:100%;text-align:left;font-size:17px;padding:10px 14px;margin:0;letter-spacing:0;box-sizing:border-box}
  .opt b{display:inline-block;flex:none;min-width:28px;height:28px;line-height:28px;text-align:center;border-radius:50%;background:#7a2a2a;color:#ffd86b}
  .opt.bad{opacity:.38;text-decoration:line-through;cursor:not-allowed;background:#1c0808;border-color:#4a2a2a;box-shadow:none}
  .ov{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;
      background:radial-gradient(ellipse at center,rgba(30,8,8,.88),rgba(0,0,0,.97));text-align:center;padding:20px;z-index:20;overflow:auto}
  #mbg{position:absolute;inset:0;display:none;overflow:hidden;background:#000}
  #mimg{position:absolute;inset:-2%;background:#000 url(__MENUBG__) center/cover no-repeat;animation:mzoom 40s ease-in-out infinite alternate}
  @keyframes mzoom{from{transform:scale(1) translateX(-.6%)}to{transform:scale(1.07) translateX(.6%)}}
  #msky{position:absolute;left:0;right:0;top:0;height:58%;background:linear-gradient(#010103 0%,rgba(1,1,4,.96) 45%,rgba(2,3,8,.7) 75%,rgba(0,0,0,0) 100%)}   /* bầu trời đen, chỉ lộ ra khi sét */
  #mfx{position:absolute;inset:0;width:100%;height:100%}
  #mfl{position:absolute;inset:0;opacity:0;background:radial-gradient(ellipse at 45% 30%,rgba(200,220,255,.9),rgba(120,150,220,.35) 60%,rgba(60,80,140,.1))}
  #menu{background:radial-gradient(ellipse at center,rgba(0,0,0,.22) 0%,rgba(0,0,0,.05) 50%,rgba(0,0,0,.3) 100%)}   /* menu trong suốt để thấy khu rừng phía sau */
  #menu h1{text-shadow:0 0 22px #000,0 0 8px #000,0 0 18px #600}
  .ov h1{font-size:64px;letter-spacing:14px;margin:0 0 18px;color:#b3141a;text-shadow:0 0 18px #600,0 0 4px #000}
  .ov p{max-width:580px;line-height:1.55;color:#c9c0b0}
  button{background:#3a0d0d;color:#eee;border:1px solid #9a2a2a;padding:10px 22px;font-size:16px;
         border-radius:4px;cursor:pointer;margin:4px;font-family:inherit;letter-spacing:1px}
  button:hover{background:#6a1414;box-shadow:0 0 12px #a00}
  .mb{display:flex;flex-direction:column;align-items:center;gap:6px}
  .mb button{width:260px;font-size:19px;padding:12px 22px}
  #story{background:radial-gradient(ellipse at center,rgba(0,0,0,.62),rgba(0,0,0,.85));animation:sopen 1.2s ease}
  @keyframes sopen{0%{opacity:0;filter:brightness(3.2) blur(8px)}35%{opacity:.8;filter:brightness(1.8) blur(3px)}55%{opacity:.35}100%{opacity:1;filter:none}}
  #sttl{letter-spacing:8px;animation:stitle 1.6s ease both}
  @keyframes stitle{from{letter-spacing:34px;opacity:0;filter:blur(6px)}to{letter-spacing:8px;opacity:1;filter:none}}
  .sty{max-width:620px;padding:0 10px;margin-bottom:22px;text-align:center;line-height:1.7;color:#cfc6b6;font-size:19px}
  .sty p{margin:0 auto 14px;max-width:none;opacity:0;animation:sfade 1.5s ease forwards}
  .sty p:nth-child(1){animation-delay:.5s}.sty p:nth-child(2){animation-delay:2.4s}
  .sty b{color:#fff}
  .sty .cl{color:#ffd86b;letter-spacing:1px;text-shadow:0 0 10px #c8861a,0 0 22px #6a4a10}
  .sty kbd{background:#2a1010;border:1px solid #7a2a2a;border-radius:3px;padding:0 6px;font-family:inherit;color:#ffd86b}
  #story .mb button{opacity:0;animation:sfade 1.2s ease 3.4s forwards}
  @keyframes sfade{0%{opacity:0;filter:blur(9px);transform:translateY(12px) scale(1.04)}45%{opacity:.85}58%{opacity:.25}72%{opacity:.95}100%{opacity:1;filter:none;transform:none}}
  .hw{max-width:700px;text-align:left;line-height:1.5;color:#c9c0b0;font-size:15px}
  .hw h3{margin:14px 0 4px;color:#d9b45a;font-size:17px;letter-spacing:1px}
  .hw ul{margin:0;padding-left:20px}
  .hw b{color:#fff}
  .hw kbd{background:#2a1010;border:1px solid #7a2a2a;border-radius:3px;padding:0 6px;font-family:inherit;color:#ffd86b}
  #hud{position:absolute;top:10px;left:12px;font-size:17px;text-shadow:0 0 4px #000;z-index:5;line-height:1.5}
  #ks{color:#ffd86b;font-size:20px}
  #ot{font-size:13px;color:#bbb}
  #sl{font-size:13px;color:#999;cursor:pointer;display:inline-block;margin-top:2px}
  #sl.on{color:#7dff9a}
  #help{position:absolute;bottom:8px;left:12px;font-size:12px;color:#8a8a8a;z-index:5;text-shadow:0 0 3px #000}
  #cross{position:absolute;left:50%;top:50%;width:4px;height:4px;margin:-2px;border-radius:50%;
         background:rgba(255,255,255,.45);z-index:5;pointer-events:none}
  #prompt{position:absolute;left:50%;top:58%;transform:translateX(-50%);background:rgba(0,0,0,.65);
          padding:6px 14px;border-radius:4px;font-size:18px;display:none;z-index:6;border:1px solid #9a2a2a}
  #banner{position:absolute;left:50%;top:14%;transform:translateX(-50%);text-align:center;white-space:pre-line;
          font-size:22px;text-shadow:0 0 8px #000;opacity:0;transition:opacity .5s;z-index:6;max-width:80%;pointer-events:none}
  #whisper{position:absolute;font-size:30px;font-style:italic;color:#8a0c0c;opacity:0;transition:opacity 1s;
           z-index:4;pointer-events:none;text-shadow:0 0 10px #000;letter-spacing:3px}
  #flash{position:absolute;inset:0;background:#a00;opacity:0;pointer-events:none;transition:opacity .45s;z-index:11}
  #bars{position:absolute;inset:0;pointer-events:none;z-index:9;opacity:0;transition:opacity .6s;
        background:linear-gradient(#000 0 12%,transparent 12% 88%,#000 88%)}
  #bars.on{opacity:1}
  .chk{display:flex;align-items:center;gap:10px;justify-content:center;margin:14px 0;color:#e0d6c0;font-size:16px;cursor:pointer}
  .chk input{width:20px;height:20px;accent-color:#b3141a;cursor:pointer}
  #lids{position:absolute;inset:0;display:none;pointer-events:none;z-index:11}
  .lid{position:absolute;left:-3%;right:-3%;height:50%;background:#000;box-shadow:0 0 70px 36px #000}
  .lt{top:0;border-radius:0 0 50% 50%/0 0 34px 34px}.lb{bottom:0;border-radius:50% 50% 0 0/34px 34px 0 0}
  #skiph{position:absolute;bottom:14px;right:18px;z-index:13;font-size:12px;color:#9a8a78;opacity:.45;display:none;pointer-events:none;letter-spacing:1px}
  #fade{position:absolute;inset:0;background:#000;opacity:0;pointer-events:none;transition:opacity .8s;z-index:12}
  #scare{position:absolute;inset:0;width:100%;height:100%;display:none;pointer-events:none;z-index:10;image-rendering:pixelated}
  #hide{position:absolute;inset:0;display:none;pointer-events:none;z-index:4}
  /* Tủ: hai cánh cửa khép lại, chỉ chừa 1 kẽ hở DỌC ở giữa để nhìn ra ngoài (mép cửa có viền gỗ mờ) */
  #hide.ward{background:linear-gradient(90deg,#000 0 45.6%,#10240f 45.6% 46.6%,transparent 46.6% 53.4%,#10240f 53.4% 54.4%,#000 54.4% 100%)}
  #hide.bed{background:linear-gradient(#000 0 42%,transparent 60%),radial-gradient(ellipse at center,transparent 45%,rgba(0,0,0,.85) 100%)}
  #vig{position:absolute;inset:0;pointer-events:none;z-index:3;
       background:radial-gradient(ellipse at center,transparent 38%,rgba(0,0,0,.55) 75%,rgba(0,0,0,.95) 100%)}
  #grain{position:absolute;inset:0;width:100%;height:100%;image-rendering:pixelated;opacity:.2;
         mix-blend-mode:overlay;pointer-events:none;z-index:3}
  #lowhp{position:absolute;inset:0;pointer-events:none;z-index:3;opacity:0;
         background:radial-gradient(ellipse at center,transparent 35%,rgba(150,0,0,.75) 100%)}
  #lowhp.pulse{animation:pl 1.1s infinite}
  @keyframes pl{0%,100%{opacity:.25}50%{opacity:1}}
  #modal{position:absolute;inset:0;display:none;align-items:center;justify-content:center;
         background:rgba(0,0,0,.65);z-index:15}
  /* Bảng câu hỏi = một tờ giấy cũ */
  /* Bảng câu hỏi = tờ giấy nhàu, rách mép, chữ viết tay bằng bút chì (kiểu mấy tờ giấy trong Doors) */
  #box{position:relative;color:#16130f;border:0;padding:36px 48px 34px;width:min(760px,90%);
       text-align:center;transform:rotate(-1deg);
       font-family:'Segoe Print','Bradley Hand','Chalkboard SE','Comic Sans MS','Marker Felt',cursive;
       background:#b3a78c;background-size:100% 100%;
       clip-path:polygon(1% 3%,12% 0,27% 2.5%,44% .5%,63% 2%,82% 0,99% 2%,100% 20%,98.5% 38%,100% 57%,98% 76%,100% 98%,84% 100%,66% 98%,48% 100%,30% 98.5%,12% 100%,0 97%,1.5% 78%,0 58%,2% 38%,0 18%)}
  #mt{color:#8a0f0f;font-size:30px;margin-bottom:12px;font-weight:900;letter-spacing:2px;text-transform:uppercase;text-shadow:none}
  #mq{font-size:27px;line-height:1.4;margin-bottom:18px;color:#16130f;font-weight:900;text-transform:uppercase;letter-spacing:.5px;
      text-shadow:none;-webkit-font-smoothing:antialiased}
  #vd{display:none;margin:-4px 0 10px;color:#8a0f0f;font-size:20px;font-weight:900;letter-spacing:1px;animation:mh .8s infinite}
  #mpic{display:none;margin:0 auto 8px;height:112px;line-height:112px;font-size:92px;font-family:'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji',sans-serif;text-shadow:none}
  #mpic img{max-height:112px;max-width:70%;border:3px solid #16130f;vertical-align:middle;transform:rotate(1deg)}
  #box.pic{padding:22px 40px 18px}
  #box.pic #mt{font-size:24px;margin-bottom:4px}
  #box.pic #mq{font-size:23px;margin-bottom:6px}
  #box.pic .opt{font-size:21px;padding:6px 16px;gap:14px}
  #box.pic .opt b{min-width:34px;height:34px;line-height:30px;font-size:19px}
  #box.pic #fb{min-height:22px;margin:4px 0;font-size:17px}
  #mi{width:80%;padding:9px;font-size:22px;border:0;border-bottom:3px solid #2b2722;border-radius:0;
      background:rgba(255,255,255,.14);color:#2b2722;text-align:center;outline:none;font-family:inherit;letter-spacing:4px}
  #fb{min-height:28px;margin:10px 0;color:#8a0f0f;font-size:21px;font-weight:900;text-transform:uppercase;letter-spacing:1px}
  #box button{background:rgba(40,32,20,.06);color:#16130f;border:3px solid #16130f;border-radius:3px 8px 4px 7px;
      box-shadow:none;font-family:inherit;text-transform:uppercase;text-shadow:none;font-weight:900;font-size:19px;padding:10px 22px}
  #box button:hover{background:#16130f;color:#d8ccb0;box-shadow:none;text-shadow:none}
  #box .opt{font-size:25px;font-weight:900;padding:11px 18px;gap:16px;letter-spacing:.5px}
  #box .opt b{background:transparent;color:#8a0f0f;border:3px solid #8a0f0f;text-shadow:none;font-size:22px;min-width:40px;height:40px;line-height:36px}
  #box .opt.bad{opacity:.5;text-decoration:line-through;text-decoration-thickness:3px;cursor:not-allowed;background:rgba(0,0,0,.06);border-color:#7a6e55;color:#5e5543}
  #box .opt.bad:hover{background:rgba(0,0,0,.06);color:#5e5543}
  html,body,#stage,#c canvas{touch-action:none;overscroll-behavior:none;-webkit-touch-callout:none;-webkit-tap-highlight-color:transparent;-webkit-user-select:none}
  #tui{display:none}
  .tb{position:absolute;z-index:8;border-radius:50%;border:2px solid #9a2a2a;background:rgba(0,0,0,.45);color:#eee;font-weight:bold;
      display:flex;align-items:center;justify-content:center;pointer-events:auto;touch-action:none;user-select:none;-webkit-user-select:none}
  .tb.on{background:rgba(120,90,10,.75);border-color:#ffd86b}
  #tE{right:40px;bottom:70px;width:110px;height:110px;font-size:40px}
  #tF{right:60px;bottom:200px;width:70px;height:70px;font-size:28px}
  #tRun{right:182px;bottom:34px;width:84px;height:84px;font-size:17px;letter-spacing:1px}
  #joyB,#joyK{position:absolute;border-radius:50%;display:none;pointer-events:none;z-index:7}
  #joyB{width:150px;height:150px;margin:-75px;border:2px solid rgba(255,255,255,.35);background:rgba(255,255,255,.06)}
  #joyK{width:64px;height:64px;margin:-32px;background:rgba(255,255,255,.3);border:2px solid rgba(255,255,255,.55)}
  .touch #fs{padding:10px 16px;font-size:18px}
  .touch #mu{padding:10px 14px;font-size:18px;right:104px}
  #rot{position:fixed;inset:0;z-index:99;background:#000;color:#d9b45a;display:none;align-items:center;justify-content:center;
       text-align:center;padding:20px;font-size:22px;letter-spacing:2px}

  /* ===== GIAO DIỆN MỚI: tối giản, chữ monospace, màu vàng; menu lệch trái, HUD ở góc dưới trái ===== */
  .ov,#hud,#prompt,#banner,#help,#whisper{font-family:'Consolas','Courier New','Noto Sans Mono',monospace}
  .ov h1{color:#f2d64b;font-weight:700;text-shadow:0 0 22px rgba(242,214,75,.35),0 0 4px #000}
  .ov p,.hw{color:#cfd2c4}
  .hw h3{color:#f2d64b;letter-spacing:3px;text-transform:uppercase;font-size:15px;border-bottom:1px solid rgba(242,214,75,.3);padding-bottom:3px}
  button{background:transparent;color:#f2d64b;border:1px solid #f2d64b;border-radius:0;letter-spacing:2px;text-transform:uppercase}
  button:hover{background:#f2d64b;color:#0b0b08;box-shadow:none}
  .opt.bad{background:#1a1a12}
  #menu{align-items:flex-start;justify-content:flex-end;padding:0 0 74px 96px;text-align:left;
        background:linear-gradient(90deg,rgba(0,0,0,.9) 0%,rgba(0,0,0,.55) 38%,rgba(0,0,0,0) 72%)}
  #menu h1{font-size:76px;letter-spacing:8px;white-space:nowrap;margin:0 0 2px;line-height:1;color:#f2d64b;text-shadow:0 0 30px rgba(242,214,75,.4),0 0 4px #000}
  #menu h1:after{content:'cô giáo ma · đêm bão · 15 mảnh ghép';display:block;font-size:15px;letter-spacing:5px;font-weight:400;color:#9a9a86;margin:10px 0 34px;text-transform:uppercase;text-shadow:none}
  #menu .mb{align-items:flex-start;gap:0}
  #menu .mb button{width:340px;text-align:left;font-size:21px;padding:13px 22px;margin:0;background:transparent;border:0;border-left:3px solid rgba(242,214,75,.22);color:#d8d8c4;letter-spacing:6px}
  #menu .mb button:hover{background:rgba(242,214,75,.08);border-left-color:#f2d64b;color:#f2d64b;padding-left:34px;box-shadow:none}
  #musichint{text-align:left;color:#7a7a68}
  #story .mb button,#settings button,#howto button,#over button,#win button{border-radius:0}
  #hud{top:auto;left:0;bottom:34px;padding:12px 20px 12px 18px;font-size:15px;line-height:1.45;background:linear-gradient(90deg,rgba(0,0,0,.72),rgba(0,0,0,0));border-left:3px solid #f2d64b}
  #dn{font-size:13px;letter-spacing:4px;color:#f2d64b;text-transform:uppercase;margin-bottom:2px}
  #ks{color:#f2d64b;font-size:16px}
  #ot{font-size:12px;color:#a8a894;max-width:340px}
  #stw{border-color:#f2d64b !important;background:rgba(0,0,0,.6) !important}
  #help{top:8px;bottom:auto;left:12px;font-size:11px;color:#77776a}
  #prompt{border:1px solid #f2d64b;background:rgba(0,0,0,.7);border-radius:0;letter-spacing:1px;font-size:16px}
  #banner{font-size:20px;letter-spacing:1px;text-shadow:0 0 8px #000,0 0 3px #000}
  #fs,#mu,#pz{background:rgba(0,0,0,.55);border-radius:0}

  /* ===== Nền menu: mặt cười vàng trên nền đen, đặt bên phải ===== */
  #mbg{background:#000}
  #mimg{inset:0;background:#000 url(__MENUBG__) 74% 50%/auto 94% no-repeat;animation:none}
  #msky{display:none}

  /* ===== Bảng cốt truyện: bố cục 2 thẻ cạnh nhau, căn trái ===== */
  #story{align-items:flex-start;justify-content:center;padding:0 80px;text-align:left;
         background:linear-gradient(90deg,rgba(0,0,0,.92) 0%,rgba(0,0,0,.7) 60%,rgba(0,0,0,.45) 100%)}
  #story .sty{max-width:none;width:100%;padding:0;margin:0 0 30px;text-align:left}
  #story .sh{font-size:13px;letter-spacing:6px;color:#8a8a76;margin-bottom:18px;opacity:0;animation:sfade 1.2s ease .2s forwards}
  #story .cols{display:flex;gap:24px;align-items:stretch}
  #story .card{flex:1;padding:20px 24px 14px;background:rgba(0,0,0,.55);border-top:3px solid #f2d64b;opacity:0;animation:sfade 1.5s ease forwards}
  #story .card:nth-child(1){animation-delay:.5s}
  #story .card:nth-child(2){animation-delay:2.4s}
  #story .card.danger{border-top-color:#d01a1a}
  #story h4{margin:0 0 12px;font-size:16px;letter-spacing:5px;color:#f2d64b}
  #story .danger h4{color:#ff4a3a}
  #story ol,#story ul{margin:0;padding-left:20px;font-size:16px;line-height:1.65;color:#cfd2c4}
  #story li{margin-bottom:10px}
  #story ul{list-style:square}

  /* ===== BẢNG PHẤN: đổi màu chủ đạo sang trắng phấn + xanh bảng, bỏ vàng ===== */
  .ov h1{color:#e8f1e4;text-shadow:0 0 18px rgba(180,230,190,.3),0 0 4px #000}
  .hw h3{color:#9fd8a8;letter-spacing:2px;text-transform:none;border-bottom:1px dashed rgba(159,216,168,.4)}
  button{color:#e8f1e4;border:2px dashed #9fd8a8;letter-spacing:1px;text-transform:none;border-radius:6px}
  button:hover{background:#9fd8a8;color:#0c1a12}
  #menu{align-items:center;justify-content:flex-start;padding:60px 0 0 0;text-align:center;
        background:linear-gradient(180deg,rgba(6,20,14,.88) 0%,rgba(6,20,14,.5) 55%,rgba(0,0,0,.1) 100%)}
  #menu h1{font-size:64px;letter-spacing:4px;color:#e8f1e4;text-shadow:0 0 24px rgba(159,216,168,.4),0 0 4px #000}
  #menu h1:after{content:'cô giáo ma · đêm bão · 15 mảnh ghép';color:#8fb59a;letter-spacing:3px;text-transform:none}
  #menu .mb{align-items:center}
  #menu .mb button{width:300px;text-align:center;border:2px dashed rgba(159,216,168,.5);border-left:2px dashed rgba(159,216,168,.5);letter-spacing:2px;color:#e8f1e4;border-radius:6px;margin:6px 0}
  #menu .mb button:hover{background:rgba(159,216,168,.15);border-color:#9fd8a8;color:#fff;padding-left:22px}
  #musichint{text-align:center;color:#6f9a7a}
  #hud{left:auto;right:0;bottom:34px;padding:12px 18px 12px 20px;background:linear-gradient(270deg,rgba(0,0,0,.72),rgba(0,0,0,0));border-left:0;border-right:3px solid #9fd8a8;text-align:right}
  #dn,#ks{color:#9fd8a8}
  #stw{border-color:#9fd8a8 !important}
  #prompt{border:2px dashed #9fd8a8;border-radius:6px}
  #fs,#mu,#pz{border-radius:50%}
  #story{align-items:center;text-align:center}
  #story .card{border-top:0;border-bottom:3px solid #9fd8a8}
  #story h4{color:#9fd8a8}
  #box{background:#12281d !important;border:6px solid #6b4a2b !important;color:#eef3ea !important}
</style>
</head>
<body>
<div id="stage"><div id="c"></div><div id="mbg"><div id="mimg"></div><div id="msky"></div><canvas id="mfx"></canvas><div id="mfl"></div></div><div id="ui">
<div id="vig"></div><canvas id="grain"></canvas><div id="lowhp"></div>
<div id="cross"></div>
<div id="hud"><div id="dn"></div><div id="hp"></div><div id="hn"></div><div id="ks"></div><div id="ot"></div><div id="stw" style="width:150px;height:8px;border:1px solid #7a2a2a;background:rgba(0,0,0,.55);margin-top:5px"><div id="stb" style="height:100%;width:100%;background:#d9b45a"></div></div></div>
<div id="help">WASD / ←→: di chuyển · Kéo chuột: nhìn · Shift: Shift Lock · Giữ Space: chạy · F: đèn pin · E: tương tác · P: bức tranh · A/B/C/D: chọn đáp án · Esc: đóng</div>
<button id="fs" title="Toàn màn hình">FULL</button><button id="mu" title="Bật / tắt âm thanh">🔊</button><button id="pz" title="Bức tranh bí ẩn (phím P)">🧩</button>
<button id="lockbtn" title="Shift Lock (phím Shift)">SL</button>
<div id="tui"><div id="joyB"></div><div id="joyK"></div><div id="tE" class="tb">E</div><div id="tRun" class="tb">CHẠY</div><div id="tF" class="tb">F</div></div>
<div id="prompt"></div>
<div id="banner"></div>
<div id="whisper"></div>
<div id="hide"></div>
<canvas id="scare" width="640" height="360"></canvas>
<div id="flash"></div>
<div id="bars"></div>
<div id="lids"><div class="lid lt"></div><div class="lid lb"></div></div><div id="skiph">Enter · bỏ qua</div>
<div id="fade"></div>

<div id="modal"><div id="box">
  <div id="mt"></div><div id="vd"></div><div id="mq"></div><div id="mpic"></div><div id="pbl"></div>
  <div id="opts"></div>
  <input id="mi" autocomplete="off" spellcheck="false" inputmode="numeric">
  <div id="fb"></div>
  <button id="b1">Trả lời</button><button id="b2">Gợi ý</button><button id="b3">Đóng (Esc)</button>
</div></div>

<div id="menu" class="ov" style="display:flex">
  <h1>TRƯỜNG LÚC NỬA ĐÊM</h1>
  <div class="mb">
    <button id="start">VÀO LỚP</button>
    <button id="how">CÁCH CHƠI</button>
    <button id="settingsBtn">TÙY CHỈNH</button>
  </div>
  <p id="musichint">Chạm vào màn hình để mở nhạc</p>
</div>

<div id="settings" class="ov">
  <h1 style="font-size:40px;letter-spacing:8px">CÀI ĐẶT</h1>
  <div class="hw">
    <h3>Đồ họa</h3>
    <div class="row"><button id="gLow">THẤP</button><button id="gHigh">CAO</button></div>
    <div class="row"><button id="qm" class="sq">−</button><input id="qr" type="range" min="1" max="10" step="1" value="8"><button id="qp" class="sq">+</button></div>
    <div id="ql"></div>
    <p id="qd"></p>
    <h3>Hiệu ứng</h3>
    <label class="chk" style="justify-content:flex-start"><input type="checkbox" id="rfchk2"> Giảm hiệu ứng chớp sáng (an toàn hơn cho người nhạy cảm ánh sáng)</label>
    <h3>Âm lượng nhạc</h3>
    <div class="row"><input id="vr" type="range" min="0" max="100" step="5" value="60"><span id="vv">60%</span></div>
  </div>
  <button id="sback">Trở về</button>
</div>

<div id="story" class="ov">
  <div class="sty">
    <div class="sh">ĐÊM BÃO · SÂN TRƯỜNG</div>
    <div class="cols">
      <div class="card">
        <h4>NHIỆM VỤ</h4>
        <ol>
          <li>Bạn bị nhốt lại ở sân trường giữa đêm bão.</li>
          <li>Chạy khắp các khu, tìm <b class="cl">15 MẢNH GHÉP PHÁT SÁNG</b>. Mỗi mảnh phải <b>nhìn hình đoán đúng</b> mới lấy được.</li>
          <li>Mỗi mảnh lộ ra một phần <b>bức tranh bí ẩn</b>. Đoán đúng <b>từ khóa</b> (điền vào ô trống) thì <b>cổng thoát</b> sẽ mở.</li>
        </ol>
      </div>
      <div class="card danger">
        <h4>VERITY</h4>
        <ul>
          <li>Cô giáo ma <b>VERITY</b> luôn rình rập khi bạn trả lời câu hỏi.</li>
          <li><b>Trả lời sai, cô ấy sẽ tới sớm hơn.</b></li>
          <li>Trốn trong <b>bụi cây</b> hoặc <b>gầm bàn bóng bàn</b> (<kbd>E</kbd>).</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="mb"><button id="sgo">BẮT ĐẦU</button></div>
</div>

<div id="howto" class="ov">
  <h1 style="font-size:40px;letter-spacing:8px">HƯỚNG DẪN</h1>
  <div class="hw">
    <h3>Điều khiển</h3>
    <ul>
      <li><kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> hoặc phím mũi tên: di chuyển / xoay</li>
      <li><b>Kéo chuột</b>: nhìn xung quanh</li>
      <li><kbd>Shift</kbd> hoặc nút SL góc phải dưới: bật / tắt <b>Shift Lock</b> giống Roblox — chuột bị khóa ở giữa màn hình, hiện tâm ngắm, xoay camera mà không cần bấm chuột. Lỡ nhả chuột (Esc) thì bấm vào màn hình để khóa lại</li>
      <li>Khi tắt Shift Lock: giữ chuột trái hoặc phải rồi kéo để nhìn</li>
      <li><kbd>A</kbd><kbd>B</kbd><kbd>C</kbd><kbd>D</kbd> hoặc bấm chuột: chọn đáp án khi trả lời câu hỏi</li>
      <li>Giữ <kbd>Space</kbd>: chạy. Chạy lâu sẽ <b>hết thể lực</b> (thanh vàng dưới HUD), phải đi bộ hoặc đứng nghỉ một lúc mới chạy tiếp được</li>
      <li><kbd>F</kbd>: bật / tắt <b>đèn pin</b>. Thỉnh thoảng cả sân trường sẽ <b>mất điện</b> trong ít giây, chỉ còn đèn pin và các mảnh ghép phát sáng</li>
      <li><b>Điện thoại</b> (nên xoay ngang): cần gạt bên trái màn hình để đi, vuốt bên phải để nhìn, nút <kbd>E</kbd> để tương tác, giữ nút <kbd>CHẠY</kbd> để chạy</li>
      <li><kbd>E</kbd>: tương tác (lấy mảnh ghép, mở cổng thoát, trốn vào bụi cây / gầm bàn bóng bàn)</li>
      <li><kbd>Esc</kbd>: đóng bảng câu hỏi</li>
    </ul>
    <h3>Mục tiêu</h3>
    <ul>
      <li>Sân trường có <b>5 khu</b> thông nhau, cứ đi tự do qua lại giữa các khu. Mỗi khu giấu <b>3 mảnh ghép</b> phát sáng (tổng 15). Nhìn <b>hình ảnh</b> rồi chọn đáp án <b>A/B/C/D</b> đúng để nhặt mảnh ghép.</li>
      <li>Mỗi mảnh ghép lộ ra một phần <b>bức tranh bí ẩn</b>. Bấm <kbd>P</kbd> (hoặc nút 🧩) để xem tranh, rồi <b>đoán từ khóa</b> và điền vào các <b>ô trống</b> (phải đủ chữ, khớp ô). Đoán đúng thì chạy tới <b>cổng thoát</b> ở khu cuối cùng. Đoán sai mất 1 mạng.</li>
      <li>Chọn sai đáp án sẽ mất 1 (có 3 ).</li>
    </ul>
    <h3>Verity – cô giáo ma</h3>
    <ul>
      <li>Thỉnh thoảng <b>đèn sẽ chớp liên tục</b>. Đó là dấu hiệu <b>Verity</b> sắp xuất hiện. Trả lời sai sẽ làm cô ấy <b>đến sớm hơn</b>.</li>
      <li>Hãy <b>trốn ngay</b> vào <b>bụi cây</b> hoặc <b>gầm bàn bóng bàn</b> (nhìn vào rồi bấm <kbd>E</kbd>).</li>
      <li>Khi đã trốn, đừng cử động. Verity sẽ đến lục soát rồi bỏ đi. Chỉ ra ngoài khi cô ấy đã đi hẳn.</li>
      <li>Khi Verity xuất hiện, bảng câu hỏi sẽ <b>tự đóng</b> để bạn chạy hoặc trốn. Chọn sai đáp án sẽ gọi cô ấy <b>đến sớm hơn</b>.</li>
      <li>Nếu Verity bắt được, bạn <b>chết</b> và phải <b>chơi lại từ đầu</b> (mất hết mảnh ghép).</li>
      <li>Những đôi mắt đỏ trong bóng tối sẽ biến mất khi bạn nhìn thẳng vào chúng.</li>
    </ul>
    <p style="text-align:center;color:#8a8a8a;margin-top:14px"><i>Hãy đeo tai nghe, tắt đèn và đừng quay đầu lại.</i></p>
  </div>
  <button id="hback">Trở về</button>
</div>

<div id="over" class="ov"><h1>CÔ ĐÃ TÓM ĐƯỢC EM</h1><p id="overmsg"></p>
  <div><button id="retry">Chơi lại từ đầu</button><button id="tomenu">Menu</button></div></div>
<div id="win" class="ov"><h1 style="color:#d9b45a">RA KHỎI TRƯỜNG RỒI!</h1><p>Bạn đã trốn khỏi trường... nhưng Verity vẫn đang đứng nhìn bạn từ cửa sổ tầng hai.</p>
  <div><button id="again">Chơi lại</button><button id="tomenu2">Menu</button></div></div>

</div></div>
<div id="rot">XOAY NGANG ĐIỆN THOẠI ĐỂ CHƠI</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
const DOORS_BASE = __DATA__, EXTRA_Q = __POOL__, FIXED_Q = __FIXED__, BONUS_Q = __BONUS__, PUZZLES = __PUZ__;
const QPOOL = [].concat.apply([], DOORS_BASE.map(d=>d.questions)).concat(EXTRA_Q);
let DOORS = DOORS_BASE;
let layoutOrder=[0,1,2,3,4], wallOrder=[0,1,2,3,4], mirrorArr=[1,-1,1,-1,1], gameSeed=17;
// Mỗi ván: xáo thứ tự kiểu phòng, màu tường, hướng đối xứng, và bốc ngẫu nhiên câu hỏi + chữ số + thứ tự ghép chìa cho từng phòng
function rollGame(){
  puz=PUZZLES[Math.floor(Math.random()*PUZZLES.length)]; tileOrder=shuffle([...Array(15).keys()]); keySolved=false; buildPuzImg();
  layoutOrder=shuffle([0,1,2,3,4]); wallOrder=shuffle([0,1,2,3,4]); mirrorArr=[0,1,2,3,4].map(()=>Math.random()<.5?1:-1); gameSeed=Math.floor(Math.random()*1e6);
  const pool=shuffle(QPOOL.map((_,i)=>i)); let p=0;
  const fixed=shuffle(FIXED_Q.slice());   // 5 câu bắt buộc: mỗi phòng 1 câu, phòng nhận câu nào là ngẫu nhiên
  const bonus=shuffle(BONUS_Q.slice());   // 10 câu bổ sung: mỗi phòng 2 câu
  DOORS=[0,1,2,3,4].map(i=>{
    const base=DOORS_BASE[layoutOrder[i]];
    const picks=[];                                                   // mỗi phòng 3 câu: 1 câu bắt buộc + 2 câu bổ sung (thiếu mới bốc ngẫu nhiên)
    if(fixed.length) picks.push(fixed.pop());
    while(picks.length<3) picks.push(bonus.length?bonus.pop():QPOOL[pool[p++%pool.length]]);
    const questions=shuffle(picks).map(q=>({q:q.q,o:q.o,hint:q.hint,p:q.p,digit:Math.floor(Math.random()*10)}));   // xáo vị trí chìa 1/2/3
    const order=shuffle([0,1,2]);
    return {name:base.name,intro:base.intro,order,order_text:'Ghép chìa '+order.map(k=>k+1).join(' → chìa ')+'.',questions};
  });
}
const MUSIC_SRC = "__MUSIC__";
const PLAY_SRC = "__MUSIC2__";
const MAX_HP=3, HINTS0=5, RH=4;
const SIZES=[[34,50],[38,54],[40,56],[36,52],[38,54]];
let RW=18, RD=26;
const $=id=>document.getElementById(id);
const SRC='<!DOCTYPE html>\n'+document.documentElement.outerHTML;   // bản sao trang để mở ở tab mới
function loadNum(k,d,lo,hi){try{const v=parseInt(localStorage.getItem(k));return(v>=lo&&v<=hi)?v:d;}catch(e){return d;}}
function saveNum(k,v){try{localStorage.setItem(k,v);}catch(e){}}
// Nút tắt/bật âm thanh: mọi nút phát ra loa đều được dẫn qua 1 gain tổng (master) để tắt tiếng một lần là im hết
let MUTED=loadNum('doors_mute',0,0,1)===1;
const _mc=AudioNode.prototype.connect, masters=new WeakMap();
function masterOf(ctx){let m=masters.get(ctx); if(!m){m=ctx.createGain(); m.gain.value=MUTED?0:1; _mc.call(m,ctx.destination); masters.set(ctx,m);} return m;}
AudioNode.prototype.connect=function(d,...r){
  try{ if(typeof AudioDestinationNode!=='undefined'&&d instanceof AudioDestinationNode) d=masterOf(d.context); }catch(e){}
  return _mc.call(this,d,...r);
};
const COARSE=!!(window.matchMedia&&matchMedia('(pointer:coarse)').matches);   // điện thoại / máy tính bảng
let Q=loadNum('verity_q',COARSE?4:6,1,10), HQ=Q>=6;       // mức đồ họa 1-10 (<=5: Thấp, >=6: Cao)
let STW=1280, STH=720, mouseX=0, mouseY=0, mouseIn=false, optOrder=[], wrongSet={}, lockFailShown=false, lockBlocked=false, lockEver=false, lockMsgT=0, touchMode=COARSE;
// Cao: độ phân giải gần đầy đủ. Thấp: render độ phân giải rất nhỏ rồi phóng to kiểu pixel (low-poly retro)
const pr=()=>HQ?Math.max(.8,Math.min(window.devicePixelRatio||1,.4+Q*.12)):(0.28+Q*0.05);
let RF=loadNum('doors_rf',0,0,1)===1;   // giảm hiệu ứng chớp sáng
let puz=null, tileOrder=[], keySolved=false, puzImg=null;
let hp=MAX_HP, hints=HINTS0, door=0, solved=[false,false,false], hintShown={};
let state='menu', modalOpen=false, modalMode='q', modalIdx=0, hidden=false, doorOpen=false, transitioning=false;
let yaw=0, pitch=0, dragging=false, shake=0, bob=0, bannerT=null, cur=null, curSpot=null, spots=[];
let stam=100, tired=false, flashOn=true, blackT=0, blackD=1, nextBlack=40+Math.random()*30;   // đèn pin + mất điện
let keys={}, tt=0, stepT=0, hbT=0, evT=14, flickT=0, nextFlick=12, lampF=1, dark=0;
let shiftLock=false, expectUnlock=false, scareT=0, scareYaw=0, ghostTimer=40, scareFlashT=0;
let doorGlow=null; const GAP=.2, rooms=[];   // rooms[i]: phòng KỀ BÊN đã dựng (không phải phòng hiện tại), dùng để nhìn xuyên cửa và đi qua lại
let shapeBlocks=[], room=null, doorPivot=null, obstacles=[], inter=[], watchers=[], flameMat=null, fireMat=null;
const gh={phase:'idle',t:0,t0:1,x:0,z:0,alpha:0,peek:0,face:0,step:0,ux:0,uz:1};

// ---------- Renderer / Scene ----------
const renderer=new THREE.WebGLRenderer({antialias:(window.devicePixelRatio||1)<1.5,powerPreference:'high-performance'});
renderer.setPixelRatio(pr());
renderer.setSize(1280,720);
renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.0;
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFShadowMap;
$('c').appendChild(renderer.domElement);
const canvas=renderer.domElement;
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x070b14);
{ const c=document.createElement('canvas'); c.width=512; c.height=256; const g=c.getContext('2d');      // vòm trời đêm có sao + trăng
  const gr=g.createLinearGradient(0,0,0,256); gr.addColorStop(0,'#05070f'); gr.addColorStop(1,'#1b2538'); g.fillStyle=gr; g.fillRect(0,0,512,256);
  for(let i=0;i<260;i++){g.fillStyle='rgba(255,255,255,'+(Math.random()*.7+.2)+')'; g.fillRect(Math.random()*512,Math.random()*150,Math.random()<.1?2:1,1);}
  g.fillStyle='#e8ecf4'; g.beginPath(); g.arc(380,60,16,0,7); g.fill();
  const sky=new THREE.Mesh(new THREE.SphereGeometry(60,24,12),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(c),side:THREE.BackSide,fog:false,depthWrite:false}));
  sky.renderOrder=-1; scene.add(sky); }
scene.fog=new THREE.FogExp2(0x050912,0.045);
const camera=new THREE.PerspectiveCamera(72,16/9,0.1,110);
camera.rotation.order='YXZ';
scene.add(camera);
// Khung 16:9 luôn nằm gọn trong màn hình (letterbox), giao diện scale theo khung
const stage=$('stage'), ui=$('ui');
function fit(){
  const W=innerWidth,H=innerHeight; let w=W,h=Math.round(W*9/16);
  if(h>H){h=H;w=Math.round(H*16/9);}
  STW=w;STH=h; stage.style.width=w+'px'; stage.style.height=h+'px';
  ui.style.transform='scale('+(w/1280)+')';
  renderer.setSize(w,h); camera.aspect=16/9; camera.updateProjectionMatrix();
  $('rot').style.display=(touchMode&&H>W)?'flex':'none';
}
fit();

// Đèn pin
const spot=new THREE.SpotLight(0xfff0cc,2.1,24,Math.PI/5.2,0.5,1.1);
spot.position.set(0.2,-0.1,0);   // đèn pin gắn vào camera
 camera.add(spot); camera.add(spot.target); spot.target.position.set(0,0,-3);
spot.shadow.mapSize.set(1024,1024); spot.shadow.camera.near=0.2; spot.shadow.camera.far=16; spot.shadow.bias=-0.0006;
const ambL=new THREE.AmbientLight(0x2a3858,0.3); scene.add(ambL);   // ánh trăng xanh lạnh ban đêm
const moonL=new THREE.DirectionalLight(0x6f84b8,0.1); moonL.position.set(-8,20,6); scene.add(moonL);
// Các đèn cố định (tạo một lần để tránh biên dịch lại shader)
const lamp=new THREE.PointLight(0xe4eeff,1.1,30); scene.add(lamp);
lamp.shadow.mapSize.set(512,512); lamp.shadow.camera.near=0.3; lamp.shadow.camera.far=24; lamp.shadow.bias=-0.003;
const lampB=new THREE.PointLight(0xe4eeff,0.9,28); scene.add(lampB);
const doorLight=new THREE.PointLight(0xfff1c9,0,10); scene.add(doorLight);
const nextL=new THREE.PointLight(0xffd9a0,0,40), prevL=new THREE.PointLight(0xffc890,0,36); scene.add(nextL); scene.add(prevL);   // chiếu sáng phòng kề bên để nhìn xuyên ô cửa
const sconceL=[0,1].map((_,i)=>{const l=new THREE.PointLight(0xff9a40,1.0,9);if(i===0)scene.add(l);return l;});   // chỉ giữ 1 đèn phụ trong scene
const clueL=[0,1,2].map(()=>{const l=new THREE.PointLight(0xffaa44,.9,5.5);scene.add(l);return l;});

// Bụi bay
const DUST=320, dustPos=new Float32Array(DUST*3);
const dustGeo=new THREE.BufferGeometry(); dustGeo.setAttribute('position',new THREE.BufferAttribute(dustPos,3));
const dust=new THREE.Points(dustGeo,new THREE.PointsMaterial({color:0xffddaa,size:0.035,transparent:true,opacity:.45,depthWrite:false}));
dust.frustumCulled=false; scene.add(dust);
function resetDust(){for(let i=0;i<DUST;i++){dustPos[i*3]=(Math.random()-.5)*RW;dustPos[i*3+1]=Math.random()*RH;dustPos[i*3+2]=(Math.random()-.5)*RD;}
  dustGeo.attributes.position.needsUpdate=true;}

// ---------- Texture thủ tục ----------
const CAN={};
function T(key,w,h,draw,rx,ry){
  if(!CAN[key]){const c=document.createElement('canvas');c.width=w;c.height=h;draw(c.getContext('2d'),w,h);CAN[key]=c;}
  const t=new THREE.CanvasTexture(CAN[key]); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.repeat.set(rx||1,ry||1); t.anisotropy=4;
  if(!HQ){t.magFilter=THREE.NearestFilter;t.minFilter=THREE.NearestMipmapNearestFilter;t.anisotropy=1;}   // texture vuông pixel
  return t;
}
const rnd=(a,b)=>a+Math.random()*(b-a);
function mulberry(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function noiseFx(g,w,h,a){const id=g.getImageData(0,0,w,h),d=id.data;for(let i=0;i<d.length;i+=4){const n=(Math.random()-.5)*a;d[i]+=n;d[i+1]+=n;d[i+2]+=n;}g.putImageData(id,0,0);}
function stains(g,w,h,n,a){for(let i=0;i<n;i++){const x=rnd(0,w),y=rnd(0,h),r=rnd(6,46),gr=g.createRadialGradient(x,y,0,x,y,r);
  gr.addColorStop(0,'rgba(0,0,0,'+a+')');gr.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=gr;g.fillRect(x-r,y-r,r*2,r*2);}}
const WALLC=['#aaa68c','#82a090','#8f9ca8','#b3a68c','#8d918a'];   // tường sơn kem / xanh bạc hà / xanh nhạt / be / xám
const wallTex=(i,rx,ry)=>T('wall'+i,256,256,(g,w,h)=>{
  g.fillStyle=WALLC[i];g.fillRect(0,0,w,h);
  g.fillStyle='rgba(255,255,255,.05)';for(let x=0;x<w;x+=64)g.fillRect(x,0,2,h);
  stains(g,w,h,26,.14);noiseFx(g,w,h,18);},rx,ry);
const carpetTex=(rx,ry)=>T('carpet',256,256,(g,w,h)=>{      // sân bê tông: khe nối tấm, vết nứt, rêu
  g.fillStyle='#74776f';g.fillRect(0,0,w,h);
  g.strokeStyle='rgba(0,0,0,.45)';g.lineWidth=3;g.strokeRect(0,0,w,h);
  g.lineWidth=1;for(let i=0;i<7;i++){g.beginPath();let x=rnd(0,w),y=rnd(0,h);g.moveTo(x,y);for(let k=0;k<5;k++){x+=rnd(-30,30);y+=rnd(-30,30);g.lineTo(x,y);}g.stroke();}
  for(let i=0;i<18;i++){g.fillStyle='rgba(60,110,50,'+rnd(.1,.3)+')';g.beginPath();g.arc(rnd(0,w),rnd(0,h),rnd(3,12),0,7);g.fill();}
  stains(g,w,h,22,.25);noiseFx(g,w,h,30);},rx,ry);
const grassTex=(rx,ry)=>T('grass',256,256,(g,w,h)=>{          // bãi cỏ
  g.fillStyle='#2c4527';g.fillRect(0,0,w,h);
  for(let i=0;i<900;i++){g.strokeStyle='hsl('+Math.floor(rnd(85,125))+','+Math.floor(rnd(30,50))+'%,'+Math.floor(rnd(14,30))+'%)';const x=rnd(0,w),y=rnd(0,h);g.beginPath();g.moveTo(x,y);g.lineTo(x+rnd(-3,3),y-rnd(3,9));g.stroke();}
  for(let i=0;i<8;i++){g.fillStyle='rgba(70,50,30,'+rnd(.15,.35)+')';g.beginPath();g.ellipse(rnd(0,w),rnd(0,h),rnd(8,20),rnd(5,12),0,0,7);g.fill();}
  noiseFx(g,w,h,22);},rx,ry);
const leafTex=()=>T('leaf',128,128,(g,w,h)=>{                 // tán lá / bụi cây
  g.fillStyle='#1d3d22';g.fillRect(0,0,w,h);
  for(let i=0;i<160;i++){g.fillStyle='hsl('+Math.floor(rnd(95,135))+','+Math.floor(rnd(35,55))+'%,'+Math.floor(rnd(12,30))+'%)';g.beginPath();g.ellipse(rnd(0,w),rnd(0,h),rnd(3,9),rnd(2,5),rnd(0,3),0,7);g.fill();}
  noiseFx(g,w,h,18);});

// ---------- Texture sân trường ban đêm: dãy nhà lớp học, hàng rào, hàng cây, sân bóng ----------
const FACC=['#cfc08a','#b9cdb0','#bcc8d2','#d2bf9c','#bdbfb2'];   // tường vàng kem / xanh bạc hà / xanh nhạt / be / xám
const LOPS=['6A1','6A2','7A1','7A3','8A2','8A4','9A1','9A3','6A5','7A5'];
const facadeTex=(i,rx,ry)=>T('facade'+i,1024,512,(g,w,h)=>{          // tầng trệt: 8m x 4m = 1 phòng học (cửa ra vào + 2 cửa sổ)
  const R2=mulberry(i*131+7);
  g.fillStyle=FACC[i];g.fillRect(0,0,w,h);
  for(let k=0;k<26;k++){g.fillStyle='rgba(0,0,0,'+(.03+R2()*.07)+')';g.fillRect(R2()*w,0,2+R2()*6,h);}   // vệt nước mưa chảy dọc
  g.fillStyle='rgba(30,40,30,.55)';g.fillRect(0,h-34,w,34);                                          // chân tường
  g.fillStyle='rgba(255,255,255,.1)';g.fillRect(0,0,w,14);g.fillStyle='rgba(0,0,0,.25)';g.fillRect(0,14,w,6);
  [[400,625],[695,920]].forEach((wd,wi2)=>{                                                          // cửa sổ lớp: kính đen, thấy mờ bàn ghế + bảng
    const x1=wd[0],x2=wd[1],y1=196,y2=388;
    g.fillStyle='#26403a';g.fillRect(x1-12,y1-12,x2-x1+24,y2-y1+24);
    const lit=R2()<.12;
    const gr=g.createLinearGradient(0,y1,0,y2);
    if(lit){gr.addColorStop(0,'#8a7440');gr.addColorStop(1,'#4d4124');}else{gr.addColorStop(0,'#101a22');gr.addColorStop(1,'#04080b');}
    g.fillStyle=gr;g.fillRect(x1,y1,x2-x1,y2-y1);
    g.fillStyle=lit?'rgba(40,30,10,.5)':'rgba(40,58,70,.5)';g.fillRect(x1+16,y1+16,x2-x1-32,30);   // bảng đen phía trong
    for(let r=0;r<3;r++)for(let c=0;c<4;c++){g.fillStyle=lit?'rgba(30,22,8,.55)':'rgba(24,34,42,.8)';g.fillRect(x1+14+c*57,y1+84+r*32,40,16);}   // dãy bàn học
    g.fillStyle='rgba(190,210,230,.07)';g.beginPath();g.moveTo(x1,y2);g.lineTo(x1+70,y1);g.lineTo(x1+120,y1);g.lineTo(x1+50,y2);g.fill();   // vệt phản chiếu
    g.fillStyle='#26403a';g.fillRect((x1+x2)/2-4,y1,8,y2-y1);g.fillRect(x1,y1+62,x2-x1,7);           // khung + song cửa
    g.strokeStyle='rgba(20,30,30,.9)';g.lineWidth=3;for(let b=x1+30;b<x2;b+=30){g.beginPath();g.moveTo(b,y1);g.lineTo(b,y2);g.stroke();}   // song sắt
    g.fillStyle='rgba(0,0,0,.35)';g.fillRect(x1-18,y2+12,x2-x1+36,10);});                           // bệ cửa sổ
  g.fillStyle='#1e3a30';g.fillRect(150,168,170,h-168-34);                                             // cửa ra vào lớp
  g.fillStyle='#2f5a48';g.fillRect(162,182,146,h-168-34-26);
  g.fillStyle='#071014';g.fillRect(204,210,62,70);g.fillStyle='rgba(0,0,0,.35)';g.fillRect(234,300,4,150);
  g.fillStyle='#caa24a';g.beginPath();g.arc(290,330,6,0,7);g.fill();
  g.fillStyle='#e8efe8';g.fillRect(192,120,86,34);g.strokeStyle='#244';g.lineWidth=3;g.strokeRect(192,120,86,34);   // biển số lớp
  g.fillStyle='#143a2c';g.font='bold 26px sans-serif';g.textAlign='center';g.fillText(LOPS[Math.floor(R2()*LOPS.length)],235,146);
  stains(g,w,h,30,.2);noiseFx(g,w,h,16);},rx,ry);
const upperTex=(i,rx,ry)=>T('upper'+i,1024,512,(g,w,h)=>{            // tầng 2: hành lang có lan can, cột, cửa lớp trong bóng tối, mái ngói
  const R2=mulberry(i*977+3);
  g.fillStyle=FACC[i];g.fillRect(0,0,w,h);
  for(let k=0;k<22;k++){g.fillStyle='rgba(0,0,0,'+(.03+R2()*.07)+')';g.fillRect(R2()*w,0,2+R2()*6,h);}
  g.fillStyle='#4a2822';g.fillRect(0,0,w,46);g.fillStyle='#5f3329';for(let x=0;x<w;x+=34)g.fillRect(x,0,28,38);   // mái ngói
  g.fillStyle='rgba(0,0,0,.4)';g.fillRect(0,46,w,22);
  g.fillStyle='#070b0e';g.fillRect(0,68,w,252);                                                      // hành lang tối phía sau lan can
  [[110,290],[400,560],[690,860]].forEach(wd=>{const lit=R2()<.1;g.fillStyle=lit?'#6a5a30':'#0d1820';g.fillRect(wd[0],110,wd[1]-wd[0],176);
    g.strokeStyle='#26403a';g.lineWidth=7;g.strokeRect(wd[0],110,wd[1]-wd[0],176);g.fillRect((wd[0]+wd[1])/2-3,110,6,176);});
  g.fillStyle='#d2cbb2';g.fillRect(0,320,w,22);g.fillStyle='#8f8a78';g.fillRect(0,342,w,10);               // tay vịn lan can
  for(let x=10;x<w;x+=26){g.fillStyle='#bcb69e';g.fillRect(x,350,9,106);}                                // con tiện lan can
  g.fillStyle='#a49e88';g.fillRect(0,448,w,64);g.fillStyle='rgba(0,0,0,.3)';g.fillRect(0,448,w,8);      // sàn bê tông nhô ra
  [0,512].forEach(cx=>{g.fillStyle=FACC[i];g.fillRect(cx-22,46,44,402);g.fillStyle='rgba(0,0,0,.25)';g.fillRect(cx+14,46,8,402);});   // cột hành lang
  stains(g,w,h,26,.22);noiseFx(g,w,h,16);},rx,ry);
const fenceTex=(rx,ry)=>T('fence',256,256,(g,w,h)=>{                  // hàng rào lưới B40 (nền trong suốt)
  g.clearRect(0,0,w,h);g.strokeStyle='rgba(150,158,165,.85)';g.lineWidth=2;
  for(let k=-h;k<w+h;k+=18){g.beginPath();g.moveTo(k,0);g.lineTo(k+h,h);g.stroke();g.beginPath();g.moveTo(k+h,0);g.lineTo(k,h);g.stroke();}
  g.fillStyle='#3a4047';g.fillRect(0,0,w,10);g.fillRect(0,h-6,w,6);g.fillRect(0,0,10,h);},rx,ry);
const treeLineTex=(i,rx,ry)=>T('treeline'+i,1024,512,(g,w,h)=>{       // hàng cây đen sau hàng rào (nền trong suốt, thấy trời đêm phía trên)
  g.clearRect(0,0,w,h);const R2=mulberry(i*53+11);
  const blob=(cx,cy,rx2,ry2,c)=>{[-w,0,w].forEach(o=>{g.fillStyle=c;g.beginPath();g.ellipse(cx+o,cy,rx2,ry2,0,0,7);g.fill();});};
  for(let k=0;k<22;k++){const x=k*(w/22)+R2()*30,top=70+R2()*160;g.fillStyle='#0a0f0a';g.fillRect(x-5,top+60,10,h-top-60);}   // thân cây
  for(let k=0;k<70;k++){blob(R2()*w,120+R2()*300,34+R2()*54,28+R2()*46,'rgb('+Math.floor(6+R2()*8)+','+Math.floor(16+R2()*16)+','+Math.floor(10+R2()*10)+')');}
  g.fillStyle='#07100a';g.fillRect(0,h-150,w,150);                                                     // bụi rậm sát đất
  for(let k=0;k<40;k++)blob(R2()*w,h-150+R2()*60,40+R2()*30,34+R2()*26,'#0a1a0e');},rx,ry);
const pitchTex=()=>T('pitch',1024,796,(g,w,h)=>{                      // vạch sân bóng 18m x 14m (nền trong suốt)
  g.clearRect(0,0,w,h);const u=w/18,m=6;
  g.strokeStyle='rgba(235,240,235,.8)';g.fillStyle='rgba(235,240,235,.8)';g.lineWidth=m;
  g.strokeRect(m,m,w-2*m,h-2*m);g.beginPath();g.moveTo(w/2,m);g.lineTo(w/2,h-m);g.stroke();
  g.beginPath();g.arc(w/2,h/2,u*2.2,0,7);g.stroke();g.beginPath();g.arc(w/2,h/2,7,0,7);g.fill();
  [0,1].forEach(s=>{const x0=s?w-m:m,d=s?-1:1;
    g.strokeRect(s?w-m-u*3.5:m,h/2-u*4,u*3.5,u*8);g.strokeRect(s?w-m-u*1.6:m,h/2-u*2,u*1.6,u*4);
    g.beginPath();g.arc(x0+d*u*2.4,h/2,5,0,7);g.fill();
    g.beginPath();g.arc(x0+d*u*2.4,h/2,u*2.2,s?Math.PI-.9:-.9,s?Math.PI+.9:.9);g.stroke();});});
const stripeTex=(rx,ry)=>T('stripe',256,256,(g,w,h)=>{                // cỏ sân bóng cắt sọc
  g.fillStyle='#27441f';g.fillRect(0,0,w,h);g.fillStyle='#2f5326';g.fillRect(0,0,w,h/2);
  for(let i=0;i<1100;i++){g.strokeStyle='hsl('+Math.floor(rnd(88,120))+','+Math.floor(rnd(30,48))+'%,'+Math.floor(rnd(14,28))+'%)';const x=rnd(0,w),y=rnd(0,h);g.beginPath();g.moveTo(x,y);g.lineTo(x+rnd(-3,3),y-rnd(3,8));g.stroke();}
  noiseFx(g,w,h,22);},rx,ry);
const flagTex=()=>T('flag',128,86,(g,w,h)=>{                  // cờ đỏ sao vàng
  g.fillStyle='#c0141a';g.fillRect(0,0,w,h);g.fillStyle='#ffd21a';g.beginPath();
  for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5,r=i%2?9:22;g.lineTo(w/2+Math.cos(a)*r,h/2+Math.sin(a)*r);}g.closePath();g.fill();noiseFx(g,w,h,14);});
const woodTex=(rx,ry)=>T('wood',128,128,(g,w,h)=>{
  g.fillStyle='#9a7a52';g.fillRect(0,0,w,h);
  for(let x=0;x<w;x+=16){g.fillStyle='rgba(0,0,0,.35)';g.fillRect(x,0,2,h);}
  for(let i=0;i<60;i++){g.strokeStyle='rgba(0,0,0,'+rnd(.05,.2)+')';g.beginPath();const x=rnd(0,w);g.moveTo(x,0);g.bezierCurveTo(x+6,h/3,x-6,h*2/3,x+rnd(-3,3),h);g.stroke();}
  noiseFx(g,w,h,26);},rx,ry);
const ceilTex=(rx,ry)=>T('ceil',256,256,(g,w,h)=>{g.fillStyle='#b9b6a6';g.fillRect(0,0,w,h);g.strokeStyle='rgba(0,0,0,.35)';g.lineWidth=3;g.strokeRect(0,0,w/2,h/2);g.strokeRect(w/2,h/2,w/2,h/2);g.strokeRect(w/2,0,w/2,h/2);g.strokeRect(0,h/2,w/2,h/2);stains(g,w,h,24,.32);noiseFx(g,w,h,20);},rx,ry);
const doorTex=()=>T('door',256,512,(g,w,h)=>{                 // cổng sắt
  g.fillStyle='#0f1113';g.fillRect(0,0,w,h);g.fillStyle='#3a4047';
  for(let x=10;x<w;x+=24)g.fillRect(x,0,9,h);
  g.fillRect(0,36,w,14);g.fillRect(0,h/2-6,w,12);g.fillRect(0,h-90,w,14);
  g.fillStyle='#555d66';for(let x=10;x<w;x+=24){g.beginPath();g.moveTo(x-2,0);g.lineTo(x+4.5,-16);g.lineTo(x+11,0);g.fill();}
  stains(g,w,h,10,.25);noiseFx(g,w,h,24);});
const bookTex=()=>T('books',256,128,(g,w,h)=>{
  g.fillStyle='#1b110a';g.fillRect(0,0,w,h);
  for(let r=0;r<4;r++){let x=4;const y=r*32;while(x<w-8){const bw=rnd(6,14),bh=rnd(18,28);
    g.fillStyle='hsl('+Math.floor(rnd(0,40))+','+Math.floor(rnd(20,50))+'%,'+Math.floor(rnd(14,30))+'%)';g.fillRect(x,y+30-bh,bw,bh);x+=bw+1;}
    g.fillStyle='#000';g.fillRect(0,y+30,w,3);}
  noiseFx(g,w,h,22);});
const boardTex=()=>T('board',512,200,(g,w,h)=>{   // bảng đen + chữ phấn
  g.fillStyle='#1f3b30';g.fillRect(0,0,w,h);g.fillStyle='rgba(255,255,255,.07)';for(let i=0;i<46;i++)g.fillRect(rnd(0,w),rnd(0,h),rnd(20,90),2);
  g.fillStyle='rgba(236,236,224,.88)';g.font='34px "Segoe Print","Comic Sans MS",cursive';g.textAlign='left';
  g.fillText('Bài hôm nay: TRẢ LỜI!',22,56);g.fillText('x² − 5x + 6 = 0',22,112);
  g.fillStyle='rgba(190,40,40,.92)';g.fillText('Em ở đâu?',250,172);noiseFx(g,w,h,10);});
const paintTex=v=>T('paint'+v,256,320,(g,w,h)=>{      // áp phích treo tường: bảng tuần hoàn / bản đồ / định lý / nội quy
  const k=v%4; g.fillStyle=['#e8e1c6','#b6d2df','#2c4a3c','#d9caa6'][k]; g.fillRect(0,0,w,h);
  g.textAlign='center'; g.fillStyle=k===2?'rgba(240,240,230,.92)':'rgba(30,25,20,.8)'; g.font='bold 21px serif';
  g.fillText(['BẢNG TUẦN HOÀN','BẢN ĐỒ VIỆT NAM','ĐỊNH LÝ PY-TA-GO','NỘI QUY LỚP HỌC'][k],w/2,38);
  if(k===0){for(let r=0;r<6;r++)for(let c=0;c<7;c++){g.fillStyle='hsl('+((r*7+c)*17%360)+',45%,62%)';g.fillRect(24+c*30,64+r*36,27,32);}}
  else if(k===1){g.fillStyle='#4f89ad';g.fillRect(16,56,w-32,h-80);g.fillStyle='#6fa05a';g.beginPath();g.ellipse(120,160,22,92,.2,0,7);g.fill();g.beginPath();g.ellipse(150,250,30,22,0,0,7);g.fill();}
  else if(k===2){g.font='bold 34px serif';g.fillText('a² + b² = c²',w/2,130);g.strokeStyle='rgba(240,240,230,.9)';g.lineWidth=3;g.beginPath();g.moveTo(60,260);g.lineTo(60,170);g.lineTo(190,260);g.closePath();g.stroke();}
  else{g.strokeStyle='rgba(30,25,20,.55)';g.lineWidth=2;for(let y=70;y<h-30;y+=26){g.beginPath();g.moveTo(26,y);g.lineTo(w-26-(y%3)*14,y);g.stroke();}
    g.fillStyle='rgba(150,15,15,.85)';g.font='bold 22px serif';g.fillText('KHÔNG ĐƯỢC TRỐN',w/2,h-26);}
  stains(g,w,h,12,.28);noiseFx(g,w,h,20);});
const paperTex=()=>T('paper',128,180,(g,w,h)=>{
  g.fillStyle='#d9ceae';g.fillRect(0,0,w,h);
  g.strokeStyle='rgba(60,40,20,.55)';g.lineWidth=2;
  for(let y=26;y<h-12;y+=14){g.beginPath();g.moveTo(14,y);g.lineTo(w-14-(y%3)*10,y+((y*7)%5)-2);g.stroke();}
  g.fillStyle='rgba(120,10,10,.8)';g.font='bold 22px serif';g.fillText('?',w/2-6,22);
  stains(g,w,h,8,.25);noiseFx(g,w,h,22);});
const bloodTex=()=>T('blood',128,128,(g,w,h)=>{
  for(let i=0;i<26;i++){const x=64+rnd(-40,40),y=64+rnd(-40,40),r=rnd(2,16),gr=g.createRadialGradient(x,y,0,x,y,r);
    gr.addColorStop(0,'rgba(110,5,5,.95)');gr.addColorStop(1,'rgba(90,0,0,0)');g.fillStyle=gr;g.beginPath();g.arc(x,y,r,0,7);g.fill();}});
const handTex=()=>T('hand',128,128,(g,w,h)=>{
  g.fillStyle='rgba(115,8,8,.92)';g.strokeStyle='rgba(115,8,8,.92)';g.lineCap='round';
  g.beginPath();g.ellipse(64,88,28,32,0,0,7);g.fill();g.lineWidth=11;
  for(let i=0;i<5;i++){const a=-2.45+i*.37;g.beginPath();g.moveTo(64+Math.cos(a)*16,88+Math.sin(a)*16);g.lineTo(64+Math.cos(a)*(i==2?58:52),88+Math.sin(a)*(i==2?58:52));g.stroke();}
  g.lineWidth=3;for(let i=0;i<5;i++){const x=rnd(40,88);g.beginPath();g.moveTo(x,110);g.lineTo(x,110+rnd(6,18));g.stroke();}});
const MSG=['EM CHƯA NỘP BÀI','TRẢ LỜI ĐI','CÔ GỌI TÊN EM','ĐỪNG CHẠY','EM TRƯỢT RỒI'];
const msgTex=t=>T('msg'+t,512,128,(g,w,h)=>{
  g.font='bold 50px serif';g.textAlign='center';g.fillStyle='#7d0a0a';g.shadowColor='#400';g.shadowBlur=8;g.fillText(t,w/2,66);
  g.shadowBlur=0;for(let i=0;i<22;i++){g.fillRect(rnd(60,w-60),68,rnd(2,4),rnd(8,46));}});
const rugTex=()=>T('rug',256,512,(g,w,h)=>{
  g.fillStyle='#3b0c10';g.fillRect(0,0,w,h);
  g.strokeStyle='#b8893a';g.lineWidth=6;g.strokeRect(10,10,w-20,h-20);g.lineWidth=2;g.strokeRect(24,24,w-48,h-48);
  g.fillStyle='rgba(184,137,58,.35)';
  for(let i=0;i<5;i++){const cy=90+i*85;g.beginPath();g.moveTo(w/2,cy-34);g.lineTo(w/2+44,cy);g.lineTo(w/2,cy+34);g.lineTo(w/2-44,cy);g.closePath();g.fill();}
  stains(g,w,h,18,.3);noiseFx(g,w,h,30);});
const clockTex=()=>T('clock',128,128,(g,w,h)=>{
  g.fillStyle='#c9b98c';g.beginPath();g.arc(64,64,60,0,7);g.fill();g.strokeStyle='#2a1a08';g.lineWidth=4;g.stroke();
  g.lineWidth=3;for(let i=0;i<12;i++){const a=i/12*6.283;g.beginPath();g.moveTo(64+Math.sin(a)*48,64-Math.cos(a)*48);g.lineTo(64+Math.sin(a)*56,64-Math.cos(a)*56);g.stroke();}
  g.lineWidth=5;g.beginPath();g.moveTo(64,64);g.lineTo(64+Math.sin(.4)*30,64-Math.cos(.4)*30);g.stroke();
  g.lineWidth=3;g.beginPath();g.moveTo(64,64);g.lineTo(64+Math.sin(4.1)*44,64-Math.cos(4.1)*44);g.stroke();noiseFx(g,w,h,18);});
const webTex=()=>T('web',128,128,(g,w,h)=>{
  g.clearRect(0,0,w,h);g.strokeStyle='rgba(220,220,220,.55)';g.lineWidth=1;
  for(let i=0;i<=6;i++){const a=i/6*Math.PI/2;g.beginPath();g.moveTo(0,0);g.lineTo(Math.cos(a)*128,Math.sin(a)*128);g.stroke();}
  for(let r=18;r<130;r+=18){g.beginPath();for(let i=0;i<=6;i++){const a=i/6*Math.PI/2,rr=r*(0.9+Math.random()*.2),x=Math.cos(a)*rr,y=Math.sin(a)*rr;if(i)g.lineTo(x,y);else g.moveTo(x,y);}g.stroke();}});
// Mặt cười kinh dị: vàng úa bẩn, hốc mắt đen sâu, miệng toác quá rộng đầy răng lởm chởm. s = tỉ lệ (1 ≈ rộng 270px)
function drawSmiley(g,cx,cy,s){
  [-1,1].forEach((sg,k)=>{ g.save(); g.translate(cx+sg*58*s,cy-42*s); g.rotate(sg*.25);
    const sh=g.createRadialGradient(0,0,6*s,0,0,62*s); sh.addColorStop(0,'rgba(12,8,0,.9)'); sh.addColorStop(1,'rgba(12,8,0,0)');
    g.fillStyle=sh; g.beginPath(); g.ellipse(0,0,62*s,76*s,0,0,7); g.fill();            // quầng thâm quanh mắt
    g.fillStyle='#030202'; g.beginPath(); g.ellipse(0,0,(k?21:16)*s,(k?42:34)*s,0,0,7); g.fill();
    g.shadowColor='#ff0000'; g.shadowBlur=18*s; g.fillStyle='#ff1a12'; g.beginPath(); g.arc(1*s,-2*s,(k?9:7)*s,0,7); g.fill(); g.fillStyle='#ff8a70'; g.beginPath(); g.arc(1*s,-3*s,2.6*s,0,7); g.fill(); g.restore(); });   // mắt đỏ phát sáng
  const x0=cx-135*s, x1=cx+135*s, y0=cy+22*s;
  const mouth=()=>{ g.beginPath(); g.moveTo(x0,y0); g.quadraticCurveTo(cx,cy+200*s,x1,y0); g.quadraticCurveTo(cx,cy+62*s,x0,y0); g.closePath(); };
  mouth(); g.fillStyle='#090102'; g.fill();
  g.save(); mouth(); g.clip();
  const R2=mulberry(77);
  for(let i=-8;i<=8;i++){ const dx=i*16*s, u=Math.max(0,1-Math.pow(i*16/135,2)), x=cx+dx;
    const topY=y0+20*s*u, botY=y0+89*s*u, h1=(22+R2()*34)*s, h2=(18+R2()*30)*s;
    g.fillStyle='#bdb59c'; g.strokeStyle='rgba(25,12,4,.8)'; g.lineWidth=1.2*s;
    g.beginPath(); g.moveTo(x-9*s,topY-6*s); g.lineTo(x+(R2()-.5)*6*s,topY+h1); g.lineTo(x+9*s,topY-6*s); g.closePath(); g.fill(); g.stroke();   // răng trên
    g.beginPath(); g.moveTo(x-9*s,botY+6*s); g.lineTo(x+(R2()-.5)*6*s,botY-h2); g.lineTo(x+9*s,botY+6*s); g.closePath(); g.fill(); g.stroke(); }  // răng dưới
  g.restore();
  mouth(); g.strokeStyle='#0f0303'; g.lineWidth=5*s; g.lineJoin='round'; g.stroke();
  g.strokeStyle='rgba(85,6,6,.75)'; g.lineCap='round';                                     // vệt máu rỉ từ khóe miệng
  [[x0+8*s,y0],[x1-8*s,y0],[cx-40*s,cy+100*s],[cx+55*s,cy+98*s]].forEach(p=>{ g.lineWidth=(3+R2()*3)*s; g.beginPath(); g.moveTo(p[0],p[1]+30*s); g.lineTo(p[0]+(R2()-.5)*6*s,p[1]+(70+R2()*90)*s); g.stroke(); });
}
function grime(g,w,h,cx,cy,r){                                                              // nứt rạn + ố bẩn
  g.strokeStyle='rgba(30,22,6,.55)'; g.lineWidth=1.6;
  for(let i=0;i<14;i++){ let a=rnd(0,6.28), x=cx+Math.cos(a)*r*rnd(.5,.95), y=cy+Math.sin(a)*r*rnd(.5,.95);
    g.beginPath(); g.moveTo(x,y); for(let k=0;k<5;k++){ a+=rnd(-.7,.7); x+=Math.cos(a)*rnd(8,26); y+=Math.sin(a)*rnd(8,26); g.lineTo(x,y); } g.stroke(); }
  stains(g,w,h,34,.38);
}
const faceTex=()=>T('face',512,640,(g,w,h)=>{          // cận mặt cho cảnh jumpscare (nền trong suốt, quả cầu tròn)
  g.clearRect(0,0,w,h);
  g.save(); g.beginPath(); g.arc(w/2,h/2,252,0,7); g.clip();
  const gr=g.createRadialGradient(w/2-60,h/2-80,20,w/2,h/2,255);gr.addColorStop(0,'#b3a763');gr.addColorStop(.65,'#857b45');gr.addColorStop(1,'#2e2a15');
  g.fillStyle=gr; g.fillRect(0,0,w,h);
  grime(g,w,h,w/2,h/2,250);
  drawSmiley(g,w/2,h/2-6,1.8);
  noiseFx(g,w,h,22); g.restore();
});
const smileyMapTex=()=>T('smap',1024,512,(g,w,h)=>{     // bản đồ phủ quả cầu: mặt ở chính giữa phía trước (x = 256)
  const gr=g.createLinearGradient(0,0,0,h);gr.addColorStop(0,'#a79b5c');gr.addColorStop(.5,'#867c46');gr.addColorStop(1,'#4a4424');
  g.fillStyle=gr; g.fillRect(0,0,w,h);
  grime(g,w,h,256,256,230); grime(g,w,h,768,256,230);
  drawSmiley(g,256,262,1.05);
  noiseFx(g,w,h,26);});

// ---------- Cơn bão bên ngoài cửa sổ (mưa, sét, sấm) ----------
const haloTex=()=>T('halo',64,64,(g,w,h)=>{
  const gr=g.createRadialGradient(32,32,0,32,32,32);
  gr.addColorStop(0,'rgba(255,255,255,1)');gr.addColorStop(.35,'rgba(255,255,255,.4)');gr.addColorStop(1,'rgba(255,255,255,0)');
  g.fillStyle=gr;g.fillRect(0,0,w,h);});
const stC=document.createElement('canvas'); stC.width=256; stC.height=192;
const stG=stC.getContext('2d');
const stTex=new THREE.CanvasTexture(stC); stTex.wrapS=THREE.RepeatWrapping;
const stormMat=new THREE.MeshBasicMaterial({map:stTex,fog:false}); stormMat.userData.keep=true;
const stormL=new THREE.PointLight(0x9db8ff,0,45);   // không cần nữa (ngoài trời, cửa sổ không còn cảnh bão) -> không thêm vào scene để bớt 1 đèn
const drops=[]; for(let i=0;i<150;i++) drops.push({x:Math.random()*256,y:Math.random()*192,v:260+Math.random()*260,l:7+Math.random()*12});
const trees=[]; for(let i=0;i<15;i++) trees.push({x:i*18+Math.random()*8,h:28+Math.random()*34,w:12+Math.random()*10});
let flashV=0, boltT=0, nextBolt=3.5, thunderIn=-999, thunderNear=false, boltX=60, boltPts=[], stAcc=0;
const cl255=v=>Math.max(0,Math.min(255,Math.round(v)));
function drawStorm(dt){
  const g=stG,w=256,h=192,f=flashV;
  const gr=g.createLinearGradient(0,0,0,h);
  gr.addColorStop(0,'rgb('+cl255(10+f*190)+','+cl255(14+f*200)+','+cl255(26+f*225)+')');
  gr.addColorStop(1,'rgb('+cl255(22+f*170)+','+cl255(30+f*180)+','+cl255(46+f*200)+')');
  g.fillStyle=gr; g.fillRect(0,0,w,h);
  // mây đen trôi
  for(let i=0;i<6;i++){
    const x=((i*58+tt*5)%330)-35, y=14+(i%3)*15;
    g.fillStyle='rgba('+cl255(30+f*170)+','+cl255(36+f*170)+','+cl255(56+f*170)+',.6)';
    g.beginPath(); g.ellipse(x,y,55,15,0,0,7); g.fill();
  }
  // bóng cây, đồi phía xa
  const tc='rgb('+cl255(4+f*50)+','+cl255(6+f*55)+','+cl255(12+f*70)+')';
  g.fillStyle=tc; g.fillRect(0,h-14,w,14);
  trees.forEach(t=>{g.beginPath(); g.moveTo(t.x,h-12); g.lineTo(t.x+t.w/2,h-12-t.h); g.lineTo(t.x+t.w,h-12); g.fill();});
  // tia sét
  if(boltT>.7&&boltPts.length>1){
    g.lineJoin='round';
    g.strokeStyle='rgba(150,170,255,.28)'; g.lineWidth=7;
    g.beginPath(); boltPts.forEach((p,i)=>i?g.lineTo(p[0],p[1]):g.moveTo(p[0],p[1])); g.stroke();
    g.strokeStyle='rgba(245,248,255,'+Math.min(1,.5+f)+')'; g.lineWidth=2.4;
    g.beginPath(); boltPts.forEach((p,i)=>i?g.lineTo(p[0],p[1]):g.moveTo(p[0],p[1])); g.stroke();
    const b=boltPts[Math.floor(boltPts.length/2)];
    g.lineWidth=1.4; g.beginPath(); g.moveTo(b[0],b[1]); g.lineTo(b[0]+22,b[1]+26); g.lineTo(b[0]+14,b[1]+50); g.stroke();
  }
  // mưa
  g.strokeStyle='rgba(180,200,235,'+(.38+f*.4)+')'; g.lineWidth=1; g.beginPath();
  for(let i=0;i<drops.length;i++){
    const d=drops[i]; d.y+=d.v*dt; d.x-=d.v*dt*.18;
    if(d.y>h){d.y=-d.l;d.x=Math.random()*(w+40);} if(d.x<-10) d.x+=w+10;
    g.moveTo(d.x,d.y); g.lineTo(d.x-d.l*.18,d.y+d.l);
  }
  g.stroke();
  // lớp hơi nước mờ trên kính
  g.fillStyle='rgba(120,140,180,.07)'; g.fillRect(0,0,w,h);
}
function thunder(near){
  if(!amb||!(state==='play'||state==='scare')) return;
  try{
    const a=ac(), t0=a.currentTime, n=Math.floor(a.sampleRate*4.2), b=a.createBuffer(1,n,a.sampleRate), x=b.getChannelData(0);
    for(let i=0;i<n;i++){const t=i/n; x[i]=(Math.random()*2-1)*Math.pow(1-t,1.25)*(.6+.4*Math.sin(t*30)+.25*Math.sin(t*71));}
    const s=a.createBufferSource(), lp=a.createBiquadFilter(), g=a.createGain(), cp=a.createDynamicsCompressor();
    lp.type='lowpass'; lp.frequency.setValueAtTime(1100,t0); lp.frequency.exponentialRampToValueAtTime(45,t0+3.8);
    g.gain.value=near?9:6.5;
    cp.threshold.value=-12; cp.knee.value=8; cp.ratio.value=14; cp.attack.value=.002; cp.release.value=.25;
    s.buffer=b; s.connect(lp); lp.connect(g); g.connect(cp); cp.connect(a.destination); s.start(t0);
    noise(.35,near?1:.7);                       // tiếng nổ chát lúc sét đánh
    if(near){ noise(.6,.8); tone(70,.7,'sawtooth',.5,30); }
    tone(near?58:44,3.2,'sine',1,18);           // tiếng ầm trầm
    tone(near?95:70,1.4,'square',.28,28);
  }catch(e){}
}
function stormUpdate(dt){
  nextBolt-=dt;
  if(nextBolt<=0){
    nextBolt=state==='menu'?3.5+Math.random()*5.5:6+Math.random()*10; boltT=1; boltX=20+Math.random()*216;
    boltPts=[[boltX,0]]; let bx=boltX,by=0;
    while(by<130){bx+=(Math.random()-.5)*28; by+=10+Math.random()*14; boltPts.push([bx,by]);}
    const near=Math.random()<.6, dly=near?.06+Math.random()*.1:1.0+Math.random()*1.6;   // gần: nổ gần như cùng lúc chớp; xa: trễ 1-2,6 giây
    if(thunderPlay(dly,near)) thunderIn=-999; else{thunderIn=dly; thunderNear=near;}      // chưa có file -> tiếng tổng hợp cũ
    rainSwell(near);
  }
  if(boltT>0){
    boltT=Math.max(0,boltT-dt); const e=1-boltT;
    flashV=RF?.4*Math.max(0,1-e*1.3)
      :(e<.07?1:e<.13?.12:e<.24?.95:e<.34?.25:e<.46?.6:Math.max(0,.55*(1-(e-.46)/.54)));
  } else flashV=0;
  if(thunderIn>-100){thunderIn-=dt; if(thunderIn<=0){thunderIn=-999; thunder(thunderNear);}}
  stormL.intensity=flashV*3;
  stAcc+=dt;
  if(stAcc>(flashV>0?.016:.05)){drawStorm(stAcc); stAcc=0; stTex.needsUpdate=true;}
}
// Manh mối: cứ 3 giây phát sáng một lần
function pulseClues(){
  const ph=(tt%3)/3, p=ph<.05?ph/.05:Math.exp(-(ph-.05)*4.2);
  for(const o of inter){
    if(o.kind!=='clue') continue;
    if(solved[o.idx]){o.mat.emissiveIntensity=.7;o.L.intensity=.45;o.halo.material.opacity=0;}
    else{o.mat.emissiveIntensity=.12+2.6*p;o.L.intensity=.05+2.4*p;o.halo.material.opacity=.95*p;}
  }
}

// ---------- Ma (thực thể) ----------
const ghostRoot=new THREE.Group(); ghostRoot.rotation.order='YXZ'; ghostRoot.position.set(0,-80,0); scene.add(ghostRoot);
const gBody=new THREE.Group(); ghostRoot.add(gBody);
const gArms=[], gHair=[], gMats=[]; let gHeadG, gMouth, gLight;
(function(){
  // Ma = quả cầu mặt cười màu vàng, miệng toác đầy răng, lơ lửng giữa không trung
  gHeadG=new THREE.Group(); gHeadG.position.set(0,1.4,0); gBody.add(gHeadG);
  const mt=smileyMapTex();
  const ballM=new THREE.MeshStandardMaterial({map:mt,emissiveMap:mt,emissive:0xffffff,emissiveIntensity:.55,roughness:.85});
  const ball=new THREE.Mesh(new THREE.SphereGeometry(.72,40,32),ballM); ball.castShadow=false; gHeadG.add(ball);
  gMouth=new THREE.Object3D(); gHeadG.add(gMouth);       // chỉ dùng scale.y làm nhịp "cười" cho animGhost
  gLight=new THREE.PointLight(0xb9c4d8,0,11); gLight.position.set(0,1.5,1.3); gBody.add(gLight);
  const seen=new Set();
  ghostRoot.traverse(o=>{if(o.material&&!seen.has(o.material)){seen.add(o.material);o.material.transparent=true;o.material.opacity=0;gMats.push(o.material);}});
  ghostRoot.scale.set(1.05,1.05,1.05);
})();
function parkGhost(){ ghostSoundStop();$('bars').className='';if(camera.fov!==72){camera.fov=72;camera.updateProjectionMatrix();}gh.phase='idle';gh.alpha=0;gh.peek=0;ghostRoot.position.set(0,-80,0);ghostRoot.rotation.x=0;gLight.intensity=0;}

// ---------- Dựng phòng ----------
const M=(c,e)=>new THREE.MeshStandardMaterial({color:c,roughness:.9,emissive:e||0x000000,side:THREE.DoubleSide});

function disposeGroup(g){
  if(!g) return; scene.remove(g); const seen=new Set();
  g.traverse(o=>{ if(o.geometry) o.geometry.dispose();
    const ms=o.material?(Array.isArray(o.material)?o.material:[o.material]):[];
    ms.forEach(mt=>{ if(seen.has(mt)||(mt.userData&&mt.userData.keep))return; seen.add(mt); if(mt.map)mt.map.dispose(); if(mt.emissiveMap)mt.emissiveMap.dispose(); mt.dispose(); }); });
}
function disposeRoom(){
  disposeGroup(room); room=null; rooms.forEach(r=>r&&disposeGroup(r.room)); rooms.length=0; doorGlow=null;
}

function buildRoom(keep){
  if(!keep) disposeRoom();
  room=new THREE.Group(); scene.add(room);
  obstacles=[]; inter=[]; watchers=[]; spots=[]; doorOpen=false; curSpot=null; fireMat=null;
  const sz=SIZES[layoutOrder[door%5]]; RW=sz[0]; RD=sz[1];
  const lay=layoutOrder[door%5], hw=RW/2, hd=RD/2, m=mirrorArr[door%5], S1=-m, S2=m;
  scene.fog=new THREE.FogExp2(0x03060c,0.036+door*0.004);
  renderer.shadowMap.enabled=HQ; spot.castShadow=HQ; lamp.castShadow=false;
  const R=mulberry(gameSeed+door*7919+17);
  const pick=a=>a[Math.floor(R()*a.length)];
  const ryOf=s=>s<0?Math.PI/2:-Math.PI/2;
  const lit=tx=>new THREE.MeshStandardMaterial({map:tx,roughness:.9,side:THREE.DoubleSide});
  const woodM=new THREE.MeshStandardMaterial({map:woodTex(1,1),roughness:.75});
  const woodDark=M(0x3a2c20), woodMid=M(0x8d6e48), stone=M(0x6a6a66);   // woodMid = bìa các-tông
  const brass=new THREE.MeshStandardMaterial({color:0xd4af37,metalness:.8,roughness:.3});
  const black=new THREE.MeshBasicMaterial({color:0x000000});
  const fab=c=>new THREE.MeshStandardMaterial({color:c,roughness:1});
  const plane=(w,h,mat,x,y,z,ry,rx)=>{const p=new THREE.Mesh(new THREE.PlaneGeometry(w,h),mat);
    p.position.set(x,y,z);p.rotation.set(rx||0,ry||0,0);p.receiveShadow=true;room.add(p);return p;};
  const box=(sx,sy,sz2,mat,x,y,z,parent,cast)=>{const b=new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz2),mat);
    b.position.set(x,y,z);b.castShadow=cast!==false&&sx*sy*sz2>.25;b.receiveShadow=true;(parent||room).add(b);return b;};
  const cyl=(r1,r2,h,seg,mat,x,y,z,parent,cast)=>{const c=new THREE.Mesh(new THREE.CylinderGeometry(r1,r2,h,seg),mat);
    c.position.set(x,y,z);c.castShadow=cast!==false&&r1*r1*h>.08;c.receiveShadow=true;(parent||room).add(c);return c;};
  const addObs=(cx,cz,sx,sz2)=>obstacles.push({x1:cx-sx/2,x2:cx+sx/2,z1:cz-sz2/2,z2:cz+sz2/2});
  const dims=(fx,fz,len,dep)=>Math.abs(fz)>.5?[len,dep]:[dep,len];
  const grp=(x,z,fx,fz)=>{const g=new THREE.Group();g.position.set(x,0,z);g.rotation.y=Math.atan2(fx,fz);room.add(g);return g;};
  const wi=wallOrder[door%5];

  // sàn, trần, tường
  plane(RW,RD,new THREE.MeshStandardMaterial({map:lay===2?stripeTex(RW/4,RD/4):lay===3?grassTex(RW/3,RD/3):carpetTex(RW/2,RD/2),roughness:1}),0,0,0,0,-Math.PI/2);
  // Tường = dãy nhà lớp học 2 tầng (cửa lớp, cửa sổ tối, hành lang tầng 2, mái ngói); khu sân bóng / vườn / cổng: hai bên là hàng rào + hàng cây
  // Mỗi khu chỉ dùng chung 1 texture cho mọi mặt tường (đỡ tốn bộ nhớ card đồ họa), mặt nào dài hơn thì co giãn UV.
  const garden=(lay>=2);
  const roofM=M(0x3a1e1a);
  const facM=lit(facadeTex(wi,1,1)), upM=lit(upperTex(wi,1,1));
  let treeM=null, fenM=null;
  const tile=(pl,su,sv)=>{const uv=pl.geometry.attributes.uv;for(let i=0;i<uv.count;i++)uv.setXY(i,uv.getX(i)*su,uv.getY(i)*sv);uv.needsUpdate=true;return pl;};
  const upperPlane=(len,x,z,ry,nx,nz)=>{
    tile(plane(len,RH,upM,x,RH*1.5,z,ry),len/8,1);
    const ax=Math.abs(nz)>.5; box(ax?len:1.1,.3,ax?1.1:len,roofM,x+nx*.45,RH*2+.05,z+nz*.45,null,false); };
  const gardenFace=(len,x,z,ry,nx,nz)=>{
    treeM=treeM||new THREE.MeshStandardMaterial({map:treeLineTex(wi,1,1),alphaTest:.5,roughness:1,side:THREE.DoubleSide});
    fenM=fenM||new THREE.MeshStandardMaterial({map:fenceTex(1,1),alphaTest:.2,roughness:.6,metalness:.3,side:THREE.DoubleSide});
    tile(plane(len,RH*2,treeM,x,RH,z,ry),len/16,1);
    tile(plane(len,2.4,fenM,x+nx*.12,1.2,z+nz*.12,ry),len/2.4,1); };
  // tường có ô cửa (rộng 1,9m, cao 3m) để nhìn/đi xuyên sang khu bên cạnh; khu đầu tiên thì tường vào để kín
  const wallDoor=(zp,ry)=>{ const sh=new THREE.Shape(); sh.moveTo(-hw,0);sh.lineTo(-.95,0);sh.lineTo(-.95,3);sh.lineTo(.95,3);sh.lineTo(.95,0);sh.lineTo(hw,0);sh.lineTo(hw,RH);sh.lineTo(-hw,RH);sh.lineTo(-hw,0);
    const geo=new THREE.ShapeGeometry(sh), uv=geo.attributes.uv;
    for(let i=0;i<uv.count;i++)uv.setXY(i,uv.getX(i)/8+.026,uv.getY(i)/RH);             // UV của ShapeGeometry tính theo mét: 1 ô texture = 8m x 4m; .026 để ô cổng nằm giữa trụ tường
    const m=new THREE.Mesh(geo,facM); m.position.set(0,0,zp); m.rotation.y=ry||0; m.receiveShadow=true; room.add(m);
    upperPlane(RW,0,zp,ry||0,0,ry?-1:1); };
  wallDoor(-hd,0);
  if(door>0) wallDoor(hd,Math.PI); else { tile(plane(RW,RH,facM,0,RH/2,hd,Math.PI),RW/8,1); upperPlane(RW,0,hd,Math.PI,0,-1); }
  const sideWall=(x,ry,nx)=>{ if(garden) gardenFace(RD,x,0,ry,nx,0); else { tile(plane(RD,RH,facM,x,RH/2,0,ry),RD/8,1); upperPlane(RD,x,0,ry,nx,0); } };
  sideWall(-hw,Math.PI/2,1); sideWall(hw,-Math.PI/2,-1);
  // ốp tường gỗ
  const wains=(len,x,z,ry)=>{return;const gp=new THREE.Group();gp.position.set(x,0,z);gp.rotation.y=ry;room.add(gp);
    box(len,1.1,0.08,M(0x2f6a62),0,0.55,0,gp,false);box(len+0.04,0.07,0.13,M(0xcfc9b6),0,1.13,0.02,gp,false);box(len+0.04,0.16,0.12,M(0xcfc9b6),0,0.08,0.02,gp,false);};
  const seg=hw-1.4;
  wains(seg,-(hw+1.4)/2,-hd+0.04,0); wains(seg,(hw+1.4)/2,-hd+0.04,0);
  if(door>0){ wains(seg,-(hw+1.4)/2,hd-0.04,Math.PI); wains(seg,(hw+1.4)/2,hd-0.04,Math.PI); } else wains(RW,0,hd-0.04,Math.PI);
  wains(RD,-hw+0.04,0,Math.PI/2); wains(RD,hw-0.04,0,-Math.PI/2);
  // dầm trần

  // đèn chùm
  flameMat=new THREE.MeshBasicMaterial({color:0xf0f6ff});
  const iron=M(0x111111);
  const chand=(x,z)=>{                                  // cột đèn sân trường
    cyl(.06,.08,RH-.45,8,iron,x,(RH-.45)/2,z,null,false);box(.6,.07,.32,iron,x,RH-.45,z,null,false);
    const bulb=new THREE.Mesh(new THREE.SphereGeometry(.13,10,8),flameMat);bulb.position.set(x,RH-.55,z);room.add(bulb);addObs(x,z,.5,.5);};
  const lp1=lay===2?[hw-1.3,6.5]:[0,RD*0.12], lp2=lay===2?[-(hw-1.3),-7.5]:[0,-RD*0.28];
  chand(lp1[0],lp1[1]); chand(lp2[0],lp2[1]);
  [[-hw*.5,-RD*.36],[hw*.5,-RD*.36],[-hw*.5,RD*.36],[hw*.5,RD*.36]].forEach(q=>chand(q[0],q[1]));   // thêm cột đèn cho sân rộng
  lamp.position.set(lp1[0],RH-0.85,lp1[1]); lampB.position.set(lp2[0],RH-0.85,lp2[1]);

  // cửa ra
  const dz=-hd, fm=M(0x1a1008);
  box(0.3,3.3,0.25,fm,-1.1,1.65,dz+0.12,null,false); box(0.3,3.3,0.25,fm,1.1,1.65,dz+0.12,null,false); box(2.5,0.3,0.25,fm,0,3.15,dz+0.12,null,false);
  const glow=new THREE.Mesh(new THREE.PlaneGeometry(1.9,3.0),new THREE.MeshBasicMaterial({color:0xfff1c9}));
  glow.position.set(0,1.5,dz+0.03); room.add(glow); doorGlow=glow;
  if(door>0){
    box(0.3,3.3,0.25,fm,-1.1,1.65,hd-0.12,null,false); box(0.3,3.3,0.25,fm,1.1,1.65,hd-0.12,null,false); box(2.5,0.3,0.25,fm,0,3.15,hd-0.12,null,false);
    const jm=new THREE.MeshStandardMaterial({color:0x1a1008,roughness:1,side:THREE.DoubleSide});
    const jp=(w,h,x,y,z,rx,ry)=>{const q=new THREE.Mesh(new THREE.PlaneGeometry(w,h),jm);q.position.set(x,y,z);q.rotation.set(rx||0,ry||0,0);room.add(q);};
    jp(GAP,3,-.95,1.5,hd+GAP/2,0,Math.PI/2); jp(GAP,3,.95,1.5,hd+GAP/2,0,Math.PI/2); jp(1.9,GAP,0,3,hd+GAP/2,Math.PI/2,0); jp(1.9,GAP,0,.01,hd+GAP/2,-Math.PI/2,0);
  }
  doorPivot=new THREE.Group(); doorPivot.position.set(-0.9,0,dz+0.14); room.add(doorPivot);
  box(1.8,2.95,0.1,new THREE.MeshStandardMaterial({map:doorTex(),roughness:.7}),0.9,1.475,0,doorPivot,false);
  [0.5,2.4].forEach(y=>box(0.12,0.22,0.14,M(0x222222),0.03,y,0,doorPivot,false));
  const knob=new THREE.Mesh(new THREE.SphereGeometry(0.07,12,10),brass); knob.position.set(1.6,1.4,0.1); doorPivot.add(knob);
  const cv=document.createElement('canvas'); cv.width=128; cv.height=64; const g=cv.getContext('2d');
  g.fillStyle='#caa24a'; g.fillRect(0,0,128,64); g.strokeStyle='#5a4010'; g.lineWidth=4; g.strokeRect(3,3,122,58);
  g.fillStyle='#2a1a08'; g.font='bold 42px serif'; g.textAlign='center'; g.textBaseline='middle'; g.fillText('KHU '+(door+1),64,34);
  const pm=new THREE.Mesh(new THREE.PlaneGeometry(0.6,0.3),new THREE.MeshStandardMaterial({map:new THREE.CanvasTexture(cv),metalness:.6,roughness:.4}));
  pm.position.set(0.9,2.45,0.06); doorPivot.add(pm);
  doorLight.position.set(0,1.8,dz+1.3); doorLight.intensity=0;
  inter.push({kind:'door',x:0,z:dz,r:2.7});

  // ---- đồ nội thất (các hàm dựng) ----
  const metalM=M(0x555b63), stoneT=M(0x8d8f88), soilM=M(0x3a2a1c), trunkM=M(0x3b2a1c), netM=M(0xe8e8e8);
  const leafM=new THREE.MeshStandardMaterial({map:leafTex(),roughness:1});
  const darkWinM=new THREE.MeshBasicMaterial({color:0x080d12}), litWinM=new THREE.MeshBasicMaterial({color:0xcdb86a});
  const blob=(x,y,z,r,parent)=>{const f=new THREE.Mesh(new THREE.SphereGeometry(r,10,8),leafM);f.position.set(x,y,z);(parent||room).add(f);return f;};
  let pillar=(x,z)=>{cyl(.2,.3,3.4,8,trunkM,x,1.7,z);blob(x,3.9,z,1.5);blob(x+.7,3.4,z+.4,1.05);blob(x-.6,3.5,z-.5,1.1);addObs(x,z,.8,.8);};   // cây phượng
  let table=(x,z,sx,sz2,h)=>{box(sx,.08,sz2,stoneT,x,h,z);                                              // bàn đá
    [-1,1].forEach(s2=>box(.16,h,Math.max(.3,sz2-.3),stoneT,x+s2*(sx/2-.25),h/2,z));addObs(x,z,sx,sz2);};
  let chair=(x,z,ry)=>{cyl(.22,.22,.46,10,stoneT,x,.23,z,null,false);};                                  // ghế đá tròn
  let shelf=(x,z,fx,fz,len)=>{const gp=grp(x,z,fx,fz);box(len,.35,.55,stoneT,0,.175,0,gp);box(len-.1,1.05,.5,leafM,0,.85,0,gp);   // luống cây xén
    const d=dims(fx,fz,len,.55);addObs(x,z,d[0],d[1]);};
  let clock=(x,z,fx,fz)=>{const gp=grp(x,z,fx,fz);[-.32,.32].forEach(dx=>box(.07,2.1,.07,metalM,dx,1.05,0,gp,false));   // bảng tin dựng đứng
    box(.8,1.15,.05,M(0x9a7448),0,1.55,.03,gp,false);
    const pp=new THREE.Mesh(new THREE.PlaneGeometry(.7,1.05),new THREE.MeshStandardMaterial({map:paintTex(3),roughness:.9}));pp.position.set(0,1.55,.065);gp.add(pp);
    const d=dims(fx,fz,.8,.42);addObs(x,z,d[0],d[1]);};
  let fireplace=(x,z,fx,fz)=>{const gp=grp(x,z,fx,fz);                                                    // cột bóng rổ
    box(.14,3.2,.14,metalM,0,1.6,-.5,gp,false);box(.1,.1,.5,metalM,0,3.0,-.28,gp,false);box(1.7,1.0,.05,M(0xdfe3e6),0,3.2,-.02,gp,false);
    const rim=new THREE.Mesh(new THREE.TorusGeometry(.23,.02,6,16),M(0xd2501c));rim.rotation.x=Math.PI/2;rim.position.set(0,2.7,.25);gp.add(rim);
    sconceL[0].position.set(x+fx*1.2,1.0,z+fz*1.2);
    const d=dims(fx,fz,2.5,.9);addObs(x,z,d[0],d[1]);};
  let sofa=(x,z,fx,fz,col)=>{const gp=grp(x,z,fx,fz);box(2.4,.1,.5,stoneT,0,.46,0,gp);                    // ghế đá dài có tựa lưng gỗ
    [-1,1].forEach(sx=>box(.18,.46,.5,stoneT,sx*1.05,.23,0,gp,false));
    box(2.4,.4,.06,M(0x6a4a2a),0,.85,-.23,gp,false);[-1,1].forEach(sx=>box(.06,.5,.06,metalM,sx*1.1,.65,-.23,gp,false));
    const d=dims(fx,fz,2.4,.7);addObs(x,z,d[0],d[1]);};
  let dresser=(x,z,fx,fz)=>{const gp=grp(x,z,fx,fz);box(2.2,1.0,1,stoneT,0,.5,0,gp);box(2.1,.26,.9,soilM,0,1.13,0,gp,false);   // bồn hoa cao
    [-.85,.85].forEach(dx=>blob(dx,1.4,0,.3,gp));
    const d=dims(fx,fz,2.2,1);addObs(x,z,d[0],d[1]);};
  let barrel=(x,z)=>{cyl(.3,.26,.8,12,M(0x4d5a5a),x,.4,z);cyl(.32,.32,.05,12,metalM,x,.82,z,null,false);addObs(x,z,.7,.7);};   // thùng rác
  let crate=(x,z,s,ry)=>{const b=box(s,s,s,woodMid,x,s/2,z);b.rotation.y=ry||0;addObs(x,z,s*1.2,s*1.2);};
  const flagpole=(x,z)=>{cyl(.06,.08,6.0,8,metalM,x,3.0,z,null,false);cyl(.4,.45,.18,12,stoneT,x,.09,z);               // cột cờ
    const fl=new THREE.Mesh(new THREE.PlaneGeometry(1.5,1.0),new THREE.MeshStandardMaterial({map:flagTex(),side:THREE.DoubleSide,roughness:1}));
    fl.position.set(x+.8,5.2,z);room.add(fl);addObs(x,z,.9,.9);};
  let wardrobe=(x,z,fx,fz)=>{const gp=grp(x,z,fx,fz);                                                     // bụi cây rậm (chỗ trốn)
    box(1.5,2.4,.95,leafM,0,1.2,0,gp);blob(-.45,2.5,0,.55,gp);blob(.45,2.55,.1,.55,gp);blob(0,2.7,-.1,.55,gp);
    const dL=box(.72,2.2,.03,leafM,-.37,1.25,.49,gp,false), dR=box(.72,2.2,.03,leafM,.37,1.25,.49,gp,false), dS=box(.03,2.2,.04,black,0,1.25,.49,gp,false);
    const d=dims(fx,fz,1.5,.95);addObs(x,z,d[0],d[1]);
    const sp={kind:'hide',type:'ward',x,z,r:2.6,fx,fz,hx:x,hz:z,hy:1.5,yaw:Math.atan2(-fx,-fz),ex:x+fx*1.5,ez:z+fz*1.5,gd:2.4,bend:.85,sink:0,doors:[dL,dR,dS]};
    inter.push(sp);spots.push(sp);};
  let bed=(x,z,wallSide,fx,fz,col)=>{const gp=new THREE.Group();gp.position.set(x,0,z);gp.rotation.y=wallSide<0?0:Math.PI;room.add(gp);   // bàn bóng bàn (chui xuống gầm)
    box(2.3,.05,1.5,M(0x1d4f8a),0,.76,0,gp);box(2.3,.006,.03,netM,0,.79,0,gp,false);box(.02,.16,1.5,netM,0,.86,0,gp,false);
    [-1,1].forEach(sx=>box(.05,.72,1.2,metalM,sx*1.05,.36,0,gp,false));box(.18,.02,.16,fab(col),.7,.8,.4,gp,false);
    addObs(x,z,2.3,1.5);
    const sp={kind:'hide',type:'bed',x,z,r:2.6,fx,fz,hx:x,hz:z,hy:.32,yaw:Math.atan2(-fx,-fz),ex:x+fx*1.5,ez:z+fz*1.5,gd:2.7,bend:.72,sink:1.3};
    inter.push(sp);spots.push(sp);};
  let painting=(v,x,y,z,ry,pw,ph)=>{return;const gp=new THREE.Group();gp.position.set(x,y,z);gp.rotation.y=ry;room.add(gp);
    box(pw+.16,ph+.16,.06,M(0xb9b29c),0,0,0,gp,false);
    const t=paintTex(v),p=new THREE.Mesh(new THREE.PlaneGeometry(pw,ph),new THREE.MeshStandardMaterial({map:t,emissiveMap:t,emissive:0xffffff,emissiveIntensity:.2,roughness:.8}));
    p.position.z=.04;gp.add(p);};
  let windowAt=(x,y,z,ry,ww,hh)=>{return;ww=ww||2.0;hh=hh||1.8;const gp=new THREE.Group();gp.position.set(x,y,z);gp.rotation.y=ry;room.add(gp);
    const geo=new THREE.PlaneGeometry(ww,hh),uv=geo.attributes.uv,o=Math.random(),uvW=Math.min(1,(ww/hh)*(192/256));
    for(let i=0;i<uv.count;i++)uv.setX(i,o+uv.getX(i)*uvW);
    const gl=new THREE.Mesh(geo,Math.random()<.22?litWinM:darkWinM);gl.position.z=.02;gp.add(gl);
    box(ww+.24,.1,.14,woodDark,0,hh/2+.05,.04,gp,false);box(ww+.36,.1,.24,woodDark,0,-hh/2-.05,.08,gp,false);
    box(.1,hh+.2,.14,woodDark,-ww/2-.05,0,.04,gp,false);box(.1,hh+.2,.14,woodDark,ww/2+.05,0,.04,gp,false);
    box(.05,hh,.07,woodDark,0,0,.05,gp,false);box(ww,.05,.07,woodDark,0,hh*.12,.05,gp,false);
    const cu=fab(0x8c8a74);box(.26,hh+.3,.1,cu,-ww/2-.28,0,.09,gp,false);box(.26,hh+.3,.1,cu,ww/2+.28,0,.09,gp,false);};
  let sconceMesh=(x,z,ry)=>{if(garden&&Math.abs(x)>hw-1)return;const gp=new THREE.Group();gp.position.set(x,2.3,z);gp.rotation.y=ry;room.add(gp);   // đèn lồng gắn tường
    box(.12,.4,.12,M(0x2a2a2a),0,0,.08,gp,false);
    const fl=new THREE.Mesh(new THREE.SphereGeometry(.07,8,6),new THREE.MeshBasicMaterial({color:0xfff0c8}));fl.position.set(0,.28,.1);gp.add(fl);};
  const decal=(tx,w2,h2,x,y,z,ry,rx)=>{const p=new THREE.Mesh(new THREE.PlaneGeometry(w2,h2),
    new THREE.MeshStandardMaterial({map:tx,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2,roughness:.4}));
    p.position.set(x,y,z);p.rotation.set(rx||0,ry||0,0);p.receiveShadow=true;room.add(p);};
  const clue=(idx,x,y,z,sx,sy,sz2,lz)=>{
    const isPic=sy>=.2;                       // sy lớn -> bức tranh treo tường; sy nhỏ -> tờ giấy đặt trên mặt bàn/tủ
    const tx=isPic?paintTex(idx):paperTex();
    const mat=new THREE.MeshStandardMaterial({map:tx,emissiveMap:tx,color:0xffffff,emissive:0xffaa22,emissiveIntensity:1.4,roughness:.8,side:THREE.DoubleSide});
    if(isPic){
      box(sx+.2,sy+.2,.06,M(0xb9b29c),x,y,z+.04,null,false);            // khung tranh
      const pc=new THREE.Mesh(new THREE.PlaneGeometry(sx,sy),mat); pc.position.set(x,y,z); pc.rotation.y=Math.PI; room.add(pc);
    } else {
      const gp=new THREE.Group(); gp.position.set(x,y-sy/2+.022,z); gp.rotation.y=(idx-1)*.5+.2; room.add(gp);
      const pp=new THREE.Mesh(new THREE.PlaneGeometry(.62,.44),mat); pp.rotation.x=-Math.PI/2; gp.add(pp);   // tờ giấy nằm phẳng
    }
    const L=clueL[idx];L.color.set(0xffaa44);L.position.set(x,y+0.4,z+lz);
    const halo=new THREE.Sprite(new THREE.SpriteMaterial({map:haloTex(),color:0xffcc66,transparent:true,opacity:0,blending:THREE.AdditiveBlending,depthWrite:false,fog:false}));
    halo.position.set(x,y+.05,z+lz*.4);halo.scale.set(isPic?2.4:1.4,isPic?2.4:1.4,1);room.add(halo);
    inter.push({kind:'clue',idx,x,z,r:2.6,mat,L,halo});};

  // ---- bày trí: mỗi phòng một bố cục riêng ----
  sconceL.forEach(l=>l.color.set(0xdfe9ff));
  sconceL[0].position.set(-hw+1.2,2.4,-hd+5); sconceL[1].position.set(hw-1.2,2.6,hd-6);
  stormL.position.set(0,RH-.7,0);
  const wx=(s,o)=>s*(hw-o);
  let candle=(x,z,h)=>{box(.3,.05,.22,M(0x8a2a2a),x,h+.03,z,null,false);box(.28,.05,.2,M(0x2a4a8a),x,h+.08,z,null,false);};   // chồng sách
  const paintClue=(idx,cx)=>clue(idx,cx,2.0,hd-.1,1.5,1.2,.04,-.7);   // manh mối dạng bức tranh
  // thảm: mỗi phòng một kích thước
  const rs=[[7,12],[4.5,18],[2.4,26],[3.6,22],[6,24]][lay];
  const rug=new THREE.Mesh(new THREE.PlaneGeometry(rs[0],rs[1]),new THREE.MeshStandardMaterial({map:rugTex(),roughness:1}));
  rug.rotation.x=-Math.PI/2; rug.position.set(0,.012,0); rug.receiveShadow=true; room.add(rug); rug.visible=false;

  // ---- HÌNH DẠNG PHÒNG: khối tường đặc ở góc / cạnh làm mặt bằng thành chữ Z, T, thập, L... thay vì hình chữ nhật ----
  // Mỗi khối [x1,x2,z1,z2] (tọa độ trong phòng): có tường + ốp gỗ + tranh ở mặt trong, chặn đường đi; đồ nội thất nằm trong/sát khối sẽ tự bị bỏ qua.
  // Hành lang giữa (|x|<5) ở hai đầu phòng luôn trống để vào/ra cửa.
  shapeBlocks=[];
  const blocks=shapeBlocks;
  const inB=(x,z,m)=>{m=m||0;for(const b of blocks){if(x>b[0]-m&&x<b[1]+m&&z>b[2]-m&&z<b[3]+m)return true;}return false;};
  const paintRaw=painting;
  blocks.forEach(b=>{
    const x1=b[0],x2=b[1],z1=b[2],z2=b[3],bw=x2-x1,bd=z2-z1,cx=(x1+x2)/2,cz=(z1+z2)/2;
    obstacles.push({x1:x1,x2:x2,z1:z1,z2:z2});
    const face=(len,x,z,ry,nx,nz,ci)=>{          // một mặt tường trong của khối (bỏ mặt trùng tường ngoài)
      tile(plane(len,RH,facM,x,RH/2,z,ry),len/8,1); upperPlane(len,x,z,ry,nx,nz);
      if(len>=3){ const ps=len>6?[-len/4,len/4]:[0];
        ps.forEach((o,k)=>paintRaw((door+ci+k*2)%4,x+(ry===0||ry===Math.PI?o:0)+nx*.05,2.35,z+(ry===0||ry===Math.PI?0:o)+nz*.05,ry===0?0:ry===Math.PI?Math.PI:(nx>0?Math.PI/2:-Math.PI/2),1,1.25)); } };
    if(z1>-hd+.01) face(bw,cx,z1,Math.PI,0,-1,0);
    if(z2<hd-.01) face(bw,cx,z2,0,0,1,1);
    if(x1>-hw+.01) face(bd,x1,cz,Math.PI/2,-1,0,2);
    if(x2<hw-.01) face(bd,x2,cz,Math.PI/2,1,0,3);
  });
  const _g=(f,xi,zi,m)=>function(){return inB(arguments[xi],arguments[zi],m)?undefined:f.apply(null,arguments);};
  pillar=_g(pillar,0,1,1.3); table=_g(table,0,1,1.3); chair=_g(chair,0,1,1.3); shelf=_g(shelf,0,1,1.3);
  clock=_g(clock,0,1,1.3); fireplace=_g(fireplace,0,1,1.6); sofa=_g(sofa,0,1,1.4); dresser=_g(dresser,0,1,1.3);
  barrel=_g(barrel,0,1,1.2); crate=_g(crate,0,1,1.2); candle=_g(candle,0,1,1.0); sconceMesh=_g(sconceMesh,0,1,1.0);
  windowAt=_g(windowAt,0,2,1.3); painting=_g(painting,1,3,1.3);
  const _hide=(f,fi)=>function(){const a=arguments,x=a[0],z=a[1],fx=a[fi],fz=a[fi+1];     // tủ / giường: cả chỗ trốn lẫn lối ra phải thoáng
    if(inB(x,z,1.3)||inB(x+fx*1.6,z+fz*1.6,.3)||inB(x+fx*2.9,z+fz*2.9,.3)) return; return f.apply(null,a);};
  wardrobe=_hide(wardrobe,2); bed=_hide(bed,3);

  switch(lay){

  // ===== KHU 1: SÂN CỜ — cột cờ, 4 cây phượng, cột bóng rổ, bụi cây, bàn bóng bàn =====
  case 0:{
    [-1,1].forEach(sx=>[-1,1].forEach(sz2=>pillar(sx*(hw-4),sz2*RD*0.2)));
    flagpole(0,-RD*0.04); sofa(-3.6,-RD*0.04,1,0); sofa(3.6,-RD*0.04,-1,0);          // cột cờ giữa sân, hai ghế đá hai bên
    clock(wx(-1,.4),-RD*0.40,1,0);
    const tx0=wx(-1,1.7),tz0=-RD*0.25;
    table(tx0,tz0,1.3,2.4,.8);chair(tx0,tz0+1.7,-Math.PI/2);
    clue(0,tx0,.88,tz0+.3,.5,.08,.35,0);candle(tx0,tz0-.8,.8);
    sconceMesh(wx(-1,.1),-RD*0.15,ryOf(-1));
    wardrobe(wx(-1,.55),-RD*0.05,1,0);
    shelf(wx(-1,.3),RD*0.15,1,0,3);
    bed(wx(-1,1.4),RD*0.36,-1,0,-1,pick([0x5a1a1a,0x1a3a5a,0x3a5a2a]));
    fireplace(wx(1,.45),-RD*0.40,-1,0);
    shelf(wx(1,.3),-RD*0.20,-1,0,3);
    dresser(wx(1,.8),RD*0.05,-1,0);
    clue(1,wx(1,.8),1.28,RD*0.05,.5,.05,.4,0);
    bed(wx(1,1.4),RD*0.26,1,0,-1,pick([0x4a1a4a,0x5a3a1a,0x1a4a4a]));
    sofa(wx(1,.9),RD*0.37,-1,0,pick([0x5a1212,0x1a3a2a,0x2a2a4a]));
    wardrobe(wx(1,.55),RD*0.47,-1,0);
    wardrobe(5.5,hd-.55,0,-1);
    paintClue(2,-4.5);
    if(!inB(-7.6,hd-.8,1.2)){ box(1.0,1,1,woodMid,-7.6,.5,hd-.8); addObs(-7.6,hd-.8,1.0,1.0); }
    barrel(-(hw-.7),-hd+.8); barrel(-(hw-1.6),-hd+.7); crate(hw-.8,-hd+.8,.9,.4); crate(hw-1.8,-hd+.7,.7,.9);
    painting(0,wx(-1,.05),2.5,RD*0.36,ryOf(-1),1,1.25);
    painting(1,wx(1,.05),3.1,-RD*0.20,ryOf(1),1,1.25);
    painting(2,wx(1,.05),2.3,RD*0.26,ryOf(1),1,1.25);
    painting(0,wx(1,.05),2.3,RD*0.37,ryOf(1),1,1.25);
    painting(2,3.6,2.2,-hd+.05,0,1,1.25);
    painting(0,-2.5,2.2,hd-.05,Math.PI,1,1.25);
    windowAt(wx(-1,.06),2.4,-RD*0.25,ryOf(-1));
    windowAt(wx(1,.06),2.4,4.2,ryOf(1));
    windowAt(-6.5,2.4,-hd+.06,0); windowAt(6.5,2.4,-hd+.06,0);
    windowAt(2.5,2.4,hd-.06,Math.PI);
    sconceMesh(wx(1,.1),RD*0.05,ryOf(1));
    sconceL[1].position.set(wx(-1,.9),2.6,-RD*0.15);
    break;}

  // ===== KHU 2: DÃY LỚP HỌC — luống cây xén dọc chân nhà, bàn ghế đá có manh mối =====
  case 1:{
    sconceL[0].position.set(-hw+1.5,2.4,-1); sconceL[1].position.set(hw-1.5,2.6,6);
    [-9,-5.8,-2.6].forEach(z=>shelf(wx(-1,.3),z,1,0,3));
    [-10.4,-7.2].forEach(z=>shelf(wx(1,.3),z,-1,0,3));
    shelf(wx(1,.3),4.5,-1,0,3);
    shelf(-3.8,-hd+.3,0,1,3); shelf(3.8,-hd+.3,0,1,3);
    table(-3.6,-3,2.6,1.3,.8); chair(-3.6,-4.1,0); chair(-3.6,-1.9,Math.PI);
    clue(0,-3.0,.88,-3,.5,.08,.35,0); candle(-4.6,-3,.8);
    table(3.6,2.5,2.6,1.3,.8); chair(3.6,1.4,0); chair(3.6,3.6,Math.PI);
    clue(1,3.6,.88,2.5,.5,.08,.35,0); candle(4.6,2.5,.8);
    table(-3.6,8,2.6,1.3,.8); chair(-3.6,6.9,0); chair(-3.6,9.1,Math.PI); candle(-3.6,8,.8);
    wardrobe(wx(-1,.55),8.5,1,0);
    bed(wx(-1,1.4),11.5,-1,0,-1,pick([0x3a2a4a,0x1a3a3a,0x4a2a1a]));
    clock(wx(1,.4),8,-1,0);
    wardrobe(wx(1,.55),11.5,-1,0);
    dresser(-4.5,hd-.8,0,-1); clue(2,-4.5,1.28,hd-.8,.5,.05,.4,0);
    wardrobe(5.5,hd-.55,0,-1);
    crate(wx(-1,.8),-hd+.8,.8,.3); crate(wx(1,.9),-hd+.8,.7,.8);
    painting(1,wx(-1,.05),3.1,-5.8,ryOf(-1),1,1.25);
    painting(2,wx(1,.05),3.1,-7.2,ryOf(1),1,1.25);
    painting(0,-4.5,2.3,hd-.05,Math.PI,1,1.25);
    windowAt(wx(-1,.06),2.4,1.5,ryOf(-1)); windowAt(wx(-1,.06),2.4,5.5,ryOf(-1));
    windowAt(wx(1,.06),2.4,-3.5,ryOf(1)); windowAt(wx(1,.06),2.4,.5,ryOf(1));
    windowAt(-7.5,2.4,-hd+.06,0); windowAt(7.5,2.4,-hd+.06,0);
    windowAt(3.2,2.4,hd-.06,Math.PI); windowAt(8.5,2.4,hd-.06,Math.PI);
    sconceMesh(wx(-1,.1),3.5,ryOf(-1)); sconceMesh(wx(1,.1),-1.5,ryOf(1));
    break;}

  // ===== KHU 3: SÂN BÓNG — vạch sân, hai khung thành, ghế dự bị, cột đèn sát hàng rào, bụi cây, bàn bóng bàn =====
  case 2:{
    sconceL[1].color.set(0xdfe9ff);
    sconceL[0].position.set(-hw+1.5,2.2,-4); sconceL[1].position.set(hw-1.5,2.2,6);
    const lines=new THREE.Mesh(new THREE.PlaneGeometry(18,14),new THREE.MeshStandardMaterial({map:pitchTex(),transparent:true,depthWrite:false,roughness:1,polygonOffset:true,polygonOffsetFactor:-2}));
    lines.rotation.x=-Math.PI/2; lines.position.set(0,.025,0); room.add(lines);          // vạch kẻ sân 18m x 14m
    const goalM=M(0xeef0f0), netG=new THREE.MeshBasicMaterial({color:0xcfd6da,transparent:true,opacity:.22,side:THREE.DoubleSide,depthWrite:false});
    const goal=sg=>{ const gx=sg*9, bx=gx+sg*1.3;                                        // khung thành (rộng 4,4m, cao 2,2m) + lưới
      [-2.2,2.2].forEach(zz=>{cyl(.06,.06,2.2,8,goalM,gx,1.1,zz,null,false);cyl(.05,.05,1.9,6,goalM,bx,.95,zz,null,false);box(1.3,.08,.08,goalM,gx+sg*.65,1.9,zz,null,false);});
      box(.12,.12,4.5,goalM,gx,2.2,0,null,false); box(.08,.08,4.5,goalM,bx,1.9,0,null,false);
      const nb=new THREE.Mesh(new THREE.PlaneGeometry(4.4,1.9),netG); nb.rotation.y=Math.PI/2; nb.position.set(bx,.95,0); room.add(nb);
      [-2.2,2.2].forEach(zz=>{const ns=new THREE.Mesh(new THREE.PlaneGeometry(1.3,1.9),netG); ns.position.set(gx+sg*.65,.95,zz); room.add(ns);});
      const nt=new THREE.Mesh(new THREE.PlaneGeometry(1.3,4.4),netG); nt.rotation.x=-Math.PI/2; nt.position.set(gx+sg*.65,1.9,0); room.add(nt);
      addObs(gx+sg*.65,0,1.5,4.7); };
    goal(-1); goal(1);
    sofa(-3.6,-8.7,0,1); clue(0,-3.6,.56,-8.7,.5,.08,.35,0);                             // hai băng ghế dự bị; manh mối đặt trên ghế
    sofa(3.6,-8.7,0,1);  clue(1,3.6,.56,-8.7,.5,.08,.35,0);
    barrel(-6.2,-8.7);
    dresser(wx(-1,.8),5,1,0); clue(2,wx(-1,.8),1.28,5,.5,.05,.4,0);                      // bồn hoa cạnh sân
    wardrobe(wx(1,.55),-1.5,-1,0); wardrobe(wx(1,.55),5.5,-1,0); wardrobe(wx(-1,.55),-5,1,0);   // bụi cây ven hàng rào (chỗ trốn)
    bed(wx(-1,1.4),8,-1,0,-1,0x2a4a5a);                                                  // bàn bóng bàn (chui xuống gầm)
    wardrobe(5,hd-.55,0,-1);
    pillar(9.3,-8.6); pillar(9.3,9);
    break;}

  // ===== KHU 4: VƯỜN CÂY PHƯỢNG — hàng cây, thùng rác, bàn ghế đá =====
  case 3:{
    sconceL[0].position.set(-6,2.4,-7); sconceL[1].position.set(6,2.4,5);
    [-10,-3.5,3,9.5].forEach(z=>[-4.5,4.5].forEach(x=>pillar(x,z)));
    wardrobe(wx(-1,.55),-6,1,0);
    bed(wx(-1,1.4),.5,-1,0,-1,0x3a2a1a);
    table(-9.6,6.5,1.2,1.2,.9); clue(2,-9.6,.98,6.5,.5,.08,.35,0); candle(-9.2,6,.94);
    shelf(wx(-1,.3),-11.5,1,0,3); shelf(wx(1,.3),-12,-1,0,3);
    wardrobe(wx(1,.55),9,-1,0);
    crate(8.5,-6.5,.9,.2); clue(0,8.5,.95,-6.5,.5,.08,.35,0);
    table(-8,-9,1.4,1.4,.9); clue(1,-8,.98,-9,.5,.08,.35,0);
    [[-9.8,-14.6],[-8.8,-14.8],[9.8,-14.4],[8.8,-14.7],[-9.6,13.6],[-8.5,14.4],[9.6,14.2],[-7.5,10.5],[7.8,1.5],[7.2,-2.5]].forEach(p=>barrel(p[0],p[1]));
    crate(-8,12.3,.9,.5); crate(8.5,12,.9,.2); crate(7.6,-9.5,.8,.7); crate(-7.5,3.5,.8,.1);
    [-11,-4,3,10].forEach(z=>{windowAt(wx(-1,.06),3.3,z,ryOf(-1),2,.6);windowAt(wx(1,.06),3.3,z,ryOf(1),2,.6);});
    windowAt(-6.5,3.2,-hd+.06,0,2,.6); windowAt(6.5,3.2,-hd+.06,0,2,.6);
    sconceMesh(wx(-1,.1),-3,ryOf(-1)); sconceMesh(wx(1,.1),4,ryOf(1));
    painting(1,3.6,2.2,-hd+.05,0,1,1.25);
    break;}

  // ===== KHU 5: CỔNG TRƯỜNG — hai hàng cây phượng, tượng đài, cổng thoát =====
  case 4:{
    [-11,-4,3,10].forEach(z=>[-5.5,5.5].forEach(x=>pillar(x,z)));
    const statue=(x,z)=>{ if(inB(x,z,1.3)) return; box(1,.6,1,stone,x,.3,z);cyl(.28,.4,1.9,10,M(0x2a2a2e),x,1.55,z);
      const h2=new THREE.Mesh(new THREE.SphereGeometry(.24,12,10),M(0x2a2a2e));h2.position.set(x,2.65,z);h2.castShadow=true;room.add(h2);addObs(x,z,1,1);};
    statue(-3.6,-hd+1.3); statue(3.6,-hd+1.3);
    wardrobe(wx(-1,.55),-8,1,0);
    table(wx(-1,1.6),0,1.2,2.4,.8); clue(0,wx(-1,1.6),.88,0,.5,.08,.35,0); candle(wx(-1,1.6),-.9,.8);
    bed(wx(-1,1.4),6,-1,0,-1,0x4a1a1a);
    sofa(wx(-1,.9),12.5,1,0,0x3a1a2a);
    fireplace(wx(1,.45),-hd+2.4,-1,0);
    dresser(wx(1,.8),-1,-1,0); clue(1,wx(1,.8),1.28,-1,.5,.05,.4,0);
    wardrobe(wx(1,.55),6,-1,0);
    bed(wx(1,1.4),13,1,0,-1,0x1a3a4a);
    wardrobe(6,hd-.55,0,-1); paintClue(2,-3);
    [-12,-4,3,9].forEach(z=>windowAt(wx(-1,.06),2.1,z,ryOf(-1),2.4,2.6));
    [-9,-4,3,9].forEach(z=>windowAt(wx(1,.06),2.1,z,ryOf(1),2.4,2.6));
    windowAt(-8.5,2.1,-hd+.06,0,2.4,2.6); windowAt(8.5,2.1,-hd+.06,0,2.4,2.6);
    windowAt(-8,2.1,hd-.06,Math.PI,2.4,2.6); windowAt(9.5,2.1,hd-.06,Math.PI,2.4,2.6);
    sconceMesh(wx(-1,.1),-6,ryOf(-1)); sconceMesh(wx(1,.1),-6.5,ryOf(1));
    break;}
  }
  {const RT=mulberry(gameSeed+door*131+5);                       // cây rải thêm ngoài sân, tránh đồ đã có và lối ra/vào
    const free=(x,z)=>!obstacles.some(b=>x>b.x1-2.2&&x<b.x2+2.2&&z>b.z1-2.2&&z<b.z2+2.2);
    const nT=Math.floor(RW*RD/110);
    for(let k=0,t=0;k<nT*6&&t<nT;k++){
      const x=(RT()-.5)*(RW-5), z=(RT()-.5)*(RD-10);
      if(Math.abs(x)<3.2&&Math.abs(z)>hd-9) continue;           // chừa lối ra/vào cổng
      if(lay===2&&Math.abs(x)<11&&Math.abs(z)<9) continue;      // chừa sân bóng
      if(!free(x,z)) continue;
      pillar(x,z); t++; } }
  sconceMesh(-1.9,-hd+.1,0); sconceMesh(1.9,-hd+.1,0);

  // vết máu, dấu tay, chữ viết bằng máu, giấy rơi
  for(let i=0;i<4;i++) decal(bloodTex(),rnd(1.2,2.2),rnd(1.2,2.2),rnd(-hw+3,hw-3),.014+i*.001,rnd(-hd+4,hd-4),0,-Math.PI/2);
  decal(handTex(),.9,.9,-5.3,1.4,-hd+.02,0);
  decal(handTex(),.9,.9,5.3,1.4,-hd+.02,0);
  decal(msgTex(MSG[lay]),3.0,.6,0,3.65,-hd+.02,0);
  const paperM=new THREE.MeshStandardMaterial({color:0xcfc6a8,roughness:1});
  for(let i=0;i<14;i++){const p=new THREE.Mesh(new THREE.PlaneGeometry(.28,.38),paperM);
    p.rotation.set(-Math.PI/2,0,rnd(0,6.3));p.position.set(rnd(-hw+2,hw-2),.02+i*.0005,rnd(-hd+3,hd-3));room.add(p);}
  // ghế đổ
  const tc=new THREE.Group();tc.position.set(-2*m,0.2,RD*0.22);tc.rotation.set(0.1,rnd(0,3),1.45);room.add(tc);
  box(.5,.05,.5,woodDark,0,0,0,tc,false);box(.5,.6,.05,woodDark,0,.3,-.22,tc,false);

  // đôi mắt trong bóng tối
  const eyeMat=new THREE.MeshBasicMaterial({color:0xff2020});
  const spotsE=[[-hw+.6,3.5,-hd+3],[hw-.6,3.5,-hd+3],[-hw+.6,3.6,hd-3],[hw-.6,3.6,hd-3],[0,3.7,-hd+.6],[-hw+.6,3.3,0],[hw-.6,3.3,-2],[0,3.7,hd-.6]];
  const nW=Math.min(2+door,spotsE.length);
  for(let i=0;i<nW;i++){const s=spotsE[(i*3+door)%spotsE.length]; if(inB(s[0],s[2],1.2)) continue; const gp=new THREE.Group();gp.position.set(s[0],s[1],s[2]);
    [-0.2,0.2].forEach(dx=>{const e=new THREE.Mesh(new THREE.SphereGeometry(.07,8,6),eyeMat);e.scale.set(1.4,.8,.5);e.position.x=dx;gp.add(e);});
    room.add(gp);watchers.push({g:gp,t:rnd(0,20),off:rnd(0,6)});}
  doorOpen=(door<DOORS.length-1);      // cổng giữa các khu luôn mở; cổng thoát (khu cuối) khóa tới khi đủ mảnh ghép
  resetDust();
}
function refreshClues(){
  inter.forEach(o=>{ if(o.kind==='clue' && solved[o.idx]){
    o.mat.color.set(0x55ff88); o.mat.emissive.set(0x22aa55); o.L.color.set(0x55ff88); }});
}

// ---------- Âm thanh ----------
let AC, droneG; const ac=()=>AC||(AC=new (window.AudioContext||window.webkitAudioContext)());
function tone(f,d,type,v,f2){try{const a=ac(),o=a.createOscillator(),g=a.createGain();o.type=type||'sine';
  o.frequency.setValueAtTime(f,a.currentTime);if(f2)o.frequency.exponentialRampToValueAtTime(f2,a.currentTime+d);
  g.gain.setValueAtTime(v||.15,a.currentTime);g.gain.exponentialRampToValueAtTime(.001,a.currentTime+d);
  o.connect(g).connect(a.destination);o.start();o.stop(a.currentTime+d);}catch(e){}}
function noise(d,v){try{const a=ac(),n=Math.floor(a.sampleRate*d),b=a.createBuffer(1,n,a.sampleRate),x=b.getChannelData(0);
  for(let i=0;i<n;i++)x[i]=(Math.random()*2-1)*(1-i/n);const s=a.createBufferSource(),g=a.createGain();
  g.gain.value=v;s.buffer=b;s.connect(g).connect(a.destination);s.start();}catch(e){}}
const sGood=()=>{tone(523,.18,'triangle',.16);setTimeout(()=>tone(784,.18,'triangle',.16),110);setTimeout(()=>tone(1047,.4,'triangle',.14),230);};
const sBad=()=>{tone(220,.5,'square',.14,90);setTimeout(()=>tone(150,.5,'square',.14,60),140);noise(.35,.2);};
function scream(){
  try{const a=ac(),t0=a.currentTime;
    const mk=(type,f0,f1,vol,dur)=>{const o=a.createOscillator(),g=a.createGain();o.type=type;
      o.frequency.setValueAtTime(f0,t0);o.frequency.exponentialRampToValueAtTime(f1,t0+.35);
      const lfo=a.createOscillator(),lg=a.createGain();lfo.frequency.value=11;lg.gain.value=f1*.08;lfo.connect(lg);lg.connect(o.frequency);lfo.start(t0);lfo.stop(t0+dur);
      g.gain.setValueAtTime(.0001,t0);g.gain.exponentialRampToValueAtTime(vol,t0+.04);g.gain.setValueAtTime(vol,t0+dur*.6);g.gain.exponentialRampToValueAtTime(.001,t0+dur);
      const ws=a.createWaveShaper(),c=new Float32Array(256);for(let i=0;i<256;i++){c[i]=Math.tanh((i/128-1)*4);}ws.curve=c;
      o.connect(ws);ws.connect(g);g.connect(a.destination);o.start(t0);o.stop(t0+dur);};
    mk('sawtooth',300,1250,.35,2.3); mk('square',450,1800,.16,2.1); mk('sawtooth',90,240,.3,2.0);
    noise(1.8,.5); tone(40,1.2,'sine',.6,25);
  }catch(e){}
}
let amb=false;
function ambience(){
  try{const a=ac(); if(a.resume)a.resume(); if(amb)return; amb=true;
    const mk=(f,type,vol)=>{const o=a.createOscillator(),g=a.createGain(),lp=a.createBiquadFilter();o.type=type;o.frequency.value=f;
      lp.type='lowpass';lp.frequency.value=170;g.gain.value=vol;o.connect(lp);lp.connect(g);g.connect(a.destination);o.start();return g;};
    const g1=mk(46,'sawtooth',.05); mk(49.3,'sawtooth',.04);
    const lfo=a.createOscillator(),lg=a.createGain();lfo.frequency.value=.13;lg.gain.value=.03;lfo.connect(lg);lg.connect(g1.gain);lfo.start();
    const n=a.sampleRate*3,b=a.createBuffer(1,n,a.sampleRate),x=b.getChannelData(0);for(let i=0;i<n;i++)x[i]=Math.random()*2-1;
    const s=a.createBufferSource();s.buffer=b;s.loop=true;const bp=a.createBiquadFilter();bp.type='bandpass';bp.frequency.value=400;bp.Q.value=.6;
    const wg=a.createGain();wg.gain.value=.022;s.connect(bp);bp.connect(wg);wg.connect(a.destination);s.start();
    const od=a.createOscillator(),dl=a.createBiquadFilter();droneG=a.createGain();droneG.gain.value=0;od.type='sawtooth';od.frequency.value=62;
    dl.type='lowpass';dl.frequency.value=260;od.connect(dl);dl.connect(droneG);droneG.connect(a.destination);od.start();
    stormAudioLoad(a); stepAudioLoad(a); ghostAudioLoad(a); catchAudioLoad(a); sirenAudioLoad(a);
  }catch(e){}
}
// ---------- Tiếng khi ma bắt được (faaahhhh.mp3, ~1,7 giây; file rất to nên giảm còn CATCH_VOL) ----------
const CATCH_SRC="__CATCH__", CATCH_VOL=.6;
let catchBuf=null, catchLoading=false;
function catchAudioLoad(a){ if(!CATCH_SRC||catchBuf||catchLoading) return; catchLoading=true; decodeBuf(a,CATCH_SRC).then(b=>{catchBuf=b;}).catch(()=>{}); }
function catchSound(){
  if(!catchBuf) return false;
  try{ const a=ac(); if(a.state==='suspended'&&a.resume) a.resume();
    const g=a.createGain(), s=a.createBufferSource(); s.buffer=catchBuf; g.gain.value=CATCH_VOL;
    s.connect(g).connect(a.destination); s.start(); return true; }catch(e){ return false; }
}
// ---------- Tiếng ma (tiengma.mp3): phát 1 lần ~6 giây lúc ma xuất hiện, vào nhỏ dần rồi tắt ----------
const GHOST_SRC="__GHOST__", GH_DUR=6.2, GH_VOL=.8;
let ghBuf=null, ghLoading=false, ghSrc=null, ghGain=null;
function ghostAudioLoad(a){ if(!GHOST_SRC||ghBuf||ghLoading) return; ghLoading=true; decodeBuf(a,GHOST_SRC).then(b=>{ghBuf=b;}).catch(()=>{}); }
function ghostSoundStop(){
  try{ if(ghSrc&&ghGain){ const a=ac(),t=a.currentTime; ghGain.gain.cancelScheduledValues(t); ghGain.gain.setValueAtTime(ghGain.gain.value,t); ghGain.gain.linearRampToValueAtTime(0,t+.5); ghSrc.stop(t+.55); } }catch(e){}
  ghSrc=null; ghGain=null;
}
function ghostSound(){
  if(!ghBuf) return false;
  try{
    ghostSoundStop();
    const a=ac(); if(a.state==='suspended'&&a.resume) a.resume();
    const t=a.currentTime, g=a.createGain(), s=a.createBufferSource(); s.buffer=ghBuf;
    g.gain.setValueAtTime(0,t); g.gain.linearRampToValueAtTime(GH_VOL,t+.2);
    g.gain.setValueAtTime(GH_VOL,t+GH_DUR-1); g.gain.linearRampToValueAtTime(0,t+GH_DUR);
    s.connect(g).connect(a.destination); s.start(t,0,GH_DUR); ghSrc=s; ghGain=g; return true;
  }catch(e){ return false; }
}
// ---------- Tiếng còi kinh dị (siren-head-sounds-new.mp3, ~18 giây): lâu lâu vang lên từ xa, nhỏ dần vào/ra, tạm dừng khi ma xuất hiện ----------
const SIREN_SRC="__SIREN__", SIREN_VOL=.5, SIREN_DUR=18.2;
let sirBuf=null, sirLoading=false, sirSrc=null, sirGain=null, nextSiren=70+Math.random()*60;
function sirenAudioLoad(a){ if(!SIREN_SRC||sirBuf||sirLoading) return; sirLoading=true; decodeBuf(a,SIREN_SRC).then(b=>{sirBuf=b;}).catch(()=>{}); }
function sirenStop(){
  try{ if(sirSrc&&sirGain){ const a=ac(),t=a.currentTime; sirGain.gain.cancelScheduledValues(t); sirGain.gain.setValueAtTime(sirGain.gain.value,t); sirGain.gain.linearRampToValueAtTime(0,t+.6); sirSrc.stop(t+.65); } }catch(e){}
  sirSrc=null; sirGain=null;
}
function sirenPlay(){
  if(!sirBuf) return false;
  try{
    sirenStop();
    const a=ac(); if(a.state==='suspended'&&a.resume) a.resume();
    const t=a.currentTime, d=Math.min(SIREN_DUR,sirBuf.duration), g=a.createGain(), lp=a.createBiquadFilter(), s=a.createBufferSource(); s.buffer=sirBuf;
    lp.type='lowpass'; lp.frequency.value=5000;                      // nghe như vọng lại từ rất xa
    g.gain.setValueAtTime(0,t); g.gain.linearRampToValueAtTime(SIREN_VOL,t+2); g.gain.setValueAtTime(SIREN_VOL,t+d-3); g.gain.linearRampToValueAtTime(0,t+d);
    s.connect(lp); lp.connect(g); g.connect(a.destination); s.start(t,0,d); sirSrc=s; sirGain=g;
    s.onended=()=>{ if(sirSrc===s){sirSrc=null;sirGain=null;} };
    return true;
  }catch(e){ return false; }
}
function sirenUpdate(dt){            // gọi mỗi khung hình: mỗi ~1,5-3,5 phút còi vang một lần khi đang chơi và không có ma
  if(state!=='play'||modalOpen||transitioning||intro.on||gh.phase!=='idle'){ if(sirSrc&&(state!=='play'||gh.phase!=='idle')) sirenStop(); return; }
  if(sirSrc) return;
  nextSiren-=dt; if(nextSiren<=0){ nextSiren=90+Math.random()*120; sirenPlay(); }
}
// ---------- Bước chân thật (cắt từ tiengchan.mp3); chạy -> nhanh hơn + cao giọng hơn ----------
const STEP_SRC="__STEP__", SCLIPS=__SCLIPS__, STEP_REF=.3, STEP_VOL=1.0;   // SCLIPS: [giây bắt đầu, độ to]
let stBuf=null, stepLoading=false, lastStep=-1;
function stepAudioLoad(a){ if(!STEP_SRC||stBuf||stepLoading) return; stepLoading=true; decodeBuf(a,STEP_SRC).then(b=>{stBuf=b;}).catch(()=>{}); }
function footstep(run){
  if(!stBuf){ noise(.07,.08); tone(70,.09,'sine',.1,40); return; }   // chưa có file -> tiếng tổng hợp cũ
  try{
    const a=ac(); let i; do{ i=Math.floor(Math.random()*SCLIPS.length); }while(i===lastStep&&SCLIPS.length>1); lastStep=i;
    const c=SCLIPS[i], iv=run?.3:.46, rate=(run?1.18:1)*(1+(Math.random()-.5)*.06);
    const dur=Math.min(.5,iv*1.4*rate), wall=dur/rate, t=a.currentTime;
    const v=Math.max(.5,Math.min(2.5,STEP_REF/c[1]))*STEP_VOL*(run?1.1:1);   // cân lại độ to cho các bước đều nhau
    const g=a.createGain(), s=a.createBufferSource(); s.buffer=stBuf; s.playbackRate.value=rate;
    g.gain.setValueAtTime(0,t); g.gain.linearRampToValueAtTime(v,t+.004);
    g.gain.setValueAtTime(v,t+Math.max(.01,wall-.08)); g.gain.linearRampToValueAtTime(0,t+wall);
    s.connect(g).connect(a.destination); s.start(t,Math.max(0,c[0]-.01),dur);
  }catch(e){}
}
/*STORM-AUDIO-BEGIN*/
// ---------- Bão: mưa + sấm thật (cắt từ tiengsamset.mp3, tiếng nổ căn khớp tia chớp) ----------
const THUNDER_SRC="__THUNDER__", RAIN_SRC="__RAIN__";
const TCLIPS=__TCLIPS__;            // {n,k:'crack'|'roll',s:bắt đầu trong file,d:độ dài,c:thời điểm tiếng nổ trong clip}
const RAIN_VOL=.45;
let thBuf=null, rainBuf=null, thBus=null, rainG=null, swellG=null, rainWant=false, rainTgt=0, lastClip=-1, stormLoading=false;
function b64buf(u){const s=atob(u.slice(u.indexOf(',')+1)),b=new Uint8Array(s.length);for(let i=0;i<s.length;i++)b[i]=s.charCodeAt(i);return b.buffer;}
function decodeBuf(a,uri){return new Promise((ok,no)=>{try{const p=a.decodeAudioData(b64buf(uri),ok,no);if(p&&p.catch)p.catch(no);}catch(e){no(e);}});}
function stormAudioLoad(a){
  if(stormLoading) return; stormLoading=true;
  if(THUNDER_SRC&&TCLIPS.length) decodeBuf(a,THUNDER_SRC).then(b=>{thBuf=b;}).catch(()=>{});
  if(RAIN_SRC) decodeBuf(a,RAIN_SRC).then(b=>{rainBuf=b;rainStart(a);}).catch(()=>{});
}
function rainStart(a){
  if(rainG||!rainBuf) return;
  rainG=a.createGain(); rainG.gain.value=rainTgt; swellG=a.createGain();
  const lp=a.createBiquadFilter(); lp.type='lowpass'; lp.frequency.value=7000; lp.Q.value=.4;      // nghe qua cửa sổ: bớt chói
  lp.connect(swellG); swellG.connect(rainG); rainG.connect(a.destination);
  [[0,-.55],[rainBuf.duration*.43,.55]].forEach(p=>{                      // 2 lớp lệch pha chia trái/phải cho có độ rộng
    const s=a.createBufferSource(); s.buffer=rainBuf; s.loop=true;
    if(a.createStereoPanner){const pn=a.createStereoPanner(); pn.pan.value=p[1]; s.connect(pn); pn.connect(lp);} else s.connect(lp);
    s.start(0,p[0]);
  });
}
function rainUpdate(){                // gọi mỗi khung hình: mưa chỉ nghe khi đang chơi, nhỏ lại khi ma xuất hiện
  const want=(state==='play'||state==='scare'||state==='menu'), tgt=want?(gh.phase!=='idle'&&state!=='menu'?RAIN_VOL*.55:RAIN_VOL*(state==='menu'?.85:1)):0;
  rainWant=want;
  if(tgt!==rainTgt){rainTgt=tgt; if(rainG&&AC) rainG.gain.setTargetAtTime(tgt,AC.currentTime,.7);}
}
function rainSwell(near){             // mưa/gió dâng nhẹ ngay lúc chớp, rồi dịu lại
  if(!swellG||!AC||!rainWant) return;
  const t=AC.currentTime; swellG.gain.setTargetAtTime(near?1.35:1.15,t,.12); swellG.gain.setTargetAtTime(1,t+1.4,.9);
}
function thunderBus(a){
  if(thBus) return thBus;
  const c=a.createDynamicsCompressor(); c.threshold.value=-10; c.knee.value=10; c.ratio.value=6; c.attack.value=.003; c.release.value=.3;
  c.connect(a.destination); return thBus=c;
}
// delay = số giây từ lúc tia chớp tới lúc tiếng NỔ vang lên. Lên lịch bằng đồng hồ âm thanh nên tiếng nổ rơi đúng mốc.
// Trả về false nếu chưa có file (khi đó dùng tiếng tổng hợp cũ).
function thunderPlay(delay,near){
  if(!thBuf||!(state==='play'||state==='scare'||state==='menu')) return false;
  try{
    const a=ac(); if(a.state==='suspended'&&a.resume) a.resume();
    // gần: clip nổ gắt. xa: ưu tiên clip sấm cuộn, thỉnh thoảng dùng clip nổ nhưng làm mờ
    let pool=[]; TCLIPS.forEach((c,i)=>{ if(i===lastClip) return; if(near?c.k==='crack':(c.k==='roll'||Math.random()<.35)) pool.push(i); });
    if(!pool.length) pool=TCLIPS.map((c,i)=>i);
    const i=pool[Math.floor(Math.random()*pool.length)]; lastClip=i; const c=TCLIPS[i];
    const now=a.currentTime; let when=now+delay-c.c, off=c.s, dur=c.d;
    if(when<now){const sk=now-when; off+=sk; dur-=sk; when=now;}          // delay quá ngắn: bỏ bớt đoạn lót đầu clip
    const src=a.createBufferSource(); src.buffer=thBuf;
    const lp=a.createBiquadFilter(); lp.type='lowpass'; lp.frequency.value=near?14000:Math.max(1400,3600-delay*900);   // càng xa càng trầm
    const g=a.createGain(); g.gain.value=near?.95:Math.max(.38,.8-delay*.16);
    src.connect(lp); lp.connect(g); g.connect(thunderBus(a)); src.start(when,off,dur);
    return true;
  }catch(e){return false;}
}
/*STORM-AUDIO-END*/
const WH=['đừng quay lại...','cô đang nhìn em','phía sau em','giờ kiểm tra bắt đầu','chạy đi...','em không một mình','cô biết em ở đây','em trả lời sai rồi...'];
function whisper(txt){const w=$('whisper');w.textContent=txt||WH[Math.floor(Math.random()*WH.length)];
  w.style.left=(8+Math.random()*60)+'%';w.style.top=(15+Math.random()*60)+'%';w.style.opacity=.8;setTimeout(()=>w.style.opacity=0,2400);noise(1.2,.05);}

// ---------- Tiện ích UI ----------
function banner(t,ms){const b=$('banner');b.textContent=t;b.style.opacity=1;clearTimeout(bannerT);
  bannerT=setTimeout(()=>b.style.opacity=0,ms||2500);}
const PIECES=15;      // tổng số mảnh ghép = 5 khu x 3 câu
function totalPieces(){let n=solved.filter(Boolean).length; rooms.forEach((r,j)=>{ if(r&&j!==door) n+=r.solved.filter(Boolean).length; }); return n;}
function updateHud(){
  $('lockbtn').style.display=(state==='play'&&!touchMode)?'block':'none';
  $('tui').style.display=(touchMode&&state==='play')?'block':'none';
  $('lowhp').className=(hp===1&&state==='play')?'pulse':'';
  if(door>=DOORS.length) return;
  const D=DOORS[door];
  $('dn').textContent=D.name;
  $('hp').innerHTML='MẠNG '+'<span style="color:#d01a1a">&#9829;</span>'.repeat(Math.max(hp,0))+'<span style="color:#4a4a4a">&#9829;</span>'.repeat(MAX_HP-Math.max(hp,0));
  $('hn').textContent='Gợi ý: '+hints;
  {const n=totalPieces(); $('ks').textContent='Mảnh ghép: '+'■'.repeat(n)+'□'.repeat(PIECES-n)+'  '+n+'/'+PIECES;}
  $('ot').textContent=keySolved?('Đã giải mã! Chạy tới cổng thoát ở: '+DOORS[DOORS.length-1].name):(totalPieces()>=PIECES?'Đủ mảnh ghép! Bấm P để đoán từ khóa':'Bấm P xem bức tranh bí ẩn');
  $('pz').style.display=(state==='play')?'block':'none';
  $('lockbtn').className=shiftLock?'on':''; $('lockbtn').textContent='SL';
  $('lockbtn').style.display=(state==='play'&&!touchMode)?'block':'none';
  $('lowhp').className=(hp===1&&state==='play')?'pulse':'';
}
// Shift Lock kiểu Roblox: chuột bị khóa ở GIỮA màn hình (con trỏ ẩn, hiện tâm ngắm), xoay camera không cần bấm chuột.
// Bấm Shift (hoặc nút ) để bật/tắt. Nếu trình duyệt chặn khóa chuột trong khung nhúng -> dùng nút TAB MỚI mở game ở tab mới.
const inFrame=(function(){try{return window.top!==window;}catch(e){return true;}})();
const isLocked=()=>document.pointerLockElement===canvas;
function lockFail(){
  if(!lockEver) lockBlocked=true;        // chưa từng khóa được -> khung nhúng bị chặn
  setCursor();
  if(!shiftLock||state!=='play'||modalOpen||gh.phase!=='idle') return;   // không đè lên cảnh báo của ma
  const now=performance.now(); if(now-lockMsgT<3500) return; lockMsgT=now;  // promise reject + pointerlockerror -> chỉ báo 1 lần
}
function lockPtr(){try{const p=canvas.requestPointerLock();if(p&&p.catch)p.catch(lockFail);}catch(e){lockFail();}}
function unlockPtr(){expectUnlock=true;try{document.exitPointerLock();}catch(e){}setTimeout(()=>{expectUnlock=false;},250);}
const fakeLock=()=>shiftLock&&!isLocked()&&lockBlocked;
function setCursor(){
  const want=shiftLock&&state==='play'&&!modalOpen;
  const hide=want&&(isLocked()||lockBlocked);
  canvas.style.cursor=hide?'none':'default';
  $('cross').className=hide?'lk':'';
}
function syncLock(){
  const want=shiftLock&&state==='play'&&!modalOpen;
  if(want&&!isLocked()) lockPtr();
  else if(!want&&isLocked()) unlockPtr();
  setCursor();
  if(state!=='menu') updateHud();
}
function toggleSL(){
  shiftLock=!shiftLock; lockFailShown=false; lockMsgT=0; dragging=false;
  banner(shiftLock?'Shift Lock: BẬT — chuột khóa ở giữa màn hình':'Shift Lock: TẮT — giữ chuột trái/phải và kéo để nhìn',1800);
  syncLock(); updateHud();
}
document.addEventListener('pointerlockchange',()=>{
  if(isLocked()){lockEver=true;lockBlocked=false;}
  else if(shiftLock&&!expectUnlock&&state==='play'&&!modalOpen){   // lỡ nhả chuột (Esc): giữ Shift Lock BẬT như Roblox
    banner('Chuột đã nhả. Bấm vào màn hình để khóa lại (Shift để tắt Shift Lock).',2600);}
  setCursor();
});
document.addEventListener('pointerlockerror',lockFail);

// grain
(function(){const gc=$('grain');gc.width=160;gc.height=90;const x=gc.getContext('2d');
  setInterval(()=>{const id=x.createImageData(160,90),d=id.data;for(let i=0;i<d.length;i+=4){const v=Math.random()*255;d[i]=d[i+1]=d[i+2]=v;d[i+3]=70;}x.putImageData(id,0,0);},70);})();

function damage(msg){
  hp--; shake=0.3; sBad();
  const f=$('flash'); f.style.background='#a00'; f.style.opacity=.75; setTimeout(()=>f.style.opacity=0,350);
  banner(msg+'  -1 mạng',2500); updateHud();
  if(hp<=0) gameOver('Bạn gục ngã ở '+DOORS[door].name+'...\nBạn phải tìm lại các mảnh ghép từ đầu.');
}
function gameOver(msg){
  state='over'; closeModal(true); syncLock(); updateHud(); parkGhost();
  camera.fov=72; camera.updateProjectionMatrix(); $('scare').style.display='none'; $('flash').style.opacity=0;
  $('overmsg').style.whiteSpace='pre-line'; $('overmsg').textContent=msg;
  $('over').style.display='flex';
}

// ---------- Modal ----------
// Texture giấy nhàu cho bảng câu hỏi (nếp gấp, mảng sáng/tối, vết ố, hạt)
(function(){
  const w=640,h=560,c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');
  const gr=g.createLinearGradient(0,0,w,h);gr.addColorStop(0,'#c6bba1');gr.addColorStop(.5,'#b5a98e');gr.addColorStop(1,'#a69a7d');
  g.fillStyle=gr;g.fillRect(0,0,w,h);
  for(let i=0;i<90;i++){const x=rnd(0,w),y=rnd(0,h);
    g.fillStyle=Math.random()<.5?'rgba(255,250,235,'+rnd(.03,.12)+')':'rgba(40,30,15,'+rnd(.03,.12)+')';
    g.beginPath();g.moveTo(x,y);for(let k=0;k<4;k++)g.lineTo(x+rnd(-100,100),y+rnd(-100,100));g.closePath();g.fill();}
  for(let i=0;i<26;i++){let x=rnd(0,w),y=rnd(0,h),a=rnd(0,6.3);const pts=[[x,y]];
    for(let k=0;k<5;k++){a+=rnd(-.6,.6);x+=Math.cos(a)*rnd(30,70);y+=Math.sin(a)*rnd(30,70);pts.push([x,y]);}
    [[0,0,'rgba(35,25,10,.30)'],[1.5,1.5,'rgba(255,250,235,.28)']].forEach(s=>{
      g.save();g.translate(s[0],s[1]);g.strokeStyle=s[2];g.lineWidth=1.3;g.beginPath();
      pts.forEach((p,k)=>k?g.lineTo(p[0],p[1]):g.moveTo(p[0],p[1]));g.stroke();g.restore();});}
  stains(g,w,h,10,.13); noiseFx(g,w,h,22);
  const vg=g.createRadialGradient(w/2,h/2,h*.25,w/2,h/2,w*.75);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(50,35,10,.4)');
  g.fillStyle=vg;g.fillRect(0,0,w,h);
  $('box').style.backgroundImage='url('+c.toDataURL('image/jpeg',.88)+')';
})();
const normKey=t=>(t||'').normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/đ/g,'d').replace(/Đ/g,'D').toUpperCase().replace(/[^A-Z0-9]/g,'');
function buildPuzImg(){
  const c=document.createElement('canvas'); c.width=500; c.height=300; puzImg=c; const g=c.getContext('2d');
  const gr=g.createLinearGradient(0,0,0,300); gr.addColorStop(0,'#2b3a5a'); gr.addColorStop(1,'#8aa0c0'); g.fillStyle=gr; g.fillRect(0,0,500,300);
  const pp=puz.p;
  if(pp.indexOf('data:')===0){ const im=new Image(); im.onload=()=>{ const r=Math.min(500/im.width,300/im.height), w=im.width*r, h=im.height*r;
      g.fillStyle='#111'; g.fillRect(0,0,500,300); g.drawImage(im,(500-w)/2,(300-h)/2,w,h); if(modalOpen&&modalMode==='puz') drawPuzzle(); }; im.src=pp; }
  else { g.font="230px 'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji',sans-serif"; g.textAlign='center'; g.textBaseline='middle'; g.fillText(pp,250,160); }
}
function drawPuzzle(){
  const c=$('pcv'); if(!c||!puzImg) return;
  const g=c.getContext('2d'), W=c.width, H=c.height, cols=5, rows=3, tw=W/cols, th=H/rows;
  const n=Math.min(15,totalPieces()), rev=new Set(tileOrder.slice(0,n));
  g.fillStyle='#120d09'; g.fillRect(0,0,W,H);
  for(let k=0;k<15;k++){ const cx=(k%cols)*tw, cy=Math.floor(k/cols)*th;
    if(rev.has(k)) g.drawImage(puzImg,cx,cy,tw,th,cx,cy,tw,th);
    else { g.fillStyle='#1e1610'; g.fillRect(cx+1,cy+1,tw-2,th-2); g.fillStyle='rgba(217,180,90,.28)'; g.font='bold 34px serif'; g.textAlign='center'; g.textBaseline='middle'; g.fillText('?',cx+tw/2,cy+th/2); } }
  g.strokeStyle='rgba(0,0,0,.65)'; g.lineWidth=2;
  for(let i=0;i<=cols;i++){g.beginPath();g.moveTo(i*tw,0);g.lineTo(i*tw,H);g.stroke();}
  for(let j=0;j<=rows;j++){g.beginPath();g.moveTo(0,j*th);g.lineTo(W,j*th);g.stroke();}
}
function showBlanks(){
  const t=normKey($('mi').value); let k=0, h='';
  for(const ch of puz.a){ if(ch===' '){h+='<span class="pg"></span>';continue;} h+='<span class="pc">'+(k<t.length?t[k]:'')+'</span>'; k++; }
  $('pbl').innerHTML=h;
}
function openPuzzle(){
  if(state!=='play'||modalOpen||intro.on||!puz) return;
  if(gh.phase!=='idle'){ banner('Không phải lúc này! Verity đang tới!',1500); return; }
  if(hidden) return;
  modalMode='puz'; $('box').classList.add('pic','pz');
  const n=Math.min(PIECES,totalPieces());
  $('mt').textContent='BỨC TRANH BÍ ẨN ('+n+'/'+PIECES+' mảnh)';
  $('mq').textContent=keySolved?'Bạn đã giải mã! Chạy tới cổng thoát.':'Đoán từ khóa của bức tranh rồi điền vào ô trống:';
  $('mpic').style.display='block'; $('mpic').innerHTML='<canvas id="pcv" width="500" height="300"></canvas>';
  $('pbl').style.display='flex'; $('opts').style.display='none'; $('b2').style.display='none';
  $('mi').style.display=''; $('mi').setAttribute('inputmode','text'); $('mi').placeholder='Nhập từ khóa'; $('b1').style.display=''; $('b1').textContent='Đoán';
  drawPuzzle(); showBlanks(); openModal();
}
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function openModal(){modalOpen=true;syncLock();$('modal').style.display='flex';$('fb').textContent='';
  if(modalMode==='code'||modalMode==='puz') setTimeout(()=>$('mi').focus(),30);}
function closeModal(silent){modalOpen=false;$('modal').style.display='none';$('mi').value='';keys={};$('box').classList.remove('pz');$('pbl').style.display='none';
  if(!silent) syncLock();}
function openQ(i){
  const q=DOORS[door].questions[i]; modalMode='q'; modalIdx=i;
  $('mt').textContent='Câu hỏi '+(i+1); $('mq').textContent=q.q;
  {const pc=$('mpic'); pc.innerHTML=''; pc.textContent=''; $('pbl').style.display='none'; $('box').classList.remove('pz');
   if(q.p){ pc.style.display='block'; $('box').classList.add('pic');
     if(q.p.indexOf('data:')===0){const im=document.createElement('img'); im.src=q.p; pc.appendChild(im);} else pc.textContent=q.p; }
   else { pc.style.display='none'; $('box').classList.remove('pic'); } }
  $('b2').style.display='inline-block';
  $('mi').style.display='none'; $('b1').style.display='none';
  optOrder=shuffle([0,1,2,3]); wrongSet={};            // q.o[0] là đáp án đúng
  const box=$('opts'); box.innerHTML=''; box.style.display='flex';
  optOrder.forEach((oi,k)=>{
    const b=document.createElement('button'); b.className='opt';
    const l=document.createElement('b'); l.textContent='ABCD'[k];
    const t=document.createElement('span'); t.textContent=q.o[oi];
    b.appendChild(l); b.appendChild(t); b.onclick=()=>choose(k); box.appendChild(b);
  });
  openModal(); if(hintShown[door+'-'+i]) $('fb').textContent=''+q.hint;
}
function verityAngry(){           // trả lời sai làm Verity nổi giận
  if(gh.phase==='idle') ghostTimer=Math.min(ghostTimer,5);
  else if(gh.phase==='hunt'&&!hidden){
    const dx=camera.position.x-gh.x, dz=camera.position.z-gh.z, d=Math.hypot(dx,dz)||1, st=Math.min(2.5,Math.max(0,d-1.3));
    gh.x+=dx/d*st; gh.z+=dz/d*st; whisper('sai rồi...');
  }
}
function choose(k){
  if(!modalOpen||modalMode!=='q'||wrongSet[k]) return;
  const q=DOORS[door].questions[modalIdx];
  if(optOrder[k]===0){
    solved[modalIdx]=true; sGood(); closeModal(); refreshClues(); updateHud();
    {const n=totalPieces(); banner('Đúng! Nhặt được mảnh ghép '+n+'/'+PIECES+'\nBấm P (nút 🧩) để xem tranh & đoán từ khóa',3200);}
  } else {
    wrongSet[k]=true; $('opts').children[k].classList.add('bad'); $('fb').textContent='Sai rồi!';
    verityAngry(); damage('Verity trừng phạt câu trả lời sai!');
  }
}
function openCode(){
  const D=DOORS[door]; modalMode='code';
  $('mpic').style.display='none'; $('box').classList.remove('pic'); $('mt').textContent='Ổ khóa'; $('mq').textContent='Nhập mật mã '+D.questions.length+' chữ số. '+D.order_text;
  $('b2').style.display='none'; $('opts').style.display='none'; $('mi').style.display=''; $('b1').style.display=''; openModal();
}
function submit(){
  if(modalMode==='puz'){
    const t=normKey($('mi').value), a=normKey(puz.a);
    if(t.length!==a.length){ $('fb').textContent='Phải đủ '+a.length+' chữ cái để khớp các ô trống!'; return; }
    if(t===a){ keySolved=true; closeModal(); sGood(); tone(70,1.2,'sawtooth',.12,40);
      banner('ĐÚNG RỒI! Từ khóa: '+puz.a+'\nChạy tới cổng thoát ở '+DOORS[DOORS.length-1].name+'!',4200); updateHud(); }
    else { $('fb').textContent='Sai từ khóa!'; $('mi').value=''; showBlanks(); verityAngry(); damage('Đoán sai từ khóa, Verity nghe thấy!'); }
    return;
  }
  if(modalMode!=='code') return;
  const v=$('mi').value; if(!v.trim()) return;
  const D=DOORS[door];
  const code=D.order.map(i=>D.questions[i].digit).join('');
  if(v.trim()===code){ closeModal(); doorOpen=true; setTimeout(prebuildNext,60); sGood(); tone(70,1.2,'sawtooth',.12,40); banner('Cửa đã mở! Hãy bước vào ánh sáng...',3000); }
  else { $('fb').textContent='Mật mã sai!'; $('mi').value=''; verityAngry(); damage('Ổ khóa kêu inh ỏi, Verity nghe thấy!'); }
}
$('b1').onclick=submit; $('b3').onclick=()=>closeModal();
$('b2').onclick=()=>{
  const k=door+'-'+modalIdx, q=DOORS[door].questions[modalIdx];
  if(hintShown[k]){$('fb').textContent=''+q.hint;return;}
  if(hints<=0){$('fb').textContent='Hết lượt gợi ý!';return;}
  hints--; hintShown[k]=true; $('fb').textContent=''+q.hint; updateHud();
};
$('mi').addEventListener('keydown',e=>{if(e.key==='Enter')submit();});
$('mi').addEventListener('input',()=>{if(modalMode==='puz')showBlanks();});
$('pz').onclick=()=>{openPuzzle();};

// ---------- Luồng game ----------
function startRoom(){
  solved=[false,false,false]; buildRoom(); hidden=false; spot.intensity=2.1; $('hide').style.display='none';
  camera.position.set(0,1.6,RD/2-2); yaw=0; pitch=0; lampF=1; dark=0; blackT=0; nextBlack=40+Math.random()*30; flashOn=true; shDur=0; shadowG.visible=false; nextShadow=25+Math.random()*50; parkGhost();
  ghostTimer=(door===0?24:16)+Math.random()*16; updateHud(); setTimeout(prebuildNext,60);
  const rb=[DOORS[door].name.toUpperCase()+'\n'+DOORS[door].intro+'\nTìm đủ '+PIECES+' mảnh ghép rải khắp trường rồi chạy ra cổng thoát!',5600];
  if(introWant){ introWant=false; introSnd=0; introBegin(); intro.banner=rb; } else banner(rb[0],rb[1]);
}
let inStory=false, storyTm=[];
function storyStop(){storyTm.forEach(clearTimeout); storyTm=[];}
function storyIntro(){            // bảng cốt truyện: tắt nhạc, hiệu ứng + âm thanh lúc chữ hiện ra
  storyStop(); try{musicStop();}catch(e){}
  const hit=()=>{try{tone(95,.6,'sine',.13,55); noise(.18,.07);}catch(e){}};
  $('sgo').disabled=true;
  try{noise(1,.1); tone(48,2.4,'sine',.24,28);}catch(e){}      // tiếng ngân trầm lúc bảng hiện
  storyTm.push(setTimeout(()=>{hit(); try{tone(1400,.5,'sine',.025,500);}catch(e){}},550));
  storyTm.push(setTimeout(()=>{hit(); try{tone(1250,.5,'sine',.025,420);}catch(e){}},2450));
  storyTm.push(setTimeout(()=>{$('sgo').disabled=false; $('sgo').focus(); try{tone(520,.5,'sine',.05,300);}catch(e){}},3500));
}
function showOnly(id){['menu','story','howto','settings','over','win'].forEach(i=>$(i).style.display=(i===id?'flex':'none'));
  inStory=(id==='story'); if(inStory) storyIntro(); else storyStop();}
let introWant=false;
function resetGame(){stam=100;tired=false;rollGame();introWant=true;musicStop();hp=MAX_HP;hints=HINTS0;door=0;hintShown={};state='play';ambience();playMusicStart();
  camera.fov=72;camera.updateProjectionMatrix();$('scare').style.display='none';
  showOnly(''); startRoom(); syncLock();}
function toMenu(){playMusicStop();state='menu';closeModal(true);syncLock();parkGhost();showOnly('menu');buildRoom();camera.position.set(0,1.6,RD/2-2);yaw=0;pitch=0;musicStart();}
// Trong khung Streamlit (chặn khóa chuột): bấm CHƠI -> mở game ở tab mới để Shift Lock chạy chuẩn. Bị chặn popup thì chơi tại chỗ.
$('start').onclick=()=>{
  if(inFrame){
    try{
      const w=window.open(URL.createObjectURL(new Blob([SRC],{type:'text/html'}))+'#fromframe','_blank');
      if(w){return;}
    }catch(e){}
  }
  showOnly('story');            // bảng cốt truyện trước khi vào game
};
// Tab mới do trang Streamlit mở ra: biến luôn tab cũ thành game (không còn tab thừa), rồi tự đóng tab mới này.
// Nếu trình duyệt không cho thì giữ tab mới, tab cũ để nguyên (không làm trống).
if(!inFrame&&location.hash==='#fromframe'&&window.opener){
  try{
    const top0=window.opener.top;
    top0.location.href=URL.createObjectURL(new Blob([SRC],{type:'text/html'}))+'#takeover';
    let n=0; const iv=setInterval(()=>{
      n++; let ok=false;
      try{ ok=top0.location.href.indexOf('#takeover')>0&&top0.document.readyState==='complete'&&!!top0.document.getElementById('start'); }catch(e){}
      if(ok){ clearInterval(iv); setTimeout(()=>{try{window.close();}catch(e){}},400); }
      else if(n>40) clearInterval(iv);    // ~6s không được -> thôi, giữ nguyên cả hai tab
    },150);
  }catch(e){}
}
function setRF(v){RF=!!v; saveNum('doors_rf',RF?1:0); $('rfchk2').checked=RF;}
$('rfchk2').onchange=()=>setRF($('rfchk2').checked); setRF(RF);
$('tomenu').onclick=toMenu; $('tomenu2').onclick=toMenu;
$('sgo').onclick=()=>{storyStop();resetGame();};
$('how').onclick=()=>showOnly('howto'); $('hback').onclick=()=>showOnly('menu');
// ----- Cài đặt đồ họa (kiểu Roblox: thanh trượt 1-10; 1-5 = Thấp, 6-10 = Cao) -----
function updateSettingsUI(){
  $('qr').value=Q;
  $('ql').textContent='Mức đồ họa: '+Q+' / 10 — '+(Q>=6?'CAO':'THẤP');
  $('qd').textContent=Q>=6
    ?'Cao: bóng đổ động, độ phân giải đầy đủ, nhiễu hạt phim và bụi bay. Đẹp hơn nhưng cần máy khỏe.'
    :'Thấp: kiểu pixel low-poly retro — hình ảnh vuông pixel, texture thô, tắt bóng đổ, nhiễu hạt và bụi. Rất mượt trên máy yếu.';
  $('gLow').style.boxShadow=Q<=5?'0 0 10px #a00':'none'; $('gHigh').style.boxShadow=Q>=6?'0 0 10px #a00':'none';
}
function applyQuality(noBuild){
  HQ=Q>=6;
  renderer.setPixelRatio(pr()); renderer.setSize(STW,STH);
  canvas.style.imageRendering=HQ?'auto':'pixelated';
  renderer.toneMappingExposure=HQ?1.0:1.25;
  [[spot,Q>=9?1024:512],[lamp,Q>=9?512:256]].forEach(a=>{
    if(a[0].shadow.map){a[0].shadow.map.dispose();a[0].shadow.map=null;} a[0].shadow.mapSize.set(a[1],a[1]);});
  $('grain').style.display=HQ?'block':'none'; dust.visible=HQ;
  gMats.forEach(m=>{m.needsUpdate=true;});
  saveNum('verity_q',Q); updateSettingsUI();
  if(!noBuild) buildRoom();
}
$('settingsBtn').onclick=()=>{showOnly('settings');updateSettingsUI();};
$('sback').onclick=()=>showOnly('menu');
$('qr').oninput=()=>{Q=+$('qr').value;updateSettingsUI();};
$('qr').onchange=()=>{Q=+$('qr').value;applyQuality();};
$('qm').onclick=()=>{Q=Math.max(1,Q-1);applyQuality();};
$('qp').onclick=()=>{Q=Math.min(10,Q+1);applyQuality();};
$('gLow').onclick=()=>{Q=3;applyQuality();};
$('gHigh').onclick=()=>{Q=10;applyQuality();};

// ----- Nhạc menu -----
const bgm=new Audio(); bgm.loop=true; bgm.preload='auto'; if(MUSIC_SRC) bgm.src=MUSIC_SRC;
let musicVol=loadNum('doors_vol',60,0,100)/100, fadeI=null;
$('vr').value=Math.round(musicVol*100); $('vv').textContent=Math.round(musicVol*100)+'%';
function fadeTo(v,done){
  clearInterval(fadeI);
  fadeI=setInterval(()=>{const d=v-bgm.volume;
    if(Math.abs(d)<.03){bgm.volume=v;clearInterval(fadeI);if(done)done();}
    else bgm.volume=Math.max(0,Math.min(1,bgm.volume+Math.sign(d)*.03));},40);
}
function musicStart(){
  if(!MUSIC_SRC||state!=='menu') return;
  if(bgm.paused) bgm.volume=0;
  const p=bgm.play();
  const ok=()=>{$('musichint').style.display='none'; if(state==='menu') fadeTo(musicVol); else bgm.pause();};
  const blocked=()=>{$('musichint').style.display='block';};     // trình duyệt chặn tự phát -> chờ người chơi bấm
  if(p&&p.then) p.then(ok).catch(blocked); else ok();
}
function musicStop(){ $('musichint').style.display='none'; fadeTo(0,()=>bgm.pause()); }
// Nhạc nền khi đang chơi (nhỏ lại khi ma xuất hiện)
const pbgm=new Audio(); pbgm.loop=true; pbgm.preload='auto'; if(PLAY_SRC) pbgm.src=PLAY_SRC;
let pduck=1;
function playMusicStart(){ if(!PLAY_SRC||!pbgm.paused) return; pbgm.volume=Math.min(1,musicVol*.8); const p=pbgm.play(); if(p&&p.catch)p.catch(()=>{}); }
function playMusicStop(){ pbgm.pause(); try{pbgm.currentTime=0;}catch(e){} }
$('vr').oninput=()=>{musicVol=+$('vr').value/100;$('vv').textContent=$('vr').value+'%';saveNum('doors_vol',$('vr').value);
  if(!bgm.paused){clearInterval(fadeI);bgm.volume=musicVol;}};
['pointerdown','keydown'].forEach(ev=>addEventListener(ev,()=>{if(state==='menu'&&!inStory&&bgm.paused)musicStart();},true));
['pointerdown','keydown'].forEach(ev=>addEventListener(ev,()=>{try{const a=ac(); if(a.resume)a.resume(); stormAudioLoad(a);}catch(e){}},{capture:true,once:true}));   // nạp tiếng sấm cho menu
function snapLights(){const f=l=>({p:l.position.clone(),c:l.color.clone()}); return {lamp:f(lamp),lampB:f(lampB),door:f(doorLight),sc:sconceL.map(f),cl:clueL.map(f)};}
function applyLights(o){const a=(l,v)=>{l.position.copy(v.p);l.color.copy(v.c);}; a(lamp,o.lamp);a(lampB,o.lampB);a(doorLight,o.door);sconceL.forEach((l,i)=>a(l,o.sc[i]));clueL.forEach((l,i)=>a(l,o.cl[i]));}
const saveRoomState=()=>({blocks:shapeBlocks,room,obstacles,inter,watchers,spots,doorPivot,flameMat,fireMat,doorOpen,RW,RD,doorGlow,fog:scene.fog,solved,lights:snapLights()});
function loadRoomState(o){shapeBlocks=o.blocks||[];room=o.room;obstacles=o.obstacles;inter=o.inter;watchers=o.watchers;spots=o.spots;doorPivot=o.doorPivot;flameMat=o.flameMat;fireMat=o.fireMat;doorOpen=o.doorOpen;curSpot=null;RW=o.RW;RD=o.RD;doorGlow=o.doorGlow;scene.fog=o.fog;solved=o.solved;applyLights(o.lights);}
// Đặt các phòng kề bên theo gốc tọa độ = phòng hiện tại; đèn phụ chiếu sáng phòng kế/phòng trước để nhìn xuyên ô cửa
function layoutNeighbors(){
  room.position.z=0; room.visible=true; watchers.forEach(w=>{w.g.visible=true;});
  rooms.forEach((r,j)=>{ if(!r) return;
    if(j===door+1){ r.room.position.z=-(RD/2+r.RD/2+GAP); r.room.visible=true; }
    else if(j===door-1){ r.room.position.z=(RD/2+r.RD/2+GAP); r.room.visible=true; }
    else r.room.visible=false;
    r.watchers.forEach(w=>{w.g.visible=false;}); });
  const nb=rooms[door+1], pb=rooms[door-1];
  if(nb) nextL.position.set(0,RH-.9,nb.room.position.z+nb.RD/2-3.5);
  if(pb) prevL.position.set(0,RH-.9,pb.room.position.z-pb.RD/2+3.5);
}
// Mở được cửa -> dựng sẵn phòng kế tiếp ngay sau cánh cửa; ánh sáng/va chạm vẫn của phòng hiện tại cho tới khi bước qua
function prebuildNext(){
  if(rooms[door+1]||door+1>=DOORS.length||state!=='play') return;
  const C=saveRoomState();
  door++; try{ buildRoom(true); }finally{ door--; }
  const N=saveRoomState(); N.solved=[false,false,false]; rooms[door+1]=N;
  loadRoomState(C); layoutNeighbors();
}
// Bước qua ô cửa (tiến hoặc lùi): đổi "gốc tọa độ" sang phòng kia, người chơi + các phòng dịch tương ứng nên không có điểm cắt
function switchRoom(ni){
  const target=rooms[ni]; if(!target) return;
  const fwd=ni>door, off=RD/2+target.RD/2+GAP;
  rooms[door]=saveRoomState(); rooms[ni]=null;
  camera.position.z+=(fwd?1:-1)*off;
  const chasing=gh.phase!=='idle';
  if(chasing) gh.z+=(fwd?1:-1)*off;           // Verity đang đuổi: giữ nguyên, chỉ đổi sang tọa độ phòng mới để cô ấy vẫn bám theo qua cửa
  door=ni; loadRoomState(target); layoutNeighbors();
  doorLight.intensity=0; hidden=false; $('hide').style.display='none'; refreshClues();
  if(!chasing){ parkGhost(); ghostTimer=16+Math.random()*16; }
  updateHud(); setTimeout(prebuildNext,60);
  if(!target.visited){ target.visited=true; if(!chasing) banner(DOORS[door].name.toUpperCase()+'\n'+DOORS[door].intro,3800); }
}
function nextRoom(){
  transitioning=true; $('fade').style.opacity=1;
  setTimeout(()=>{
    door++;
    if(door>=DOORS.length){playMusicStop();state='win';syncLock();updateHud();parkGhost();showOnly('win');}
    else startRoom();
    $('fade').style.opacity=0; transitioning=false;
  },900);
}
function toggleHide(sp){
  if(!hidden){
    if(gh.phase!=='idle'&&Math.hypot(gh.x-camera.position.x,gh.z-camera.position.z)<3&&gh.phase==='hunt'){banner('Quá muộn! Verity ở quá gần!',1500);return;}
    hidden=true; curSpot=sp; wardDoors(sp,true); camera.position.set(sp.hx,sp.hy,sp.hz); yaw=sp.yaw; pitch=0; spot.intensity=0;
    $('hide').className=sp.type; $('hide').style.display='block'; noise(.25,.08); tone(90,.2,'square',.05,70);
  } else {
    if(gh.phase!=='idle'){banner('Verity vẫn còn ở đây... đừng ra!',1600);return;}
    hidden=false; wardDoors(curSpot,false); let ex=curSpot.ex,ez=curSpot.ez,k=0;
    while(hit(ex,ez)&&k<4){ex+=curSpot.fx*.5;ez+=curSpot.fz*.5;k++;}
    camera.position.set(ex,1.6,ez); spot.intensity=2.1; $('hide').style.display='none'; curSpot=null; noise(.2,.06);
  }
}
function toggleFlash(){
  if(state!=='play'||modalOpen||hidden||transitioning||intro.on) return;
  flashOn=!flashOn; tone(flashOn?900:600,.05,'square',.06); noise(.03,.05);
}
function startBlackout(){
  blackD=blackT=35+Math.random()*50; nextBlack=60+Math.random()*90;   // mất điện ~60 giây (35-85) flashOn=true;
  try{ tone(80,.6,'sawtooth',.14,35); noise(.25,.14); }catch(e){}
  banner('MẤT ĐIỆN!\nDùng đèn pin (F) — mảnh ghép vẫn phát sáng',3200);
}
function endBlackout(){ blackT=0; try{ tone(140,.3,'square',.06,260); }catch(e){} banner('Điện đã có lại.',1800); }
function act(){
  if(hidden){toggleHide();return;}
  if(!cur) return;
  if(cur.kind==='hide') toggleHide(cur);
  else if(gh.phase!=='idle'){banner('Không phải lúc này! Hãy trốn đi!',1500);}
  else if(cur.kind==='clue'){ if(!solved[cur.idx]) openQ(cur.idx); }
  else if(cur.kind==='door'){
    if(doorOpen) return;
    if(keySolved){ doorOpen=true; sGood(); tone(70,1.2,'sawtooth',.12,40); banner('Cổng thoát đã mở! Chạy ra ngoài, nhanh lên!',3200); }
    else banner('Cổng bị khóa. Hãy đoán đúng từ khóa của bức tranh (phím P). Đang có '+totalPieces()+'/'+PIECES+' mảnh.',2600);
  }
}

// ---------- Ma: logic ----------
function startGhost(){
  gh.phase='warn'; gh.t=5.2; gh.alpha=0;
  if(modalOpen) closeModal(true), syncLock();
  banner('ĐÈN CHỚP… VERITY ĐANG TỚI!\nTRỐN NGAY: bụi cây hoặc gầm bàn bóng bàn (E)',4600);
  tone(90,1.6,'sawtooth',.12,45);
}
function ghostSpawn(){
  // Ma hiện ra Ở XA người chơi: chọn điểm xa nhất trong phòng (giữa 4 cạnh + 4 góc). Người chơi vẫn đi lại bình thường.
  const ax=RW/2-2.5, az=RD/2-2.5;
  const c=[[0,-az],[0,az],[-ax,0],[ax,0],[-ax,-az],[ax,-az],[-ax,az],[ax,az]];
  const okc=c.filter(p=>!shapeBlocks.some(b=>p[0]>b[0]-1.8&&p[0]<b[1]+1.8&&p[1]>b[2]-1.8&&p[1]<b[3]+1.8)), cc=okc.length?okc:c;   // không cho ma hiện hình trong tường
  let best=cc[0],bd=-1; cc.forEach(p=>{const d=Math.hypot(p[0]-camera.position.x,p[1]-camera.position.z);if(d>bd){bd=d;best=p;}});
  gh.x=best[0]; gh.z=best[1]; gh.phase='reveal'; gh.t0=gh.t=2.2; gh.step=0; gh.alpha=0; gh.shr=false;
  gh.face=Math.atan2(camera.position.x-gh.x,camera.position.z-gh.z);
  if(ghostSound()) gh.shr=true;            // có file tiếng ma -> bỏ tiếng gào tổng hợp
  else{ noise(1.4,.3); tone(70,1.6,'sawtooth',.2,160); }
}
// Ma và người chơi ở hai phòng khác nhau -> ma đi tới ô cửa giữa hai phòng trước rồi mới đuổi tiếp (không xuyên tường)
const gzone=z=>z>RD/2+GAP/2+.05?1:(z<-RD/2-GAP/2-.05?-1:0);
function ghostGoal(tx,tz){
  const gz=gzone(gh.z), tzn=gzone(tz);
  if(gz!==0&&gz!==tzn) return [0,gz*(RD/2+GAP/2)];
  return [tx,tz];
}
function moveGhost(tx,tz,sp,dt){
  const dx=tx-gh.x,dz=tz-gh.z,d=Math.hypot(dx,dz)||1,s=Math.min(d,sp*dt);
  gh.x+=dx/d*s; gh.z+=dz/d*s; if(d>.05) gh.face=Math.atan2(dx,dz); return d;
}
function caught(){
  if(state!=='play') return;
  state='scare'; gh.phase='scare'; scareT=0; closeModal(true); syncLock();
  const dx=gh.x-camera.position.x, dz=gh.z-camera.position.z, d=Math.hypot(dx,dz)||1;
  gh.ux=dx/d; gh.uz=dz/d; scareYaw=Math.atan2(-gh.ux,-gh.uz); gh.alpha=1;
  $('scare').style.display='block'; $('banner').style.opacity=0; $('prompt').style.display='none';
  ghostSoundStop(); if(!catchSound()) scream();   // có file -> phát tiếng của bạn, thiếu file -> tiếng gào tổng hợp cũ
  shake=.5;
}
function updGhost(dt){
  const P=gh.phase;
  if(P==='idle'){
    ghostTimer-=dt;
    if(ghostTimer<=0&&!transitioning&&state==='play') startGhost();
    return;
  }
  if(P==='warn'){ gh.t-=dt; if(gh.t<=0) ghostSpawn(); return; }
  if(P==='reveal'){
    // Ma chập chờn hiện hình ở xa (người chơi vẫn điều khiển bình thường) -> gào một tiếng -> bắt đầu đuổi
    gh.t-=dt; const e=gh.t0-gh.t;
    gh.alpha=e<1.2?Math.min(1,e/1.2)*(Math.random()<.35?.3:1):1;
    gh.face=Math.atan2(camera.position.x-gh.x,camera.position.z-gh.z);
    if(Math.random()<dt*2) noise(.25,.1);
    if(e>1.2&&!gh.shr){gh.shr=true; tone(900,.9,'sawtooth',.14,260); tone(120,1,'square',.14,50); noise(.9,.3);}
    if(gh.t<=0){gh.phase='hunt'; gh.t=0; gh.step=0;
      noise(1.2,.35); tone(60,1.4,'sawtooth',.22,200); whisper('chạy đi...');
      banner('VERITY ĐANG ĐUỔI THEO BẠN!\nTRỐN NGAY (bụi cây / gầm bàn bóng bàn — E)',3200);}
    return;
  }
  if(P==='hunt'||P==='search') gh.alpha=Math.min(1,gh.alpha+dt*1.4);
  const px=camera.position.x, pz=camera.position.z;
  if(P==='hunt'){
    if(!hidden){
      const g=ghostGoal(px,pz); moveGhost(g[0],g[1],3.6,dt);
      if(Math.hypot(gh.x-px,gh.z-pz)<1.15){caught();return;}
    } else {
      const sp=curSpot, ex=sp.x+sp.fx*sp.gd, ez=sp.z+sp.fz*sp.gd, g=ghostGoal(ex,ez); moveGhost(g[0],g[1],3.6,dt);
      if(Math.hypot(gh.x-ex,gh.z-ez)<0.12){gh.phase='search'; gh.t0=gh.t=6+Math.random()*1.5; gh.peek=0; whisper('tôi biết bạn ở đây...');}
    }
    gh.step-=dt; if(gh.step<=0){gh.step=.55; const dd=Math.hypot(gh.x-px,gh.z-pz); tone(45,.25,'sine',Math.min(.5,1/(dd*.3+1)),30); noise(.08,Math.min(.2,.6/(dd+1)));}
  } else if(P==='search'){
    gh.t-=dt; const sp=curSpot;
    gh.x=sp.x+sp.fx*sp.gd; gh.z=sp.z+sp.fz*sp.gd; gh.face=Math.atan2(-sp.fx,-sp.fz);
    const tp=gh.t0*.55, goal=gh.t<tp?1-gh.t/tp:0;
    gh.peek+=(goal-gh.peek)*Math.min(1,dt*3);
    if(Math.random()<dt*1.2) noise(.3,.05);
    if(gh.t<=0){gh.phase='leave'; gh.t=3; tone(60,1.8,'sawtooth',.14,35);}
  } else if(P==='leave'){
    gh.t-=dt; gh.peek=Math.max(0,gh.peek-dt*1.2); const sp=curSpot;
    if(sp) moveGhost(gh.x+sp.fx*6,gh.z+sp.fz*6,2.2,dt);
    gh.alpha=Math.max(0,Math.min(1,gh.t/1.6));
    if(gh.t<=0){parkGhost(); ghostTimer=25+Math.random()*20; banner('Verity đã đi rồi... Bạn có thể ra ngoài.',2800);}
  }
}
function animGhost(dt){
  const act2=gh.phase!=='idle';
  if(!act2){return;}
  const t=tt;
  const hunting=(gh.phase==='hunt'||gh.phase==='scare');
  gMats.forEach(m=>m.opacity=gh.alpha);
  gLight.intensity=gh.alpha*2.4*(0.6+0.4*Math.random());
  if(gh.phase!=='scare'){
    const sp=curSpot;
    const sink=(gh.phase==='search'||gh.phase==='leave')&&sp?sp.sink*.6*gh.peek:0;
    const bend=(gh.phase==='search'||gh.phase==='leave')&&sp?sp.bend*gh.peek:(gh.phase==='reveal'?.65*Math.max(0,gh.t/gh.t0):0);
    ghostRoot.position.set(gh.x,-sink+Math.sin(t*2)*.04,gh.z);
    let da=gh.face-ghostRoot.rotation.y; da=Math.atan2(Math.sin(da),Math.cos(da));
    ghostRoot.rotation.y+=da*Math.min(1,dt*8);
    ghostRoot.rotation.x=bend;
  }
  const tgt=hunting?-1.35:(gh.phase==='reveal'?-.8:-.2);
  gArms.forEach((a,i)=>{a.sh.rotation.x+=((tgt+Math.sin(t*3+i)*.1)-a.sh.rotation.x)*Math.min(1,dt*6);a.el.rotation.x=-.25+Math.sin(t*5+i*2)*.08;});
  gHeadG.rotation.set(Math.sin(t*2.1)*.12,Math.sin(t*1.3)*.2,Math.sin(t*7)*.07+(Math.random()<dt*3?(Math.random()-.5)*.8:0));
  const lunge=gh.phase==='reveal'&&gh.t0-gh.t>3.3;
  if(gh.phase==='scare'||lunge){gHeadG.rotation.z+=(Math.random()-.5)*.5;gHeadG.rotation.y+=(Math.random()-.5)*.4;}
  gHair.forEach((h,i)=>{h.rotation.x=Math.sin(t*2+i)*.12;});
  gMouth.scale.y=(gh.phase==='scare'||lunge)?1.1+Math.abs(Math.sin(t*40))*.5:.35+Math.sin(t*3)*.1+(gh.phase==='search'?gh.peek*.5:0);
  {const sq=.9+gMouth.scale.y*.15, sx=Math.min(1.06,2-sq); gHeadG.scale.set(sx,sq,sx);}   // mặt cười phồng/xẹp theo nhịp "cười"
}
const sc=$('scare'), scx=sc.getContext('2d');
function drawScare(t){
  const w=sc.width,h=sc.height; scx.clearRect(0,0,w,h);
  if(t<.12||t>2.2||(!RF&&Math.random()<.18)||!CAN.face) return;
  const k=1+Math.min(t,.6)*.9+Math.sin(t*50)*.04, fh=h*1.35*k, fw=fh*512/640;
  scx.fillStyle='rgba(0,0,0,.55)'; scx.fillRect(0,0,w,h);
  scx.save(); scx.translate(w/2+(Math.random()-.5)*w*.04,h*.52+(Math.random()-.5)*h*.04); scx.rotate((Math.random()-.5)*.08);
  scx.drawImage(CAN.face,-fw/2,-fh/2,fw,fh); scx.restore();
  scx.fillStyle='rgba(140,150,175,'+(.08+Math.random()*.16)+')'; scx.fillRect(0,0,w,h);
  scx.fillStyle='rgba(0,0,0,.25)'; for(let y=0;y<h;y+=4) scx.fillRect(0,y,w,1);
}
function updScare(dt){
  scareT+=dt;
  let da=scareYaw-yaw; da=Math.atan2(Math.sin(da),Math.cos(da)); yaw+=da*(1-Math.exp(-dt*16));
  pitch+=(0.18-pitch)*(1-Math.exp(-dt*10));
  const e=Math.min(1,scareT/.25), fd=3.0-1.0*(1-Math.pow(1-e,3));
  ghostRoot.position.set(camera.position.x+gh.ux*fd+(Math.random()-.5)*.05,(Math.random()-.5)*.05,camera.position.z+gh.uz*fd+(Math.random()-.5)*.05);
  ghostRoot.rotation.y=Math.atan2(-gh.ux,-gh.uz); ghostRoot.rotation.x=.8*Math.min(1,scareT/.2);
  camera.fov=72+Math.min(scareT,1.2)*18; camera.updateProjectionMatrix();
  shake=Math.max(shake,.3);
  scareFlashT-=dt; if(scareFlashT<=0){scareFlashT=.06;const f=$('flash');
    if(RF){f.style.transition='opacity .3s';f.style.background='#667';f.style.opacity=.22;}
    else{f.style.transition='none';f.style.background=Math.random()<.4?'#fff':'#8890a0';f.style.opacity=Math.random()<.6?(.3+Math.random()*.6):0;}}
  drawScare(scareT);
  if(scareT>2.6){ const f=$('flash'); f.style.transition='opacity .45s'; gameOver('Verity đã bắt được bạn.\nCô nói: \"Em trượt rồi.\"\nBạn phải tìm lại các mảnh ghép từ đầu.'); }
}

// ---------- Điều khiển ----------
addEventListener('keydown',e=>{
  if(modalOpen){
    if(e.code==='Escape') closeModal();
    else if(modalMode==='q'&&!e.repeat&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&(e.key||'').length===1){
      const k='ABCD'.indexOf(e.key.toUpperCase()); if(k>=0) choose(k);
    }
    return;
  }
  if((e.code==='ShiftLeft'||e.code==='ShiftRight')&&!e.repeat){ if(state==='play'&&!transitioning) toggleSL(); return; }
  keys[e.code]=true;
  if(intro.on){ if(e.code==='Enter') introEnd(); return; }   // đang tỉnh dậy: khóa điều khiển, Enter để bỏ qua
  if(e.code==='KeyE'&&state==='play'&&!transitioning) act();
  if(e.code==='KeyF'&&!e.repeat) toggleFlash();
  if(e.code==='KeyP'&&!e.repeat&&state==='play'&&!transitioning) openPuzzle();
  if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)) e.preventDefault();
});
addEventListener('keyup',e=>{keys[e.code]=false;});
canvas.addEventListener('mousedown',()=>{
  dragging=!shiftLock&&state==='play'&&!modalOpen;
  if(shiftLock&&state==='play'&&!modalOpen&&!isLocked()) lockPtr();
});
canvas.addEventListener('contextmenu',e=>e.preventDefault());
addEventListener('mouseup',()=>dragging=false);
document.documentElement.addEventListener('mouseleave',()=>{mouseIn=false;});
document.addEventListener('mouseleave',()=>{mouseIn=false;});
document.addEventListener('mouseout',e=>{if(!e.relatedTarget)mouseIn=false;});   // con trỏ rời khung/iframe -> ngừng xoay
addEventListener('blur',()=>{mouseIn=false;dragging=false;keys={};});                           // mất focus (bấm ra ngoài iframe) -> ngừng xoay
document.addEventListener('visibilitychange',()=>{mouseIn=false;dragging=false;keys={};});
addEventListener('mousemove',e=>{
  const r=stage.getBoundingClientRect();
  mouseX=(e.clientX-r.left)/r.width*2-1; mouseY=(e.clientY-r.top)/r.height*2-1;
  mouseIn=Math.abs(mouseX)<=1&&Math.abs(mouseY)<=1;
  if(state!=='play'||modalOpen) return;
  // Vuốt sang phải -> quay phải, sang trái -> quay trái (cả khi khóa chuột thật lẫn khi bị trình duyệt chặn)
  if(isLocked()||dragging||fakeLock()){
    if(Math.abs(e.movementX)>250||Math.abs(e.movementY)>250) return;   // Chrome đôi khi báo delta khổng lồ lúc vừa khóa chuột
    yaw-=e.movementX*0.0025; pitch=Math.max(-1.3,Math.min(1.3,pitch-e.movementY*0.0025));
  }
});
addEventListener('resize',fit);
document.addEventListener('fullscreenchange',fit);
$('lockbtn').onclick=()=>{if(state==='play'&&!modalOpen&&!transitioning)toggleSL();};
document.querySelectorAll('#ui button').forEach(b=>b.addEventListener('click',()=>b.blur()));   // nhả focus để Space/Enter không bấm lại nút
function setMute(v){
  MUTED=!!v; saveNum('doors_mute',MUTED?1:0); $('mu').textContent=MUTED?'🔇':'🔊';
  try{ const m=AC&&masters.get(AC); if(m) m.gain.setTargetAtTime(MUTED?0:1,AC.currentTime,.04); }catch(e){}
  bgm.muted=MUTED; pbgm.muted=MUTED;
}
$('mu').onclick=()=>setMute(!MUTED); setMute(MUTED);
$('fs').onclick=()=>{try{if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen();}catch(e){}};
if(!document.documentElement.requestFullscreen){ $('fs').style.display='none'; $('mu').style.right='10px'; $('pz').style.right='74px'; }   // iPhone không hỗ trợ toàn màn hình

// ----- Điều khiển cảm ứng: cần gạt trái = đi, vuốt phải = nhìn, nút E = tương tác, nút CHẠY = chạy -----
const joy={x:0,y:0}; let touchRun=false, joyId=null, joyOX=0, joyOY=0, lookId=null, lookX=0, lookY=0;
const toUI=(cx,cy)=>{const r=stage.getBoundingClientRect(),k=1280/r.width;return[(cx-r.left)*k,(cy-r.top)*k];};
const joyR=()=>60*stage.getBoundingClientRect().width/1280;
function setTouch(on){
  touchMode=on; document.body.classList.toggle('touch',on);
  if(on&&shiftLock){shiftLock=false;dragging=false;syncLock();}
  $('help').style.display=on?'none':'';
  $('lockbtn').style.display=(!on&&state==='play')?'block':'none'; $('tui').style.display=(on&&state==='play')?'block':'none';
  fit();
}
function stopJoy(){joyId=null;joy.x=joy.y=0;$('joyB').style.display=$('joyK').style.display='none';}
function placeJoy(el,cx,cy){const p=toUI(cx,cy);el.style.left=p[0]+'px';el.style.top=p[1]+'px';el.style.display='block';}
addEventListener('touchstart',()=>{if(!touchMode)setTouch(true);},{capture:true,passive:true});   // lần chạm đầu tiên -> bật giao diện cảm ứng
canvas.addEventListener('touchstart',e=>{
  e.preventDefault();                                   // chặn cuộn trang + chuột giả lập
  if(state!=='play'||modalOpen) return;
  const r=stage.getBoundingClientRect(), mid=r.left+r.width*.5;
  for(const t of e.changedTouches){
    if(t.clientX<mid&&joyId===null){joyId=t.identifier;joyOX=t.clientX;joyOY=t.clientY;placeJoy($('joyB'),joyOX,joyOY);placeJoy($('joyK'),joyOX,joyOY);}
    else if(t.clientX>=mid&&lookId===null){lookId=t.identifier;lookX=t.clientX;lookY=t.clientY;}
  }
},{passive:false});
canvas.addEventListener('touchmove',e=>{
  e.preventDefault();
  for(const t of e.changedTouches){
    if(t.identifier===joyId){
      let dx=t.clientX-joyOX, dy=t.clientY-joyOY; const R=joyR(), d=Math.hypot(dx,dy);
      if(d>R){dx*=R/d;dy*=R/d;}
      joy.x=dx/R; joy.y=dy/R; if(Math.hypot(joy.x,joy.y)<.15){joy.x=joy.y=0;}    // vùng chết
      placeJoy($('joyK'),joyOX+dx,joyOY+dy);
    } else if(t.identifier===lookId){
      if(state==='play'&&!modalOpen){
        const k=.0035*1280/Math.max(1,STW);
        yaw-=(t.clientX-lookX)*k; pitch=Math.max(-1.3,Math.min(1.3,pitch-(t.clientY-lookY)*k));
      }
      lookX=t.clientX; lookY=t.clientY;
    }
  }
},{passive:false});
const tEnd=e=>{for(const t of e.changedTouches){if(t.identifier===joyId)stopJoy(); if(t.identifier===lookId)lookId=null;}};
canvas.addEventListener('touchend',tEnd); canvas.addEventListener('touchcancel',tEnd);
function tBtn(el,down,up){
  el.addEventListener('touchstart',e=>{e.preventDefault();e.stopPropagation();down();},{passive:false});
  ['touchend','touchcancel'].forEach(n=>el.addEventListener(n,e=>{e.preventDefault();if(up)up();}));
}
tBtn($('tE'),()=>{if(state==='play'&&!transitioning)act();});
tBtn($('tF'),()=>toggleFlash());
tBtn($('tRun'),()=>{touchRun=true;$('tRun').classList.add('on');},()=>{touchRun=false;$('tRun').classList.remove('on');});
setTouch(touchMode);

function hit(x,z){for(const b of obstacles){if(x>b.x1-0.35&&x<b.x2+0.35&&z>b.z1-0.35&&z<b.z2+0.35)return true;}return false;}



// ---------- Phông nền menu: tranh lâu đài ma trong rừng + mưa, dơi, mắt phát sáng, sét (nhịp sét dùng chung với hệ thống bão) ----------
const msky=$('msky'), mbg=$('mbg'), mfx=$('mfx'), mfl=$('mfl'), mimg=$('mimg'), mctx=mfx.getContext('2d');
const IMW=849, IMH=420;
const EYES0=[[95,60,0],[88,283,0],[72,198,1],[99,200,1],[790,66,1],[808,158,0],[777,296,0],[640,305,0],[752,250,1],[230,288,1],[110,244,0],[648,282,1],[60,300,0],[825,230,0]]
  .map(e=>({x:e[0],y:e[1],c:e[2]?'#ffc840':'#ff2a1a',t:Math.random()*9,p:.6+Math.random()*1.4}));
const EYES=[];
const BATS=Array.from({length:0},()=>({x:Math.random()*IMW,y:30+Math.random()*150,vx:25+Math.random()*35,ph:Math.random()*6,s:.7+Math.random()*.8}));
const MRAIN=Array.from({length:220},()=>({x:Math.random(),y:Math.random(),v:1.1+Math.random()*.9,l:.025+Math.random()*.03}));
let mBolt=null, mLastBolt=0;
function menuBg(dt,on){
  mbg.style.display=on?'block':'none'; $('hud').style.display=on?'none':''; if(on) $('pz').style.display='none';
  if(!on) return;
  const w=STW,h=STH; if(mfx.width!==w||mfx.height!==h){mfx.width=w;mfx.height=h;}
  const sc=Math.max(w/IMW,h/IMH), ox=(w-IMW*sc)/2, oy=(h-IMH*sc)/2, g=mctx;
  g.clearRect(0,0,w,h);
  const fv=flashV;
  mimg.style.filter='brightness('+(.5+fv*1.0).toFixed(2)+') contrast(1.08)';
  msky.style.opacity=(.94*(1-Math.min(1,fv*1.35))).toFixed(2);          // sét đánh -> trời sáng bừng lên, hết sét -> đen lại
  if(AC&&Math.random()<dt*.22) tone(3600+Math.random()*1800,.05,'sine',.02,6200);   // tiếng dơi rít xa
  mfl.style.opacity=Math.min(.6,fv*.6).toFixed(2);
  // tia sét thêm: mỗi lần sét đánh dựng một đường gấp khúc từ mây xuống
  if(boltT>mLastBolt+.3){ let x=w*(.1+Math.random()*.8), y=0; mBolt=[[x,y]]; while(y<h*(.45+Math.random()*.25)){x+=(Math.random()-.5)*w*.04; y+=h*(.03+Math.random()*.05); mBolt.push([x,y]);} }
  mLastBolt=boltT;
  if(mBolt&&boltT>.72&&fv>.05){ g.save(); g.lineJoin='round'; g.shadowColor='#9db8ff'; g.shadowBlur=18;
    g.strokeStyle='rgba(235,242,255,'+Math.min(1,fv+.2)+')'; g.lineWidth=Math.max(1.5,sc*1.1);
    g.beginPath(); mBolt.forEach((p,i)=>i?g.lineTo(p[0],p[1]):g.moveTo(p[0],p[1])); g.stroke(); g.restore(); }
  // dơi
  BATS.forEach(b=>{ b.x+=b.vx*dt; b.ph+=dt*11; if(b.x>IMW+20){b.x=-20;b.y=30+Math.random()*150;}
    const X=ox+b.x*sc, Y=oy+(b.y+Math.sin(b.ph*.4)*6)*sc, k=b.s*sc*3.2, f=Math.sin(b.ph);
    g.fillStyle='#04030a'; g.beginPath(); g.moveTo(X,Y);
    g.quadraticCurveTo(X-k*1.2,Y-k*(1.1+f*.8),X-k*2.2,Y+k*.3); g.quadraticCurveTo(X-k*1.1,Y+k*.1,X,Y+k*.6);
    g.quadraticCurveTo(X+k*1.1,Y+k*.1,X+k*2.2,Y+k*.3); g.quadraticCurveTo(X+k*1.2,Y-k*(1.1+f*.8),X,Y); g.fill(); });
  // mắt phát sáng trong rừng (chớp mắt thỉnh thoảng)
  EYES.forEach(e=>{ const v=Math.sin(tt*e.p+e.t); if(v<-.82) return;
    const X=ox+e.x*sc, Y=oy+e.y*sc, d=3.2*sc, r=Math.max(1.4,1.3*sc);
    g.save(); g.shadowColor=e.c; g.shadowBlur=10; g.fillStyle=e.c; g.globalAlpha=.65+.35*Math.max(0,v);
    g.beginPath(); g.arc(X-d,Y,r,0,6.3); g.arc(X+d,Y,r,0,6.3); g.fill(); g.restore(); });
  // mưa
  g.strokeStyle='rgba(175,190,215,.33)'; g.lineWidth=Math.max(1,sc*.5); g.beginPath();
  MRAIN.forEach(r=>{ r.y+=r.v*dt; r.x-=.12*dt; if(r.y>1){r.y=-.05;r.x=Math.random()*1.1;} if(r.x<0)r.x+=1.05;
    g.moveTo(r.x*w,r.y*h); g.lineTo(r.x*w-r.l*w*.12,(r.y+r.l)*h); });
  g.stroke();
}
// ---------- Cảnh mở đầu kiểu Granny: mở mắt (mờ) -> chớp mắt -> nhìn đôi bàn tay -> từ từ ngồi dậy ----------
const intro={on:false,e:0,banner:null,hb:null}, INTRO_DUR=10.6;
const handsG=new THREE.Group(); handsG.visible=false; handsG.position.set(0,-.3,-.55); camera.add(handsG);
const handFingers=[], handRoots=[];
(function(){
  // da: texture nhỏ có chấm tàn nhang / sắc đỏ nhẹ ở khớp để không bị "nhựa"
  const cv=document.createElement('canvas'); cv.width=cv.height=128; const g=cv.getContext('2d');
  g.fillStyle='#d6a083'; g.fillRect(0,0,128,128);
  for(let i=0;i<900;i++){ g.fillStyle='rgba('+(150+Math.random()*60|0)+','+(95+Math.random()*40|0)+','+(75+Math.random()*30|0)+','+(Math.random()*.22)+')'; g.fillRect(Math.random()*128,Math.random()*128,1+Math.random()*2,1+Math.random()*2); }
  for(let y=0;y<128;y+=32){ g.fillStyle='rgba(120,60,50,.16)'; g.fillRect(0,y+10,128,5); }       // nếp khớp ngón
  const tex=new THREE.CanvasTexture(cv);
  const skin=new THREE.MeshStandardMaterial({map:tex,color:0xffffff,roughness:.62,metalness:0,emissive:0x351811}),
        nail=new THREE.MeshStandardMaterial({color:0xe8c4b4,roughness:.35,emissive:0x2a1812}),
        cuff=new THREE.MeshStandardMaterial({color:0x34373f,roughness:1,emissive:0x0d0e11});
  const cylSeg=(len,r0,r1)=>{const m=new THREE.Mesh(new THREE.CylinderGeometry(r1,r0,len,10),skin); m.rotation.x=Math.PI/2; m.position.z=-len/2; return m;};   // dọc theo -z
  const ball=r=>new THREE.Mesh(new THREE.SphereGeometry(r,10,8),skin);
  // một ngón: 3 đốt có khớp xoay được
  const finger=(len,r,x,z,spread)=>{
    const root=new THREE.Group(); root.position.set(x,0,z); root.rotation.y=spread;
    const p1=new THREE.Group(), p2=new THREE.Group(), p3=new THREE.Group();
    root.add(p1); p1.add(ball(r*1.04)); p1.add(cylSeg(len[0],r,r*.93));
    p2.position.z=-len[0]; p1.add(p2); p2.add(ball(r*.93)); p2.add(cylSeg(len[1],r*.93,r*.86));
    p3.position.z=-len[1]; p2.add(p3); p3.add(ball(r*.86)); p3.add(cylSeg(len[2],r*.86,r*.74));
    const tip=ball(r*.74); tip.position.z=-len[2]; p3.add(tip);
    const n=new THREE.Mesh(new THREE.SphereGeometry(r*.62,8,6),nail); n.scale.set(1,.35,1.35); n.position.set(0,r*.55,-len[2]*.62); p3.add(n);   // móng
    return {root,p:[p1,p2,p3]};
  };
  [-1,1].forEach(side=>{
    const h=new THREE.Group(); h.position.x=side*.17; h.rotation.set(-.3,-side*.2,side*.07); handsG.add(h); handRoots.push(h);
    const palm=new THREE.Mesh(new THREE.BoxGeometry(.084,.024,.088),skin); palm.position.z=-.01; h.add(palm);
    [-1,1].forEach(sx=>{const e=ball(.0125); e.scale.set(1,.95,1.6); e.position.set(sx*.042,0,-.01); h.add(e);});       // bo tròn hai cạnh bàn tay
    const back=new THREE.Mesh(new THREE.SphereGeometry(.044,12,8),skin); back.scale.set(1,.28,1.1); back.position.set(0,.008,-.008); h.add(back);  // mu bàn tay
    const defs=[[.036,.025,.02,.0098,-.0315,.07],[.04,.027,.021,.0105,-.0105,.0],[.037,.025,.02,.0098,.0105,-.05],[.029,.019,.016,.0088,.0315,-.12]];   // trỏ, giữa, nhẫn, út
    defs.forEach((d,i)=>{ const f=finger([d[0],d[1],d[2]],d[3],d[4]*(side>0?1:1),-.054,d[5]*side*(side>0?-1:-1)); h.add(f.root); handFingers.push({p:f.p,i,side}); });
    // ngón cái: 2 đốt chếch ra ngoài
    const tr=new THREE.Group(); tr.position.set(-side*.044,-.002,-.012); tr.rotation.y=side*.78; h.add(tr);
    const t1=new THREE.Group(), t2=new THREE.Group(); tr.add(t1); t1.add(ball(.0115)); t1.add(cylSeg(.033,.0115,.0105));
    t2.position.z=-.033; t1.add(t2); t2.add(ball(.0105)); t2.add(cylSeg(.027,.0105,.009)); const tt2=ball(.009); tt2.position.z=-.027; t2.add(tt2);
    const tn=new THREE.Mesh(new THREE.SphereGeometry(.0056,8,6),nail); tn.scale.set(1,.35,1.4); tn.position.set(0,.0075,-.02); t2.add(tn);
    handFingers.push({p:[t1,t2,t2],i:4,side});
    // cổ tay + ống tay áo
    const wr=cylSeg(.05,.027,.03); wr.position.z=.0; wr.position.z=.06; h.add(wr); wr.scale.set(1,1,1);
    const cf=new THREE.Mesh(new THREE.CylinderGeometry(.041,.047,.13,14),cuff); cf.rotation.x=Math.PI/2; cf.position.z=.15; h.add(cf);
  });
})();
// ---------- Tay cầm đèn pin (hiện khi bật đèn, hạ xuống khi tắt) ----------
const flashG=new THREE.Group(); flashG.visible=false; camera.add(flashG); let flashAmt=0;
(function(){
  const skin=new THREE.MeshStandardMaterial({color:0xd6a083,roughness:.65,emissive:0x40201a}),
        metal=new THREE.MeshStandardMaterial({color:0x2b2d33,roughness:.4,metalness:.7,emissive:0x0c0c0f}),
        cuff=new THREE.MeshStandardMaterial({color:0x34373f,roughness:1,emissive:0x0d0e11}),
        lens=new THREE.MeshBasicMaterial({color:0xfff2c8});
  const g=new THREE.Group(); g.position.set(.25,-.27,-.5); g.rotation.set(.05,.14,-.03); flashG.add(g);
  const cy=(r0,r1,len,m,z)=>{const c=new THREE.Mesh(new THREE.CylinderGeometry(r1,r0,len,14),m); c.rotation.x=Math.PI/2; c.position.z=z; g.add(c); return c;};
  cy(.03,.03,.2,metal,0);                    // thân đèn
  cy(.034,.034,.012,metal,-.06);              // vòng nối đầu đèn
  cy(.034,.05,.075,metal,-.135);              // đầu đèn loe ra
  cy(.043,.043,.006,lens,-.174);              // mặt kính phát sáng
  cy(.026,.026,.022,metal,.11);               // đuôi đèn
  // bàn tay nắm quanh thân đèn: 4 ngón (vòng cung) + ngón cái
  for(let i=0;i<4;i++){
    const t=new THREE.Mesh(new THREE.TorusGeometry(.04,.0125,6,12,Math.PI*1.5),skin);
    t.position.z=.065-i*.026; t.rotation.z=Math.PI*.9; g.add(t);
  }
  const palm=new THREE.Mesh(new THREE.BoxGeometry(.05,.06,.105),skin); palm.position.set(-.032,-.01,.012); g.add(palm);
  const thumb=new THREE.Mesh(new THREE.CylinderGeometry(.011,.013,.07,8),skin); thumb.rotation.x=Math.PI/2; thumb.position.set(.012,.04,-.03); g.add(thumb);
  // cổ tay + ống tay áo kéo xuống góc dưới màn hình
  const wr=new THREE.Mesh(new THREE.CylinderGeometry(.03,.034,.12,12),skin); wr.rotation.x=1.15; wr.position.set(-.04,-.075,.115); g.add(wr);
  const cf=new THREE.Mesh(new THREE.CylinderGeometry(.05,.058,.16,14),cuff); cf.rotation.x=1.15; cf.position.set(-.05,-.14,.2); g.add(cf);
})();
// ---------- Bóng đen thỉnh thoảng lướt ngang qua tầm nhìn ----------
const shadowG=new THREE.Group(); shadowG.visible=false; scene.add(shadowG);
const shBody=new THREE.Group(); shadowG.add(shBody);
const shMat=new THREE.MeshBasicMaterial({color:0x020204,transparent:true,opacity:0,fog:false,depthWrite:false});
const shEyeMat=new THREE.MeshBasicMaterial({color:0xe8eeff,transparent:true,opacity:0,fog:false});
let shHead, shLegs=[], shArms=[];
(function(){
  const bx=(w,h,d,x,y,z,par)=>{const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),shMat); m.position.set(x,y,z); (par||shBody).add(m); return m;};
  bx(.5,.78,.26,0,1.28,0);
  shHead=new THREE.Group(); shHead.position.set(0,1.82,0); shBody.add(shHead);
  const hd=new THREE.Mesh(new THREE.SphereGeometry(.14,12,10),shMat); hd.scale.set(.9,1.2,1); shHead.add(hd);
  [-1,1].forEach(sx=>{const e=new THREE.Mesh(new THREE.SphereGeometry(.018,6,5),shEyeMat); e.scale.set(1.5,.8,.5); e.position.set(sx*.055,.03,.125); shHead.add(e);});
  [-1,1].forEach(sx=>{ const lg=new THREE.Group(); lg.position.set(sx*.13,.9,0); shBody.add(lg); bx(.19,.9,.2,0,-.45,0,lg); shLegs.push(lg);
    const ar=new THREE.Group(); ar.position.set(sx*.33,1.6,0); shBody.add(ar); bx(.12,.8,.14,0,-.4,0,ar); shArms.push(ar); });
})();
let shDur=0, shT=0, shA=[0,0], shB=[0,0], nextShadow=30+Math.random()*60;
function startShadow(){
  nextShadow=35+Math.random()*80;
  if(gh.phase!=='idle') return;
  const f=[-Math.sin(yaw),-Math.cos(yaw)], r=[Math.cos(yaw),-Math.sin(yaw)], d=4.5+Math.random()*3.5, dir=Math.random()<.5?1:-1, sp=8;
  const cx=camera.position.x+f[0]*d, cz=camera.position.z+f[1]*d;
  shA=[cx-r[0]*sp*dir, cz-r[1]*sp*dir]; shB=[cx+r[0]*sp*dir, cz+r[1]*sp*dir];
  shDur=1.1+Math.random()*.7; shT=0; shadowG.visible=true;
  try{ tone(70,.9,'sine',.07,45); noise(.5,.04); }catch(e){}
}
function updShadow(dt){
  if(shDur<=0) return;
  if(hidden||gh.phase!=='idle'){shDur=0; shadowG.visible=false; return;}
  shT+=dt; const k=shT/shDur;
  if(k>=1){shDur=0; shadowG.visible=false; return;}
  const lim=(a,m)=>Math.max(-m,Math.min(m,a));
  const x=lim(shA[0]+(shB[0]-shA[0])*k,RW/2-.8), z=lim(shA[1]+(shB[1]-shA[1])*k,RD/2-.8);
  shadowG.position.set(x,Math.abs(Math.sin(tt*11))*.05,z);
  const mv=Math.atan2(shB[0]-shA[0],shB[1]-shA[1]); shBody.rotation.y=mv;
  let hy=Math.atan2(camera.position.x-x,camera.position.z-z)-mv; hy=Math.atan2(Math.sin(hy),Math.cos(hy)); shHead.rotation.y=Math.max(-1.4,Math.min(1.4,hy));   // quay đầu nhìn người chơi
  const sw=Math.sin(tt*14)*.7; shLegs[0].rotation.x=sw; shLegs[1].rotation.x=-sw; shArms[0].rotation.x=-sw*.8; shArms[1].rotation.x=sw*.8;
  const a=Math.sin(Math.PI*k); shMat.opacity=.93*Math.min(1,a*3); shEyeMat.opacity=Math.min(1,a*3);
}
const easeIO=x=>x<=0?0:x>=1?1:x*x*(3-2*x);
function introBegin(){
  intro.on=true; intro.e=0; handsG.visible=false; $('lids').style.display='block'; $('skiph').style.display='block'; $('hud').style.display='none';
  $('c').style.filter='blur(10px)'; setLids(0);
  try{ noise(.8,.04); }catch(e){}
  let n=0; clearInterval(intro.hb);
  intro.hb=setInterval(()=>{ if(!intro.on||++n>7){clearInterval(intro.hb);return;}      // tiếng tim đập
    try{ tone(52,.16,'sine',.3,36); setTimeout(()=>{try{tone(46,.14,'sine',.2,34);}catch(e){}},190);}catch(e){} },900);
}
function setLids(o){
  const l=$('lids'); if(o>=.995){ l.style.display='none'; return; } l.style.display='block';
  const h=((1-o)*50).toFixed(2)+'%'; l.children[0].style.height=h; l.children[1].style.height=h;
}
function introEnd(){
  if(!intro.on) return; intro.on=false; clearInterval(intro.hb);
  handsG.visible=false; $('lids').style.display='none'; $('skiph').style.display='none'; $('c').style.filter=''; $('hud').style.display='';
  if(intro.banner){ banner(intro.banner[0],intro.banner[1]); intro.banner=null; }
}
let introSnd=0;
function introUpdate(dt){
  const e=(intro.e+=dt);
  // mí mắt: nhắm -> hé từ từ -> chớp -> mở hẳn
  let o; if(e<.9)o=0; else if(e<2.6)o=.8*easeIO((e-.9)/1.7); else if(e<3.1)o=.8*(1-easeIO((e-2.6)/.5)*.92); else if(e<3.9)o=.064+.936*easeIO((e-3.1)/.8); else o=1;
  setLids(o);
  $('c').style.filter='blur('+Math.max(0,9*(1-easeIO((e-1.2)/4.4))).toFixed(1)+'px)';
  // camera: nằm nhìn trần -> quay xuống nhìn tay -> ngồi dậy
  const sit=easeIO((e-6.4)/3.7);
  let pitchT = e<3.2 ? 1.0+Math.sin(e*.9)*.06 : (e<5.4 ? 1.0+(-.5-1.0)*easeIO((e-3.2)/2.2) : -.5);
  if(e>=6.4) pitchT=-.5*(1-sit);
  pitch=pitchT; yaw=Math.sin(e*.55)*.07*(1-sit);
  camera.position.y=.42+(1.6-.42)*sit+Math.sin(e*1.7)*.008*(1-sit)+Math.sin(e*3.1)*.012*sit*(1-sit)*4;
  // đôi tay: hiện lên trước mặt, nắm mở ngón tay, rồi hạ xuống khi ngồi dậy
  handsG.visible=false;   // đã bỏ đôi bàn tay ở cảnh mở đầu
  const up=easeIO((e-3.4)/1.2)*(1-easeIO((e-6.6)/1.6));
  handsG.position.y=-.62+(.62-.2)*up; handsG.position.z=-.55;
  handFingers.forEach(f=>{ const c=.5+.5*Math.sin(e*1.5+f.i*.55+(f.side>0?.7:0)), base=f.i===4?.15:.2;
    f.p[0].rotation.x=-(base+.38*c); if(f.p[1]!==f.p[2]){ f.p[1].rotation.x=-(.22+.62*c); f.p[2].rotation.x=-(.12+.42*c); } else f.p[1].rotation.x=-(.1+.3*c); });
  handRoots.forEach((h,k)=>{ h.rotation.z=(k?1:-1)*.07+Math.sin(e*7+k*2)*.006; h.position.y=Math.sin(e*5.5+k)*.0025; });   // tay run nhẹ lúc mới tỉnh
  if(e>3.1&&introSnd<1){introSnd=1; try{noise(.35,.05);}catch(x){}}           // hít vào lúc chớp mắt
  if(e>6.4&&introSnd<2){introSnd=2; try{noise(.9,.06); tone(70,.5,'sine',.05,50);}catch(x){}}   // tiếng vải sột soạt lúc ngồi dậy
  if(e>=INTRO_DUR) introEnd();
}
// Trốn trong tủ: hai cánh cửa 3D trước đây che kín tầm nhìn (camera nằm trong tủ) -> khi trốn, hé hai cánh ra tạo khe hở thật để thấy phòng bên ngoài
function wardDoors(sp,open){
  if(!sp||!sp.doors) return; const [l,r,m]=sp.doors, g=open?.09:0;
  l.position.x=-.37-g; r.position.x=.37+g; m.visible=!open;
}
function update(dt){
  tt+=dt;
  if(state!=='play'){flashG.visible=false;flashAmt=0;shDur=0;shadowG.visible=false;}
  stormUpdate(dt); pulseClues(); rainUpdate(); sirenUpdate(dt);
  const inMenu=(state==='menu');
  if(room) room.visible=!inMenu;
  menuBg(dt,inMenu);
  if(PLAY_SRC&&!pbgm.paused){pduck+=((gh.phase!=='idle'&&state==='play'?.3:1)-pduck)*Math.min(1,dt*2);pbgm.volume=Math.max(0,Math.min(1,musicVol*.8*pduck));}
  for(let i=0;i<DUST;i++){dustPos[i*3+1]+=Math.sin(tt*.6+i)*0.0009+0.0006;dustPos[i*3]+=Math.cos(tt*.4+i*1.7)*0.0007;
    if(dustPos[i*3+1]>RH)dustPos[i*3+1]=0;}
  dustGeo.attributes.position.needsUpdate=true;
  sconceL.forEach((l,i)=>l.intensity=(0.3+0.1*Math.sin(tt*13+i*2.1)*Math.sin(tt*5.3+i))*lampF);
  if(fireMat) fireMat.opacity=.7+.2*Math.sin(tt*17)*Math.sin(tt*7.3);
  animGhost(dt);
  if(state==='scare'){ updScare(dt); return; }
  if(state!=='play') return;
  if(modalOpen&&joyId!==null) stopJoy();
  if(!modalOpen){ if(keys.ArrowLeft) yaw+=1.8*dt; if(keys.ArrowRight) yaw-=1.8*dt; }
  // Shift Lock dự phòng (không khóa được chuột): xoay camera theo vị trí chuột so với tâm khung
  // (khi không khóa được chuột, con trỏ ẩn nhưng vẫn chạm mép màn hình -> chạm mép thì tiếp tục xoay về phía đó)
  if(!modalOpen&&fakeLock()&&mouseIn&&!dragging){
    const eb=.94, f=v=>Math.abs(v)>eb?Math.sign(v)*(Math.abs(v)-eb)/(1-eb):0;
    yaw-=f(mouseX)*2.6*dt; pitch=Math.max(-1.3,Math.min(1.3,pitch-f(mouseY)*1.6*dt));
  }
  let moving=false, ranNow=false;
  if(!modalOpen&&!hidden&&!transitioning&&!intro.on){
    let f=0,s=0;
    if(keys.KeyW||keys.ArrowUp)f++; if(keys.KeyS||keys.ArrowDown)f--; if(keys.KeyD)s++; if(keys.KeyA)s--;
    if(touchMode&&joyId!==null){f-=joy.y; s+=joy.x;}
    if(f||s){
      moving=true; const run=(keys.Space||touchRun)&&!tired&&stam>0; ranNow=run; const sp=(run?5.2:3.2)*dt, l=Math.hypot(f,s), mag=Math.min(1,l);
      const fx=-Math.sin(yaw),fz=-Math.cos(yaw),rx=Math.cos(yaw),rz=-Math.sin(yaw);
      const dx=(fx*f+rx*s)/l*sp*mag, dzz=(fz*f+rz*s)/l*sp*mag;
      if(!hit(camera.position.x+dx,camera.position.z)) camera.position.x+=dx;
      if(!hit(camera.position.x,camera.position.z+dzz)) camera.position.z+=dzz;
      bob+=dt*(run?12:9);
      stepT-=dt; if(stepT<=0){footstep(run);stepT=run?.3:.46;}
    }
    const nb=rooms[door+1], pb=rooms[door-1];
    const inLine=Math.abs(camera.position.x)<.8;
    const zmin=doorOpen?-RD/2-1.5:-RD/2+0.7;
    const zmax=(pb&&inLine)?RD/2+GAP+1.5:RD/2-0.5;           // đã có phòng trước: cho phép đi ngược qua ô cửa
    camera.position.x=Math.max(-RW/2+0.5,Math.min(RW/2-0.5,camera.position.x));
    camera.position.z=Math.max(zmin,Math.min(zmax,camera.position.z));
    if(doorOpen&&camera.position.z<-RD/2+0.6) camera.position.x=Math.max(-0.75,Math.min(0.75,camera.position.x));
    if(pb&&camera.position.z>RD/2-0.6) camera.position.x=Math.max(-0.75,Math.min(0.75,camera.position.x));
    if(!transitioning){
      if(doorOpen&&nb){ if(camera.position.z<-RD/2-GAP-.55) switchRoom(door+1); }
      else if(doorOpen&&door>=DOORS.length-1&&camera.position.z<-RD/2-0.3) nextRoom();         // cửa cuối: sang màn thắng
      else if(pb&&camera.position.z>RD/2+GAP+.55) switchRoom(door-1);    // đi ngược lại phòng trước
    }
  }
  if(ranNow){ stam=Math.max(0,stam-dt*14); if(stam<=0&&!tired){ tired=true; banner('HẾT SỨC! Đi bộ hoặc đứng nghỉ để lấy lại sức.',2200); try{noise(.6,.1); tone(110,.5,'sine',.06,70);}catch(e){} } }
  else{ stam=Math.min(100,stam+dt*(moving?9:18)); if(tired&&stam>=30){ tired=false; } }
  if(state==='play'){ const sb=$('stb'); sb.style.width=stam.toFixed(0)+'%'; sb.style.background=tired?'#b3141a':(stam<30?'#d98a3a':'#d9b45a'); }
  if(hidden&&curSpot){
    if(curSpot.type==='ward'){ yaw=curSpot.yaw; pitch=0; }       // trốn trong tủ: chỉ nhìn qua khe hở, không xoay camera được
    else { yaw=Math.max(curSpot.yaw-.75,Math.min(curSpot.yaw+.75,yaw)); pitch=Math.max(-.35,Math.min(.4,pitch)); }
  }
  if(!hidden) camera.position.y=1.6+(moving?Math.sin(bob)*0.04:0);
  if(intro.on) introUpdate(dt);
  nextL.intensity=blackT>0?0:(rooms[door+1]?.3:0); prevL.intensity=blackT>0?0:(rooms[door-1]?.15:0);
  if(doorOpen){ if(doorPivot.rotation.y>-1.7) doorPivot.rotation.y=Math.max(-1.7,doorPivot.rotation.y-dt*1.5);   // cánh cửa mở vào phía trong phòng
    if(doorGlow&&rooms[door+1]) doorGlow.visible=false;      // đã có phòng sau -> thấy thẳng phòng sau qua ô cửa
    doorLight.intensity=Math.min(1.8,doorLight.intensity+dt*1.5); }

  // mắt trong bóng tối: chỉ hiện khi bạn không nhìn vào
  const fxv=-Math.sin(yaw), fzv=-Math.cos(yaw);
  watchers.forEach(w=>{
    const dx=w.g.position.x-camera.position.x, dzv=w.g.position.z-camera.position.z, d=Math.hypot(dx,dzv)||1;
    const dot=(dx*fxv+dzv*fzv)/d, on=Math.sin(tt*.5+w.off)>-0.3;
    w.g.visible=on&&dot<0.45&&!hidden;
    w.g.children.forEach(e=>e.scale.y=(Math.sin(tt*2+w.off)>0.97)?0.05:0.8);
  });

  // tương tác
  cur=null; let txt='';
  if(hidden){ txt=gh.phase==='idle'?'[E] Ra khỏi chỗ trốn':'Đừng cử động...'; }
  else if(!modalOpen&&!transitioning&&!intro.on){
    const px=camera.position.x,pz=camera.position.z; let best=99;
    for(const o of inter){
      if(o.kind==='clue'&&solved[o.idx]) continue;
      if(o.kind==='door'&&doorOpen) continue;
      const dx=o.x-px,dzz=o.z-pz,d=Math.hypot(dx,dzz);
      if(d<o.r&&(dx*fxv+dzz*fzv)/(d||1)>0.35&&d<best){best=d;cur=o;}
    }
    if(cur) txt=cur.kind==='hide'?(cur.type==='bed'?'[E] Chui xuống gầm bàn bóng bàn':'[E] Trốn vào bụi cây'):cur.kind==='door'?(keySolved?'[E] Mở cổng thoát':'[E] Cổng thoát (cần đoán đúng từ khóa)'):'[E] Lấy mảnh ghép (nhìn hình đoán)';
  }
  const p=$('prompt'); p.style.display=txt?'block':'none'; p.textContent=txt;

  // sự kiện ngẫu nhiên + nhịp tim
  const ghostOn=gh.phase!=='idle';
  if(!modalOpen&&!transitioning&&!ghostOn){
    nextFlick-=dt; if(nextFlick<=0){flickT=.5;nextFlick=10+Math.random()*15;tone(120,.5,'sawtooth',.05,60);}
    evT-=dt; if(evT<=0){evT=12+Math.random()*14;tone(rnd(110,240),.8,'sawtooth',.04,rnd(60,100)); if(Math.random()<.6)whisper();}
  }
  if(!modalOpen&&!transitioning&&!intro.on){
    if(blackT>0){ blackT-=dt; if(blackT<=0) endBlackout(); }
    else { nextBlack-=dt; if(nextBlack<=0) startBlackout(); }
    if(!hidden){ if(shDur<=0){ nextShadow-=dt; if(nextShadow<=0) startShadow(); } }
  }
  updShadow(dt);
  hbT-=dt;
  if(hbT<=0){
    if(ghostOn&&gh.phase!=='leave'){const dd=Math.hypot(gh.x-camera.position.x,gh.z-camera.position.z);
      const iv=gh.phase==='warn'?.8:(gh.phase==='search'?.42:.38+.5*Math.min(1,Math.max(0,(dd-2)/12)));
      tone(55,.12,'sine',.4,40);setTimeout(()=>tone(48,.12,'sine',.32,36),150);hbT=iv;shake=Math.max(shake,.012);}
    else if(hp===1){tone(55,.12,'sine',.35,40);setTimeout(()=>tone(48,.12,'sine',.3,36),170);hbT=.85;}
    else hbT=.3;
  }
  if(droneG&&AC){const dd=ghostOn?Math.hypot(gh.x-camera.position.x,gh.z-camera.position.z):99;
    droneG.gain.setTargetAtTime(ghostOn?(.05+.12*Math.max(0,1-dd/18)):0,AC.currentTime,.3);}

  // ánh sáng: tối dần khi ma xuất hiện
  const dtarget=gh.phase==='warn'?.5:(ghostOn?.9:0); dark+=(dtarget-dark)*Math.min(1,dt*3);
  lampF=1; if(flickT>0){flickT-=dt;lampF=Math.random()<.5?.08:1;}
  if(gh.phase==='warn') lampF=(Math.sin(tt*40)>.1&&Math.random()<.55)?1:.04;
  else if(ghostOn) lampF=Math.random()<.1?.6:.05+Math.random()*.08;
  if(RF) lampF=gh.phase==='warn'?.35+.25*Math.sin(tt*2.5):(ghostOn?.12:(flickT>0?.5:1));   // chế độ giảm chớp: đèn mờ/sáng chậm, không nhấp nháy
  // Sét đánh: đèn điện trong phòng tắt phụt đúng 1 nhịp lúc tia chớp rồi sáng lại (giảm chớp: chỉ mờ đi nhẹ)
  if(boltT>0&&(1-boltT)<.22) lampF=Math.min(lampF,RF?.45:.04);
  let bf=1;
  if(blackT>0){ const el=blackD-blackT; bf=(!RF&&(el<.6||blackT<.8))?(Math.random()<.35?1:0):0; lampF*=bf; }
  ambL.intensity=blackT>0?(.02+flashV*1.2):(.22*(1-dark*.7)+flashV*1.2);
  lamp.intensity=.3*lampF; lampB.intensity=.22*lampF;
  if(flameMat){const v=Math.max(blackT>0?.04:.15,lampF);flameMat.color.setRGB(v*.94,v*.98,v);}
  if(!hidden) spot.intensity=flashOn&&!intro.on?(blackT>0?3.8:1.5)*(0.96+0.04*Math.sin(tt*23))*(ghostOn&&blackT<=0?.5:1):0;
  flashAmt+=((flashOn&&!hidden&&!intro.on)?1-flashAmt:-flashAmt)*Math.min(1,dt*10);
  flashG.visible=flashAmt>.03; flashG.position.set(Math.sin(bob*.5)*.006,-(1-flashAmt)*.4+Math.abs(Math.sin(bob))*.005*(moving?1:0),0);

  updGhost(dt);
}

let last=performance.now();
function loop(now){
  requestAnimationFrame(loop);
  const dt=Math.min(0.05,(now-last)/1000); last=now;
  update(dt);
  camera.rotation.set(pitch,yaw,Math.sin(tt*.7)*0.004);
  if(shake>0){camera.rotation.z+=(Math.random()-.5)*shake;camera.rotation.x+=(Math.random()-.5)*shake*.4;shake=Math.max(0,shake-dt*.6);}
  renderer.render(scene,camera);
}
applyQuality(true);
buildRoom(); camera.position.set(0,1.6,RD/2-2);
musicStart();
requestAnimationFrame(loop);
})();
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# STREAMLIT
# ---------------------------------------------------------------------------
# Khung game luôn 16:9 theo chiều rộng trang
st.markdown(
    """
<style>
.block-container{padding:3.2rem 1rem 0 1rem !important;max-width:100% !important;}
iframe[title="streamlit.components.v1.html"]{
    width:100% !important;height:auto !important;aspect-ratio:16/9;
    max-height:calc(100vh - 4rem);border:0;background:#000;}
</style>
""",
    unsafe_allow_html=True,
)

MENU_BG = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAOEA4QDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD8qqKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACijFFABRRRQAUUUUAFFFFABRRRQAUUYooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKMUU9BQNK7GYpQKkZajKn0oTHKNgIwKAOKXoOaFK45JpyfYlBiinZTPU0fu/7x/KpTaLGkZppGKk+Tsx/Kl256E1fMnuHLfYixRg+lWFtpX+6rH6CnjTrpukTn8KzcorqHI+xVGR2oIPpVr+z7pTgxP+VBsbnH+qf8qfNHuHJLsVMUo61M1tIvVWH4U3y9v3iR+FF0HKxlFO/d/3j+VIdmeGNBFhh60U7C+tGQO9NDG4pw6UoBPQE0uwjtTaC1xtNPWpCvFMYc0ILWEoooqtBBRRRUsAooopAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRQBml20AJRQRilCk0AJRS45xQV4oASilC+uaML6mgBMUDip4L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GWRikp78E4pCuBmvqLdjzkr6jaKKKBhTadTaACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoopQM0AJRQRigAmgBVGWFTNGTgKCTUYXaRnpXf/C7wBdeN9ft7e3id0ZwDgVzV68MPTdWbskXBOUuWJ3f7OnwKu/H/iC2kaBmh3jORxX65fCX4bWfw88O28EMIR9oyQPavPv2afglbfD7w9BNNAFmKg5Ir3bzywKjgA8V/L3F3Ev1+t7OnK8D7XLsFyLmaJo1CknOcmpfxqCAEcmps5r8hbbl7ux77VgJoOBSGg11R8wAnNFFGMiiM+4xCaBRtpQtZSipO4BRS4HrRgetKxIgopcCkqkNBRRRVDCiiikwCiiipAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKQ9KWkPSgBtFFFABRRRQAUUUUAKvWnU1etOoAKKKKACiiigApV60lAOKaAfRSZozVEi0w9acTTaTGgoooqUMKcOlNpwPFVcTFopM0ZqkxCNSU4nim1jJajQho460pGaTbRGCerGQ6hYQarYS206eYHBGDX50ftjfsxNaT3Gq6fbEbiWO1a/R3lGBHasfxl4Ws/GWiz2txGHZlIGRX3PDmfVsrrxinoeTjcMq8XY/n81fTZNMuWglUq6sQQRVEsTwa+tP2uP2erjwVrFxfW8DCJnJGBXyc8bRna6kNnvX9a5ZmFLMcOq1J3Pg61GdGTjJEdFFFexsYrUKbT8UwjFSAUUUUwCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACl3UlOUcU0rgIRmprcLuwajjXLYPSrL26+WCmTITgAVEn0DfQtabpT6zqsVjErNJIwUAV+oH7FX7NCaBpMOqapb4cgMu8V89/sSfszy/EDVYdcvYGKQsGG4V+p2m2kGjaTDY28Yj8oBeBX4dx1xC6UfqdCXqfT5bgrvnZIoRIfJjG1U4AFOii70RxfMWPerCriv5ysn8R9i3yRsgAwKSlPFJRZLSJEbtahRRRQWHaijtRWTJYUo6GkpR0NNAJRRRTKCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo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VaP490+C0urhEnOBlm5r6CVoZY1lt385W5BU5r+f/wAJ+PNY8JX8VzY3MkQVs4DV95fs1/t4qk1to+syFmYhd7mvwbiHgWdJOtg1zL8j6bD5kpu0j9EOnXg0lUPDXiHS/F2mRXtndpKXGdqtWgFcEgoQPWvw2vhauFm41VY+kpzUldCUUpGO9IeKwehtcUdaD1pobJp/160rX1RMhtKOtBGKBSIButJSk5pKaNEFFFFMoKKKKggKKKKYBRRRTuVcKKKKTEwooopCCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAClXrSU5RTAWilFOVAx60npuS2kMpj9aldNnvVaSYqeFLURlroWtdiZOnNMggeablTt9als0iuELXDeQq9SxxXiHx5/am0H4QWNxDDcpNPggbWB5r3cuynE5nUUaUbnBia8aa1Z6P8QPiNpHw802We4uU8xRnaWr88f2kv2yZ9Za4s9MnZVJK/K1eF/G39qTWfiVqc7Q3Mi27McKG7V4TeXkl45eZmZyc5Jr+huHuCqeDUauKWvY+XxGYXvGDLPiHxJe+Ir6S4vJWkLMTyaysjt0pW5FISAK/XoQjTiowVj56TbYjUlBOaKoQUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAKvSlpF6UtABRRRQAUUUUAFFFKOtNW6iYckYzxVq0na12y27Mk6nIYHmq3SjJ7HFNpSXkOMnF3R9Kfs9/ta678NL+GHUbyWe2DDAdu1fpR8Jf2p9B+JdjADOkUhABywr8RQm75iSTXU+DviTrXgy9jls7mSONWztDGvz7POEsLmfNUgrTZ6tDMakLRufvpDNBeIJIJRIp9DU2G7jAr83PgT+3G9v5FpqUxYggEs1fbfgL44aL4ytYit0gZv9qv50zrhjGZdJuotD6jC5jCejPSAuDTzUcEkNygeBvMB9DUoRgPmXFfD2ktEexzc2o0nNA60pxSCkAN1pKU80lUjRBRRRTKCiiioICiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigApy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UUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAKBmjbSjpRQVYTbSg4OKKT+KgTQ7NJRRSsTYD0ptOPSm0xhml3UlFNNoAJzRRRRe4C7qN1JRSAXdRupKKAF3UbqSigAPJooooAKAcUUUABOaUHFJRVWAXdRupKKT1DYUtSZoopAFFFFAC7qN1JRQKwu40bqSiruxi7qM0lFDYC7qN1JRUALuo3UlFAC7qN1JRSsAu6koopgFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQA4dKKQHFG6gq4tJ/FRupM85oEx1FJuo3UCFPSm0pOaSgAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKq4BRRRSAKKKKQBRRRQAUUUUAFFFFVcAoooouAUUUVIBRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUDrQA4cUUUUAFNPWnUh+9QAbaNtLRQVYTbSU49KbQJhRRRQIKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiimgCiiiqAKKKKgAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACgdaKKAHUUUUAFIfvUUUALRRRQWB6U2iiglhRRRQIKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiimgCiiiqAKKKKgAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD//2Q=="

_html = (GAME_HTML.replace("__DATA__", build_data())
         .replace("__POOL__", build_pool())
         .replace("__FIXED__", build_fixed())
         .replace("__BONUS__", build_bonus())
         .replace("__PUZ__", build_puz())
         .replace("__MENUBG__", MENU_BG)
         .replace("__MUSIC__", load_mp3(MUSIC_FILE, PLAY_MUSIC_FILE, True))
         .replace("__MUSIC2__", load_mp3(PLAY_MUSIC_FILE))
         .replace("__CATCH__", load_mp3(CATCH_FILE))
         .replace("__GHOST__", load_mp3(GHOST_FILE))
         .replace("__STEP__", load_mp3(STEP_FILE))
         .replace("__SIREN__", load_mp3(SIREN_FILE))
         .replace("__SCLIPS__", json.dumps(STEP_CLIPS))
         .replace("__THUNDER__", load_asset(THUNDER_FILE, "audio/mpeg"))
         .replace("__RAIN__", load_asset(RAIN_FILE, "audio/wav"))
         .replace("__TCLIPS__", json.dumps(THUNDER_CLIPS)))
components.html(_html, height=720, scrolling=False)
st.download_button("Tải game (.html) để chơi độc lập", _html, file_name="verity_escape.html", mime="text/html")
