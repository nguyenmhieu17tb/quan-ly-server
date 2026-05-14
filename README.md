# Phần mềm quản lý server cho DevOps (MVP)

Ứng dụng gồm:
- **Backend API (Python/FastAPI)** để quản lý server.
- **Frontend UI (Node.js + Express + HTML/CSS/JS)** để thao tác trực quan.
- **Docker / Docker Compose** để chạy nhanh toàn bộ MVP.

Thông tin server quản lý:
- `IP`
- `PORT`
- `username`
- `password`
- `cpu_cores`
- `ram_gb`
- thêm `environment`, `name`, `note`

## 1) Chạy bằng Docker Compose (khuyến nghị)

```bash
docker compose up --build
```

Sau khi chạy:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

Dữ liệu SQLite được lưu ở thư mục host `./data/servers.db`.

## 2) Chạy local không Docker

### Backend API

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend chạy tại: `http://127.0.0.1:8000`

### Frontend Node.js

Mở terminal khác:

```bash
cd frontend
npm install
npm start
```

Frontend chạy tại: `http://localhost:3000`

## 3) API chính

- `POST /servers`: tạo server
- `GET /servers`: danh sách server (hỗ trợ filter `?env=production`)
- `GET /servers/{id}`: chi tiết server
- `PATCH /servers/{id}`: cập nhật server
- `DELETE /servers/{id}`: xoá server

## 4) Lưu ý bảo mật

Bản MVP này đang lưu `password` dạng plain text để phát triển nhanh.
Trước khi dùng production, nên:
- mã hoá/băm password hoặc dùng vault/secrets manager,
- thêm authentication/authorization,
- thêm audit log và phân quyền người dùng.
