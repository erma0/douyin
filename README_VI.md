![douyin](https://socialify.git.ci/erma0/douyin/image?description=1&font=Source%20Code%20Pro&forks=1&issues=1&language=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Auto)

# ✨DouyinCrawler

> ❤️ [Mã nguồn mở không dễ dàng, hoan nghênh tặng sao ⭐](#star-history)

## 📢 Tuyên bố từ chối trách nhiệm

> Mục đích ban đầu của dự án này là học `python` crawler, gọi dòng lệnh `Aria2` và các trường hợp triển khai `WebUI` bằng `python`. Sau đó nó được sử dụng để trải nghiệm lập trình AI (phần giao diện người dùng và tương tác backend đều do AI tạo ra). Chức năng ứng dụng là lấy thông tin công khai trên nền tảng Douyin, chỉ dùng cho mục đích kiểm tra và nghiên cứu học tập, nghiêm cấm sử dụng cho mục đích thương mại hoặc bất kỳ mục đích bất hợp pháp nào.
>
> Bất kỳ người dùng nào sử dụng trực tiếp hoặc gián tiếp hoặc phổ biến nội dung của kho lưu trữ này đều phải tự chịu trách nhiệm về hành động của mình và những người đóng góp cho kho lưu trữ này không chịu trách nhiệm về bất kỳ hậu quả nào phát sinh từ những hành động đó.
>
> **Nếu các bên liên quan tin rằng mã của dự án này có thể vi phạm quyền của họ, vui lòng liên hệ với tôi ngay lập tức để xóa mã liên quan**.
>
> Việc sử dụng nội dung của kho lưu trữ này có nghĩa là bạn đồng ý với tất cả các điều khoản và điều kiện của tuyên bố từ chối trách nhiệm này. Nếu bạn không chấp nhận tuyên bố từ chối trách nhiệm trên, vui lòng ngừng sử dụng dự án này ngay lập tức.

---

## 🏠 Địa chỉ dự án

> [https://github.com/erma0/douyin](https://github.com/erma0/douyin)

## 🍬 Tính năng

### 📊 Thu thập dữ liệu
- ✅ Dữ liệu tác phẩm được chỉ định
- ✅ Tác phẩm trang chủ người dùng
- ✅ Tác phẩm người dùng đã thích (yêu cầu mục tiêu mở quyền)
- ✅ Tác phẩm người dùng yêu thích (yêu cầu mục tiêu mở quyền)
- ✅ Tác phẩm theo chủ đề thử thách
- ✅ Tác phẩm trong bộ sưu tập
- ⚠️ Tác phẩm nhạc gốc (chức năng bất thường)
- ✅ Tìm kiếm tác phẩm theo từ khóa

### 🎯 Tính năng ứng dụng
- 🔄 **Thu thập tăng dần**: Thu thập tăng dần thông minh các tác phẩm trang chủ người dùng
- ⬇️ **Tải xuống hàng loạt**: Tích hợp Aria2, hỗ trợ tải xuống hàng loạt video/hình ảnh
- 🎨 **Giao diện trực quan**: Ứng dụng máy tính để bàn React, hiển thị nhật ký thời gian thực
- 🎉 **Hướng dẫn chạy lần đầu**: Giao diện chào mừng thân thiện, hướng dẫn cấu hình

## 🚀 Bắt đầu nhanh

### Yêu cầu môi trường

> 📍 Môi trường thử nghiệm: `Win10 x64` + `Python 3.12` + `Node.js 22.13.0` + `uv 0.9+`


### Khởi động nhanh

- Tải xuống phiên bản mới nhất từ [Releases](https://github.com/erma0/douyin/releases)
- Giải nén và nhấp đúp để chạy `DouyinCrawler.exe`


Hướng dẫn sử dụng chi tiết vui lòng xem [USAGE_VI.md](USAGE_VI.md)

## ⚠️ Vấn đề đã biết

1. **Chức năng âm nhạc bất thường** - Thu thập tác phẩm nhạc gốc có thể thất bại

## 🔨 Xây dựng và Đóng gói

### 📁 Thư mục Script

Tất cả các script xây dựng đã được sắp xếp vào thư mục `scripts/`:

```
scripts/
├── build/              # Script đóng gói
│   ├── pyinstaller.ps1      # Đóng gói PyInstaller
│   ├── pyinstaller-dir.spec # Cấu hình chế độ thư mục
│   ├── pyinstaller-onefile.spec # Cấu hình tệp đơn
│   └── nuitka.ps1           # Đóng gói Nuitka
├── setup/              # Cấu hình môi trường
│   ├── uv.ps1               # Cấu hình môi trường uv
│   ├── aria2.ps1            # Tải xuống aria2
│   └── pyinstaller.ps1      # Cài đặt riêng PyInstaller
└── dev.ps1             # Xây dựng môi trường phát triển
```

### 🚀 Bắt đầu nhanh

#### Cách 1: Sử dụng Menu Khởi động nhanh (Khuyên dùng)

```powershell
.\quick-start.ps1
```

Cung cấp menu tương tác, chọn thao tác bằng số.

#### Cách 2: Thực thi Script thủ công

Xem chi tiết thư mục script.

### 📦 Hướng dẫn đóng gói

#### PyInstaller (Khuyên dùng)
- ✅ Tốc độ đóng gói nhanh (5-10 phút)
- ✅ Hỗ trợ chế độ thư mục và chế độ tệp đơn
- ✅ Khả năng tương thích tốt
- 📦 Kích thước: Chế độ thư mục ~30MB, Tệp đơn ~21MB

#### Nuitka (Hiệu suất cao)
- ✅ Biên dịch thành mã gốc, hiệu suất tốt hơn
- ✅ Tốc độ khởi động nhanh
- ⚠️ Thời gian biên dịch lâu (10-20 phút)
- ⚠️ Yêu cầu trình biên dịch MinGW64 (tự động tải xuống)
- 📦 Kích thước: Chế độ thư mục ~45MB, Tệp đơn ~35MB

#### Sản phẩm đóng gói
- **Chế độ thư mục**: `dist/DouyinCrawler/DouyinCrawler.exe` (Khởi động nhanh)
- **Chế độ tệp đơn**: `dist/DouyinCrawler.exe` (Dễ dàng phân phối)
- **Gói phát hành**: `release/DouyinCrawler_*.zip` (Tự động tạo)


## 📊 Tech Stack

- **Backend**: Python 3.12, PyWebView
- **Frontend**: React 18, TypeScript, Vite
- **Tải xuống**: Aria2
- **Đóng gói**: PyInstaller / Nuitka

## Lịch sử Star

[![Star History Chart](https://api.star-history.com/svg?repos=erma0/douyin&type=Date)](https://star-history.com/#erma0/douyin&Date)
