import os
import random
import threading
import time
from flask import Flask, request, jsonify, render_template_string
import pyautogui
import pygame

# 初始化Flask应用
app = Flask(__name__)
app.config["DEBUG"] = True

# 获取当前脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 防止pyautogui的故障安全功能中断程序
pyautogui.FAILSAFE = False

# 声音文件配置
SOUND_FILES = {
    "鸡你太美": os.path.join(BASE_DIR, "src", "j1.mp3"),
    "鸡你太美2": os.path.join(BASE_DIR, "src", "j2.mp3"),
    "蚊子叫": os.path.join(BASE_DIR, "src", "j3.mp3")
}


class PrankManager:
    def __init__(self):
        self.is_jittering = False
        self.stop_event = threading.Event()
        self.current_sound = list(SOUND_FILES.keys())[0]
        self.audio_initialized = False
        self._init_audio_system()

    def _init_audio_system(self):
        """初始化音频系统"""
        try:
            pygame.mixer.init()
            self.audio_initialized = pygame.mixer.get_init()
            if not self.audio_initialized:
                print("⚠️ 音频系统初始化失败，声音功能将不可用")
        except Exception as e:
            print(f"❌ 音频初始化错误: {str(e)}")
            self.audio_initialized = False

    def jitter_mouse(self, duration=5):
        """使鼠标随机抖动"""
        if self.is_jittering:
            return {"status": "error", "message": "鼠标已经在抖动了"}

        self.is_jittering = True
        self.stop_event.clear()

        original_x, original_y = pyautogui.position()

        def _jitter():
            start_time = time.time()
            while not self.stop_event.is_set() and (time.time() - start_time) < duration:
                x_offset = random.randint(-60, 60)
                y_offset = random.randint(-60, 60)
                current_x, current_y = pyautogui.position()
                pyautogui.moveTo(current_x + x_offset, current_y + y_offset, duration=0.1)
                time.sleep(0.05)

            pyautogui.moveTo(original_x, original_y, duration=0.3)
            self.is_jittering = False

        threading.Thread(target=_jitter, daemon=True).start()
        return {"status": "success", "message": f"鼠标开始抖动，持续{duration}秒"}

    def stop_jitter(self):
        """停止鼠标抖动"""
        if self.is_jittering:
            self.stop_event.set()
            return {"status": "success", "message": "鼠标抖动已停止"}
        return {"status": "error", "message": "鼠标没有在抖动"}

    def set_sound(self, sound_name):
        """设置要播放的声音"""
        if sound_name in SOUND_FILES:
            self.current_sound = sound_name
            return {"status": "success", "message": f"已设置声音为: {sound_name}"}
        return {"status": "error", "message": "无效的声音选择"}

    def play_sound(self):
        """播放当前选择的声音"""
        if not self.audio_initialized:
            return {"status": "error", "message": "音频系统未初始化"}

        sound_file = SOUND_FILES.get(self.current_sound)
        if not sound_file:
            return {"status": "error", "message": "声音文件未配置"}

        if not os.path.exists(sound_file):
            return {"status": "error", "message": f"声音文件 {sound_file} 不存在"}

        try:
            sound = pygame.mixer.Sound(sound_file)
            sound.play()
            return {"status": "success", "message": f"正在播放: {self.current_sound}"}
        except Exception as e:
            return {"status": "error", "message": f"播放失败: {str(e)}"}


prank_manager = PrankManager()

# HTML页面模板 (H5优化)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>游戏整蛊器</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        :root {
            --primary-color: #e74c3c;
            --secondary-color: #3498db;
            --dark-color: #2c3e50;
            --light-color: #ecf0f1;
            --success-color: #2ecc71;
            --warning-color: #f39c12;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft YaHei', sans-serif;
            background-color: var(--light-color);
            color: var(--dark-color);
            line-height: 1.6;
            padding: 0;
            margin: 0;
        }

        .container {
            max-width: 100%;
            min-height: 100vh;
            padding: 20px 15px;
            display: flex;
            flex-direction: column;
        }

        header {
            text-align: center;
            margin-bottom: 20px;
            padding: 15px;
            background-color: var(--primary-color);
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        h1 {
            font-size: 1.8rem;
            margin-bottom: 5px;
        }

        .subtitle {
            font-size: 0.9rem;
            opacity: 0.8;
        }

        .prank-section {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .section-title {
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: var(--primary-color);
            display: flex;
            align-items: center;
        }

        .section-title i {
            margin-right: 10px;
        }

        .control-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }

        select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
            margin-bottom: 10px;
            background-color: #f9f9f9;
        }

        .btn {
            display: inline-block;
            width: 100%;
            padding: 15px;
            font-size: 1rem;
            font-weight: bold;
            text-align: center;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 10px;
        }

        .btn-primary {
            background-color: var(--primary-color);
            color: white;
        }

        .btn-secondary {
            background-color: var(--secondary-color);
            color: white;
        }

        .btn-warning {
            background-color: var(--warning-color);
            color: white;
        }

        .btn:disabled {
            background-color: #95a5a6;
            cursor: not-allowed;
            opacity: 0.7;
        }

        .btn:active {
            transform: scale(0.98);
        }

        .status {
            padding: 12px;
            border-radius: 8px;
            margin-top: 15px;
            font-size: 0.9rem;
            display: none;
        }

        .status.success {
            background-color: rgba(46, 204, 113, 0.2);
            color: #27ae60;
            display: block;
        }

        .status.error {
            background-color: rgba(231, 76, 60, 0.2);
            color: #c0392b;
            display: block;
        }

        .connection-info {
            text-align: center;
            font-size: 0.8rem;
            color: #7f8c8d;
            margin-top: auto;
            padding-top: 20px;
        }

        .tab-container {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }

        .tab {
            padding: 10px 15px;
            cursor: pointer;
            flex: 1;
            text-align: center;
            border-bottom: 3px solid transparent;
        }

        .tab.active {
            border-bottom: 3px solid var(--primary-color);
            font-weight: bold;
            color: var(--primary-color);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        @media (min-width: 768px) {
            .container {
                max-width: 500px;
                margin: 0 auto;
                padding: 30px 20px;
            }

            .btn-group {
                display: flex;
                gap: 10px;
            }

            .btn {
                width: auto;
                flex: 1;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>游戏整蛊器</h1>
            <p class="subtitle">远程控制整蛊工具</p>
        </header>

        <div class="tab-container">
            <div class="tab active" onclick="switchTab('mouse')">鼠标控制</div>
            <div class="tab" onclick="switchTab('sound')">声音控制</div>
        </div>

        <div id="mouse-tab" class="tab-content active">
            <div class="prank-section">
                <h2 class="section-title">
                    <span>🖱️</span> 鼠标抖动
                </h2>

                <div class="control-group">
                    <label for="duration">抖动时长</label>
                    <select id="duration">
                        <option value="3">3秒</option>
                        <option value="5" selected>5秒</option>
                        <option value="10">10秒</option>
                        <option value="15">15秒</option>
                    </select>
                </div>

                <div class="btn-group">
                    <button id="jitterBtn" class="btn btn-primary" onclick="startJitter()">动他鼠标</button>
                    <button id="stopBtn" class="btn btn-warning" onclick="stopJitter()" disabled>停止抖动</button>
                </div>

                <div id="mouse-status" class="status"></div>
            </div>
        </div>

        <div id="sound-tab" class="tab-content">
            <div class="prank-section">
                <h2 class="section-title">
                    <span>🔊</span> 发出怪叫
                </h2>

                <div class="control-group">
                    <label for="sound-select">选择怪叫声音</label>
                    <select id="sound-select" onchange="changeSound()">
                        {% for sound_name in sound_files %}
                        <option value="{{ sound_name }}">{{ sound_name }}</option>
                        {% endfor %}
                    </select>
                </div>

                <button id="playSoundBtn" class="btn btn-secondary" onclick="playSound()">发出怪叫</button>

                <div id="sound-status" class="status"></div>
            </div>
        </div>

        <div class="connection-info">
            <p>目标电脑IP: {{ ip }} | 端口: 5000</p>
            <p>确保设备在同一网络下</p>
        </div>
    </div>

    <script>
        // 切换标签页
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            document.querySelector(`.tab[onclick="switchTab('${tabName}')"]`).classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        }

        // 鼠标抖动功能
        function startJitter() {
            const duration = document.getElementById('duration').value;
            document.getElementById('jitterBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;

            fetch(`/api/jitter?duration=${duration}`)
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('mouse-status');
                    statusDiv.className = 'status ' + (data.status === 'success' ? 'success' : 'error');
                    statusDiv.textContent = data.message;

                    if (data.status === 'success') {
                        // 抖动结束后恢复按钮状态
                        setTimeout(() => {
                            document.getElementById('jitterBtn').disabled = false;
                            document.getElementById('stopBtn').disabled = true;
                        }, duration * 1000);
                    } else {
                        document.getElementById('jitterBtn').disabled = false;
                    }
                })
                .catch(error => {
                    document.getElementById('mouse-status').className = 'status error';
                    document.getElementById('mouse-status').textContent = '请求失败: ' + error.message;
                    document.getElementById('jitterBtn').disabled = false;
                });
        }

        function stopJitter() {
            fetch('/api/stop')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('mouse-status');
                    statusDiv.className = 'status ' + (data.status === 'success' ? 'success' : 'error');
                    statusDiv.textContent = data.message;

                    document.getElementById('jitterBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                })
                .catch(error => {
                    document.getElementById('mouse-status').className = 'status error';
                    document.getElementById('mouse-status').textContent = '请求失败: ' + error.message;
                });
        }

        // 声音功能
        function changeSound() {
            const soundName = document.getElementById('sound-select').value;
            fetch(`/api/set_sound?sound=${encodeURIComponent(soundName)}`)
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('sound-status');
                    statusDiv.className = 'status ' + (data.status === 'success' ? 'success' : 'error');
                    statusDiv.textContent = data.message;
                })
                .catch(error => {
                    document.getElementById('sound-status').className = 'status error';
                    document.getElementById('sound-status').textContent = '设置失败: ' + error.message;
                });
        }

        function playSound() {
            fetch('/api/play_sound')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('sound-status');
                    statusDiv.className = 'status ' + (data.status === 'success' ? 'success' : 'error');
                    statusDiv.textContent = data.message;
                })
                .catch(error => {
                    document.getElementById('sound-status').className = 'status error';
                    document.getElementById('sound-status').textContent = '播放失败: ' + error.message;
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """主页路由"""
    from socket import gethostbyname, gethostname
    local_ip = gethostbyname(gethostname())
    return render_template_string(HTML_TEMPLATE, ip=local_ip, sound_files=list(SOUND_FILES.keys()))


@app.route('/api/jitter', methods=['GET'])
def api_jitter():
    """API接口：开始鼠标抖动"""
    duration = request.args.get('duration', default=5, type=float)
    return jsonify(prank_manager.jitter_mouse(duration))


@app.route('/api/stop', methods=['GET'])
def api_stop():
    """API接口：停止鼠标抖动"""
    return jsonify(prank_manager.stop_jitter())


@app.route('/api/set_sound', methods=['GET'])
def api_set_sound():
    """API接口：设置声音"""
    sound_name = request.args.get('sound')
    return jsonify(prank_manager.set_sound(sound_name))


@app.route('/api/play_sound', methods=['GET'])
def api_play_sound():
    """API接口：播放声音"""
    return jsonify(prank_manager.play_sound())


@app.route('/favicon.ico')
def favicon():
    """处理favicon请求"""
    return '', 204



if __name__ == '__main__':
    import sys
    if sys.stdout is None:  # 解决打包后无控制台的问题
        sys.stdout = open(os.devnull, 'w')
    # 检查资源文件
    print("资源检查:")
    for name, path in SOUND_FILES.items():
        exists = "ok" if os.path.exists(path) else "no"
        print(f"  {exists} {name}: {path}")

    # 获取本机IP
    from socket import gethostbyname, gethostname

    local_ip = gethostbyname(gethostname())

    print(f"\n 请访问以下地址:")
    print(f" - 本机: http://localhost:5000")
    print(f" - 局域网: http://{local_ip}:5000")

    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000)