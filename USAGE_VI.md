# Hướng dẫn sử dụng

**[English](./USAGE_EN.md) | Tiếng Việt | [简体中文](./USAGE.md)**

## 📋 Mục lục

- [Lấy Cookie](#lấy-cookie)
- [Tính năng](#tính-năng)
- [Câu hỏi thường gặp](#câu-hỏi-thường-gặp)
- [Sử dụng nâng cao](#sử-dụng-nâng-cao)

---

## 🍪 Lấy Cookie

Cookie là thông tin xác thực cần thiết để lấy dữ liệu.

### Cách 1: Đăng nhập để lấy (Có thể không hoạt động)

> 💡 Chỉ chế độ GUI

1. Mở cài đặt ứng dụng
2. Nhấp vào nút "Đăng nhập để lấy"
3. Hoàn thành đăng nhập Douyin trong cửa sổ bật lên (hỗ trợ mã QR/số điện thoại)
4. Cookie sẽ được tự động điền sau khi đăng nhập thành công
5. Nhấp "Lưu cài đặt"

### Cách 2: Thủ công (Khuyến nghị)

1. Truy cập `https://www.douyin.com/search/deepseek?type=video` và đăng nhập
2. Nhấn `F12` để mở công cụ nhà phát triển
3. Chuyển sang tab `Network`, làm mới trang
4. Nhập `/aweme/v1/web/search/item` vào bộ lọc, nhấp vào bất kỳ yêu cầu nào
5. Tìm trường `Cookie:` trong `Request Headers`, sao chép toàn bộ nội dung
6. Dán và lưu trong cài đặt ứng dụng

> 💡 Mẹo: Khuyến nghị làm theo hình ảnh bên dưới để lấy Cookie, lọc các yêu cầu post, sao chép nội dung trường `Cookie:`.

![Sơ đồ](./docs/images/image.png)

Cookie hợp lệ phải chứa: `sessionid`, `ttwid`

---

## 🎯 Tính năng

### Loại thu thập

| Loại | Mô tả | Ví dụ đầu vào | Trạng thái |
|------|-------|---------------|------------|
| **Tác phẩm đơn** | Lấy thông tin tác phẩm đơn | `https://www.douyin.com/video/7xxx` | ✅ Bình thường |
| **Bài đăng người dùng** | Lấy tác phẩm đã đăng | `https://www.douyin.com/user/MS4wLjABxxx` | ✅ Bình thường |
| **Yêu thích người dùng** | Lấy tác phẩm đã thích | `https://www.douyin.com/user/MS4wLjABxxx` | ✅ Bình thường |
| **Bộ sưu tập người dùng** | Lấy tác phẩm đã lưu | `https://www.douyin.com/user/MS4wLjABxxx` | ✅ Bình thường |
| **Hashtag** | Lấy tác phẩm hashtag | `https://www.douyin.com/hashtag/xxx` | ✅ Bình thường |
| **Mix** | Lấy tác phẩm mix/playlist | `https://www.douyin.com/mix/xxx` | ✅ Bình thường |
| **Nhạc** | Lấy tác phẩm sử dụng nhạc | `https://www.douyin.com/music/7xxx` | ✅ Bình thường |
| **Tìm kiếm từ khóa** | Tìm kiếm tác phẩm liên quan | `phong cảnh` | ✅ Bình thường |
| **Đang theo dõi** | Lấy người dùng đang theo dõi | `https://www.douyin.com/user/MS4wLjABxxx` | ✅ Bình thường |
| **Người theo dõi** | Lấy người theo dõi | `https://www.douyin.com/user/MS4wLjABxxx` | ✅ Bình thường |

### Tải xuống hàng loạt

Cần hỗ trợ Aria2:

```powershell
# Cài đặt Aria2
.\scripts\setup\aria2.ps1
```

Nhấp "Tải xuống tất cả" để tự động tải xuống kết quả thu thập qua Aria2.

> 💡 Mẹo: Trong chế độ CLI, tải xuống được bật mặc định, có thể tắt bằng tham số `--no-download`.

### Cài đặt

| Tùy chọn | Mặc định | Mô tả |
|----------|----------|-------|
| Đường dẫn tải xuống | `./download` | Thư mục lưu tệp tải xuống |
| Số lần thử lại tối đa | 3 | Số lần thử lại tối đa khi tải xuống thất bại (0-10) |
| Số lượng đồng thời tối đa | 5 | Số tác vụ tải xuống đồng thời (1-10) |
| Máy chủ Aria2 | `localhost` | Địa chỉ máy chủ Aria2 RPC |
| Cổng Aria2 | 6800 | Cổng dịch vụ Aria2 RPC |
| Mật khẩu Aria2 | `douyin_crawler_default_secret` | Mật khẩu Aria2 RPC |
| Thu thập tăng dần | Bật | Chỉ thu thập tác phẩm mới (chỉ trang chủ người dùng) |
| Tải tiêu đề | Tắt | Lưu tiêu đề tác phẩm dưới dạng tệp văn bản |
| Tải bìa | Tắt | Tải xuống hình ảnh bìa tác phẩm |
| Khoảng thời gian tải xuống | 0 | Khoảng thời gian giữa các tác vụ tải xuống tính bằng giây (0-60), 0 = không khoảng |

---

## ❓ Câu hỏi thường gặp

### Cookie không hợp lệ hoặc đã hết hạn

Lấy lại Cookie, đảm bảo chứa các trường cần thiết như `sessionid`.

> 💡 Mẹo: Khuyến nghị làm theo sơ đồ trong phần [Lấy Cookie](#lấy-cookie).

### Kết quả thu thập trống

1. Kiểm tra định dạng liên kết có đúng không
2. Cập nhật Cookie
3. Cần người dùng mục tiêu mở quyền

### Tải xuống thất bại

1. Xác nhận Aria2 đã được cài đặt: `aria2c --version`
2. Kiểm tra đường dẫn tải xuống/dung lượng ổ đĩa
3. Thử giảm số lượng đồng thời
4. Một số tác vụ có thể thất bại vì lý do không rõ, thử nhiều lần

### Khởi động ứng dụng thất bại

1. Xác nhận frontend đã được xây dựng
2. Xác nhận đã cài đặt dependencies
3. Xác nhận không bị chặn bởi tường lửa hoặc phần mềm bảo mật
4. Xác nhận đã cài đặt webview2 (người dùng Windows GUI)

### Liên hệ hỗ trợ

Khi gửi [Issue](https://github.com/erma0/douyin/issues), vui lòng bao gồm: liên kết mục tiêu, thông báo lỗi, phiên bản hệ thống

---

## 🎓 Sử dụng nâng cao

### Chế độ máy chủ

```bash
python -m backend.server              # Cổng mặc định 8000
python -m backend.server --port 9000  # Chỉ định cổng
python -m backend.server --dev        # Chế độ phát triển
```

Biến môi trường: `DOUYIN_HOST`, `DOUYIN_PORT`, `DOUYIN_DEV`, `DOUYIN_LOG_LEVEL`

### HTTP API

```bash
# Bắt đầu tác vụ thu thập
curl -X POST http://localhost:8000/api/task/start \
  -H "Content-Type: application/json" \
  -d '{"type": "favorite", "target": "https://www.douyin.com/user/MS4wLjABxxx", "limit": 20}'

# Lấy kết quả
curl http://localhost:8000/api/task/results/task_xxx
```

Các endpoint chính:

**Quản lý tác vụ**
- `POST /api/task/start` - Bắt đầu tác vụ
- `POST /api/task/cancel` - Hủy tác vụ
- `GET /api/task/status` - Trạng thái tác vụ
- `GET /api/task/results/{task_id}` - Kết quả thu thập

**Quản lý cài đặt**
- `GET /api/settings` - Lấy cài đặt
- `POST /api/settings` - Lưu cài đặt
- `GET /api/settings/first-run` - Kiểm tra lần chạy đầu tiên

**Quản lý Aria2**
- `GET /api/aria2/config` - Lấy cấu hình Aria2
- `GET /api/aria2/status` - Lấy trạng thái kết nối Aria2
- `POST /api/aria2/start` - Khởi động dịch vụ Aria2
- `GET /api/aria2/config-path` - Lấy đường dẫn tệp cấu hình cho tác vụ đã hoàn thành

**Thao tác tệp**
- `POST /api/file/open-folder` - Mở thư mục
- `POST /api/file/check-exists` - Kiểm tra tệp tồn tại
- `POST /api/file/read-config` - Đọc tệp cấu hình
- `GET /api/file/find-local/{work_id}` - Tìm tệp đã tải xuống cục bộ
- `GET /api/file/media/{file_path:path}` - Phát trực tuyến tệp phương tiện

**Tiện ích hệ thống**
- `GET /api/system/clipboard` - Lấy nội dung clipboard
- `POST /api/system/open-url` - Mở URL
- `POST /api/system/cookie-login` - Đăng nhập để lấy Cookie (chỉ GUI)

**Giao tiếp thời gian thực**
- `GET /api/events` - Luồng sự kiện SSE

### Chế độ dòng lệnh

```bash
# Sử dụng cơ bản
python -m backend.cli -u https://www.douyin.com/user/xxx -l 20

# Chỉ định loại
python -m backend.cli -u liên_kết -t favorite  # post/favorite/collection/hashtag/music/mix/aweme/search/follower/following

# Bộ lọc tìm kiếm
python -m backend.cli -u "ẩm thực" -t search --sort-type 2 --publish-time 7

# Thu thập hàng loạt (urls.txt mỗi dòng một liên kết)
python -m backend.cli -u urls.txt -l 50

# Chỉ thu thập, không tải xuống
python -m backend.cli -u liên_kết --no-download

# Tải xuống kèm tiêu đề và bìa
python -m backend.cli -u liên_kết --download-title --download-cover
```

Tham số bộ lọc:
- `--sort-type`: 0=tổng hợp, 1=nhiều lượt thích nhất, 2=mới nhất
- `--publish-time`: 0=không giới hạn, 1=trong một ngày, 7=trong một tuần, 180=trong nửa năm
- `--filter-duration`: 0-1=dưới 1 phút, 1-5=1-5 phút, 5-10000=trên 5 phút

Tùy chọn tải xuống:
- `--download-title`: Lưu tiêu đề tác phẩm dưới dạng tệp văn bản
- `--download-cover`: Tải xuống hình ảnh bìa tác phẩm

> 💡 Mẹo: Tùy chọn dòng lệnh được ưu tiên hơn cài đặt trong tệp cấu hình

### Triển khai Docker

```bash
# Sử dụng compose (Khuyên dùng)
docker compose up -d

# Hoặc xây dựng và chạy thủ công
docker build -t douyin-crawler .
docker run -d -p 80:8000 -e DOUYIN_HOST=0.0.0.0 douyin-crawler
```

> 💡 Mẹo: Cookie có thể được cung cấp qua biến `DOUYIN_COOKIE` trong tệp `.env`; chỉ định URL backend khi xây dựng với `--build-arg VITE_API_BASE_URL=http://your-host`

---

**Chúc bạn sử dụng vui vẻ!** 🎉
