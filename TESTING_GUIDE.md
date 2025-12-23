# 📘 Hướng Dẫn Kiểm Thử (Testing Guide) - PitchManager

Tài liệu này mô tả chi tiết về bộ test suite đã được xây dựng cho dự án PitchManager và hướng dẫn cách chạy kiểm thử.

## 🏗️ Cấu Trúc Bộ Test

Bộ test được đặt trong thư mục `main/tests/` và được chia thành 3 module chính để dễ quản lý và bảo trì:

```
main/tests/
├── __init__.py
├── test_models.py        # Unit Tests: Kiểm tra logic của các Models
├── test_payment_flow.py  # Integration Tests: Kiểm tra luồng đặt sân & thanh toán
└── test_search_flow.py   # Integration Tests: Kiểm tra luồng tìm kiếm & lọc sân
```

---

## 🧪 Chi Tiết Các Kịch Bản Kiểm Thử

### 1. Unit Tests (`test_models.py`)
File này kiểm tra tính đúng đắn của dữ liệu và logic nghiệp vụ ở cấp độ database (Models).

*   **TimeSlot**:
    *   Tính toán thời lượng (`duration_hours`) chính xác (ví dụ: 7h-9h là 2 tiếng).
    *   Validation: Giờ bắt đầu phải trước giờ kết thúc.
*   **Voucher**:
    *   Kiểm tra `is_valid()`: Còn hạn, chưa hết lượt dùng, đang kích hoạt.
    *   Validation: Ngày bắt đầu phải trước ngày kết thúc.
*   **PitchTimeSlot**:
    *   Tính giá tiền (`get_price`) dựa trên giá sân và thời lượng.
    *   Kiểm tra tính khả dụng (`is_available_on_date`):
        *   Trống nếu chưa ai đặt.
        *   Bận nếu có đơn `CONFIRMED` hoặc `PENDING`.
        *   Trống nếu đơn cũ đã bị `CANCELLED` hoặc `REJECTED`.
*   **Booking**:
    *   Tự động tính toán `final_price` và `duration` khi lưu.
    *   Validation: Không cho phép đặt ngày trong quá khứ.
    *   Validation: Không cho phép đặt khung giờ không thuộc về sân.

### 2. Integration Tests - Luồng Đặt Sân (`test_payment_flow.py`)
File này mô phỏng hành vi của người dùng khi thực hiện đặt sân, đảm bảo quy trình diễn ra trơn tru từ đầu đến cuối.

*   **Đặt sân thông thường**: Đặt không có voucher, kiểm tra giá gốc.
*   **Đặt sân có Voucher**:
    *   Voucher hợp lệ: Giá giảm đúng theo % (ví dụ: giảm 10%).
    *   Voucher hết hạn/không hợp lệ: Hệ thống từ chối áp dụng và giữ nguyên giá gốc.
    *   Voucher 100%: Giá về 0.
*   **Ràng buộc Voucher**:
    *   Một người dùng không thể dùng lại voucher đã dùng (trừ khi đơn trước đó bị hủy/từ chối).

### 3. Integration Tests - Luồng Tìm Kiếm (`test_search_flow.py`)
File này kiểm tra chức năng tìm kiếm và bộ lọc trên trang danh sách sân.

*   **Tìm kiếm từ khóa**: Tìm theo tên sân, tên cơ sở, địa chỉ (không phân biệt hoa thường).
*   **Bộ lọc (Filter)**:
    *   Lọc theo Loại sân (5vs5, 7vs7).
    *   Lọc theo Khoảng giá (0-100k, 200k-300k...).
    *   Lọc theo Ngày: Ẩn các sân đã kín lịch vào ngày được chọn.
*   **Sắp xếp (Sort)**:
    *   Giá tăng dần / giảm dần.
    *   Tên A-Z.
*   **Kết hợp**: Tìm kiếm + Lọc + Sắp xếp cùng lúc.

---

## 🚀 Hướng Dẫn Chạy Test

### 1. Chuẩn bị môi trường
Đảm bảo bạn đã kích hoạt virtual environment của dự án:

```bash
# Trên Linux/Mac
source project1/bin/activate

# Trên Windows
# project1\Scripts\activate
```

### 2. Lệnh chạy test

**Chạy toàn bộ test (Khuyên dùng):**
```bash
python manage.py test main.tests
```

**Chạy riêng lẻ từng phần:**

*   Chỉ chạy test Models:
    ```bash
    python manage.py test main.tests.test_models
    ```

*   Chỉ chạy test luồng Đặt sân:
    ```bash
    python manage.py test main.tests.test_payment_flow
    ```

*   Chỉ chạy test luồng Tìm kiếm:
    ```bash
    python manage.py test main.tests.test_search_flow
    ```

### 3. Đọc kết quả
*   **OK**: Tất cả các test đều qua.
*   **FAIL**: Có logic bị sai (kết quả thực tế khác kết quả mong đợi).
*   **ERROR**: Có lỗi code (bug) làm test không chạy được.

---

## 💡 Lưu ý cho Developer
*   Test sử dụng một database riêng biệt (tự động tạo và xóa sau khi chạy), không ảnh hưởng đến dữ liệu thật.
*   Khi sửa code logic (ví dụ: cách tính giá), hãy chạy lại test để đảm bảo không làm hỏng tính năng cũ.
