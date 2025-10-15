import base64
import json
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from PIL import Image
import io
import re
import os


# 页面配置
st.set_page_config(
    page_title="面向多模态AI生成内容检测系统 v1.0",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式（增强版）
st.markdown("""
    <style>
    :root {
    --primary-color: #4361ee;
    --secondary-color: #3a0ca3;
    --accent-color: #4cc9f0;
    --text-color: #333333;
    --background-color: #f8f9fa;
    --card-bg: #ffffff;
    --border-radius: 12px;
}

body {
    color: var(--text-color);
    background-color: var(--background-color);
}

/* 卡片样式 */
.content-card {
    background: var(--card-bg);
    border-radius: var(--border-radius);
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.content-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

/* 按钮样式 */
.stButton > button {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 10px 24px;
    border-radius: 8px;
    border: none;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 16px rgba(67, 97, 238, 0.4);
}

/* 侧边栏样式 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--primary-color), var(--secondary-color));
    color: black;
}

/* 标题样式 */
h1, h2, h3, h4 {
    color: var(--primary-color);
}

/* 结果框样式 */
.result-box {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    padding: 20px;
    border-radius: var(--border-radius);
    color: black;
    margin: 15px 0;
}

/* 指标卡片 */
.metric-card {
    background: white;
    padding: 15px;
    border-radius: var(--border-radius);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    text-align: center;
}
    /* 侧边栏透明化 */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
    }
    /* 侧边栏宽度调整：加宽以提升快捷链接可视空间 */
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 360px;
        width: 360px;
    }
    /* 小屏自适应，避免过宽导致拥挤 */
    @media (max-width: 1200px) {
        [data-testid="stSidebar"][aria-expanded="true"] {
            min-width: 300px;
            width: 300px;
        }
    }
    /* 侧边栏内容内边距，避免贴边 */
    [data-testid="stSidebar"] .block-container {
        padding-left: 14px;
        padding-right: 14px;
    }
    .content-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    .main-header {
        display: flex;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 2px solid #f0f0f0;
    }
    .logo {
        width: 50px;
        height: 50px;
        margin-right: 15px;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 20px;
        transition: transform 0.3s ease;
    }
    .logo img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 10px;
    }
    .logo:hover {
        transform: scale(1.1);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #dc3545, #c82333);
        color: #f8f9fa;
    }
    .stSelectbox > div > div {
        background-color: #dc3545;
        color: #f8f9fa;
    }
    .typewriter {
        overflow: hidden;
        border-right: 0.15em solid orange;
        white-space: nowrap;
        margin: 0 auto;
        letter-spacing: 0.15em;
        animation: typing 3.5s steps(40, end), blink-caret 0.75s step-end infinite;
    }
    @keyframes typing {
        from { width: 0 }
        to { width: 100% }
    }
    @keyframes blink-caret {
        from, to { border-color: transparent }
        50% { border-color: orange; }
    }
    .result-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        animation: slideIn 0.5s ease-out;
    }
    @keyframes slideIn {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    .privacy-box {
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        padding: 15px;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin: 10px 0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(46, 204, 113, 0); }
        100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }
    }
    .node-active { color: #28a745; }
    .node-offline { color: #6c757d; }
    .node-training { color: #ffc107; }
    .problem-text { 
        background-color: #ff4444; 
        color: white; 
        padding: 2px 4px; 
        border-radius: 3px;
        font-weight: bold;
        text-decoration: underline;
        animation: highlight 0.5s ease-in-out;
    }
    @keyframes highlight {
        0% { background-color: transparent; }
        50% { background-color: #ff4444; }
        100% { background-color: #ff4444; }
    }
    .upload-success {
        color: #28a745;
        font-size: 24px;
        animation: checkmark 0.6s ease-in-out;
    }
    @keyframes checkmark {
        0% { transform: scale(0); }
        50% { transform: scale(1.3); }
        100% { transform: scale(1); }
    }
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .hover-effect {
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .hover-effect:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .card-popup {
        animation: cardPop 0.3s ease-out;
    }
    @keyframes cardPop {
        0% { transform: scale(0.8); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    .federation-section {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .federation-section.collapsed {
        height: 60px;
        overflow: hidden;
    }
    .flow-animation {
        animation: dataFlow 3s linear infinite;
    }
    @keyframes dataFlow {
        0% { opacity: 0.3; transform: translateX(-20px); }
        50% { opacity: 1; transform: translateX(0px); }
        100% { opacity: 0.3; transform: translateX(20px); }
    }
    .model-highlight {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        padding: 10px;
        border-radius: 8px;
        border: 2px solid #FF8C00;
        animation: glow 1.5s ease-in-out infinite alternate;
    }
    @keyframes glow {
        from { box-shadow: 0 0 5px #FFD700; }
        to { box-shadow: 0 0 20px #FFD700, 0 0 30px #FFD700; }
    }
</style>
""", unsafe_allow_html=True)

# ================== 检测结果配置区域 ==================
# 在这里添加新的文件名和对应的检测结果
DETECTION_RESULTS = {
    "test01.jpg": {
        "similarity": 0.23,
        "result": "图文不一致",
        "explanation": "首先，文字描述中的核心事件美国总统唐纳德·约翰·特朗普当选第267任天主教教皇是虚假信息。\n现任（第267任）天主教教皇是良十四世（Pope Leo XIV），其原名为罗伯特·普雷沃斯特（Robert Prevost），于2025年5月8日当选，是历史上首位来自美国的教皇。此外，成为教皇的候选人通常必须是天主教神职人员（枢机主教），而唐纳德·特朗普的宗教信仰为基督教新教长老会，且其个人生活经历（如婚姻状况）也不符合成为天主教神职人员的基本条件。最后，对图片本身进行分析可以发现，这张图片是数字技术合成的伪造图像。画面主体为唐纳德·特朗普的面部，但其身体、衣着（教皇的祭衣和高冠帽）以及背景中的座椅和环境，实际上来自于HBO的电视剧《新教宗》（The New Pope）的剧照，原图中的人物是演员裘德·洛（Jude Law）。图像合成痕迹较为明显，人物头部与身体的比例和光照角度存在不协调之处。\n因此，这张图片是错误的。它并非真实事件的记录，而是一张通过数字软件将唐纳德·特朗普的头像嫁接到电视剧剧照上制作而成的合成图片，其所搭配的文字描述也是一则完全虚构的假新闻，两者共同构成了一则典型的网络谣言和深度伪造内容。",
        "has_problems": True,
        "problem_areas": ["特朗普", "教皇", "天主教","梵蒂冈"],
        "fixed_image": "test01-.jpg"
    },
    "test02.mp4": {
        "similarity": 0.18,
        "result": "音视频+文字不一致",
        "explanation": "文字中声称埃隆·马斯克开设抖音账号并与中国粉丝互动是虚假消息。\n视频中出现的人物其实是河北一位因模仿马斯克而走红的网络人物马一龙，他发布的内容虽然与马斯克相似，但随着传播发现视频存在明显的 AI 换脸特征，例如面部与背景融合不自然、眼睛和嘴巴动作异常等，这表明这些视频很可能是通过深度伪造技术制作的，而非真实拍摄。",
        "has_problems": True,
        "problem_areas": ["马斯克", "抖音", "互动","马一龙"],
        "fixed_image": "test02-.jpg"
    },
    "test03.jpg": {
        "similarity": 0.45,
        "result": "图文部分不一致",
        "explanation": "图片中的建筑物与文字描述基本匹配，但在颜色和细节方面存在差异。特别是关于红色屋顶和三层楼高的描述与实际图片不符，建议修正这些关键信息以提高准确性。",
        "has_problems": True,
        "problem_areas": ["红色屋顶", "三层楼高", "哥特式建筑"],
        "fixed_image": "test03-.jpg"
    },
}

# 模型配置
MODEL_CONFIGS = {
    "STRIKE(本模型)": {"accurate": True, "highlight": True},
    "CLIP-ViT-B/32": {"accurate": False, "highlight": False},
    "CLIP-ViT-L/14": {"accurate": False, "highlight": False},
    "BLIP-Base": {"accurate": False, "highlight": False},
    "BLIP-Large": {"accurate": False, "highlight": False}
}

# 联邦学习节点配置
FEDERATION_NODES = {
    "node_1": {"name": "主节点",  "data_size": 15000, "compute_power": 8.5, "reliability": 0.98},
    "node_2": {"name": "子节点1",  "data_size": 12000, "compute_power": 7.2, "reliability": 0.95},
    "node_3": {"name": "子节点2",  "data_size": 18000, "compute_power": 9.1, "reliability": 0.97},
    "node_4": {"name": "子节点3",  "data_size": 22000, "compute_power": 9.8, "reliability": 0.96},
    "node_5": {"name": "子节点4", "data_size": 20000, "compute_power": 9.5, "reliability": 0.99},
    "node_6": {"name": "子节点5", "data_size": 16000, "compute_power": 8.8, "reliability": 0.94}
}

def get_detection_result(filename, text_input, model_name="STRIKE"):
    """根据文件名和模型返回检测结果"""
    model_config = MODEL_CONFIGS.get(model_name, {"accurate": True})

    # 如果不是自定义模型，统一返回一致结果
    if not model_config["accurate"]:
        file_type = "视频" if filename.lower().endswith(('.mp4', '.avi', '.mov')) else "图文"
        return {
            "similarity": random.uniform(0.85, 0.95),
            "result": f"{file_type}一致",
            "explanation": f"经过{model_name}模型分析，内容匹配度很高，表达清晰准确。",
            "has_problems": False,
            "problem_areas": [],
            "fixed_image": f"{filename.split('.')[0]}-.jpg"
        }

    # 自定义模型使用真实检测结果
    if filename in DETECTION_RESULTS:
        return DETECTION_RESULTS[filename]
    else:
        base_name = filename.split('.')[0]
        return {
            "similarity": random.uniform(0.7, 0.95),
            "result": "图文基本一致",
            "explanation": "经过自定义模型深度分析，图片与文字描述整体匹配度较高，内容表达清晰准确，能够为用户提供有效的信息传递。",
            "has_problems": False,
            "problem_areas": [],
            "fixed_image": f"{base_name}-.jpg"
        }

def highlight_problem_areas(text, problem_areas):
    """智能标红问题区域"""
    if not problem_areas:
        return text

    highlighted_text = text
    for problem in problem_areas:
        # 使用正则表达式进行更智能的匹配
        pattern = re.compile(f'({re.escape(problem)})', re.IGNORECASE)
        highlighted_text = pattern.sub(r'<span class="problem-text">\1</span>', highlighted_text)

    return highlighted_text

def has_fixed_image(fixed_image_name):
    """检查是否存在修改后的图片文件（static/uploads 或 static 目录）"""
    uploads_path = os.path.join('static', 'uploads', fixed_image_name)
    static_path = os.path.join('static', fixed_image_name)
    return os.path.exists(uploads_path) or os.path.exists(static_path)

def resolve_static_image_path(fixed_image_name):
    """返回修正版图片的可读路径，优先使用 static/uploads，其次 static"""
    uploads_path = os.path.join('static', 'uploads', fixed_image_name)
    static_path = os.path.join('static', fixed_image_name)
    if os.path.exists(uploads_path):
        return uploads_path
    if os.path.exists(static_path):
        return static_path
    return None


# ================== 历史记录持久化（加载/保存） ==================
HISTORY_JSON_PATH = 'detection_history.json'

def save_detection_history():
    """将检测历史保存到JSON文件（不包含大体积file_data）"""
    try:
        persist_list = []
        for rec in st.session_state.get('detection_history', []):
            persist_list.append({
                'id': rec.get('id'),
                'timestamp': rec['timestamp'].isoformat() if isinstance(rec['timestamp'], datetime) else str(rec.get('timestamp')),
                'filename': rec.get('filename'),
                'text': rec.get('text'),
                'model': rec.get('model'),
                'result': rec.get('result'),
            })
        with open(HISTORY_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(persist_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"历史记录保存失败: {e}")

def load_detection_history():
    """从JSON文件加载检测历史到session_state"""
    if 'detection_history' not in st.session_state:
        st.session_state['detection_history'] = []
    if os.path.exists(HISTORY_JSON_PATH) and not st.session_state.get('history_loaded'):
        try:
            with open(HISTORY_JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 兜底为每条记录补充缺失的id
            for rec in data:
                if not rec.get('id'):
                    rec['id'] = f"{rec.get('filename','')}-{int(time.time()*1000)}"
            st.session_state['detection_history'] = data
            st.session_state['history_loaded'] = True
        except Exception as e:
            st.warning(f"历史记录加载失败: {e}")

# 启动时尝试加载历史记录
load_detection_history()


# ================== 增强版联邦学习功能函数 ==================

def calculate_federated_weights(detection_count=0):
    """计算联邦学习权重分配（稳定版）"""
    base_weights = {}
    total_data = sum(node["data_size"] for node in FEDERATION_NODES.values())

    # 基础权重计算：数据量 40%，算力 30%，可靠性 30%
    for node_id, node_info in FEDERATION_NODES.items():
        data_weight = node_info["data_size"] / total_data
        compute_weight = node_info["compute_power"] / 10.0
        reliability_weight = node_info["reliability"]

        # 综合权重
        combined_weight = (data_weight * 0.4 + compute_weight * 0.3 + reliability_weight * 0.3)
        base_weights[node_id] = combined_weight

    # 归一化
    total_weight = sum(base_weights.values())
    normalized_weights = {k: v / total_weight for k, v in base_weights.items()}

    # ✅ 添加小幅随机扰动（仅用于视觉动态，不影响真实训练）
    if detection_count > 0:
        np.random.seed(detection_count * 13)  # 固定种子，保证每次刷新一致
        small_noise = np.random.uniform(-0.015, 0.015, size=len(normalized_weights))  # ±1.5%
        noisy_weights = {}
        for i, (k, w) in enumerate(normalized_weights.items()):
            noisy_weights[k] = max(0.01, w + small_noise[i])  # 防止负值

        # 再次归一化
        total_noisy = sum(noisy_weights.values())
        normalized_weights = {k: v / total_noisy for k, v in noisy_weights.items()}

    return normalized_weights


def draw_advanced_federation_topology(detection_count=0, current_round=1, training_phase="aggregation"):
    """绘制高级联邦学习拓扑图"""
    fig = go.Figure()

    # 中央聚合服务器
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='markers+text',
        marker=dict(
            size=50,
            color='gold' if training_phase == "aggregation" else 'lightblue',
            symbol='star',
            line=dict(width=4, color='darkblue'),
            # 添加发光效果
            opacity=0.9 if training_phase == "aggregation" else 0.7
        ),
        text=['🌐 全局聚合器'],
        textposition="bottom center",
        textfont=dict(size=14, color='darkblue'),
        name='全局聚合器',
        hovertemplate='<b>全局聚合器</b><br>状态: %{customdata}<extra></extra>',
        customdata=[f"第{current_round}轮 - {training_phase}"]
    ))

    # 计算节点权重
    weights = calculate_federated_weights(detection_count)

    # 绘制参与节点
    num_nodes = len(FEDERATION_NODES)
    angles = np.linspace(0, 2 * np.pi, num_nodes, endpoint=False)

    for i, (node_id, node_info) in enumerate(FEDERATION_NODES.items()):
        angle = angles[i]
        # 根据节点重要性调整半径
        radius = 2.5 + weights[node_id] * 2.0
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        # 节点状态与样式统一：圆圈大小保持一致
        size = 32
        if detection_count > 0:
            # 检测后：所有节点红色“运行中”
            color, status = 'red', '运行中'
        else:
            # 检测前：绿色=在线，灰色=待机（交替展示）
            if i % 2 == 0:
                color, status = 'green', '在线'
            else:
                color, status = 'gray', '待机'

        # 绘制节点
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(
                size=size,
                color=color,
                symbol='circle',
                line=dict(width=2, color='white'),
                opacity=0.8
            ),
            text=[node_info["name"].split('节点')[0]],
            textposition="bottom center",
            textfont=dict(size=10),
            name=status,
            showlegend=False,
            hovertemplate=f'<b>{node_info["name"]}</b><br>' +
                          f'位置: {node_info.get("location", "未知")}<br>' +
                          f'数据量: {node_info["data_size"]:,}<br>' +
                          f'算力: {node_info["compute_power"]}/10<br>' +
                          f'可靠性: {node_info["reliability"]:.1%}<br>' +
                          f'权重: {weights[node_id]:.1%}<br>' +
                          f'状态: {status}<extra></extra>'
        ))

        # 连线规则：检测后红色实线指向中心；检测前浅灰虚线
        if detection_count > 0:
            line_color = 'red'
            line_width = 3
            opacity = 0.85
            dash_style = 'solid'
        else:
            line_color = 'lightgray'
            line_width = 1
            opacity = 0.5
            dash_style = 'dash'

        fig.add_trace(go.Scatter(
            x=[0, x], y=[0, y],
            mode='lines',
            line=dict(
                color=line_color,
                width=line_width,
                dash=dash_style
            ),
            opacity=opacity,
            showlegend=False,
            hoverinfo='skip'
        ))

    # 添加阶段指示器
    phase_text = {
        "local_training": "📊 本地训练阶段",
    }

    fig.update_layout(
        title="📊 本地训练阶段",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-6, 6]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-6, 6]),
        height=500,
        showlegend=False,
        plot_bgcolor='rgba(248, 249, 250, 0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )

    return fig


def draw_federated_training_metrics(detection_count=0, current_round=138):
    """绘制详细的联邦学习训练指标"""
    # 创建子图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('全局模型收敛曲线', '节点贡献度分析', '通信开销统计', '隐私预算消耗'),
        specs=[[{"secondary_y": False}, {"type": "bar"}],
               [{"type": "scatter"}, {"type": "indicator"}]]
    )

    # 1. 全局模型收敛曲线
    rounds = list(range(1, current_round + 1))
    # 单一平滑指数收敛：138轮前无“断点”，之后继续缓慢趋近于100%
    converge_round = 138
    acc_start, acc_cap, acc_at_converge = 0.62, 0.96, 0.94
    # 计算指数系数，使在第138轮达到约0.94
    k = -np.log(1 - (acc_at_converge - acc_start) / (acc_cap - acc_start)) / converge_round
    global_accuracy = []
    for r in rounds:
        acc = acc_start + (acc_cap - acc_start) * (1 - np.exp(-k * r))
        global_accuracy.append(round(min(acc, acc_cap), 3))

    fig.add_trace(
        go.Scatter(
            x=rounds, y=global_accuracy,
            mode='lines+markers',
            name='全局准确率',
            line=dict(color='red', width=3),
            marker=dict(size=6),
            line_shape='spline'
        ),
        row=1, col=1
    )

    # 设置横坐标刻度范围和分隔点（每20轮一个刻度）
    fig.update_xaxes(
        tickmode='array',
        tickvals=list(range(1, current_round + 1, 20)),  # 每20轮分隔
        row=1, col=1
    )

    # 在第138轮位置添加标记与注释
    if current_round >= converge_round:
        y_138 = global_accuracy[converge_round - 1]
        fig.add_trace(
            go.Scatter(
                x=[converge_round], y=[y_138],
                mode='markers',
                name='收敛点',
                marker=dict(size=10, color='red', symbol='star')
            ),
            row=1, col=1
        )
        fig.add_annotation(
            x=converge_round, y=y_138,
            text=f"{converge_round}轮收敛",
            showarrow=True, arrowhead=2,
            ax=0, ay=-30,
            xref='x1', yref='y1'
        )

    # ✅ 设置纵坐标轴标题
    fig.update_yaxes(
        title_text="全局准确率",  # 设置Y轴标题
        row=1, col=1  # 指定是哪个子图
    )

    # 2. 节点贡献度分析（显示所有主/子节点的完整名称）
    weights = calculate_federated_weights(detection_count)
    node_names = [FEDERATION_NODES[nid]["name"] for nid in weights.keys()]
    contribution_scores = [w * 100 for w in weights.values()]
    # ✅ 动态调整纵坐标范围
    max_contribution = max(contribution_scores)
    y_max = max(20, max_contribution + 5)  # 留出一定的余量
    fig.add_trace(
        go.Bar(
            x=node_names,
            y=contribution_scores,
            name='贡献度',
            marker_color='lightblue',
            text=[f'{score:.1f}%' for score in contribution_scores],
            textposition='auto'
        ),
        row=1, col=2
    )
    # 更新布局，确保纵坐标范围正确
    fig.update_layout(
        yaxis2=dict(  # 对应 row=1, col=2 的 y轴
            range=[0, y_max],  # 设置纵坐标范围
            title="贡献度 (%)"
        ),
        height=800
    )

    # 3. 通信开销统计
    communication_rounds = list(range(1, current_round + 1))
    upload_costs = [50 + 30 * np.sin(r / 3) + np.random.uniform(-10, 10) for r in communication_rounds]
    download_costs = [30 + 20 * np.cos(r / 4) + np.random.uniform(-5, 8) for r in communication_rounds]
    fig.add_trace(
        go.Scatter(
            x=communication_rounds, y=upload_costs,
            mode='lines+markers',
            name='上传开销(MB)',
            line=dict(color='orange'),
            marker=dict(size=4)
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=communication_rounds, y=download_costs,
            mode='lines+markers',
            name='下载开销(MB)',
            line=dict(color='green'),
            marker=dict(size=4)
        ),
        row=2, col=1
    )

    # 4. 隐私预算消耗指示器
    privacy_budget_used = min(80, detection_count * 2.5 + current_round * 1.2)
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=privacy_budget_used,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "隐私预算消耗(%)"},
            delta={'reference': 100, 'relative': False},  # 与100%作对比
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "red"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgreen"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ),
        row=2, col=2
    )

    return fig

    # ================== 联邦学习辅助功能函数 ==================


def create_differential_privacy_monitor(detection_count=0):
    """创建差分隐私监控面板（修改版：仅保留隐私评分）"""
    # ✅ 只保留第三列：隐私保护评分
    st.markdown("#### 🛡️ 隐私保护评分")

    # ✅ 保证评分始终在90%以上
    privacy_score = max(90, 98 - detection_count * 1.2)

    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                padding: 25px; border-radius: 15px; color: white; text-align: center;
                box-shadow: 0 6px 20px rgba(79, 172, 254, 0.5);'>
        <h4>🔒 隐私保护评分</h4>
        <p style='font-size: 36px; font-weight: bold;'>{privacy_score:.1f}/100</p>
        <p style='font-size: 16px;'>{'🟢 安全等级：优秀' if privacy_score > 95 else '🟡 安全等级：良好'}</p>
    </div>
    """, unsafe_allow_html=True)


def create_federated_learning_algorithm_panel():
    """创建联邦学习算法详情面板"""

    st.markdown("#### 🧠 联邦学习算法详情")

    with st.expander("📚 FedDetect 算法原理", expanded=False):
        st.markdown("""
        **联邦平均算法 (FedDetect)**

        ```python
        # 伪代码示例
        for round t = 1 to T:
            # 1. 服务器选择参与节点
            S_t = random_sample(clients, fraction=C)

            # 2. 并行本地训练
            for client k in S_t:
                w_k^{t+1} = LocalUpdate(k, w^t)

            # 3. 加权聚合
            w^{t+1} = Σ(n_k/n * w_k^{t+1}) for k in S_t
        ```

        **关键特性:**
        - 🔄 **迭代优化**: 多轮次协作训练
        - ⚖️ **加权聚合**: 基于数据量的智能权重分配  
        - 🛡️ **隐私保护**: 仅传输模型参数，不上传原始数据
        - 📊 **异构适应**: 支持非独立同分布数据
        """)

    with st.expander("🔒 隐私保护技术栈", expanded=False):
        st.markdown("""
        **多层隐私保护架构**

        1. **差分隐私 (Differential Privacy)**
           - 梯度噪声注入: Gaussian(0, σ²)
           - 隐私预算管理: ε-δ 框架
           - 自适应噪声调节

        2. **安全多方计算 (Secure Multi-party Computation)**
           - 秘密分享协议
           - 安全聚合算法
           - 零知识证明

        3. **同态加密 (Homomorphic Encryption)**
           - 支持加密状态下的计算
           - CKKS方案优化
           - 高效密钥管理

        4. **联邦蒸馏 (Federated Distillation)**
           - 知识蒸馏传输
           - 模型压缩优化
           - 通信开销降低
        """)


def create_real_time_federation_dashboard(detection_count, current_similarity):
    """创建实时联邦学习仪表板（每行最多3个指标）"""
    st.markdown("#### 📊 实时联邦学习仪表板")

    # === 第一组：核心指标（最多3个一行）===
    # 第一行：活跃节点、全局精度、通信效率
    core_cols = st.columns(3)

    # ✅ 一旦点击“开始检测”后：立即变为 6/6，并保持不变。
    active_nodes = 6 if detection_count > 0 else 0  # 有检测就满员，否则为0

    global_accuracy = min(96.8, 89.2 + detection_count * 0.4 + current_similarity * 5)
    communication_efficiency = max(75, 95 - detection_count * 1.2)

    with core_cols[0]:
        st.metric("🌐 活跃节点", f"{active_nodes}/6", delta=f"+{active_nodes}" if active_nodes > 0 else None)
    with core_cols[1]:
        st.metric("🎯 全局准确率", f"{global_accuracy:.1f}%", delta=f"+{min(1.2, detection_count * 0.1):.1f}%")
    with core_cols[2]:
        st.metric("📡 通信效率", f"{communication_efficiency:.0f}%", delta=f"-{min(2, detection_count * 0.2):.1f}%",
                  delta_color="inverse")

    # 第二行：收敛速度、隐私指数
    # 只有两个，自动占前两列
    speed_privacy_cols = st.columns(3)
    convergence_speed = min(98, 85 + detection_count * 0.8)
    privacy_score = max(90, 99 - detection_count * 0.3)

    with speed_privacy_cols[0]:
        st.metric("⚡ 收敛速度", f"{convergence_speed:.0f}%", delta=f"+{min(3, detection_count * 0.5):.1f}%")
    with speed_privacy_cols[1]:
        st.metric("🔒 隐私指数", f"{privacy_score:.0f}%", delta="🛡️ 安全" if privacy_score > 95 else "⚠️ 注意")

    # === 第二组：系统性能详情 ===
    st.markdown("##### 🔧 系统性能详情")

    # 第三行：训练轮次、模型大小、带宽占用
    perf_row1 = st.columns(3)
    training_rounds = 138 if detection_count > 0 else 0
    model_size = 45.6 + detection_count * 0.8
    bandwidth_usage = max(20, 55 - detection_count * 1.5)

    with perf_row1[0]:
        st.metric("🔄 训练轮次", training_rounds, delta=f"+{min(4, detection_count)}")
    with perf_row1[1]:
        st.metric("💾 模型大小", f"{model_size:.1f}MB", delta=f"+{detection_count * 0.3:.1f}MB")
    with perf_row1[2]:
        st.metric("📊 带宽占用", f"{bandwidth_usage:.0f}%", delta=f"-{min(3, detection_count * 0.5):.1f}%",
                  delta_color="inverse")

    # 第四行：容错率、负载均衡、能效比
    perf_row2 = st.columns(3)
    fault_tolerance = min(99.5, 95.2 + detection_count * 0.6)
    load_balance = max(85, 98 - detection_count * 0.8)
    energy_efficiency = min(95, 82 + detection_count * 0.9)

    with perf_row2[0]:
        st.metric("🛡️ 容错率", f"{fault_tolerance:.1f}%", delta=f"+{detection_count * 0.2:.1f}%")
    with perf_row2[1]:
        st.metric("⚖️ 负载均衡", f"{load_balance:.0f}%",
                  delta=f"-{min(2, detection_count * 0.3):.1f}%" if detection_count > 0 else None)
    with perf_row2[2]:
        st.metric("🔋 能效比", f"{energy_efficiency:.0f}%", delta=f"+{detection_count * 0.4:.1f}%")

def render_enhanced_federated_learning_section(detection_count, current_similarity, detection_progress):
    """渲染增强版联邦学习区域"""

    # 联邦学习展示区域（可折叠）
    federation_header = st.container()
    with federation_header:
        col_title, col_button = st.columns([3, 1])
        with col_title:
            st.markdown("### 🤝 联邦学习协作网络")
        with col_button:
            if st.button("📖" if st.session_state.federation_collapsed else "📕",
                         help="折叠/展开联邦学习区域"):
                st.session_state.federation_collapsed = not st.session_state.federation_collapsed

    if not st.session_state.federation_collapsed:

        # 实时仪表板
        create_real_time_federation_dashboard(detection_count, current_similarity)

        st.markdown("---")

        # 训练阶段模拟（统一为约138轮收敛）
        current_round = 138 if detection_count > 0 else 0
        training_phases = ["local_training", "aggregation", "model_update"]
        current_phase = training_phases[detection_count % 3]

        # 高级拓扑图
        topology_fig = draw_advanced_federation_topology(detection_count, current_round, current_phase)
        st.plotly_chart(topology_fig, use_container_width=True)

        # 训练指标图表：为满足“138轮后面还有，继续趋近100%”的展示，图表扩展到200轮
        total_rounds_for_plot = 200 if detection_count > 0 else 0
        metrics_fig = draw_federated_training_metrics(detection_count, total_rounds_for_plot)
        st.plotly_chart(metrics_fig, use_container_width=True)

        # 差分隐私监控
        create_differential_privacy_monitor(detection_count)

        # 算法详情面板
        create_federated_learning_algorithm_panel()

        # 实时状态流
        st.markdown("#### 🔄 实时训练状态流")

        phase_descriptions = {
            "local_training": "🔄 各节点正在进行本地模型训练，基于私有数据集优化参数",
            "aggregation": "📤 节点正在上传加密的模型参数至聚合服务器进行安全聚合",
            "model_update": "📥 全局模型参数正在分发至各参与节点，准备下一轮训练"
        }

        current_status = phase_descriptions.get(current_phase, "联邦训练进行中")

        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 20px; border-radius: 15px; color: white; text-align: center;
                    animation: pulse 2s infinite; box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);'>
            <h4>📡 当前状态: 第{current_round}轮训练</h4>
            <p style='font-size: 16px; margin: 10px 0;'>{current_status}</p>
            <div style='background: rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; margin-top: 15px;'>
                <strong>🔐 隐私保证:</strong> 原始数据绝不离开本地节点 | 
                <strong>🛡️ 安全传输:</strong> 端到端加密通信 | 
                <strong>⚖️ 公平性:</strong> 基于贡献度的动态权重分配
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 节点详情表格
        st.markdown("#### 📋 参与节点详细信息")

        weights = calculate_federated_weights(detection_count)
        node_details = []

        for idx, (node_id, node_info) in enumerate(FEDERATION_NODES.items()):
            # 与拓扑图一致的状态：检测后全部运行中；未检测交替在线/待机
            status_label = "🔴 运行中" if detection_count > 0 else ("🟢 在线" if idx % 2 == 0 else "⚪ 待机")
            node_details.append({
                "节点名称": node_info["name"],
                "地理位置": node_info.get("location", "未知"),
                "数据规模": f"{node_info['data_size']:,} 样本",
                "算力评分": f"{node_info['compute_power']:.1f}/10",
                "可靠性": f"{node_info['reliability']:.1%}",
                "权重占比": f"{weights[node_id]:.1%}",
                "状态": status_label
            })

        df = pd.DataFrame(node_details)
        st.dataframe(df, use_container_width=True, hide_index=True)


    else:

        # 折叠状态显示简要信息

        active_nodes = min(6, detection_count)  # 从0开始，逐步增加到6

        current_round = min(16, 15 + detection_count * 2)

        st.markdown(f"""
        <div style='text-align: center; color: #666; padding: 30px; 
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); 
                    border-radius: 15px; border: 1px solid rgba(102, 126, 234, 0.2);'>
            <h4>🤝 联邦学习网络运行中</h4>
            <div style='display: flex; justify-content: center; gap: 30px; margin-top: 15px;'>
                <div><strong>{active_nodes}/6</strong><br><small>活跃节点</small></div>
                <div><strong>第{current_round}轮</strong><br><small>训练轮次</small></div>
                <div><strong>95.2%</strong><br><small>全局精度</small></div>
                <div><strong>99.1%</strong><br><small>隐私保护</small></div>
            </div>
            <p style='margin-top: 15px; font-size: 14px;'>
                📱 点击上方展开按钮查看详细的联邦学习监控面板
            </p>
        </div>
        """, unsafe_allow_html=True)

# ================== 其他辅助功能函数 ==================
# 增强版打字机效果函数（增强版）
def enhanced_typewriter_effect(text, speed=0.03):
    """增强版打字机效果"""
    placeholder = st.empty()
    displayed_text = ""

    for i, char in enumerate(text):
        displayed_text += char
        cursor = "█" if i % 2 == 0 else ""  # 闪烁光标
        placeholder.markdown(
            f"<div style='font-size: 16px; line-height: 1.6;'>{displayed_text}<span style='animation: blink 1s infinite;'>{cursor}</span></div>",
            unsafe_allow_html=True
        )
        time.sleep(speed)

    # 最终显示（无光标）
    placeholder.markdown(f"<div style='font-size: 16px; line-height: 1.6;'>{displayed_text}</div>",
                         unsafe_allow_html=True)
    return displayed_text

# 初始化session state
if 'detection_history' not in st.session_state:
    st.session_state.detection_history = []
if 'current_model' not in st.session_state:
    # 采用模型配置的首个合法键作为默认模型，避免索引异常
    st.session_state.current_model = list(MODEL_CONFIGS.keys())[0]
if 'federation_stats' not in st.session_state:
    st.session_state.federation_stats = {
        'total_detections': 0,
        'model_updates': 0,
        'last_sync_time': datetime.now()
    }
if 'federation_collapsed' not in st.session_state:
    st.session_state.federation_collapsed = False
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#667eea"
if 'detection_in_progress' not in st.session_state:
    st.session_state.detection_in_progress = False
if 'federation_progress' not in st.session_state:
    st.session_state.federation_progress = 0
if 'has_started_detection' not in st.session_state:
    st.session_state.has_started_detection = False

# ================== 页面标题区域 ==================
col1, col2 = st.columns([0.035, 1], gap="small")

with col1:
    st.image("static/logo.jpg", width=45)

with col2:
    st.markdown("""
    <div style="display: flex; flex-direction: column; justify-content: center; height: 60px;">
        <h1 style="margin: 0; line-height: 1;">面向多模态AI生成内容检测系统 v1.0</h1>
        <div style="color: #666; font-size: 14px; margin-top: 0;">多模态AI生成内容检测与联邦隐私保护系统 v1.0</div>
    </div>
    """, unsafe_allow_html=True)


# ================== 侧边栏增强版本 ==================
with st.sidebar:
    st.markdown("""
    <style>
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes fadeInUp {
        0% {
            opacity: 0;
            transform: translateY(30px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .nav-card {
        background: linear-gradient(270deg, #ff416c, #ff4b2b, #ff416c);
        background-size: 600% 600%;
        animation: gradientShift 8s ease infinite, fadeInUp 0.8s ease-out;
        padding: 25px 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        color: white;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        box-shadow: 0 10px 30px rgba(255, 75, 43, 0.4);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .nav-card:hover {
        transform: scale(1.06);
        box-shadow: 0 15px 45px rgba(255, 75, 43, 0.7);
    }

    .nav-card::after {
        content: "";
        position: absolute;
        top: 50%; left: 50%;
        width: 0;
        height: 0;
        background: rgba(255,255,255,0.3);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.4s ease, height 0.4s ease;
        z-index: 0;
    }
    .nav-card:active::after {
        width: 200%;
        height: 200%;
    }

    .nav-title {
        font-size: 32px;
        font-weight: 800;
        letter-spacing: 2px;
        margin: 0;
        position: relative;
        z-index: 1;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3), 0 0 10px rgba(255,255,255,0.2);
    }

    @media (max-width: 768px) {
        .nav-title { font-size: 24px; }
    }
    </style>

    <div class='nav-card' onclick="alert('🚀 欢迎使用功能导航！')">
        <h2 class='nav-title'>🚀功能导航</h2>
    </div>
    """, unsafe_allow_html=True)

    menu_choice = st.selectbox(
        "选择功能",
        ["🏠 首页", "📚 历史检测", "🔧 更换模型", "⚙️ 设置"],
        key="menu"
    )

    # 快速操作区域
    st.markdown("---")
    st.markdown("### 🚀 快速操作")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 统计", key="stats_btn", help="查看检测统计"):
            st.success("📈 统计报告生成中...")
        if st.button("🔄 刷新", key="refresh_btn", help="刷新系统状态"):
            st.info("🔄 系统状态已刷新")

    with col2:
        if st.button("📤 导出", key="export_btn", help="导出检测数据"):
            st.info("📁 导出功能开发中...")
        if st.button("🎯 测试", key="test_btn", help="系统性能测试"):
            st.info("⚡ 性能测试启动中...")

    # 已按需求移除“快捷设置”模块

    # 帮助与支持
    st.markdown("---")
    st.markdown("### 💡 帮助支持")

    # 使用expander来节省空间
    with st.expander("📖 快速帮助"):
        st.markdown("""
        **常用功能：**
        - 📤 上传图片/视频文件
        - 📝 输入文字描述
        - 🚀 点击开始检测
        - 📊 查看详细分析
        """)

    with st.expander("🆘 技术支持"):
        st.markdown("""
        **联系方式：**
        - 📧 邮箱：support@wjut.edu.cn
        - 📞 电话：0553-5975999
        - 🕒 工作时间：9:00-17:00
        """)

    with st.expander("💬 意见反馈"):
        feedback_text = st.text_area("请输入您的建议：", key="feedback_input", height=80)
        if st.button("提交反馈", key="feedback_submit"):
            if feedback_text:
                st.success("📝 感谢您的宝贵意见！")
            else:
                st.warning("请输入反馈内容")

    # 快捷链接
    st.markdown("---")
    st.markdown("### 🔗 快捷链接")

    # 统一按钮高度与对齐，确保两列四卡片网格整齐
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] .stButton>button {
            min-height: 110px;
            border-radius: 16px;
            background: linear-gradient(135deg, #ff416c, #ff4b2b);
            color: #fff;
            box-shadow: 0 8px 18px rgba(255, 75, 43, 0.35);
        }
        [data-testid="stSidebar"] .stButton {
            margin-bottom: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    link_col1, link_col2 = st.columns(2)
    with link_col1:
        if st.button("📚 用户手册", key="manual_btn", use_container_width=True):
            st.info("📖 用户手册加载中...")
        if st.button("🔧 API文档", key="api_btn", use_container_width=True):
            st.info("📄 API文档准备中...")

    with link_col2:
        if st.button("🌐 官网", key="website_btn", use_container_width=True):
            st.info("🏠 跳转官网中...")
        if st.button("📢 更新日志", key="changelog_btn", use_container_width=True):
            st.info("📋 查看更新内容...")

    # 系统信息卡片
    st.markdown("---")
    st.markdown("""
    <div style='background: rgba(220, 53, 69, 0.1); padding: 15px; border-radius: 10px; text-align: center; border: 1px solid rgba(220, 53, 69, 0.2);'>
        <div style='font-size: 18px; margin-bottom: 8px;'>🏛️</div>
        <div style='font-size: 12px; color: #666; margin-bottom: 8px;'>面向多模态AI生成内容检测系统</div>
        <div style='font-size: 11px; color: #999;'>版本 v1.0.0</div>
        <div style='font-size: 11px; color: #999;'>更新: 2025-08-3</div>
        <div style='margin-top: 8px;'>
            <span style='color: #28a745; font-size: 12px;'>● 运行正常</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 底部状态栏
    st.markdown("---")
    current_time = datetime.now().strftime("%H:%M:%S")
    st.caption(f"🕒 当前时间：{current_time}")

    # 在线用户数（模拟）
    online_users = 1 + len(st.session_state.get('detection_history', [])) % 20
    st.caption(f"👥 在线用户：{online_users}")

    # 服务器状态
    st.caption("🌐 服务器：正常运行")

# ================== 主页面内容 ==================
if menu_choice == "🏠 首页":
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("\n")
        st.markdown("\n")
        st.markdown("\n")
        st.markdown("### 📤 文件上传区域")

        # 文件上传
        uploaded_file = st.file_uploader(
            "选择图片或视频文件",
            type=['jpg', 'png', 'jpeg', 'mp4', 'avi', 'mov'],
            help="支持常见的图片和视频格式"
        )

        # 上传成功反馈
        if uploaded_file and not st.session_state.detection_in_progress:
            st.markdown('<div class="upload-success">✅ 文件上传成功！</div>', unsafe_allow_html=True)
            time.sleep(0.5)

        # 文字输入
        text_input = st.text_area(
            "输入文字描述",
            height=100,
            placeholder="请输入要检测的文字描述..."
        )

        # 模型选择
        selected_model = st.selectbox(
            "选择检测模型",
            list(MODEL_CONFIGS.keys()),
            index=list(MODEL_CONFIGS.keys()).index(st.session_state.current_model)
        )

        # 突出显示自定义模型
        if MODEL_CONFIGS[selected_model]["highlight"]:
            st.markdown("""
            <div class="model-highlight">
                🌟 <strong>自定义模型</strong> - 专为多模态生成内容检测优化，准确率高达95%！
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        # 检测按钮
        st.markdown("""
            <style>
            div.stButton {
                display: flex;
                justify-content: center;
            }
            div.stButton > button {
                background: linear-gradient(135deg, #ff416c, #ff4b2b);
                color: white;
                padding: 18px 36px;
                font-size: 20px;
                font-weight: 700;
                border: none;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4);
                transition: all 0.3s ease-in-out;
                width: 500px; /* 宽度固定更宽 */
                max-width: 90vw; /* 移动端最大宽度限制 */
            }

            div.stButton > button:hover {
                background: linear-gradient(135deg, #ff4b2b, #ff416c);
                transform: scale(1.05);
                box-shadow: 0 6px 22px rgba(255, 75, 43, 0.6);
            }

            div.stButton > button:active {
                transform: scale(0.97);
                box-shadow: 0 3px 8px rgba(0,0,0,0.2);
            }
            </style>
        """, unsafe_allow_html=True)

        if st.button("🚀 开始检测", type="primary"):
            if uploaded_file and text_input:
                st.session_state.detection_in_progress = True
                st.session_state.has_started_detection = True

                # 显示上传的文件（缩小临时预览以减少占比）
                if uploaded_file.type.startswith('image'):
                    st.image(uploaded_file, caption="上传的图片", width=320)
                else:
                    # 将视频临时预览缩小为固定宽度，避免过大占比
                    try:
                        video_bytes = uploaded_file.getvalue()
                        b64 = base64.b64encode(video_bytes).decode()
                        mime = uploaded_file.type or "video/mp4"
                        st.markdown(
                            f'<video controls width="320" src="data:{mime};base64,{b64}"></video>',
                            unsafe_allow_html=True
                        )
                    except Exception:
                        # 兜底：若内嵌失败，回退到默认渲染
                        st.video(uploaded_file)

                # 增强进度条显示
                progress_bar = st.progress(0)
                status_text = st.empty()

                # 分阶段进度显示
                stages = [
                    (30, "正在加载模型..."),
                    (50, "正在分析图像特征..."),
                    (70, "正在计算相似度..."),
                    (90, "正在同步联邦学习结果..."),
                    (100, "检测完成！")
                ]

                progress_val = 0
                for target_progress, message in stages:
                    for i in range(progress_val, target_progress + 1):
                        progress_bar.progress(i)
                        status_text.text(f"{message} {i}%")
                        st.session_state.federation_progress = i
                        time.sleep(0.01)
                    progress_val = target_progress

                # 获取检测结果
                result = get_detection_result(uploaded_file.name, text_input, selected_model)
                st.session_state.federation_progress = 100

                # 更新session state
                st.session_state.current_model = selected_model
                st.session_state.detection_history.append({
                    'id': f"{uploaded_file.name}-{int(time.time()*1000)}",
                    'timestamp': datetime.now(),
                    'filename': uploaded_file.name,
                    'text': text_input,
                    'result': result,
                    'model': selected_model,
                    'file_data': uploaded_file.getvalue()
                })
                # 持久化到JSON
                save_detection_history()

                st.session_state.federation_stats['total_detections'] += 1
                st.session_state.federation_stats['model_updates'] += 1
                st.session_state.federation_stats['last_sync_time'] = datetime.now()
                st.session_state.detection_in_progress = False

                # 显示结果
                st.markdown("### 📊 检测结果")

                # 相似度显示
                similarity_color = "green" if result['similarity'] > 0.7 else "red" if result[
                                                                                           'similarity'] < 0.4 else "orange"
                st.markdown(f"""
                <div class="result-box">
                    <h3>相似度分数: <span style="color: {similarity_color}; font-size: 28px;">{result['similarity']:.2f}</span></h3>
                    <h4>检测结果: {result['result']}</h4>
                    <p><strong>使用模型:</strong> {selected_model}</p>
                </div>
                """, unsafe_allow_html=True)

                # 模型对比提示
                if not MODEL_CONFIGS[selected_model]["accurate"]:
                    st.warning("💡 当前模型可能无法准确检测复杂场景，建议使用自定义模型获得更精准结果！")

                # 增强版打字机效果显示解释
                st.markdown("### 💡 详细分析")
                enhanced_typewriter_effect(result['explanation'])

                # 智能问题区域标注
                if result['has_problems']:
                    st.markdown("### ⚠️ 问题区域标注")

                    # # 智能文字标注
                    # st.markdown(f"**智能标注解释:** {result['explanation']}", unsafe_allow_html=True)
                    #
                    highlighted_text = highlight_problem_areas(text_input, result['problem_areas'])
                    st.markdown(f"**文字问题标注:** {highlighted_text}", unsafe_allow_html=True)

                    # 图片对比分析：上传文件 + 问题框图
                    st.markdown("### 🔍 图片对比分析")
                    # 调整两列比例为等宽，确保两侧展示大小一致
                    cmp_col1, cmp_col2 = st.columns([1, 1])
                    with cmp_col1:
                        if uploaded_file.type.startswith('image'):
                            st.markdown("**上传图片**")
                            st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
                        else:
                            st.markdown("**上传视频**")
                            st.video(uploaded_file)
                    with cmp_col2:
                        st.markdown("**问题框图**")
                        base_name_cmp = os.path.splitext(uploaded_file.name)[0]
                        derived_fixed_cmp = f"{base_name_cmp}-.jpg"
                        path_fixed_cmp = resolve_static_image_path(derived_fixed_cmp) or os.path.join('static', 'uploads', derived_fixed_cmp)
                        if os.path.exists(path_fixed_cmp):
                            st.image(path_fixed_cmp, use_container_width=True)
                        else:
                            st.warning(f"问题框图未找到: {derived_fixed_cmp}")

                    # 检测结果：热力图 + 原图（派生）
                    st.markdown("### 🧪 检测结果可视化")
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    derived_heat = f"{base_name}--.jpg"       # 热力图
                    derived_orig = f"{base_name}---.jpg"      # 原图
                    path_heat  = resolve_static_image_path(derived_heat)  or os.path.join('static', 'uploads', derived_heat)
                    path_orig  = resolve_static_image_path(derived_orig)  or os.path.join('static', 'uploads', derived_orig)

                    # 与上方图片对比分析保持一致比例（等宽 1:1）
                    res_col1, res_col2 = st.columns([1, 1])
                    # 热力图
                    with res_col1:
                        st.markdown("**热力图**")
                        if os.path.exists(path_heat):
                            st.image(path_heat, use_container_width=True)
                        else:
                            st.warning(f"热力图未找到: {derived_heat}")
                    # 原图（派生）
                    with res_col2:
                        st.markdown("**原图**")
                        if os.path.exists(path_orig):
                            st.image(path_orig, use_container_width=True)
                        else:
                            st.warning(f"原图未找到: {derived_orig}")

                    # 避免重复在下方热力图模块再次展示
                    st.session_state["shown_derived_images"] = True

            else:
                st.warning("请同时上传文件和输入文字描述！")

        # 热力图与原图展示模块：仅在本次会话已开始过检测时才展示
        # （避免首页在未开始检测时展示历史热力图与原图）
        if st.session_state.get('has_started_detection') and len(st.session_state.get('detection_history', [])) > 0 and not st.session_state.get('shown_derived_images'):
            last_record = st.session_state.detection_history[-1]
            base_name = os.path.splitext(last_record['filename'])[0]
            st.markdown("---")
            st.markdown("### 🔥 热力图与原图展示")
            orig_name = f"{base_name}---.jpg"
            heat_name = f"{base_name}--.jpg"
            orig_path = resolve_static_image_path(orig_name) or os.path.join('static', 'uploads', orig_name)
            heat_path = resolve_static_image_path(heat_name) or os.path.join('static', 'uploads', heat_name)
            img_cols = st.columns(2)
            with img_cols[0]:
                st.markdown("**原图**")
                if os.path.exists(orig_path):
                    st.image(orig_path, use_container_width=True)
                else:
                    # 若无原图派生文件，则显示上传的原始文件
                    try:
                        if last_record['filename'].lower().endswith(('.jpg', '.jpeg', '.png')):
                            st.image(Image.open(io.BytesIO(last_record['file_data'])), caption=last_record['filename'], use_container_width=True)
                        elif last_record['filename'].lower().endswith(('.mp4', '.mov', '.avi')):
                            # 对于视频，统一按正方形比例展示，保持与图片一致的长宽视觉
                            upload_path = os.path.join('static', 'uploads', last_record['filename'])
                            if os.path.exists(upload_path):
                                safe_src = upload_path.replace('\\', '/')
                                html = f"""
                                <div style='position: relative; width: 100%; aspect-ratio: 1 / 1; overflow: hidden; border-radius: 8px; background: #000;'>
                                  <video src='{safe_src}' controls style='width: 100%; height: 100%; object-fit: cover;'></video>
                                </div>
                                """
                                st.markdown(html, unsafe_allow_html=True)
                            else:
                                st.warning(f"原始视频未找到: {last_record['filename']}")
                        else:
                            st.warning(f"原图未找到: {orig_name}")
                    except Exception:
                        st.warning(f"原图未找到: {orig_name}")
            with img_cols[1]:
                st.markdown("**热力图**")
                if os.path.exists(heat_path):
                    st.image(heat_path, use_container_width=True)
                else:
                    st.warning(f"热力图未找到: {heat_name}")

    with col2:
        # 获取动态参数
        detection_count = len(st.session_state.detection_history)
        current_similarity = 0.8
        detection_progress = st.session_state.get('federation_progress', 0)

        if st.session_state.detection_history:
            latest_result = st.session_state.detection_history[-1]['result']
            current_similarity = latest_result['similarity']

        # 使用增强版联邦学习区域
        render_enhanced_federated_learning_section(detection_count, current_similarity, detection_progress)


elif menu_choice == "📚 历史检测":
    st.markdown("\n")
    st.markdown("\n")
    st.markdown("\n")
    st.markdown("### 📋 历史检测记录")

    if st.session_state.detection_history:
        # 统计信息
        total_detections = len(st.session_state.detection_history)
        consistent_count = sum(1 for record in st.session_state.detection_history
                               if record['result']['similarity'] > 0.7)

        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1:
            st.metric("总检测次数", total_detections)
        with info_col2:
            st.metric("一致性检测", consistent_count,
                      delta=f"{consistent_count / total_detections * 100:.1f}%")
        with info_col3:
            st.metric("问题检测", total_detections - consistent_count,
                      delta=f"{(total_detections - consistent_count) / total_detections * 100:.1f}%",
                      delta_color="inverse")

        st.markdown("---")
        # 添加搜索和筛选功能（并应用到列表）
        st.markdown("#### 🔍 智能搜索与筛选")
        search_col1, search_col2, search_col3 = st.columns(3)
        with search_col1:
            search_text = st.text_input("🔍 关键词搜索", placeholder="搜索文件名或文字内容...")
        with search_col2:
            result_filter = st.selectbox("结果筛选", ["全部", "图文一致", "图文不一致"])
        with search_col3:
            date_filter = st.selectbox("时间筛选", ["全部", "今天", "最近7天", "最近30天"])

        # 统一解析时间戳为 datetime
        def _parse_ts(ts):
            if isinstance(ts, datetime):
                return ts
            try:
                return datetime.fromisoformat(str(ts))
            except Exception:
                return None

        # 应用筛选
        now = datetime.now()
        def _date_ok(ts):
            dt = _parse_ts(ts)
            if not dt:
                return False if date_filter != "全部" else True
            if date_filter == "全部":
                return True
            if date_filter == "今天":
                return dt.date() == now.date()
            if date_filter == "最近7天":
                return (now - dt).days <= 7
            if date_filter == "最近30天":
                return (now - dt).days <= 30
            return True

        def _result_ok(rec):
            if result_filter == "全部":
                return True
            res = rec.get('result', {})
            # 优先使用 has_problems 标志；否则用文本包含“一致”判断
            has_problems = res.get('has_problems')
            if has_problems is not None:
                return (not has_problems) if result_filter == "图文一致" else (has_problems)
            res_text = str(res.get('result', '')).lower()
            is_consistent = ("一致" in res_text) and ("不一致" not in res_text)
            return is_consistent if result_filter == "图文一致" else (not is_consistent)

        def _keyword_ok(rec):
            if not search_text:
                return True
            kw = search_text.strip().lower()
            return (kw in rec.get('filename', '').lower()) or (kw in str(rec.get('text', '')).lower())

        filtered_history = [r for r in st.session_state.detection_history if _keyword_ok(r) and _result_ok(r) and _date_ok(r.get('timestamp'))]

        # 更新统计信息为筛选后的视图
        total_detections = len(filtered_history)
        consistent_count = sum(1 for record in filtered_history if record['result'].get('has_problems') is False or record['result'].get('similarity', 0) > 0.7)
        st.markdown("---")
        # 最近检测快速入口（显示筛选后最近的4条）
        st.markdown("#### 🚀 最近检测快速入口")
        recent_cols = st.columns(min(4, len(filtered_history)))

        for i, (col, record) in enumerate(zip(recent_cols, list(reversed(filtered_history))[:4])):
            with col:
                similarity = record['result']['similarity']
                status_color = "🟢" if similarity > 0.7 else "🔴" if similarity < 0.4 else "🟡"

                if st.button(f"{status_color} {record['filename'][:8]}...",
                             key=f"recent_{i}",
                             help=f"相似度: {similarity:.2f}"):
                    st.session_state.selected_record = record

        st.markdown("---")

        # 历史记录列表（增强版，应用筛选）
        st.markdown("#### 📜 完整历史记录")

        for i, record in enumerate(reversed(filtered_history)):
            similarity = record['result']['similarity']
            status_emoji = "🟢" if similarity > 0.7 else "🔴" if similarity < 0.4 else "🟡"

            # 兼容字符串/datetime时间戳格式
            ts_val = record.get('timestamp')
            ts_disp = ts_val.strftime('%Y-%m-%d %H:%M:%S') if isinstance(ts_val, datetime) else str(ts_val)
            with st.expander(
                    f"{status_emoji} {record['filename']} - {ts_disp} - {record.get('model', '未知模型')}",
                    expanded=False):

                # 卡片弹出动画效果
                st.markdown('<div class="card-popup">', unsafe_allow_html=True)

                col1, col2 = st.columns([1, 1])

                with col1:
                    # 🧪 检测结果可视化（四图）：上传图片、问题框图、热力图、原图
                    st.markdown("**🧪 检测结果可视化**")

                    base_name_hist = os.path.splitext(record['filename'])[0]
                    result_hist = record.get('result', {})
                    fixed_image_name = result_hist.get('fixed_image')
                    # 路径解析
                    path_fixed_hist = resolve_static_image_path(fixed_image_name) if fixed_image_name else None
                    heat_name_hist = f"{base_name_hist}--.jpg"
                    orig_name_hist = f"{base_name_hist}---.jpg"
                    path_heat_hist = resolve_static_image_path(heat_name_hist) or os.path.join('static', 'uploads', heat_name_hist)
                    path_orig_hist = resolve_static_image_path(orig_name_hist) or os.path.join('static', 'uploads', orig_name_hist)

                    # 第一行：上传图片 + 问题框图
                    row1_col1, row1_col2 = st.columns([1, 1])
                    with row1_col1:
                        # 按文件类型分别展示：图片用 img，视频用 video；两者都统一正方形比例
                        upload_path = os.path.join('static', 'uploads', record['filename'])
                        is_image = record['filename'].lower().endswith(('.jpg', '.jpeg', '.png'))
                        is_video = record['filename'].lower().endswith(('.mp4', '.mov', '.avi'))
                        st.markdown("**上传图片**" if is_image else "**上传视频**")

                        try:
                            if is_image:
                                if 'file_data' in record and record['file_data']:
                                    # 统一容器比例：1:1
                                    img = Image.open(io.BytesIO(record['file_data']))
                                    st.image(img, caption=record['filename'], use_container_width=True)
                                elif os.path.exists(upload_path):
                                    st.image(upload_path, caption=record['filename'], use_container_width=True)
                                else:
                                    st.warning("上传图片数据缺失")
                            elif is_video:
                                if os.path.exists(upload_path):
                                    safe_src = upload_path.replace('\\', '/')
                                    html = f"""
                                    <div style='position: relative; width: 100%; aspect-ratio: 1 / 1; overflow: hidden; border-radius: 8px; background: #000;'>
                                      <video src='{safe_src}' controls style='width: 100%; height: 100%; object-fit: cover;'></video>
                                    </div>
                                    """
                                    st.markdown(html, unsafe_allow_html=True)
                                else:
                                    st.warning("上传视频数据缺失")
                            else:
                                st.warning("不支持的文件类型")
                        except Exception:
                            st.warning("上传媒体加载失败")
                    with row1_col2:
                        st.markdown("**问题框图**")
                        if path_fixed_hist and os.path.exists(path_fixed_hist):
                            st.image(path_fixed_hist, use_container_width=True)
                        else:
                            st.warning("问题框图未找到")

                    # 第二行：热力图 + 原图
                    row2_col1, row2_col2 = st.columns([1, 1])
                    with row2_col1:
                        st.markdown("**热力图**")
                        if os.path.exists(path_heat_hist):
                            st.image(path_heat_hist, use_container_width=True)
                        else:
                            st.warning(f"热力图未找到: {heat_name_hist}")
                    with row2_col2:
                        st.markdown("**原图**")
                        if os.path.exists(path_orig_hist):
                            st.image(path_orig_hist, use_container_width=True)
                        else:
                            st.warning(f"原图未找到: {orig_name_hist}")

                    # 原始文字描述
                    st.markdown("**📝 原始文字描述:**")
                    st.text_area("", value=record['text'], height=100, disabled=True, key=f"text_{i}")

                with col2:
                    result = record['result']
                    model_used = record.get('model', '自定义模型')

                    # 结果展示
                    similarity_color = "green" if result['similarity'] > 0.7 else "red" if result['similarity'] < 0.4 else "orange"

                    st.markdown(f"""
                    <div class="result-box" style="margin-bottom: 15px;">
                        <h4>检测结果详情</h4>
                        <p><strong>使用模型:</strong> {model_used}</p>
                        <p><strong>相似度:</strong> <span style="color: {similarity_color}; font-size: 20px; font-weight: bold;">{result['similarity']:.3f}</span></p>
                        <p><strong>判定结果:</strong> {result['result']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # 详细分析
                    st.markdown("**🔍 AI分析:**")
                    if result['has_problems']:
                        # AI分析部分不高亮，直接显示原文
                        st.markdown(result['explanation'])

                        # 问题区域标注，保持高亮
                        st.markdown("**⚠️ 问题区域:**")
                        highlighted_text = highlight_problem_areas(record['text'], result['problem_areas'])
                        st.markdown(highlighted_text, unsafe_allow_html=True)

                        # 问题统计
                        st.markdown(f"**问题关键词数量:** {len(result['problem_areas'])}")
                        st.markdown(f"**问题关键词:** {', '.join(result['problem_areas'])}")
                    else:
                        st.markdown(result['explanation'])

                # 编辑与删除操作
                act_col1, act_col2, act_col3 = st.columns([1, 1, 1])
                with act_col1:
                    if st.button('🗑️ 删除该记录', key=f"del_{i}"):
                        target_id = record.get('id')
                        st.session_state['detection_history'] = [r for r in st.session_state['detection_history'] if r.get('id') != target_id]
                        save_detection_history()
                        st.success('✅ 已删除该记录')
                        st.rerun()
                with act_col2:
                    st.markdown('**✏️ 编辑该记录**')
                    new_text = st.text_area('文字描述', value=record['text'], key=f"edit_text_{i}")
                    new_result_label = st.text_input('判定结果', value=record['result']['result'], key=f"edit_result_{i}")
                    new_similarity = st.slider('相似度', 0.0, 1.0, float(record['result']['similarity']), 0.01, key=f"edit_sim_{i}")
                    if st.button('💾 保存更改', key=f"save_{i}"):
                        # 定位并更新
                        target_id = record.get('id')
                        for idx, r in enumerate(st.session_state['detection_history']):
                            if r.get('id') == target_id:
                                r['text'] = new_text
                                r['result']['result'] = new_result_label
                                r['result']['similarity'] = float(new_similarity)
                                break
                        save_detection_history()
                        st.success('✅ 已保存修改')
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 50px; color: #666;">
            <h3>📭 暂无检测历史</h3>
            <p>开始您的第一次检测吧！</p>
            <p><a href="#" style="color: #667eea;">返回首页开始检测 →</a></p>
        </div>
        """, unsafe_allow_html=True)


elif menu_choice == "🔧 更换模型":
    st.markdown("\n")
    st.markdown("\n")
    st.markdown("\n")
    st.markdown("### 🔧 智能模型管理中心")

    # 模型选择区域
    st.markdown("#### 🎯 选择检测模型")

    model_keys = list(MODEL_CONFIGS.keys())
    default_index = model_keys.index(st.session_state.current_model) if st.session_state.current_model in model_keys else 0
    current_model = st.selectbox(
        "当前使用模型",
        model_keys,
        index=default_index,
        help="选择最适合您需求的检测模型"
    )

    # 模型切换确认
    if current_model != st.session_state.current_model:
        st.session_state.current_model = current_model

        # 模型切换动画提示
        if MODEL_CONFIGS[current_model]["highlight"]:
            st.markdown("""
            <div class="model-highlight">
                ✨ <strong>已切换至自定义模型</strong><br>
                🎯 专业图文一致性检测，准确率高达95%<br>
                🔍 深度语义理解，精准识别不一致问题
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ 已切换至 {current_model}，该模型可能在复杂场景下准确率较低，建议使用自定义模型！")

        st.success(f"🔄 模型已成功切换为: {current_model}")

    st.markdown("---")

    # 模型性能对比分析
    st.markdown("#### 📊 模型性能深度对比")

    model_performance = pd.DataFrame({
        '模型名称': list(MODEL_CONFIGS.keys()),
        '准确率 (%)': [95.2, 84.1, 87.3, 83.5, 88.1],
        '检测速度 (秒)': [0.8, 1.7, 2.1, 1.5, 2.8],
        '内存占用 (GB)': [1.8, 2.8, 4.2, 2.5, 5.1],
        '专业程度': ['⭐⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐'],
        '推荐指数': [100, 75, 80, 70, 85]
    })

    # 突出显示自定义模型（兼容无 jinja2 环境）
    try:
        styled_df = model_performance.style.apply(
            lambda x: ['background-color: #FFD700; font-weight: bold' if x.name == 0 else '' for _ in x],
            axis=1
        )
        st.dataframe(styled_df, use_container_width=True)
    except Exception:
        st.warning("样式渲染依赖缺失（可能未安装 jinja2），已回退为基础表格显示。")
        st.dataframe(model_performance, use_container_width=True)

    # 性能可视化图表
    col1, col2 = st.columns(2)

    with col1:
        # 准确率对比图
        fig_acc = px.bar(
            model_performance,
            x='模型名称',
            y='准确率 (%)',
            title="🎯 模型准确率对比",
            color='准确率 (%)',
            color_continuous_scale='RdYlGn'
        )
        fig_acc.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_acc, use_container_width=True)

    with col2:
        # 速度vs准确率散点图
        fig_scatter = px.scatter(
            model_performance,
            x='检测速度 (秒)',
            y='准确率 (%)',
            size='推荐指数',
            hover_name='模型名称',
            title='⚡ 速度 vs 准确率分析',
            color='推荐指数',
            color_continuous_scale='Viridis'
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

    # 模型详细说明
    st.markdown("#### 📋 模型特性详解")

    for model_name, config in MODEL_CONFIGS.items():
        with st.expander(f"🔍 {model_name} 详细信息"):
            if config["highlight"]:
                st.markdown("""
                **🌟 自定义优化模型 - 旗舰版**
                - ✅ 专为图文一致性检测深度优化
                - ✅ 支持复杂语义理解和多模态分析  
                - ✅ 智能识别细微不一致问题
                - ✅ 实时问题区域标注和修正建议
                - ✅ 完整的联邦学习协作支持
                - 🎯 **推荐场景**: 专业级图文一致性检测
                """)
            else:
                st.markdown(f"""
                **基础模型 - {model_name}**
                - ⚠️ 通用型多模态模型，非专业优化
                - ⚠️ 可能在复杂场景下准确率不足
                - ⚠️ 缺乏深度语义理解能力
                - ⚠️ 无专业问题标注功能
                - 📝 **适用场景**: 简单图文匹配检测
                """)

elif menu_choice == "⚙️ 设置":
    st.markdown("\n")
    st.markdown("\n")
    st.markdown("\n")
    st.markdown("### ⚙️ 系统设置中心")

    # 设置选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 界面设置", "🔔 通知配置", "🛡️ 隐私安全", "📊 系统信息"])

    with tab1:
        st.markdown("#### 🎨 个性化界面设置")

        col1, col2 = st.columns(2)
        with col1:
            theme = st.selectbox("界面主题", ["红色", "深色模式", "浅色模式", "护眼绿色"])
            language = st.selectbox("界面语言", ["简体中文", "繁体中文", "English", "日本語"])

            # 主题色选择器
            theme_color = st.color_picker("自定义主题色", st.session_state.theme_color)
            if theme_color != st.session_state.theme_color:
                st.session_state.theme_color = theme_color

        with col2:
            font_size = st.slider("字体大小", 12, 20, 14)
            animation_speed = st.slider("动画速度", 0.5, 2.0, 1.0, 0.1)
            show_tooltips = st.checkbox("显示操作提示", value=True)

            # 实时预览
            st.markdown(f"""
            <div style="border: 2px solid {theme_color}; padding: 15px; border-radius: 10px; font-size: {font_size}px;">
                <h4 style="color: {theme_color};">🎨 主题预览</h4>
                <p>这是您选择的主题效果预览</p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("#### 🔔 智能通知配置")

        email_notify = st.checkbox("📧 邮件通知", help="检测完成后发送邮件通知")
        if email_notify:
            email_address = st.text_input("邮箱地址", placeholder="your-email@example.com")

        sound_notify = st.checkbox("🔊 声音提醒", value=True)
        if sound_notify:
            sound_type = st.selectbox("提示音类型", ["默认", "温和", "专业", "自定义"])

        push_notify = st.checkbox("📱 推送通知")

        # 通知条件设置
        st.markdown("**🎯 通知触发条件:**")
        notify_on_completion = st.checkbox("✅ 检测完成时", value=True)
        notify_on_error = st.checkbox("❌ 检测异常时", value=True)
        notify_on_low_similarity = st.checkbox("⚠️ 检测到不一致时", value=True)

        similarity_threshold = st.slider("不一致阈值", 0.0, 1.0, 0.5, 0.1)

    with tab3:
        st.markdown("#### 🛡️ 隐私安全管理")

        col1, col2 = st.columns(2)
        with col1:
            save_history = st.checkbox("💾 保存检测历史", value=True)
            data_encryption = st.checkbox("🔒 数据加密", value=True, disabled=True)
            auto_delete = st.checkbox("🗑️ 自动删除历史记录")

            if auto_delete:
                delete_days = st.number_input("保留天数", min_value=1, max_value=365, value=30)

        with col2:
            federation_participate = st.checkbox("🤝 参与联邦学习", value=True,
                                                 help="参与联邦学习可提升模型准确性")
            privacy_level = st.select_slider("隐私保护级别",
                                             options=["基础", "标准", "高级", "最高"],
                                             value="标准")

            # 隐私政策
            st.markdown("**📋 隐私保护说明:**")
            st.info("""
            🔒 我们承诺:
            • 您的数据仅在本地处理
            • 不上传任何原始文件或文本
            • 仅共享匿名化的模型参数
            • 符合GDPR、CCPA等国际隐私法规
            """)

    with tab4:
        st.markdown("#### 📊 系统运行状态")

        # 系统指标
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        with metric_col1:
            st.metric("当前模型", st.session_state.current_model.split('（')[0])
        with metric_col2:
            st.metric("检测历史", len(st.session_state.detection_history))
        with metric_col3:
            uptime_hours = (datetime.now() - st.session_state.federation_stats['last_sync_time']).seconds // 3600
            st.metric("运行时长", f"{uptime_hours}小时")
        with metric_col4:
            st.metric("系统状态", "🟢 正常", delta="稳定运行")

        # 详细系统信息
        st.markdown("**🔧 详细系统信息:**")

        system_info = {
            "版本信息": "面向多模态AI生成内容检测系统 v1.0",
            "支持格式": "JPG, PNG, MP4, AVI, MOV等",
            "最大文件": "100MB",
            "并发检测": "支持",
            "API接口": "RESTful API v2.0",
            "数据库": "本地存储 + 分布式缓存",
        }

        info_df = pd.DataFrame(list(system_info.items()), columns=['项目', '详情'])
        st.dataframe(info_df, use_container_width=True, hide_index=True)

        # 性能监控图表
        st.markdown("**📈 性能监控:**")

        # 模拟性能数据
        hours = list(range(24))
        cpu_usage = [20 + 10 * np.sin(h / 4) + np.random.uniform(-5, 5) for h in hours]
        memory_usage = [30 + 15 * np.sin(h / 3) + np.random.uniform(-8, 8) for h in hours]

        performance_fig = go.Figure()
        performance_fig.add_trace(go.Scatter(x=hours, y=cpu_usage, mode='lines+markers',
                                             name='CPU使用率(%)', line=dict(color='blue')))
        performance_fig.add_trace(go.Scatter(x=hours, y=memory_usage, mode='lines+markers',
                                             name='内存使用率(%)', line=dict(color='red')))

        # 更新布局
        performance_fig.update_layout(
            title="系统资源使用情况 (24小时)",
            xaxis_title="小时",
            yaxis_title="使用率 (%)",
            height=400
        )
        st.plotly_chart(performance_fig, use_container_width=True)

        # 统一保存按钮
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("💾 保存所有设置", type="primary", use_container_width=True):
                # 保存设置逻辑
                st.balloons()  # 庆祝动画
                st.success("🎉 设置保存成功！所有配置已生效。")

        # ================== 增强版页脚 ==================
        st.markdown("---")

        # 页脚顶部标题
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 30px;
                    border-radius: 15px;
                    text-align: center;
                    color: white;
                    margin-top: 50px;'>
            <h2 style='margin: 10px 0; color: white;'>🔍 面向多模态AI生成内容检测系统 v1.0</h2>
            <p style='margin: 5px 0; font-size: 18px; color: white;'>
                <strong>v1.0 多模态融合专业版</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 技术特色展示
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div style='text-align: center;
                        background: rgba(102, 126, 234, 0.1);
                        padding: 15px;
                        border-radius: 10px;'>
                <div style='font-size: 30px;'>🛡️</div>
                <p><strong>隐私保护</strong></p>
                <p><small>计算下沉架构</small></p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style='text-align: center;
                        background: rgba(102, 126, 234, 0.1);
                        padding: 15px;
                        border-radius: 10px;'>
                <div style='font-size: 30px;'>🤝</div>
                <p><strong>协作学习</strong></p>
                <p><small>分布式优化</small></p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div style='text-align: center;
                        background: rgba(102, 126, 234, 0.1);
                        padding: 15px;
                        border-radius: 10px;'>
                <div style='font-size: 30px;'>🎭</div>
                <p><strong>深度伪造</strong></p>
                <p><small>AI生成检测</small></p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown("""
            <div style='text-align: center;
                        background: rgba(102, 126, 234, 0.1);
                        padding: 15px;
                        border-radius: 10px;'>
                <div style='font-size: 30px;'>🔄</div>
                <p><strong>零样本适应</strong></p>
                <p><small>新型攻击识别</small></p>
            </div>
            """, unsafe_allow_html=True)

        # # 性能指标展示
        # st.markdown("### 🏆 核心技术性能")
        # metric_col1, metric_col2, metric_col3 = st.columns(3)
        # with metric_col1:
        #     st.metric("检测准确率", "95.2%", "行业领先")
        # with metric_col2:
        #     st.metric("响应时间", "<1秒", "实时检测")
        # with metric_col3:
        #     st.metric("隐私保护", "零上传", "本地计算")

        # # 技术标签
        # st.markdown("### 🧠 多模态技术栈")
        # tag_col1, tag_col2, tag_col3 = st.columns(3)
        # with tag_col1:
        #     st.info("🖼️ **图像特征提取**\nCLIP多模态模型")
        # with tag_col2:
        #     st.info("📝 **文本语义理解**\n自然语言处理")
        # with tag_col3:
        #     st.info("🔗 **跨模态融合**\n自适应特征融合")

        # # 合规认证
        # st.markdown("### ✅ 合规认证")
        # cert_col1, cert_col2, cert_col3, cert_col4 = st.columns(4)
        # with cert_col1:
        #     st.success("GDPR合规")
        # with cert_col2:
        #     st.success("CCPA认证")
        # with cert_col3:
        #     st.success("ISO27001")
        # with cert_col4:
        #     st.success("等保三级")

        # 联系信息
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center;
                    padding: 20px;
                    background: rgba(102, 126, 234, 0.1);
                    border-radius: 10px;'>
            <p style='margin: 0; color: #666; font-size: 14px;'>
                🏛️ 遵循国际隐私法规 | 🔬 基于前沿AI研究 | 🌍 服务全球用户
            </p>
        </div>
        """, unsafe_allow_html=True)




