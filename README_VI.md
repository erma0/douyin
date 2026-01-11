![douyin](https://socialify.git.ci/erma0/douyin/image?description=1&font=Source%20Code%20Pro&forks=1&issues=1&language=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Auto)

# ✨DouyinCrawler

**[English](./README_EN.md) | Tiếng Việt | [简体中文](./README.md)**

> ❤️[Mã nguồn mở không dễ dàng, hoan nghênh tặng sao⭐](#star-history)

## 📢Tuyên bố từ chối trách nhiệm

> Mục đích ban đầu của dự án này là học `python` crawler, gọi dòng lệnh `Aria2` và các trường hợp triển khai `WebUI` bằng `python`. Sau đó nó được sử dụng để trải nghiệm lập trình AI (phần giao diện người dùng và tương tác backend đều do AI tạo ra). Chức năng ứng dụng là lấy thông tin công khai trên nền tảng Douyin, chỉ dùng cho mục đích kiểm tra và nghiên cứu học tập, nghiêm cấm sử dụng cho mục đích thương mại hoặc bất kỳ mục đích bất hợp pháp nào.
>
> Bất kỳ người dùng nào sử dụng trực tiếp hoặc gián tiếp hoặc phổ biến nội dung của kho lưu trữ này đều phải tự chịu trách nhiệm về hành động của mình và những người đóng góp cho kho lưu trữ này không chịu trách nhiệm về bất kỳ hậu quả nào phát sinh từ những hành động đó.
>
> **Nếu các bên liên quan tin rằng mã của dự án này có thể vi phạm quyền của họ, vui lòng liên hệ với tôi ngay lập tức để xóa mã liên quan**.
>
> Việc sử dụng nội dung của kho lưu trữ này có nghĩa là bạn đồng ý với tất cả các điều khoản và điều kiện của tuyên bố từ chối trách nhiệm này. Nếu bạn không chấp nhận tuyên bố từ chối trách nhiệm trên, vui lòng ngừng sử dụng dự án này ngay lập tức.

---

## 🏠Địa chỉ dự án

> [https://github.com/erma0/douyin](https://github.com/erma0/douyin)

## 🍬Tính năng

### 📊 Thu thập dữ liệu
- ✅ Tác phẩm đơn / Bài đăng người dùng / Yêu thích / Bộ sưu tập
- ✅ Hashtag / Mix / Nhạc / Tìm kiếm từ khóa

### 🎯 Tính năng ứng dụng
- 🔄 **Thu thập tăng dần**: Thu thập tăng dần thông minh các tác phẩm trang chủ người dùng
- ⬇️ **Tải xuống hàng loạt**: Tích hợp Aria2, hỗ trợ tải xuống hàng loạt video/hình ảnh
- 🎨 **Nhiều chế độ**: Ứng dụng GUI / Máy chủ Web / Dòng lệnh
- 🌐 **RESTful API**: v2.0 cung cấp HTTP API đầy đủ

## 📸 Giao diện

![Giao diện phần mềm](./docs/images/main.png)

## 🚀Bắt đầu nhanh

### Người dùng Windows

Tải xuống từ [Releases](https://github.com/erma0/douyin/releases), giải nén và chạy `DouyinCrawler.exe`

### Máy chủ / Docker / Linux

```bash
# Docker (Khuyên dùng)
docker compose up -d

# Hoặc khởi động thủ công
uv sync
cd frontend && pnpm install && pnpm build && cd ..
python -m backend.server
```

Truy cập `http://localhost:8000`

### Dòng lệnh

```bash
python -m backend.cli -u https://www.douyin.com/user/xxx -l 20
```

📖 Hướng dẫn sử dụng chi tiết vui lòng xem [USAGE_VI.md](USAGE_VI.md)

## 🔨Xây dựng và Đóng gói

```powershell
# Menu tương tác
.\quick-start.ps1

# Hoặc đóng gói trực tiếp
.\scripts\build\pyinstaller.ps1
```

Cấu trúc thư mục script:
```
scripts/
├── build/          # Script đóng gói (PyInstaller / Nuitka)
├── setup/          # Cấu hình môi trường (uv / aria2)
└── dev.ps1         # Xây dựng môi trường phát triển
```

## 📊 Tech Stack

- **Backend**: Python 3.12, FastAPI, PyWebView
- **Frontend**: React 18, TypeScript, Vite
- **Tải xuống**: Aria2
- **Đóng gói**: PyInstaller / Nuitka

## Lịch sử Star

[![Star History Chart](https://api.star-history.com/svg?repos=erma0/douyin&type=Date)](https://star-history.com/#erma0/douyin&Date)
