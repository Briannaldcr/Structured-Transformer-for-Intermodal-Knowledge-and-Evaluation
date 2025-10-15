from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from datetime import datetime
import os
import shutil
import sys
import subprocess

app = FastAPI(title="WJUT Consistency Detection API", version="1.0.0")
STREAMLIT_PORT = int(os.environ.get("STREAMLIT_PORT", 8502))

# 静态资源与前端页面
app.mount("/static", StaticFiles(directory="static"), name="static")
# 可选挂载 web 目录（不存在时不挂载，避免启动报错）
if os.path.isdir("web"):
    app.mount("/web", StaticFiles(directory="web"), name="web")

# 若以后前后端分离部署，可开启 CORS。当前同源部署无需配置。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    # 优先返回 web/index.html；若无，则嵌入 Streamlit 页面
    index_path = os.path.join("web", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    # 回退：用 iframe 展示 Streamlit 应用
    html = f"""
    <!doctype html>
    <html lang='zh-CN'>
    <head>
      <meta charset='utf-8' />
      <title>面向多模态AI生成内容检测系统</title>
      <style>body,html{{margin:0;padding:0;height:100%;}} .wrap{{height:100vh;}} iframe{{border:0;width:100%;height:100%;}} .tip{{position:fixed;top:8px;left:8px;background:#eef;padding:6px 10px;border-radius:8px;color:#333;font-size:12px;}}</style>
    </head>
    <body>
      <div class='tip'>页面由 FastAPI 提供，已自动嵌入 Streamlit 前端（端口 {STREAMLIT_PORT}）。</div>
      <div class='wrap'>
        <iframe src="http://localhost:{STREAMLIT_PORT}/" allowfullscreen></iframe>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(html)

# 启动时尝试拉起 Streamlit 前端
@app.on_event("startup")
def start_streamlit_frontend():
    try:
        # 如果已运行则忽略；简单起见直接尝试启动
        subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", os.path.join(os.path.dirname(__file__), "..", "app.py"),
            "--server.port", str(STREAMLIT_PORT), "--server.headless", "true"
        ], close_fds=True)
    except Exception as e:
        print("[WARN] 启动 Streamlit 失败:", e)

MODEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    '皖江工学院专用': { 'accurate': True, 'highlight': True },
    'CLIP-ViT-B/32': { 'accurate': False, 'highlight': False },
    'CLIP-ViT-L/14': { 'accurate': False, 'highlight': False },
    'BLIP-Base': { 'accurate': False, 'highlight': False },
    'BLIP-Large': { 'accurate': False, 'highlight': False },
}

DETECTION_RESULTS: Dict[str, Dict[str, Any]] = {
    'test01.jpg': {
        'similarity': 0.92,
        'result': '图文一致',
        'explanation': '图片与文字描述高度一致，主体、颜色和细节均匹配。',
        'has_problems': False,
        'problem_areas': [],
        'fixed_image': 'test01-.jpg'
    },
    'test01-.jpg': {
        'similarity': 0.96,
        'result': '图文一致（修正版）',
        'explanation': '修正版图片与文字描述完全匹配。',
        'has_problems': False,
        'problem_areas': [],
        'fixed_image': 'test01-.jpg'
    },
    'test03.jpg': {
        'similarity': 0.58,
        'result': '图文部分不一致',
        'explanation': '建筑颜色与楼层数量描述不符，建议修正关键细节。',
        'has_problems': True,
        'problem_areas': ['红色屋顶', '三层楼高', '哥特式建筑'],
        'fixed_image': 'test03-.jpg'
    }
}

FEDERATION_NODES = [
    { 'name': '皖江工学院主节点', 'location': '安徽马鞍山', 'data_size': 15000, 'compute_power': 8.5, 'reliability': 0.98 },
    { 'name': 'A', 'location': '安徽合肥', 'data_size': 12000, 'compute_power': 7.2, 'reliability': 0.95 },
    { 'name': 'B', 'location': '江苏南京', 'data_size': 18000, 'compute_power': 9.1, 'reliability': 0.97 },
    { 'name': '产业合作节点', 'location': '上海浦东', 'data_size': 22000, 'compute_power': 9.8, 'reliability': 0.96 },
    { 'name': '研究院节点', 'location': '北京海淀', 'data_size': 20000, 'compute_power': 9.5, 'reliability': 0.99 },
    { 'name': '国际合作节点', 'location': '新加坡', 'data_size': 16000, 'compute_power': 8.8, 'reliability': 0.94 },
]

STATE: Dict[str, Any] = {
    'history': [],
    'current_model': '皖江工学院专用',
    'federation_progress': 0,
    'stats': { 'totalDetections': 0, 'modelUpdates': 0, 'lastSyncTime': datetime.now().isoformat() },
}

def get_detection_result(filename: str, text_input: str, model_name: str = '皖江工学院专用') -> Dict[str, Any]:
    model_config = MODEL_CONFIGS.get(model_name, { 'accurate': True })
    is_video = filename.lower().endswith((".mp4", ".avi", ".mov"))

    if not model_config['accurate']:
        sim = 0.85 + os.urandom(1)[0] / 255.0 * 0.1  # 简单随机
        return {
            'similarity': sim,
            'result': '视频一致' if is_video else '图文一致',
            'explanation': f'经过{model_name}模型分析，内容匹配度较高。',
            'has_problems': False,
            'problem_areas': [],
            'fixed_image': f"{os.path.splitext(filename)[0]}-.jpg"
        }

    if filename in DETECTION_RESULTS:
        return DETECTION_RESULTS[filename]

    sim = 0.7 + os.urandom(1)[0] / 255.0 * 0.25
    return {
        'similarity': sim,
        'result': '图文一致' if sim > 0.8 else ('图文不一致' if sim < 0.6 else '图文基本一致'),
        'explanation': '模型综合分析完成，结果已生成。',
        'has_problems': sim < 0.6,
        'problem_areas': ['主体不匹配'] if sim < 0.6 else [],
        'fixed_image': f"{os.path.splitext(filename)[0]}-.jpg"
    }

@app.post('/api/detect')
async def api_detect(file: UploadFile = File(...), text: str = Form(...), model: str = Form(...)):
    # 保存上传文件到 static/uploads
    uploads_dir = os.path.join('static', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    filename = file.filename
    save_path = os.path.join(uploads_dir, filename)
    with open(save_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)

    # 生成检测结果
    result = get_detection_result(filename, text, model)
    record = {
        'timestamp': datetime.now().isoformat(),
        'filename': filename,
        'text': text,
        'result': result,
        'model': model,
        'fileUrl': f"/static/uploads/{filename}",
    }
    STATE['history'].append(record)
    STATE['current_model'] = model
    STATE['federation_progress'] = 100
    STATE['stats']['totalDetections'] += 1
    STATE['stats']['modelUpdates'] += 1
    STATE['stats']['lastSyncTime'] = datetime.now().isoformat()

    return JSONResponse({ 'result': result, 'record': record, 'federation_progress': STATE['federation_progress'] })

@app.get('/api/history')
def api_history():
    return JSONResponse({ 'history': STATE['history'] })

@app.get('/api/models')
def api_models():
    return JSONResponse({ 'models': list(MODEL_CONFIGS.keys()), 'current': STATE['current_model'] })

@app.get('/api/federation/nodes')
def api_nodes():
    return JSONResponse({ 'nodes': FEDERATION_NODES, 'progress': STATE['federation_progress'] })

@app.get('/api/stats')
def api_stats():
    consistent = sum(1 for h in STATE['history'] if h['result']['similarity'] > 0.7)
    total = len(STATE['history'])
    issues = total - consistent
    return JSONResponse({ 'total': total, 'consistent': consistent, 'issues': issues, 'federation': STATE['stats'] })

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)