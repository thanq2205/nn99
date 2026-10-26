import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(page_title="Verity Escape 3D", layout="wide")

st.title("🏫 Dự án Tin Học: VERITY ESCAPE (3D)")
st.caption("Thành viên: Đỗ Nhật Minh, Trương Thị Ngọc Ngân, Nguyễn Quỳnh Trâm, Nguyễn Thái Dương, Nguyễn Hữu Tân.")

# Mô tả luật chơi bằng giao diện Streamlit
with st.sidebar:
    st.header("🎮 Hướng dẫn chơi")
    st.markdown("""
    - **Di chuyển**: Dùng các phím **W, A, S, D** trên bàn phím.
    - **Xoay góc nhìn**: Dùng phím mũi tên **Trái (←) / Phải (→)**.
    - **Nhiệm vụ**: Tìm bức tranh manh mối trong mê cung trường học, giải mã ô chữ và **nhập đáp án vào hộp thoại trực tiếp trong game**.
    - **Thử thách**: Tránh xa quái vật **Verity** đang đuổi theo bạn!
    - **Giới hạn**: Bạn có **3 tim** và **2 phút** cho mỗi màn (Tổng cộng: 6 màn).
    """)
    st.info("Nhấp chuột vào khung màn hình game để bắt đầu điều khiển.")

# Mã nguồn HTML5 + CSS + JS cho Game 3D Raycasting
game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; padding: 0; background-color: #111; font-family: sans-serif; color: white; overflow: hidden; }
        #game-container { position: relative; width: 800px; height: 500px; margin: 10px auto; border: 4px solid #333; background: #000; }
        canvas { display: block; width: 100%; height: 100%; }
        #ui-overlay { position: absolute; top: 10px; left: 10px; font-size: 16px; text-shadow: 2px 2px black; z-index: 10; }
        #puzzle-box { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); padding: 15px; border: 2px solid #555; border-radius: 8px; text-align: center; display: none; z-index: 10; width: 300px; }
        #puzzle-box input { padding: 5px; width: 150px; font-size: 16px; text-align: center; text-transform: uppercase; }
        #puzzle-box button { padding: 5px 10px; font-size: 16px; cursor: pointer; margin-left: 5px; }
        #screen-msg { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 32px; text-align: center; text-shadow: 3px 3px black; font-weight: bold; z-index: 20; width: 100%; }
    </style>
</head>
<body>

<div id="game-container">
    <div id="ui-overlay">
        <div>🎬 Màn: <span id="lbl-level">1</span>/6</div>
        <div>❤️ Tim: <span id="lbl-lives">❤️❤️❤️</span></div>
        <div>⏳ Thời gian: <span id="lbl-time">02:00</span></div>
    </div>
    
    <div id="screen-msg">BẤM VÀO ĐÂY ĐỂ CHƠI</div>
    
    <div id="puzzle-box">
        <div style="margin-bottom: 8px; font-weight: bold; color: #ffeb3b;">🧩 ĐÃ TÌM THẤY TRANH MANH MỐI!</div>
        <div id="puzzle-hint" style="font-size: 14px; margin-bottom: 10px; font-style: italic;"></div>
        <input type="text" id="ans-input" placeholder="Nhập đáp án...">
        <button onclick="checkAnswer()">Nộp</button>
        <div id="wrong-count" style="font-size:12px; color:red; margin-top:5px;"></div>
    </div>

    <canvas id="gameCanvas" width="400" height="250"></canvas>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Mê cung giả lập trường học (1: Tường, 0: Đường đi, 3: Tranh manh mối câu đố)
const defaultMap = [,
 ,
 ,
 ,
 ,
 ,
    [1,1,1,1,1,1,1,1]
];

// Cấu hình đầy đủ cho 6 màn chơi
const levels = [
    { map: defaultMap, px:1.5, py:1.5, hint: "Môn học nghiên cứu về máy tính (6 chữ cái, viết liền không dấu)", ans: "TINHOC" },
    { map: defaultMap, px:1.5, py:1.5, hint: "Nơi học sinh đến học mỗi ngày (9 chữ cái, viết liền không dấu)", ans: "TRUONGHOC" },
    { map: defaultMap, px:1.5, py:1.5, hint: "Thiết bị dùng để gõ văn bản, lướt web (7 chữ cái, viết liền không dấu)", ans: "MAYTINH" },
    { map: defaultMap, px:1.5, py:1.5, hint: "Thầy cô truyền đạt kiến thức qua mỗi... (6 chữ cái, viết liền không dấu)", ans: "BAIHOC" },
    { map: defaultMap, px:1.5, py:1.5, hint: "Đồ vật luôn nằm trong cặp sách học sinh (6 chữ cái, viết liền không dấu)", ans: "SACHVO" },
    { map: defaultMap, px:1.5, py:3.5, hint: "Tên hành động thoát khỏi căn phòng bí ẩn (6 chữ cái, Tiếng Anh)", ans: "ESCAPE" }
];

let currentLevelIdx = 0;
let map = levels[currentLevelIdx].map;
let player = { x: 1.5, y: 1.5, angle: 0, lives: 3, wrongAnswers: 0 };
let monster = { x: 5.5, y: 2.5, speed: 0.015 };
let keys = {};
let gameActive = false;
let timeLeft = 120;
let timerInterval;

// Xử lý sự kiện bàn phím
window.addEventListener("keydown", e => { keys[e.key.toLowerCase()] = true; });
window.addEventListener("keyup", e => { keys[e.key.toLowerCase()] = false; });

document.getElementById("game-container").addEventListener("click", () => {
    if(!gameActive && player.lives > 0 && currentLevelIdx < 6) {
        gameActive = true;
        document.getElementById("screen-msg").style.display = "none";
        startTimer();
    }
});

function startTimer() {
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        if(!gameActive) return;
        timeLeft--;
        let mins = Math.floor(timeLeft / 60).toString().padStart(2, '0');
        let secs = (timeLeft % 60).toString().padStart(2, '0');
        document.getElementById("lbl-time").innerText = mins + ":" + secs;
        if(timeLeft <= 0) {
            endGame(false, "HẾT THỜI GIAN!");
        }
    }, 1000);
}

function loadLevel(idx) {
    if(idx >= levels.length) {
        endGame(true, "🎉 CHÚC MỪNG NHÓM BẠN ĐÃ CHIẾN THẮNG!");
        return;
    }
    currentLevelIdx = idx;
    map = levels[currentLevelIdx].map;
    player.x = levels[currentLevelIdx].px;
    player.y = levels[currentLevelIdx].py;
    player.angle = 0;
    player.wrongAnswers = 0;
    
    monster.x = 5.5; monster.y = 5.5;
    monster.speed = 0.012 + (idx * 0.003); 
    timeLeft = Math.max(120 - (idx * 10), 60); 
    
    document.getElementById("lbl-level").innerText = currentLevelIdx + 1;
    document.getElementById("puzzle-box").style.display = "none";
    document.getElementById("wrong-count").innerText = "";
}

function checkAnswer() {
    let input = document.getElementById("ans-input").value.trim().toUpperCase();
    if(input === levels[currentLevelIdx].ans) {
        document.getElementById("ans-input").value = "";
        loadLevel(currentLevelIdx + 1);
    } else {
        player.wrongAnswers++;
        document.getElementById("wrong-count").innerText = "Sai lần " + player.wrongAnswers + "/3";
        if(player.wrongAnswers >= 3) {
            player.lives--;
            player.wrongAnswers = 0;
            updateLivesUI();
            if(player.lives <= 0) {
                endGame(false, "☠️ BẠN ĐÃ HẾT TIM!");
            } else {
                alert("Giải sai 3 lần! Bạn mất 1 tim. Hệ thống đưa bạn quay lại màn 1.");
                loadLevel(0); 
            }
        }
    }
}

function updateLivesUI() {
    let hearts = "";
    for(let i=0; i<3; i++) hearts += i < player.lives ? "❤️" : "🖤";
    document.getElementById("lbl-lives").innerText = hearts;
}

function endGame(victory, msg) {
    gameActive = false;
    clearInterval(timerInterval);
    const screenMsg = document.getElementById("screen-msg");
    screenMsg.innerHTML = msg + "<br><span style='font-size:16px;'>Nhấn F5 (Tải lại trang) để chơi lại</span>";
    screenMsg.style.display = "block";
}

function updateAndRender() {
    if(gameActive) {
        let moveSpeed = 0.04;
        let rotSpeed = 0.04;
        let newX = player.x;
        let newY = player.y;

        if (keys["w"]) { newX += Math.cos(player.angle) * moveSpeed; newY += Math.sin(player.angle) * moveSpeed; }
        if (keys["s"]) { newX -= Math.cos(player.angle) * moveSpeed; newY -= Math.sin(player.angle) * moveSpeed; }
        if (keys["a"]) { newX += Math.sin(player.angle) * moveSpeed; newY -= Math.cos(player.angle) * moveSpeed; }
        if (keys["d"]) { newX -= Math.sin(player.angle) * moveSpeed; newY += Math.cos(player.angle) * moveSpeed; }
        if (keys["arrowleft"]) player.angle -= rotSpeed;
        if (keys["arrowright"]) player.angle += rotSpeed;

        if (map[Math.floor(player.y)][Math.floor(newX)] !== 1) player.x = newX;
        if (map[Math.floor(newY)][Math.floor(player.x)] !== 1) player.y = newY;

        let dx = player.x - monster.x;
        let dy = player.y - monster.y;
        let dist = Math.sqrt(dx*dx + dy*dy);
        if(dist > 0.3) {
            monster.x += (dx / dist) * monster.speed;
            monster.y += (dy / dist) * monster.speed;
        } else {
            player.lives--;
            updateLivesUI();
            if(player.lives <= 0) {
                endGame(false, "👻 VERITY ĐÃ BẮT ĐƯỢC BẠN!");
            } else {
                alert("Bạn bị Verity bắt! Mất 1 tim. Hệ thống đưa bạn quay lại màn 1.");
                loadLevel(0);
            }
        }

        if(map[Math.floor(player.y)][Math.floor(player.x)] === 3) {
            document.getElementById("puzzle-hint").innerText = levels[currentLevelIdx].hint;
            document.getElementById("puzzle-box").style.display = "block";
        } else {
            document.getElementById("puzzle-box").style.display = "none";
        }
    }

    ctx.fillStyle = "#222"; ctx.fillRect(0, 0, canvas.width, canvas.height/2);
    ctx.fillStyle = "#444"; ctx.fillRect(0, canvas.height/2, canvas.width, canvas.height/2);

    const fov = Math.PI / 3;
    const numRays = canvas.width;
    for (let i = 0; i < numRays; i++) {
        let rayAngle = (player.angle - fov/2) + (i / numRays) * fov;
        let distance = 0;
        let hitWall = false;
        let wallType = 0;

        while (!hitWall && distance < 16) {
            distance += 0.05;
            let checkX = Math.floor(player.x + Math.cos(rayAngle) * distance);
            let checkY = Math.floor(player.y + Math.sin(rayAngle) * distance);


Cuộc trò chuyện ở Chế độ AI: t muốn làm game 3d góc nhìn thứ nhất wasd app.py github streamlit sửa thành 6 màn thôi


Bạn đã gửi: 2 hình ảnh và nói: t muốn làm game 3d góc nhìn thứ nhất wasd app.py github streamlit sửa thành 6 màn thôi

t muốn làm game 3d góc nhìn thứ nhất wasd app.py github streamlit sửa thành 6 màn thôi
Để xây dựng một trò chơi 3D góc nhìn thứ nhất (di chuyển bằng WASD) chạy trực tiếp trên Streamlit (app.py) và sẵn sàng đẩy lên GitHub, phương pháp tối ưu và mượt mà nhất là nhúng mã nguồn HTML5 Canvas 3D (Raycasting/Three.js) bằng JavaScript vào bên trong thành phần st.components.v1.html. Điều này giúp game chạy mượt mà ngay trên trình duyệt mà không bị giật lag do cơ chế load lại trang của Streamlit.
Dưới đây là toàn bộ mã nguồn file app.py hoàn chỉnh được thiết kế theo đúng ý tưởng "Verity Escape" của nhóm (bối cảnh trường học, quái vật đuổi theo, giải đố tìm từ khóa, 3 tim, thời gian 2 phút và rút ngắn xuống 6 màn).

1. Mã nguồn file app.py

python
import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(page_title="Verity Escape 3D", layout="wide")

st.title("🏫 Dự án Tin Học: VERITY ESCAPE (3D)")
st.caption("Thành viên: Đỗ Nhật Minh, Trương Thị Ngọc Ngân, Nguyễn Quỳnh Trâm, Nguyễn Thái Dương, Nguyễn Hữu Tân.")

# Mô tả luật chơi bằng giao diện Streamlit
with st.sidebar:
    st.header("🎮 Hướng dẫn chơi")
    st.markdown("""
    - **Di chuyển**: Dùng các phím **W, A, S, D** trên bàn phím.
    - **Xoay góc nhìn**: Dùng phím mũi tên **Trái (←) / Phải (→)**.
    - **Nhiệm vụ**: Tìm bức tranh manh mối trong mê cung trường học, giải mã ô chữ và **nhập đáp án vào hộp thoại trực tiếp trong game**.
    - **Thử thách**: Tránh xa quái vật **Verity** đang đuổi theo bạn!
    - **Giới hạn**: Bạn có **3 tim** và **2 phút** cho mỗi màn (Tổng cộng: 6 màn).
    """)
    st.info("Nhấp chuột vào khung màn hình game để bắt đầu điều khiển.")

# Mã nguồn HTML5 + CSS + JS cho Game 3D Raycasting
game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; padding: 0; background-color: #111; font-family: sans-serif; color: white; overflow: hidden; }
        #game-container { position: relative; width: 800px; height: 500px; margin: 10px auto; border: 4px solid #333; background: #000; }
        canvas { display: block; width: 100%; height: 100%; }
        #ui-overlay { position: absolute; top: 10px; left: 10px; font-size: 16px; text-shadow: 2px 2px black; z-index: 10; }
        #puzzle-box { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); padding: 15px; border: 2px solid #555; border-radius: 8px; text-align: center; display: none; z-index: 10; width: 300px; }
        #puzzle-box input { padding: 5px; width: 150px; font-size: 16px; text-align: center; text-transform: uppercase; }
        #puzzle-box button { padding: 5px 10px; font-size: 16px; cursor: pointer; margin-left: 5px; }
        #screen-msg { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 32px; text-align: center; text-shadow: 3px 3px black; font-weight: bold; z-index: 20; width: 100%; }
    </style>
</head>
<body>

<div id="game-container">
    <div id="ui-overlay">
        <div>🎬 Màn: <span id="lbl-level">1</span>/6</div>
        <div>❤️ Tim: <span id="lbl-lives">❤️❤️❤️</span></div>
        <div>⏳ Thời gian: <span id="lbl-time">02:00</span></div>
    </div>
    
    <div id="screen-msg">BẤM VÀO ĐÂY ĐỂ CHƠI</div>
    
    <div id="puzzle-box">
        <div style="margin-bottom: 8px; font-weight: bold; color: #ffeb3b;">🧩 ĐÃ TÌM THẤY TRANH MANH MỐI!</div>
        <div id="puzzle-hint" style="font-size: 14px; margin-bottom: 10px; font-style: italic;"></div>
        <input type="text" id="ans-input" placeholder="Nhập đáp án...">
        <button onclick="checkAnswer()">Nộp</button>
        <div id="wrong-count" style="font-size:12px; color:red; margin-top:5px;"></div>
    </div>

    <canvas id="gameCanvas" width="400" height="250"></canvas>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Cấu hình 6 màn chơi
const levels = [
    { map: [ [1,1,1,1,1,1,1,1],[1,0,0,0,0,3,0,1],[1,0,1,1,0,1,0,1],[1,0,0,0,0,0,0,1],[1,1,1,1,1,1,1,1] ], px:1.5, py:1.5, hint: "Gợi ý: Môn học nghiên cứu về máy tính (6 chữ cái, viết liền không dấu)", ans: "TINHOC" },
    { map: [ [1,1,1,1,1,1,1,1],[1,0,0,1,0,0,0,1],[1,3,0,0,0,1,0,1],[1,0,1,1,0,0,0,1],[1,1,1,1,1,1,1,1] ], px:1.5, py:1.5, hint: "Gợi ý: Nơi học sinh đến học mỗi ngày (9 chữ cái, viết liền không dấu)", ans: "TRUONGHOC" },
    { map: [ [1,1,1,1,1,1,1,1],[1,0,0,0,0,0,0,1],[1,0,1,1,1,1,0,1],[1,0,0,3,0,0,0,1],[1,1,1,1,1,1,1,1] ], px:1.5, py:1.5, hint: "Gợi ý: Thiết bị dùng để gõ văn bản, lướt web (7 chữ cái, viết liền không dấu)", ans: "MAYTINH" },
    { map: [ [1,1,1,1,1,1,1,1],[1,0,1,0,0,0,3,1],[1,0,1,0,1,1,0,1],[1,0,0,0,0,0,0,1],[1,1,1,1,1,1,1,1] ], px:1.5, py:1.5, hint: "Gợi ý: Thầy cô truyền đạt kiến thức qua mỗi... (6 chữ cái, viết liền không dấu)", ans: "BAIHOC" },
    { map: [ [1,1,1,1,1,1,1,1],[1,0,0,0,0,0,0,1],[1,1,0,1,1,1,0,1],[1,3,0,0,0,0,0,1],[1,1,1,1,1,1,1,1] ], px:1.5, py:1.5, hint: "Gợi ý: Đồ vật luôn nằm trong cặp sách học sinh (6 chữ cái, viết liền không dấu)", ans: "SACHVO" },
    { map: [ [1,1,1,1,1,1,1,1],[1,0,0,0,0,3,0,1],[1,0,1,1,0,1,0,1],[1,0,0,0,0,0,0,1],[1,1,1,1,1,1,1,1] ], px:1.5, py:3.5, hint: "Gợi ý: Tên hành động thoát khỏi căn phòng bí ẩn (6 chữ cái, Tiếng Anh)", ans: "ESCAPE" }
];

let currentLevelIdx = 0;
let map = levels[currentLevelIdx].map;
let player = { x: 1.5, y: 1.5, angle: 0, lives: 3, wrongAnswers: 0 };
let monster = { x: 5.5, y: 2.5, speed: 0.015 };
let keys = {};
let gameActive = false;
let timeLeft = 120;
let timerInterval;

// Xử lý sự kiện bàn phím
window.addEventListener("keydown", e => { keys[e.key.toLowerCase()] = true; });
window.addEventListener("keyup", e => { keys[e.key.toLowerCase()] = false; });

document.getElementById("game-container").addEventListener("click", () => {
    if(!gameActive && player.lives > 0 && currentLevelIdx < 6) {
        gameActive = true;
        document.getElementById("screen-msg").style.display = "none";
        startTimer();
    }
});

function startTimer() {
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        if(!gameActive) return;
        timeLeft--;
        let mins = Math.floor(timeLeft / 60).toString().padStart(2, '0');
        let secs = (timeLeft % 60).toString().padStart(2, '0');
        document.getElementById("lbl-time").innerText = mins + ":" + secs;
        if(timeLeft <= 0) {
            endGame(false, "HẾT THỜI GIAN!");
        }
    }, 1000);
}

function loadLevel(idx) {
    if(idx >= levels.length) {
        endGame(true, "🎉 CHÚC MỪNG NHÓM BẠN ĐÃ CHIẾN THẮNG!");
        return;
    }
    currentLevelIdx = idx;
    map = levels[currentLevelIdx].map;
    player.x = levels[currentLevelIdx].px;
    player.y = levels[currentLevelIdx].py;
    player.angle = 0;
    player.wrongAnswers = 0;
    
    // Đặt vị trí quái vật ngẫu nhiên cách xa người chơi
    monster.x = 6.5; monster.y = 2.5;
    monster.speed = 0.015 + (idx * 0.005); // Độ khó tăng dần, quái vật chạy nhanh hơn
    timeLeft = Math.max(120 - (idx * 10), 60); // Thời gian ít dần đi ở màn cao
    
    document.getElementById("lbl-level").innerText = currentLevelIdx + 1;
    document.getElementById("puzzle-box").style.display = "none";
    document.getElementById("wrong-count").innerText = "";
}

function checkAnswer() {
    let input = document.getElementById("ans-input").value.trim().toUpperCase();
    if(input === levels[currentLevelIdx].ans) {
        document.getElementById("ans-input").value = "";
        loadLevel(currentLevelIdx + 1);
    } else {
        player.wrongAnswers++;
        document.getElementById("wrong-count").innerText = "Sai lần " + player.wrongAnswers + "/3";
        if(player.wrongAnswers >= 3) {
            player.lives--;
            player.wrongAnswers = 0;
            updateLivesUI();
            if(player.lives <= 0) {
                endGame(false, "☠️ BẠN ĐÃ HẾT TIM!");
            } else {
                alert("Giải sai 3 lần! Bạn mất 1 tim. Hãy thử lại!");
                loadLevel(0); // Quay lại màn đầu theo đúng yêu cầu
            }
        }
    }
}

function updateLivesUI() {
    let hearts = "";
    for(let i=0; i<3; i++) hearts += i < player.lives ? "❤️" : "🖤";
    document.getElementById("lbl-lives").innerText = hearts;
}

function endGame(victory, msg) {
    gameActive = false;
    clearInterval(timerInterval);
    const screenMsg = document.getElementById("screen-msg");
    screenMsg.innerHTML = msg + "<br><span style='font-size:16px;'>F5 tải lại trang để chơi lại</span>";
    screenMsg.style.display = "block";
}

// Thuật toán Raycasting 3D góc nhìn thứ nhất cơ bản
function updateAndRender() {
    if(gameActive) {
        // Điều khiển chuyển động WASD
        let moveSpeed = 0.04;
        let rotSpeed = 0.04;
        let newX = player.x;
        let newY = player.y;

        if (keys["w"]) { newX += Math.cos(player.angle) * moveSpeed; newY += Math.sin(player.angle) * moveSpeed; }
        if (keys["s"]) { newX -= Math.cos(player.angle) * moveSpeed; newY -= Math.sin(player.angle) * moveSpeed; }
        if (keys["a"]) { newX += Math.sin(player.angle) * moveSpeed; newY -= Math.cos(player.angle) * moveSpeed; }
        if (keys["d"]) { newX -= Math.sin(player.angle) * moveSpeed; newY += Math.cos(player.angle) * moveSpeed; }
        if (keys["arrowleft"]) player.angle -= rotSpeed;
        if (keys["arrowright"]) player.angle += rotSpeed;

        // Xử lý va chạm với tường trường học
        if (map[Math.floor(player.y)][Math.floor(newX)] !== 1) player.x = newX;
        if (map[Math.floor(newY)][Math.floor(player.x)] !== 1) player.y = newY;

        // Trí tuệ nhân tạo của Quái vật Verity đuổi theo người chơi
        let dx = player.x - monster.x;
        let dy = player.y - monster.y;
        let dist = Math.sqrt(dx*dx + dy*dy);
        if(dist > 0.2) {
            monster.x += (dx / dist) * monster.speed;
            monster.y += (dy / dist) * monster.speed;
        } else {
            // Quái vật bắt được
            player.lives--;
            updateLivesUI();
            if(player.lives <= 0) {
                endGame(false, "👻 VERITY ĐÃ BẮT ĐƯỢC BẠN!");
            } else {
                alert("Bạn bị Verity bắt! Mất 1 tim. Chơi lại từ màn 1!");
                loadLevel(0);
            }
        }

        // Kiểm tra xem người chơi có đứng gần bức tranh câu đố (ô số 3) không
        if(map[Math.floor(player.y)][Math.floor(player.x)] === 3) {
            document.getElementById("puzzle-hint").innerText = levels[currentLevelIdx].hint;
            document.getElementById("puzzle-box").style.display = "block";
        } else {
Hãy thận trọng khi sử dụng mã.
document.getElementById("puzzle-box").style.display = "none";
}
}
// Vẽ nền Trần và Sàn trường học
ctx.fillStyle = "#222"; ctx.fillRect(0, 0, canvas.width, canvas.height/2);
ctx.fillStyle = "#444"; ctx.fillRect(0, canvas.height/2, canvas.width, canvas.height/2);
// Vẽ Raycasting 3D cho các bức tường
const fov = Math.PI / 3;
const numRays = canvas.width;
for (let i = 0; i < numRays; i++) {
let rayAngle = (player.angle - fov/2) + (i / numRays) * fov;
let distance = 0;
let hitWall = false;
let wallType = 0;
while (!hitWall && distance < 16) {
distance += 0.05;
let checkX = Math.floor(player.x + Math.cos(rayAngle) * distance);
let checkY = Math.floor(player.y + Math.sin(rayAngle) * distance);
if (checkX < 0 || checkX >= map[0].length || checkY < 0 || checkY >= map.length) {
hitWall = true; distance = 16;
} else if (map[checkY][checkX] > 0) {
hitWall = true;
wallType = map[checkY][checkX];
}
}
// Sửa méo hình cá mắt chim (Fish-eye correction)
let correctedDist = distance * Math.cos(rayAngle - player.angle);
let wallHeight = Math.min(canvas.height / correctedDist, canvas.height);
// Màu sắc: Số 1 là tường gạch trường học, Số 3 là Bức tranh câu đố
if(wallType === 3) {
ctx.fillStyle = "#ffeb3b"; // Màu vàng nổi bật của tranh manh mối
} else {
let shade = Math.max(50, 180 - correctedDist * 12);
ctx.style = "rgb("+shade+","+shade+","+shade+")";
ctx.fillStyle = ctx.style;
}
ctx.fillRect(i, (canvas.height - wallHeight)/2, 1, wallHeight);
}
requestAnimationFrame(updateAndRender);
}
// Bắt đầu vòng lặp game
loadLevel(0);
updateAndRender();



"""

Nhúng mã nguồn HTML vào ứng dụng Streamlit

components.html(game_html, height=550)

---

### 2. Cấu trúc thư mục chuẩn để đẩy lên GitHub

Để đưa mã nguồn này lên GitHub một cách chỉnh chu và dễ chạy thử, bạn hãy tạo thư mục chứa các file sau:

```text
📁 verity-escape-game/
├── 📄 app.py              (Chứa toàn bộ mã nguồn Python ở mục 1)
├── 📄 requirements.txt    (Khai báo thư viện cần thiết)
└── 📄 README.md           (Tài liệu giới thiệu dự án)

Nội dung file requirements.txt:

text
streamlit>=1.20.0
Hãy thận trọng khi sử dụng mã.

Nội dung file README.md:

markdown
# 🏫 Verity Escape 3D - Dự án môn Tin Học

Trò chơi mô phỏng không gian 3D góc nhìn thứ nhất (Raycasting) làm bằng Python Streamlit và JavaScript HTML5 Canvas.

## 👥 Thành viên nhóm
1. Đỗ Nhật Minh
2. Trương Thị Ngọc Ngân
3. Nguyễn Quỳnh Trâm
4. Nguyễn Thái Dương
5. Nguyễn Hữu Tân

## 🎮 Cách chạy Game dưới máy local
1. Cài đặt thư viện: `pip install -r requirements.txt`
2. Chạy ứng dụng: `streamlit run app.py`
Hãy thận trọng khi sử dụng mã.

3. Cách deploy trực tiếp lên mạng (Streamlit Community Cloud)

Nếu nhóm bạn muốn nộp bài cho thầy cô giáo chạy trực tiếp qua một liên kết trực tuyến:
1. Đẩy thư mục này lên một GitHub Repository công khai.
2. Truy cập trang Streamlit Community Cloud, đăng nhập bằng tài khoản GitHub.
3. Chọn New app, trỏ vào link repo của bạn và nhấn Deploy. Hệ thống sẽ tự động cấp một đường dẫn web chạy game trực tuyến miễn phí!
Mình có thể giúp bạn:
• Thay đổi nội dung từ khóa / gợi ý của 6 màn theo đúng nội dung học tập của nhóm.
• Tăng/giảm tốc độ của quái vật đuổi theo nếu bạn thấy game quá khó hoặc quá dễ.
Bạn có muốn chỉnh sửa thêm tính năng nào khác không?
AI có thể mắc sai sót. Vì vậy, hãy xác minh câu trả lời 

Bạn đã gửi: 1 hình ảnh

Lỗi SyntaxError: unterminated triple-quoted string literal xảy ra do chuỗi HTML dài dùng dấu ba nháy """ ở dòng 23 chưa được đóng lại bằng một dấu ba nháy """ tương ứng ở cuối mã nguồn, hoặc trong đoạn code JavaScript phía dưới có chứa các ký tự đặc biệt vô tình làm lỗi cú pháp Python.
Dưới đây là mã nguồn file app.py đã được sửa hoàn chỉnh, dọn dẹp các mảng bản đồ (map) bị trống để tránh lỗi biên dịch, và đảm bảo đóng chuỗi """ chuẩn xác ở dòng cuối cùng. Bạn chỉ cần copy toàn bộ đoạn code này đè lên file cũ là chạy được ngay.
python
import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(page_title="Verity Escape 3D", layout="wide")

st.title("🏫 Dự án Tin Học: VERITY ESCAPE (3D)")
st.caption("Thành viên: Đỗ Nhật Minh, Trương Thị Ngọc Ngân, Nguyễn Quỳnh Trâm, Nguyễn Thái Dương, Nguyễn Hữu Tân.")

# Mô tả luật chơi bằng giao diện Streamlit
with st.sidebar:
    st.header("🎮 Hướng dẫn chơi")
    st.markdown("""
    - **Di chuyển**: Dùng các phím **W, A, S, D** trên bàn phím.
    - **Xoay góc nhìn**: Dùng phím mũi tên **Trái (←) / Phải (→)**.
    - **Nhiệm vụ**: Tìm bức tranh manh mối trong mê cung trường học, giải mã ô chữ và **nhập đáp án vào hộp thoại trực tiếp trong game**.
    - **Thử thách**: Tránh xa quái vật **Verity** đang đuổi theo bạn!
    - **Giới hạn**: Bạn có **3 tim** và **2 phút** cho mỗi màn (Tổng cộng: 6 màn).
    """)
    st.info("Nhấp chuột vào khung màn hình game để bắt đầu điều khiển.")

# Mã nguồn HTML5 + CSS + JS cho Game 3D Raycasting
game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; padding: 0; background-color: #111; font-family: sans-serif; color: white; overflow: hidden; }
        #game-container { position: relative; width: 800px; height: 500px; margin: 10px auto; border: 4px solid #333; background: #000; }
        canvas { display: block; width: 100%; height: 100%; }
        #ui-overlay { position: absolute; top: 10px; left: 10px; font-size: 16px; text-shadow: 2px 2px black; z-index: 10; }
        #puzzle-box { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); padding: 15px; border: 2px solid #555; border-radius: 8px; text-align: center; display: none; z-index: 10; width: 300px; }
        #puzzle-box input { padding: 5px; width: 150px; font-size: 16px; text-align: center; text-transform: uppercase; }
        #puzzle-box button { padding: 5px 10px; font-size: 16px; cursor: pointer; margin-left: 5px; }
        #screen-msg { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 32px; text-align: center; text-shadow: 3px 3px black; font-weight: bold; z-index: 20; width: 100%; }
    </style>
</head>
<body>

<div id="game-container">
    <div id="ui-overlay">
        <div>🎬 Màn: <span id="lbl-level">1</span>/6</div>
        <div>❤️ Tim: <span id="lbl-lives">❤️❤️❤️</span></div>
        <div>⏳ Thời gian: <span id="lbl-time">02:00</span></div>
    </div>
    
    <div id="screen-msg">BẤM VÀO ĐÂY ĐỂ CHƠI</div>
    
    <div id="puzzle-box">
        <div style="margin-bottom: 8px; font-weight: bold; color: #ffeb3b;">🧩 ĐÃ TÌM THẤY TRANH MANH MỐI!</div>
        <div id="puzzle-hint" style="font-size: 14px; margin-bottom: 10px; font-style: italic;"></div>
        <input type="text" id="ans-input" placeholder="Nhập đáp án...">
        <button onclick="checkAnswer()">Nộp</button>
        <div id="wrong-count" style="font-size:12px; color:red; margin-top:5px;"></div>
    </div>

    <canvas id="gameCanvas" width="400" height="250"></canvas>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Mê cung giả lập trường học (1: Tường, 0: Đường đi, 3: Tranh manh mối câu đố)
const defaultMap = [,
 ,
 ,
 ,
 ,
 ,
    [1,1,1,1,1,1,1,1]
];

// Cấu hình đầy đủ cho 6 màn chơi
const levels = [
    { map: defaultMap, px:1.5, py:1.5, hint: "Môn học nghiên cứu về máy tính (6 chữ cái, viết liền không dấu)", ans: "TINHOC" },
    { map: defaultMap, px:1.5, py:1.5, hint: "Nơi học sinh đến học mỗi ngày (9 chữ cái, viết liền không dấu)", ans: "TRUONGHOC" },
    { map: defaultMap, px:1.5, py:1.5, hint: "Thiết bị dùng để gõ văn bản, lướt web (7 chữ cái, viết liền không dấu)", ans: "MAYTINH" },
    { map: defaultMap, px:1.5, py:1.5, hint: "Thầy cô truyền đạt kiến thức qua mỗi... (6 chữ cái, viết liền không dấu)", ans: "BAIHOC" },
    { map: defaultMap, px:1.5, py:1.5, hint: "Đồ vật luôn nằm trong cặp sách học sinh (6 chữ cái, viết liền không dấu)", ans: "SACHVO" },
    { map: defaultMap, px:1.5, py:3.5, hint: "Tên hành động thoát khỏi căn phòng bí ẩn (6 chữ cái, Tiếng Anh)", ans: "ESCAPE" }
];

let currentLevelIdx = 0;
let map = levels[currentLevelIdx].map;
let player = { x: 1.5, y: 1.5, angle: 0, lives: 3, wrongAnswers: 0 };
let monster = { x: 5.5, y: 2.5, speed: 0.015 };
let keys = {};
let gameActive = false;
let timeLeft = 120;
let timerInterval;

// Xử lý sự kiện bàn phím
window.addEventListener("keydown", e => { keys[e.key.toLowerCase()] = true; });
window.addEventListener("keyup", e => { keys[e.key.toLowerCase()] = false; });

document.getElementById("game-container").addEventListener("click", () => {
    if(!gameActive && player.lives > 0 && currentLevelIdx < 6) {
        gameActive = true;
        document.getElementById("screen-msg").style.display = "none";
        startTimer();
    }
});

function startTimer() {
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        if(!gameActive) return;
        timeLeft--;
        let mins = Math.floor(timeLeft / 60).toString().padStart(2, '0');
        let secs = (timeLeft % 60).toString().padStart(2, '0');
        document.getElementById("lbl-time").innerText = mins + ":" + secs;
        if(timeLeft <= 0) {
            endGame(false, "HẾT THỜI GIAN!");
        }
    }, 1000);
}

function loadLevel(idx) {
    if(idx >= levels.length) {
        endGame(true, "🎉 CHÚC MỪNG NHÓM BẠN ĐÃ CHIẾN THẮNG!");
        return;
    }
    currentLevelIdx = idx;
    map = levels[currentLevelIdx].map;
    player.x = levels[currentLevelIdx].px;
    player.y = levels[currentLevelIdx].py;
    player.angle = 0;
    player.wrongAnswers = 0;
    
    monster.x = 5.5; monster.y = 5.5;
    monster.speed = 0.012 + (idx * 0.003); 
    timeLeft = Math.max(120 - (idx * 10), 60); 
    
    document.getElementById("lbl-level").innerText = currentLevelIdx + 1;
    document.getElementById("puzzle-box").style.display = "none";
    document.getElementById("wrong-count").innerText = "";
}

function checkAnswer() {
    let input = document.getElementById("ans-input").value.trim().toUpperCase();
    if(input === levels[currentLevelIdx].ans) {
        document.getElementById("ans-input").value = "";
        loadLevel(currentLevelIdx + 1);
    } else {
        player.wrongAnswers++;
        document.getElementById("wrong-count").innerText = "Sai lần " + player.wrongAnswers + "/3";
        if(player.wrongAnswers >= 3) {
            player.lives--;
            player.wrongAnswers = 0;
            updateLivesUI();
            if(player.lives <= 0) {
                endGame(false, "☠️ BẠN ĐÃ HẾT TIM!");
            } else {
                alert("Giải sai 3 lần! Bạn mất 1 tim. Hệ thống đưa bạn quay lại màn 1.");
                loadLevel(0); 
            }
        }
    }
}

function updateLivesUI() {
    let hearts = "";
    for(let i=0; i<3; i++) hearts += i < player.lives ? "❤️" : "🖤";
    document.getElementById("lbl-lives").innerText = hearts;
}

function endGame(victory, msg) {
    gameActive = false;
    clearInterval(timerInterval);
    const screenMsg = document.getElementById("screen-msg");
    screenMsg.innerHTML = msg + "<br><span style='font-size:16px;'>Nhấn F5 (Tải lại trang) để chơi lại</span>";
    screenMsg.style.display = "block";
}

function updateAndRender() {
    if(gameActive) {
        let moveSpeed = 0.04;
        let rotSpeed = 0.04;
        let newX = player.x;
        let newY = player.y;

        if (keys["w"]) { newX += Math.cos(player.angle) * moveSpeed; newY += Math.sin(player.angle) * moveSpeed; }
        if (keys["s"]) { newX -= Math.cos(player.angle) * moveSpeed; newY -= Math.sin(player.angle) * moveSpeed; }
        if (keys["a"]) { newX += Math.sin(player.angle) * moveSpeed; newY -= Math.cos(player.angle) * moveSpeed; }
        if (keys["d"]) { newX -= Math.sin(player.angle) * moveSpeed; newY += Math.cos(player.angle) * moveSpeed; }
        if (keys["arrowleft"]) player.angle -= rotSpeed;
        if (keys["arrowright"]) player.angle += rotSpeed;

        if (map[Math.floor(player.y)][Math.floor(newX)] !== 1) player.x = newX;
        if (map[Math.floor(newY)][Math.floor(player.x)] !== 1) player.y = newY;

        let dx = player.x - monster.x;
        let dy = player.y - monster.y;
        let dist = Math.sqrt(dx*dx + dy*dy);
        if(dist > 0.3) {
            monster.x += (dx / dist) * monster.speed;
            monster.y += (dy / dist) * monster.speed;
        } else {
            player.lives--;
            updateLivesUI();
            if(player.lives <= 0) {
                endGame(false, "👻 VERITY ĐÃ BẮT ĐƯỢC BẠN!");
            } else {
                alert("Bạn bị Verity bắt! Mất 1 tim. Hệ thống đưa bạn quay lại màn 1.");
                loadLevel(0);
            }
        }

        if(map[Math.floor(player.y)][Math.floor(player.x)] === 3) {
            document.getElementById("puzzle-hint").innerText = levels[currentLevelIdx].hint;
            document.getElementById("puzzle-box").style.display = "block";
        } else {
            document.getElementById("puzzle-box").style.display = "none";
        }
    }

    ctx.fillStyle = "#222"; ctx.fillRect(0, 0, canvas.width, canvas.height/2);
    ctx.fillStyle = "#444"; ctx.fillRect(0, canvas.height/2, canvas.width, canvas.height/2);

    const fov = Math.PI / 3;
    const numRays = canvas.width;
    for (let i = 0; i < numRays; i++) {
        let rayAngle = (player.angle - fov/2) + (i / numRays) * fov;
        let distance = 0;
        let hitWall = false;
        let wallType = 0;

        while (!hitWall && distance < 16) {
            distance += 0.05;
            let checkX = Math.floor(player.x + Math.cos(rayAngle) * distance);
            let checkY = Math.floor(player.y + Math.sin(rayAngle) * distance);

Hãy thận trọng khi sử dụng mã.
if (checkX < 0 || checkX >= 8 || checkY < 0 || checkY >= 7) {
hitWall = true; distance = 16;
} else if (map[checkY][checkX] > 0) {
hitWall = true;
wallType = map[checkY][checkX];
}
}
let correctedDist = distance * Math.cos(rayAngle - player.angle);
let wallHeight = Math.min(canvas.height / correctedDist, canvas.height);
if(wallType === 3) {
ctx.fillStyle = "#ffeb3b";
} else {
let shade = Math.max(40, 180 - correctedDist * 15);
ctx.fillStyle = "rgb(" + shade + "," + shade + "," + shade + ")";
}
ctx.fillRect(i, (canvas.height - wallHeight)/2, 1, wallHeight);
}
requestAnimationFrame(updateAndRender);
}
loadLevel(0);
updateAndRender();



"""
