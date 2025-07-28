import asyncio
from asyncio import subprocess
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import psutil
import uvicorn

app = FastAPI()

@app.get("/test")
def test():
    return {"code": "0","message":"This is a test."}

@app.get("/testv2")
def testv2(name: str):
    return {"code": "0","message": f"Hello {name}"}

@app.get("/testv3")
def testv3():
    return {"code": "0","message": "Just test for deploy."}
# 获取 CPU 温度（Linux）
def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read().strip()) / 1000
            return round(temp, 1)
    except:
        return None
# 获取内存使用率
def get_mem_usage():
    mem = psutil.virtual_memory()
    return {
        "used": round(mem.used / (1024 ** 3), 1),  # GB
        "total": round(mem.total / (1024 ** 3), 1),
        "percent": mem.percent
    }
# 获取硬盘温度（需 smartctl）
def get_disk_temp(disk="/dev/nvme0"):
    try:
        result = subprocess.run(
            ["sudo", "smartctl", "-A", disk],
            capture_output=True,
            text=True
        )
        output = result.stdout
        if "Temperature_Celsius" in output:
            for line in output.split('\n'):
                if "Temperature_Celsius" in line:
                    return int(line.split()[-1])
        return None
    except:
        return None
# WebSocket 实时推送数据
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = {
            "cpu_temp": get_cpu_temp(),
            "mem_usage": get_mem_usage(),
            "disk_temp": get_disk_temp(),
        }
        await websocket.send_json(data)
        await asyncio.sleep(1)  # 每秒推送一次

# 提供测试页面
@app.get("/")
def read_root():
    return HTMLResponse("""
    <html>
        <head>
            <title>服务器监控</title>
            <script>
                const ws = new WebSocket("ws://" + window.location.host + "/ws");
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    document.getElementById("cpu").innerText = `CPU 温度: ${data.cpu_temp || 'N/A'}°C`;
                    document.getElementById("mem").innerText = `内存: ${data.mem_usage.percent}% (${data.mem_usage.used}GB/${data.mem_usage.total}GB)`;
                    document.getElementById("disk").innerText = `硬盘温度: ${data.disk_temp || 'N/A'}°C`;
                };
            </script>
        </head>
        <body>
            <h1>服务器实时监控</h1>
            <p id="cpu">CPU 温度: 加载中...</p>
            <p id="mem">内存: 加载中...</p>
            <p id="disk">硬盘温度: 加载中...</p>
        </body>
    </html>
    """)

if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0", port=8000, reload=False)
