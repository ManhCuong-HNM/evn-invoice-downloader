# ⚡ EVN Tool AIO - Phiên Bản Tự Động Giải Captcha AI Offline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)

**EVN Tool AIO** là giải pháp phần mềm toàn diện, khép kín, được phát triển nhằm tự động hóa quy trình quản lý hóa đơn tiền điện từ Tổng công ty Điện lực miền Bắc (EVN NPC). Điểm đột phá lớn nhất của phiên bản này là **tích hợp mô hình AI OCR chạy Offline 100%** giúp giải quyết Captcha tự động, nhanh chóng mà không tốn bất kỳ chi phí API nào hay lo lắng về độ trễ/nghẽn mạng.

---

## 🌟 CÁC TÍNH NĂNG NỔI BẬT

1. **Giải Captcha AI Offline 100%:** Sử dụng mô hình Deep Learning được huấn luyện từ tập dữ liệu lớn ảnh thực tế, tự động hóa giải mã Captcha EVN trực tiếp trên CPU của máy tính cá nhân. Lập trình viên có thể tận dụng kiến trúc mô hình này để huấn luyện lại (train lại) theo tập dữ liệu captcha mới nếu cần.
2. **Quy trình Hậu cần Toàn diện:**
   - **Tải Hóa Đơn:** Quét danh sách tài khoản từ file Excel, đăng nhập và tải file zip hóa đơn.
   - **Giải Nén:** Giải nén hàng loạt các file zip hóa đơn tự động.
   - **Ánh Xạ (Mapping):** Đổi tên file PDF hóa đơn từ Mã Khách Hàng (`PA...`) sang Mã Quản Lý Mới hoặc ngược lại dựa theo file ánh xạ Excel.
   - **In Ấn:** Gửi lệnh in tự động hàng loạt hóa đơn PDF ra máy in đã chọn.
3. **Trích Xuất Dữ Liệu:** Đọc thông tin chi tiết từ các hóa đơn PDF (chỉ số, tiền điện, ngày tháng...) và xuất ra file báo cáo Excel kết quả.
4. **Giao Diện Hiện Đại:** Thiết kế giao diện PyQt6 cao cấp, hỗ trợ 2 chế độ Dark Mode / Light Mode và bảng điều khiển Console ghi nhận tiến trình trực quan.

---

## 🧠 THÔNG TIN 3 MÔ HÌNH AI GIẢI CAPTCHA

Phần mềm tích hợp sẵn 3 phiên bản mô hình AI trong thư mục `models/` để người dùng linh hoạt lựa chọn tùy thuộc vào cấu hình phần cứng của máy tính:

| Tên Mô Hình  | Dung Lượng | Tốc Độ Giải  | Độ Chính Xác |  Cấu Hình Khuyến Nghị   | Phù Hợp Cho                                                               |
| :----------- | :--------: | :----------: | :----------: | :---------------------: | :------------------------------------------------------------------------ |
| **Lite**     | `26.3 MB`  | **~6.8 ms**  |  `~97.60%`   |  RAM 4GB - CPU Đời cũ   | Máy văn phòng cơ bản, máy cấu hình yếu, ưu tiên tốc độ nhanh.             |
| **Standard** | `46.8 MB`  | **~8.2 ms**  |  `~96.80%`   | RAM 8GB - CPU Đời trung | Máy cấu hình trung bình, cần cân bằng tối ưu giữa RAM và độ chính xác.    |
| **Premium**  | `453.6 MB` | **~20.6 ms** | **~97.80%**  | RAM >= 16GB - CPU Khỏe  | Máy tính cấu hình mạnh, RAM rảnh rỗi lớn, ưu tiên độ chính xác tuyệt đối. |

_Lưu ý: Thời gian giải được đo đạc thực tế trên vi xử lý CPU thông thường._

---

## 🛠️ HƯỚNG DẪN CẤU HÌNH & CHỌN MODEL AI ĐỘNG

Ứng dụng hỗ trợ chuyển đổi linh hoạt cả 3 mô hình AI cực kỳ tiện lợi thông qua 2 hình thức:

### 1. Dành cho Người dùng phổ thông (Chọn trực tiếp trên GUI)

Người dùng chỉ cần chọn mô hình mong muốn tại ComboBox **`🤖 Model AI`** (Premium / Standard / Lite) nằm ngay trên tab **Tải Hóa Đơn**. Hệ thống sẽ tự động lưu lại cấu hình mô hình được chọn cho lần chạy sau mà không cần thao tác kỹ thuật gì phức tạp.

### 2. Dành cho Lập trình viên / Cấu hình nâng cao (Qua file `config.json`)

Lập trình viên có thể điều chỉnh cấu hình chi tiết thông qua tệp `config.json` ở thư mục gốc của dự án:

- `"model_type"`: Điền `"Lite"`, `"Standard"` hoặc `"Premium"`.
- `"confidence_threshold"`: Ngưỡng tự tin tối thiểu (ví dụ `80.0`). Nếu AI giải captcha có độ tự tin thấp hơn ngưỡng này, tool sẽ tự refresh đổi mã captcha mới dưới nền.

_Ví dụ cấu hình file `config.json`:_

```json
{
  "excel_path": "./TK-MK-EVN_template.xlsx",
  "folder_path": "./",
  "pdf_path": "./Hoadon/HoaDon_Tong",
  "save_pdf_path": "./Hoadon",
  "confidence_threshold": 80.0,
  "model_type": "Premium"
}
```

---

## 📦 PHƯƠNG ÁN ĐÓNG GÓI DẠNG THƯ MỤC THƯ VIỆN (ONEDIR)
Phần mềm được đóng gói dưới dạng thư mục kèm thư viện liên kết (`--onedir`) mang lại nhiều ưu điểm vượt trội:
- **Khởi động siêu tốc:** Ứng dụng mở lên ngay lập tức mà không có độ trễ do phải giải nén thư viện ra thư mục Temp như chế độ One-file.
- **Quản lý mô hình trực quan:** Thư mục chứa các mô hình AI `models/` được đặt nằm ngay bên cạnh file chạy chính `EVN_Tool_AIO_v3.2.exe`. Giúp chương trình định vị mô hình cực kỳ chính xác và ổn định.
- **Phân phối:** Khi phát hành, toàn bộ thư mục này sẽ được nén lại thành một file `.zip`. Người dùng tải về chỉ việc giải nén và click chạy trực tiếp file `.exe`.

---

## 💻 HƯỚNG DẪN CÀI ĐẶT

### 1. Dành cho Người dùng phổ thông (Bản đóng gói sẵn)
Nếu bạn không biết lập trình và chỉ muốn sử dụng trực tiếp:
1. Truy cập vào mục **Releases** trên kho chứa GitHub này.
2. Tải phiên bản mới nhất dưới dạng file nén `.zip` (chứa tệp chạy `.exe` và thư mục `models/` đi kèm).
3. Giải nén vào một thư mục trên ổ cứng.
4. Nhấp đúp (Double-click) trực tiếp vào tệp **`.exe`** chính của ứng dụng để khởi chạy và sử dụng ngay lập tức mà không cần cài đặt Python hay chạy bất kỳ script nào khác.

### 2. Dành cho Lập trình viên (Chạy từ mã nguồn)
Để cài đặt và phát triển ứng dụng trên máy tính cá nhân từ mã nguồn:

#### Bước 1: Clone dự án
```bash
git clone https://github.com/ManhCuong-HNM/evn-invoice-downloader.git
cd evn-invoice-downloader
```

#### Bước 2: Tải và thiết lập mô hình AI giải Captcha (Bắt buộc)
Vì lý do giới hạn dung lượng của GitHub, thư mục `models/` chứa các mô hình AI không được đẩy lên Git. Sau khi clone code, bạn cần thiết lập như sau để ứng dụng hoạt động:
1. Tạo một thư mục tên là **`models`** ngay tại thư mục gốc của dự án.
2. Truy cập vào mục **Releases** của kho chứa này, tải về các tệp mô hình AI bạn muốn sử dụng (Premium, Standard hoặc Lite).
3. Đặt các tệp mô hình vào đúng cấu trúc thư mục con dưới đây:
   - Bản Lite: `models/Lite/captcha_model.onnx`
   - Bản Standard: `models/Standard/captcha_model.onnx`
   - Bản Premium: `models/Premium/captcha_model.onnx` và `models/Premium/captcha_model.onnx.data`

#### Bước 3: Tạo và kích hoạt môi trường ảo (Khuyến nghị)
```bash
python -m venv .venv_standard
# Kích hoạt trên Windows PowerShell:
.venv_standard\Scripts\Activate.ps1
```

#### Bước 4: Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
# Hoặc cài thủ công các gói chính:
pip install PyQt6 pandas selenium webdriver-manager requests openpyxl Pillow onnxruntime pdfplumber
```

#### Bước 5: Khởi chạy ứng dụng
```bash
python main_pyqt6.py
```

---

## 📖 HƯỚNG DẪN CHI TIẾT CÁC TAB CHỨC NĂNG

### 1. Tab [⬇ Tải Hóa Đơn]
- **Mục đích:** Tải hóa đơn tự động từ danh sách tài khoản EVN.
- **Cách sử dụng:**
  1. Chuẩn bị file Excel danh sách tài khoản (xem định dạng trong file `TK-MK-EVN_template.xlsx`).
  2. Chọn file Excel tài khoản và chọn thư mục để lưu trữ các file tải về.
  3. Chọn Tháng và Năm của hóa đơn cần tải.
  4. Chọn Trình duyệt chạy tự động (Chrome / Edge) và mô hình AI phù hợp với cấu hình máy tính.
  5. Bấm **BẮT ĐẦU TẢI** để tiến hành.

### 2. Tab [🔧 Công Cụ]
Chứa 3 công cụ xử lý hậu cần sau khi tải hóa đơn về:
- **Tab con [📦 Giải Nén]:** 
  - *Mục đích:* Giải nén hàng loạt các file `.zip` hóa đơn vừa tải về, đồng thời tự động phân loại chúng vào 2 thư mục con riêng biệt:
    - **`HoaDon_Tong`**: Chứa các file PDF hóa đơn tiền điện (tờ hóa đơn tổng).
    - **`HoaDon_ChiTiet`**: Chứa các file PDF bảng kê chi tiết chỉ số tiêu thụ điện (tờ chi tiết).
  - *Cách sử dụng:* Chọn thư mục chứa file zip đã tải về và bấm **Chạy giải nén**. Hệ thống sẽ tự động quét, giải nén và phân chia tệp tin vào 2 thư mục trên một cách thông minh.
- **Tab con [🔀 Ánh Xạ]:**
  - *Mục đích:* Đổi tên hàng loạt file PDF hóa đơn để tiện theo dõi theo mã quản lý riêng của người dùng (ví dụ: mã địa điểm, tên viết tắt, mã cơ sở hoặc mã quản lý nội bộ).
  - *Cách sử dụng:* 
    1. Chọn thư mục chứa các file PDF cần đổi tên.
    2. Chọn file Excel Mapping (định dạng như file `Mapping_template.xlsx` gồm 2 cột: **Mã KH** và **Mã Quản Lý Mới** của bạn).
    3. Chọn ký hiệu Tháng/Năm và bấm nút **Mã KH → Mã Mới** (để đổi tên file thành mã quản lý riêng của bạn) hoặc **Mã Mới → Mã KH** (để đổi tên ngược lại).
- **Tab con [🖨️ In Ấn]:**
  - *Mục đích:* Tự động gửi toàn bộ file PDF trong thư mục được chọn ra máy in mặc định của hệ điều hành.
  - *Cách sử dụng:* Chọn thư mục chứa PDF và bấm **Gửi lệnh in**.

### 3. Tab [📊 Trích Xuất]
- **Mục đích:** Đọc tự động nội dung PDF hóa đơn và trích xuất dữ liệu ra file báo cáo Excel tổng hợp.
- **Phân biệt hai chế độ trích xuất:**
  - **📄 Hóa Đơn Tổng:** Áp dụng cho các tài khoản điện thông thường (mỗi tài khoản / mã đăng nhập chỉ chứa duy nhất **1 mã khách hàng điện**).
  - **📋 Hóa Đơn Chi Tiết:** Áp dụng cho các tài khoản điện lực dạng gộp (1 tài khoản điện lực quản lý **nhiều mã khách hàng điện** gộp chung với nhau). Chế độ này sẽ giúp trích xuất chi tiết dữ liệu tách biệt của từng mã khách hàng riêng lẻ nằm trong tài khoản gộp đó.
- **Cách sử dụng:** 
  1. Chọn thư mục chứa file PDF hóa đơn cần trích xuất.
  2. Chọn chế độ trích xuất phù hợp với tài khoản của bạn (Hóa đơn Tổng hoặc Hóa đơn Chi Tiết).
  3. Chọn thư mục lưu file Excel kết quả.
  4. Bấm **BẮT ĐẦU TRÍCH XUẤT**. Kết quả sẽ lưu dưới tên file `KetQua-Ngày-Tháng-Năm.xlsx`.

---

## 🛡️ AN TOÀN & BẢO MẬT THÔNG TIN

- **Chạy Local 100%:** Mô hình giải Captcha chạy hoàn toàn local, mã nguồn không gửi bất kỳ hình ảnh captcha hay tài khoản mật khẩu nào lên máy chủ bên thứ ba (ngoài trang chính thức CSKH của EVN NPC khi thực hiện đăng nhập).
- **Tuyệt đối không đẩy thông tin nhạy cảm:** Hãy luôn đảm bảo file cấu hình thật `config.json` và các file chứa thông tin tài khoản thật `TK-MK-EVN.xlsx` nằm trong file `.gitignore` để tránh bị lộ thông tin trên GitHub công cộng. Chỉ sử dụng file `TK-MK-EVN_template.xlsx` làm mẫu.

---

## 🔍 TỪ KHÓA TÌM KIẾM (KEYWORDS)

`tải hóa đơn evn` • `download hoa don dien` • `cskh npc` • `evn npc` • `giai captcha evn` • `captcha solver evn` • `dien luc mien bac` • `auto download evn` • `tool tai hoa don evn` • `trich xuat hoa don dien` • `pyqt6 selenium` • `ocr captcha offline`

---

## 📄 GIẤY PHÉP BẢN QUYỀN

Dự án này được phân phối dưới dạng mã nguồn mở theo các điều khoản của **[Giấy phép MIT](LICENSE)**. Bản quyền © 2026 thuộc về **CuongNM.HNM**.

---

_Được phát triển với mục đích đơn giản hóa công tác quản lý hóa đơn năng lượng cho doanh nghiệp và hộ tiêu thụ điện lớn._
