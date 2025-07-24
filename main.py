from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/test")
def test():
    return {"code":"0","message":"This is a test."}

if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0", port=8000, reload=True)
