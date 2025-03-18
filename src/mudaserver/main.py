from fastapi import FastAPI
import uvicorn


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI with Poetry!"}


def main():
    uvicorn.run(app="src.mudaserver.main:app")

if __name__ == "__main__":
    main()