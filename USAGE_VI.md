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

### Các bước

1. Truy cập https://www.douyin.com và đăng nhập
2. Nhấn `F12` để mở công cụ nhà phát triển
3. Chuyển sang tab `Network`, làm mới trang
4. Nhập `aweme` vào bộ lọc, nhấp vào bất kỳ yêu cầu nào
5. Tìm trường `Cookie:` trong `Request Headers`, sao chép toàn bộ nội dung
6. Dán và lưu trong cài đặt ứng dụng

![Sơ đồ](./docs/images/image.png)

Cookie hợp lệ phải chứa: `sessionid`, `ttwid`, `__ac_nonce`

---

## 🎯 Tính năng

### Loại thu thập

| Loại | Ví dụ đầu vào |
|------|---------------|
| Tác phẩm đơn | `https://www.douyin.com/video/7xxx` |
| Bài đăng người dùng | `https://www.douyin.com/user/MS4wLjABxxx` |
| Yêu thích/Bộ sưu tập | Liên kết trang chủ người dùng |
| Hashtag | `https://www.douyin.com/hashtag/xxx` |
| Mix | Liên kết mix |
| Nhạc | `https://www.douyin.com/music/7xxx` |
| Tìm kiếm từ khóa | `Phong cảnh` |

### Tải xuống hàng loạt

Cần hỗ trợ Aria2:

```powershell
# Cài đặt Aria2
.\scripts\setup\aria2.ps1
```

Nhấp "Tải xuống tất cả" để tự động tải xuống kết quả thu thập qua Aria2.

### Cài đặt

| Tùy chọn | Mặc định |
|----------|----------|
| Đường dẫn tải xuống | `./download` |
| Số lần thử lại tối đa | 3 |
| Số lượng đồng thời tối đa | 5 |
| Cổng Aria2 | 6800 |

---

## ❓ Câu hỏi thường gặp

### Cookie không hợp lệ hoặc đã hết hạn

Lấy lại Cookie, đảm bảo chứa các trường cần thiết như `sessionid`.

### Kết quả thu thập trống

1. Kiểm tra định dạng liên kết có đúng không
2. Cập nhật Cookie
3. Yêu thích/Bộ sưu tập yêu cầu người dùng mục tiêu mở quyền

### Tải xuống thất bại

1. Xác nhận Aria2 đã được cài đặt: `aria2c --version`
2. Kiểm tra dung lượng ổ đĩa
3. Thử giảm số lượng đồng thời

### Khởi động ứng dụng thất bại

```powershell
.\scripts\dev.ps1 -Clean
```

### Liên hệ hỗ trợ

Khi gửi [Issue](https://github.com/erma0/douyin/issues), vui lòng bao gồm: liên kết mục tiêu, thông báo lỗi, phiên bản phần mềm

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
  -d '{"type": "favorite", "target": "liên_kết_người_dùng", "limit": 20}'

# Lấy kết quả
curl http://localhost:8000/api/task/results/task_xxx
```

Các endpoint chính:
- `POST /api/task/start` - Bắt đầu tác vụ
- `GET /api/task/status` - Trạng thái tác vụ
- `GET /api/task/results/{task_id}` - Kết quả thu thập
- `GET /api/settings` - Lấy cài đặt
- `POST /api/settings` - Lưu cài đặt
- `GET /api/events` - Luồng sự kiện SSE

### Chế độ dòng lệnh

```bash
# Sử dụng cơ bản
python -m backend.cli -u https://www.douyin.com/user/xxx -l 20

# Chỉ định loại
python -m backend.cli -u liên_kết -t favorite  # post/favorite/collection/hashtag/music/mix/aweme/search

# Bộ lọc tìm kiếm
python -m backend.cli -u "ẩm thực" -t search --sort-type 2 --publish-time 7

# Thu thập hàng loạt (urls.txt mỗi dòng một liên kết)
python -m backend.cli -u urls.txt -l 50

# Chỉ thu thập, không tải xuống
python -m backend.cli -u liên_kết --no-download
```

Tham số bộ lọc:
- `--sort-type`: 0=tổng hợp, 1=nhiều lượt thích nhất, 2=mới nhất
- `--publish-time`: 0=không giới hạn, 1=trong một ngày, 7=trong một tuần, 180=trong nửa năm
- `--filter-duration`: 0-1=dưới 1 phút, 1-5=1-5 phút, 5-10000=trên 5 phút

---

**Chúc bạn sử dụng vui vẻ!** 🎉
