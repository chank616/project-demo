from fastapi import FastAPI
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

if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0", port=8000, reload=False)
