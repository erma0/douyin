# Hướng dẫn sử dụng

## 📋 Mục lục

- [Cài đặt Aria2](#cài-đặt-aria2)
- [Lấy Cookie](#lấy-cookie)
- [Mô tả tính năng](#mô-tả-tính-năng)
- [Quản lý cấu hình](#quản-lý-cấu-hình)
- [Các câu hỏi thường gặp](#các-câu-hỏi-thường-gặp)
- [Khắc phục sự cố](#khắc-phục-sự-cố)
- [Sử dụng nâng cao](#sử-dụng-nâng-cao)

---

## Cài đặt Aria2

Chức năng tải xuống hàng loạt cần sự hỗ trợ của Aria2:

```powershell
# Cách 1: Sử dụng script dự án (Khuyên dùng)
.\scripts\setup\aria2.ps1

# Cách 2: Cài đặt thủ công
# 1. Tải xuống https://github.com/aria2/aria2/releases
# 2. Giải nén vào thư mục aria2 của dự án hoặc thêm vào PATH hệ thống
# 3. Xác minh: aria2c --version
```


## 🍪 Lấy Cookie

Cookie là thông tin xác thực cần thiết để lấy dữ liệu.

### Các bước thực hiện

1. **Mở phiên bản web Douyin**
   - Truy cập https://www.douyin.com
   - Đăng nhập vào tài khoản Douyin của bạn

2. **Mở Công cụ dành cho nhà phát triển**
   - Nhấn phím `F12`
   - Hoặc nhấp chuột phải vào trang → Chọn "Kiểm tra" (Inspect)

3. **Chuyển sang tab Network**
   - Nhấp vào tab `Network` (Mạng) ở trên cùng
   - Làm mới trang (F5)

4. **Tìm yêu cầu**
   - Nhập `aweme` vào bộ lọc
   - Tìm bất kỳ yêu cầu `post/?` hoặc tương tự

5. **Sao chép Cookie**
   - Nhấp vào yêu cầu đó
   - Tìm `Request Headers` (Tiêu đề yêu cầu) ở bên phải
   - Tìm trường `Cookie:`
   - Nhấp đúp vào giá trị Cookie để chọn tất cả và sao chép

6. **Lưu Cookie**
   - Nhấp vào biểu tượng cài đặt trong ứng dụng
   - Dán Cookie vào ô nhập liệu
   - Nhấp Lưu

![Sơ đồ minh họa](./frontend/public/image.png)

### Xác minh Cookie

Cookie hợp lệ phải chứa các trường sau:
- `sessionid`
- `ttwid`
- `__ac_nonce`

Nếu Cookie thiếu các trường này, nó có thể không hoạt động bình thường.

---

## 🎯 Mô tả tính năng

### Loại thu thập

| Loại | Mô tả | Ví dụ đầu vào | Trạng thái |
|------|-------|---------------|------------|
| **Tác phẩm chỉ định** | Lấy thông tin một tác phẩm | `https://www.douyin.com/video/7xxx` | ✅ Bình thường |
| **Trang chủ người dùng** | Lấy các tác phẩm do người dùng đăng | `https://www.douyin.com/user/MS4wLjABxxx` | ✅ Bình thường |
| **Người dùng thích** | Lấy các tác phẩm người dùng đã thích | Liên kết trang chủ người dùng | ✅ Bình thường |
| **Người dùng yêu thích** | Lấy các tác phẩm người dùng đã yêu thích | Liên kết trang chủ người dùng | ✅ Bình thường |
| **Chủ đề thử thách** | Lấy các tác phẩm theo chủ đề | `https://www.douyin.com/hashtag/xxx` | ✅ Bình thường |
| **Bộ sưu tập** | Lấy các tác phẩm trong bộ sưu tập | Liên kết bộ sưu tập | ✅ Bình thường |
| **Nhạc gốc** | Lấy các tác phẩm sử dụng nhạc này | `https://www.douyin.com/music/7xxx` | ✅ Bình thường |
| **Tìm kiếm từ khóa** | Tìm kiếm các tác phẩm liên quan | `Phong cảnh` | ✅ Bình thường |

### Giới hạn số lượng thu thập

- **Tất cả**: Thu thập tất cả dữ liệu có sẵn (có thể chậm)
- **20/50/100 mục**: Thu thập nhanh số lượng chỉ định
- **Tùy chỉnh**: Nhập số lượng bất kỳ

### Tải xuống hàng loạt

Nhấp vào nút "Tải xuống tất cả bằng một cú nhấp chuột", hệ thống sẽ tự động:
1. Đọc cấu hình Aria2 của kết quả thu thập
2. Gửi tác vụ tải xuống đến Aria2 qua JSON-RPC
3. Hiển thị tiến độ và trạng thái tải xuống theo thời gian thực
4. Tự động xử lý các tác vụ thất bại và lỗi

**Tính năng**:
- ✅ Hiển thị tiến độ thời gian thực
- ✅ Hỗ trợ tải lại từ điểm dừng
- ✅ Tự động bỏ qua các tệp đã tồn tại
- ✅ Xử lý lỗi và thử lại thông minh

### Tùy chọn cài đặt

| Tùy chọn | Mô tả | Giá trị mặc định |
|----------|-------|------------------|
| **Cookie** | Thông tin đăng nhập Douyin | Trống |
| **Đường dẫn tải xuống** | Vị trí lưu tệp | `./download` |
| **Số lần thử lại tối đa** | Số lần thử lại khi tải xuống thất bại | 3 |
| **Số lượng đồng thời tối đa** | Số tác vụ tải xuống cùng lúc | 5 |
| **Aria2 Host** | Địa chỉ dịch vụ Aria2 | localhost |
| **Aria2 Port** | Cổng dịch vụ Aria2 | 6800 |
| **Aria2 Secret** | Khóa bí mật Aria2 RPC | douyin_crawler_default_secret |



## ❓ Các câu hỏi thường gặp

### Q1: Thông báo "Cookie không hợp lệ hoặc đã hết hạn"

**Nguyên nhân:**
- Cookie đã hết hạn
- Định dạng Cookie không chính xác
- Chưa đăng nhập tài khoản Douyin

**Giải pháp:**
1. Lấy lại Cookie (tham khảo các bước ở trên)
2. Đảm bảo Cookie được sao chép đầy đủ
3. Kiểm tra xem có bao gồm các trường cần thiết không

### Q2: Kết quả thu thập trống

**Giải pháp:**
1. Kiểm tra xem liên kết có chính xác không
2. Cập nhật Cookie
3. Kiểm tra kết nối mạng

### Q3: Tải xuống thất bại

**Giải pháp:**
1. Xác nhận Aria2 đã được cài đặt: `aria2c --version`
2. Xem thông tin lỗi chi tiết trong bảng nhật ký
3. Kiểm tra xem dung lượng ổ đĩa có đủ không
4. Thử giảm số lượng đồng thời (điều chỉnh trong cài đặt)

### Q4: Khởi động ứng dụng thất bại

**Nguyên nhân có thể:**
- Phụ thuộc chưa được cài đặt
- Cổng bị chiếm dụng
- Frontend chưa được xây dựng
- Tệp cấu hình bị hỏng

**Giải pháp:**
```powershell
# Cách 1: Sử dụng script xây dựng (Khuyên dùng)
.\scripts\dev.ps1 -Clean

# Cách 2: Cài đặt lại thủ công
pip install -r requirements.txt
cd frontend
pnpm install  # hoặc npm install
pnpm build    # hoặc npm run build
```

### Q5: Trang frontend trắng xóa

**Nguyên nhân có thể:**
- Tường lửa chặn truy cập
- Frontend chưa được xây dựng
- Lỗi đường dẫn xây dựng
- Thư mục dist thiếu tệp

**Giải pháp:**
1. Kiểm tra cài đặt tường lửa, đảm bảo ứng dụng được phép truy cập mạng (thường cấu hình mạng riêng là đủ)
2. Xác nhận frontend đã được xây dựng
3. Kiểm tra xem đường dẫn xây dựng có chính xác không

### Q6: Một số tính năng không khả dụng

**Vấn đề đã biết:**
- Chức năng phân tích ID Douyin chưa được thực hiện
- Chức năng Thích/Yêu thích yêu cầu mục tiêu mở quyền, một số mục tiêu không thể lấy được
- Chức năng tự động lấy Cookie đã bị xóa

**Giải pháp:**
1. Sử dụng các tính năng ổn định được đề xuất
2. Cấu hình Cookie thủ công
3. Sử dụng liên kết đầy đủ

### Q7: Cấu hình bị mất hoặc đặt lại

**Nguyên nhân có thể:**
- Tệp cấu hình bị xóa
- Lỗi định dạng tệp cấu hình
- Vấn đề về quyền

**Giải pháp:**
```powershell
# Kiểm tra tệp cấu hình
cat config/settings.json

# Nếu tệp bị hỏng, xóa và khởi động lại
Remove-Item config/settings.json
python main.py
```

#### Q8: Một số tác vụ thất bại

**Đây là hiện tượng bình thường**, nguyên nhân có thể:
- Tệp đã tồn tại (sẽ tự động bỏ qua)
- Liên kết tải xuống đã hết hạn
- Gián đoạn mạng tạm thời
- Cookie đã hết hạn


### Liên hệ hỗ trợ

Nếu vấn đề vẫn chưa được giải quyết:

1. Xem Issues của dự án: https://github.com/erma0/douyin/issues
2. Khi gửi Issue mới, vui lòng bao gồm:
   - Liên kết mục tiêu
   - Thông tin lỗi
   - Phiên bản phần mềm
   - Phiên bản hệ thống và môi trường

## 🎓 Sử dụng nâng cao

### Chế độ dòng lệnh (Cập nhật chậm, có thể xem nhánh v4)

Ngoài giao diện GUI, còn hỗ trợ thao tác dòng lệnh:

```powershell
# Xem trợ giúp
python backend/cli.py -h

# Thu thập tác phẩm trang chủ người dùng
python backend/cli.py -u https://v.douyin.com/iybvCom1/

# Giới hạn số lượng
python backend/cli.py -l 5 -u https://v.douyin.com/iybvCom1/

# Chỉ định loại
python backend/cli.py -t like -u https://v.douyin.com/iybvCom1/
```

### Thu thập hàng loạt

Tạo tệp văn bản, mỗi dòng một liên kết:

```text
https://www.douyin.com/user/MS4wLjABxxx
https://www.douyin.com/user/MS4wLjAByyy
https://www.douyin.com/user/MS4wLjABzzz
```

Sau đó chạy:

```powershell
python backend/cli.py -u urls.txt
```

---

**Chúc bạn sử dụng vui vẻ!** 🎉
