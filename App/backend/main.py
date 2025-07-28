from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import tất cả router ở một nơi
from api.movie import router as movie_router
from api.auth import router as auth_router
from api.search import router as search_router
from api.rating import router as rating_router
from api.user import router as user_router

app = FastAPI(
    title="Movie API",
    description="Backend API",
    version="2.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Danh sách các router cần include
routers = [
    (movie_router, "/api/v1", ["movies"]),
    (search_router, "/api/v1", ["movies"]),
    (auth_router, "/api/v1", ["Authentication"]),
    (rating_router, "/api/v1", ["Rating"]),
    (user_router, "/api/v1", ["UserLog"])   # <-- thêm dòng này
]




# Gộp router
for router, prefix, tags in routers:
    app.include_router(router, prefix=prefix, tags=tags)


@app.get("/")
async def root():
    return {"message": "Welcome to the Movie API"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5000)

