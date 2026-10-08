# Hệ thống đặt bàn nhà hàng
- Đề tài nhóm Vũ Khoa
## Danh sách thành viên
- Hệ thống được thực hiện bởi 4 thành viên:

| STT | Họ và Tên | Vai trò & Nhiệm vụ |
| :--- | :--- | :--- | 
| **1** | Đặng Vũ Khoa | Phân tích và kiểm thử, làm báo cáo |
| **2** | Phan Hoàng Tấn Dũng | Thiết kế dữ liệu, viết logic thuật toán và các chức năng dịch vụ  | 
| **3** | Huỳnh Tuấn Kiệt | Làm giao diện cho user |
| **4** | Trịnh Nguyễn Kỳ Anh | Làm giao diện cho admin |

Dàn ý 
Thành viên 1 - Thiết kế Dữ liệu, Xử lý Logic & Tích hợp Dịch vụ
​Xây dựng cấu trúc dữ liệu:
​Tạo bản vẽ ERD và thiết kế bảng dữ liệu (Thông tin tài khoản, Sơ đồ bàn, Lịch đặt, Thanh toán, Thông báo).
​Cấu hình chỉ mục và tối ưu hóa câu lệnh truy vấn dữ liệu để tìm bàn trống nhanh.
​Xử lý logic nghiệp vụ:
​Lập trình thuật toán kiểm tra xung đột thời gian đặt bàn (tránh bị trùng/đúp bàn).
​Viết quy trình đặt bàn, hủy đặt bàn, chuyển bàn và cập nhật trạng thái bàn.
​Tích hợp hệ thống bên ngoài:
​Tích hợp cổng thanh toán trực tuyến (Momo, VNPay, ZaloPay) để xử lý nhận cọc.
​Tích hợp dịch vụ tự động gửi SMS / Email / Zalo ZNS xác nhận và nhắc lịch khách hàng.
​Cấu hình cơ chế cập nhật trạng thái bàn theo thời gian thực (Real-time).
​Thành viên 2 - Xây dựng Giao diện Đặt bàn dành cho Khách hàng
​Trải nghiệm chọn & Đặt bàn:
​Thiết kế giao diện tìm kiếm, chọn ngày giờ, chọn khu vực và số lượng khách.
​Xây dựng mô hình sơ đồ bàn trực quan cho phép khách hàng chủ động chọn góc/bàn mong muốn.
​Tạo biểu mẫu điền thông tin đặt bàn và các ghi chú đặc biệt (sinh nhật, dị ứng, ghế trẻ em).
​Thanh toán & Xác nhận:
​Xây dựng màn hình quét mã QR / Thanh toán tiền cọc.
​Tạo màn hình hiển thị Phiếu đặt bàn / Mã QR Check-in.
​Quản lý tài khoản khách hàng:
​Tạo giao diện đăng ký, đăng nhập và trang quản lý thông tin cá nhân.
​Xây dựng màn hình xem lại lịch sử đặt bàn, cho phép khách hàng tự thực hiện yêu cầu hủy hoặc đổi giờ.
​Thành viên 3 - Xây dựng Giao diện Quản lý dành cho Nhà hàng & Lễ tân
​Màn hình vận hành thực tế cho Lễ tân:
​Dựng sơ đồ trạng thái bàn hiển thị theo thời gian thực (Bàn trống, Bàn có khách, Bàn đã cọc, Bàn sắp đến).
​Xây dựng chức năng quét mã QR / Nhập SĐT để Check-in cho khách nhanh chóng.
​Tạo tính năng xếp bàn/chuyển bàn linh hoạt cho khách đến trực tiếp không qua đặt trước.
​Màn hình Quản trị & Cấu hình:
​Tạo giao diện vẽ/chỉnh sửa sơ đồ nhà hàng (Thêm, xóa, sửa, gộp bàn, chia khu vực).
​Tạo trang cài đặt khung giờ hoạt động, giới hạn số khách tối đa theo khung giờ và mức tiền cọc.
​Thống kê & Báo cáo:
​Thiết kế giao diện biểu đồ theo dõi tỷ lệ lấp đầy bàn, lượng khách hủy bàn và tổng tiền cọc thu được.
​Thành viên 4 - Phân tích Nghiệp vụ, Kiểm thử Chất lượng & Viết Tài liệu
​Thu thập & Phân tích yêu cầu (BA):
​Khảo sát quy trình đặt bàn thực tế và viết tài liệu mô tả chi tiết yêu cầu hệ thống (SRS).
​Xây dựng sơ đồ quy trình nghiệp vụ (Use Case, Activity Diagram) cho các trường hợp: đặt bàn, hủy bàn, hoàn cọc, quá giờ giữ bàn.
​Kiểm thử phần mềm (QA/QC):
​Viết kịch bản kiểm thử (Test Cases) chi tiết cho toàn bộ các chức năng.
​Thực hiện kiểm thử chức năng, kiểm thử giao diện trên máy tính và điện thoại.
​Thực hiện kiểm thử chịu tải để đảm bảo hệ thống không bị treo khi nhiều người cùng đặt bàn vào giờ cao điểm.
​Quản lý dự án & Tài liệu:
​Theo dõi tiến độ, quản lý danh sách lỗi (Bugs) phát sinh.
​Viết tài liệu hướng dẫn sử dụng cho khách hàng và nhân viên lễ tân.