// NỘI DUNG ĐẶC TẢ (tách riêng khỏi phần dàn trang)
exports.actors = [
  ["Guest", "Khách", "Khách hàng đặt bàn qua web; không cần tài khoản, được định danh bằng số điện thoại."],
  ["Staff", "Nhân viên", "Nhân viên nhà hàng đã đăng nhập: xem sơ đồ bàn, check-in, trả bàn, xem danh sách khách."],
  ["Admin", "Quản lý", "Người quản trị hệ thống, kế thừa toàn bộ quyền của Nhân viên; quản lý bàn, khu vực, tài khoản và xem nhật ký."],
  ["Scheduler", "Bộ hẹn giờ", "Tiến trình tự động của hệ thống (luồng nền), tự đánh dấu 'Vắng mặt' cho lượt đặt quá hạn check-in."],
];

// [mã, tên EN, nghĩa VN, actor, phụ trách]
exports.ucList = [
  ["UC01", "Search table", "Tra cứu bàn trống", "Guest", "TV1"],
  ["UC02", "Book table", "Đặt bàn", "Guest", "TV2"],
  ["UC03", "View booking", "Tra cứu lượt đặt", "Guest", "TV1"],
  ["UC04", "Modify booking", "Đổi lịch (giờ, số người)", "Guest", "TV3"],
  ["UC05", "Cancel booking", "Hủy đặt bàn", "Guest", "TV3"],
  ["UC06", "Login", "Đăng nhập nhân viên", "Staff, Admin", "TV3"],
  ["UC07", "View table map", "Xem sơ đồ bàn tương tác", "Staff, Admin", "TV4"],
  ["UC08", "Check-in", "Check-in bằng mã QR", "Staff, Admin", "TV4"],
  ["UC09", "Complete booking", "Hoàn thành / trả bàn", "Staff, Admin", "TV4"],
  ["UC10", "View guest list", "Xem danh sách khách theo ngày", "Staff, Admin", "TV1"],
  ["UC11", "Mark no-show", "Tự động đánh dấu vắng mặt", "Scheduler", "TV2"],
  ["UC12", "Manage tables", "Quản lý bàn, khu vực, bảo trì", "Admin", "TV2"],
  ["UC13", "Manage staff", "Quản lý tài khoản nhân viên", "Admin", "TV3"],
  ["UC14", "View audit log", "Xem nhật ký thao tác", "Admin", "TV1"],
];

exports.glossary = [
  ["Bàn trống (Available Table)", "Bàn đang hoạt động (không bảo trì), có sức chứa không nhỏ hơn số người và không có lượt đặt nào trùng với khung giờ đang xét, tính cả thời gian dọn bàn 15 phút ở hai đầu."],
  ["Lượt đặt (Reservation)", "Một giao dịch đặt chỗ của khách, gắn với một bàn và một khung giờ, được xác định bởi một mã xác nhận duy nhất."],
  ["Khung giờ (Time Slot)", "Khoảng từ giờ đến đến giờ đến cộng 90 phút. Ví dụ đặt 19:00 thì khung giờ là 19:00 - 20:30."],
  ["Thời gian dọn bàn (Buffer Time)", "15 phút tối thiểu giữa hai lượt đặt liên tiếp trên cùng một bàn để nhân viên dọn dẹp."],
  ["Mã xác nhận (Confirmation Code)", "Chuỗi 8 ký tự gồm chữ in hoa và chữ số, duy nhất, dùng để tra cứu lượt đặt và để sinh mã QR."],
  ["Mã QR", "Hình mã hóa địa chỉ trang check-in của lượt đặt. Nhân viên quét bằng điện thoại để check-in nhanh."],
  ["Check-in", "Hành động nhân viên xác nhận khách đã đến, chuyển lượt đặt từ 'Đã xác nhận' sang 'Đã check-in' (bàn ở trạng thái đang phục vụ)."],
  ["Vắng mặt (No-show)", "Trạng thái của lượt đặt khi khách không check-in trong vòng 15 phút sau giờ đặt; bàn được giải phóng."],
  ["Khu vực (Area)", "Nhóm bàn theo vị trí, ví dụ Trong nhà, Sân vườn, Phòng VIP."],
  ["Sơ đồ bàn (Table Map)", "Màn hình hiển thị vị trí và trạng thái các bàn theo khu vực tại một thời điểm: Trống (xanh), Đã đặt (vàng), Đang phục vụ (đỏ), Bảo trì (xám)."],
  ["Bảo trì (Maintenance)", "Trạng thái tạm ngừng sử dụng một bàn; bàn bảo trì không được xếp cho khách."],
  ["Nhật ký (Audit Log)", "Bản ghi các thao tác tạo, đổi, hủy, check-in, hoàn thành, vắng mặt của từng lượt đặt, kèm thời gian và người thực hiện."],
  ["Giao dịch (Transaction)", "Nhóm thao tác trong cơ sở dữ liệu được thực hiện trọn vẹn hoặc không thực hiện gì, dùng để tránh đặt trùng bàn."],
];

exports.rules = [
  ["BR01", "Nhà hàng mở cửa 10:00 - 22:00. Lượt đặt phải kết thúc trước giờ đóng cửa, nên giờ đến muộn nhất là 20:30.", "UC02, UC04"],
  ["BR02", "Mỗi lượt đặt kéo dài 90 phút kể từ giờ đến.", "UC01, UC02, UC04"],
  ["BR03", "Hai lượt đặt trên cùng một bàn không được trùng khung giờ và phải cách nhau ít nhất 15 phút (dọn bàn).", "UC01, UC02, UC04"],
  ["BR04", "Phải đặt trước ít nhất 60 phút và nhiều nhất 30 ngày.", "UC02, UC04"],
  ["BR05", "Số người mỗi lượt từ 1 đến 20. Sức chứa bàn không nhỏ hơn số người. Hệ thống tự xếp bàn nhỏ nhất còn đủ chỗ (ưu tiên khu vực khách chọn).", "UC01, UC02, UC04"],
  ["BR06", "Chỉ được đổi hoặc hủy khi lượt đặt đang ở trạng thái 'Đã xác nhận' và còn ít nhất 2 giờ trước giờ đặt.", "UC04, UC05"],
  ["BR07", "Chỉ được check-in trong khoảng từ 15 phút trước đến 15 phút sau giờ đặt. Quá 15 phút sau giờ đặt, lượt đặt tự chuyển sang 'Vắng mặt' và bàn được giải phóng.", "UC08, UC11"],
  ["BR08", "Khách được định danh bằng số điện thoại (10-11 chữ số, bắt đầu bằng 0). Khách cũ không bị tạo trùng; họ tên và email được cập nhật theo lần đặt mới nhất.", "UC02"],
  ["BR09", "Bàn đang bảo trì không được xếp cho khách. Chỉ bật bảo trì khi bàn không còn lượt đặt hiệu lực chưa kết thúc.", "UC01, UC12"],
  ["BR10", "Mã xác nhận gồm 8 ký tự chữ in hoa và số, duy nhất toàn hệ thống.", "UC02"],
  ["BR11", "Mật khẩu nhân viên tối thiểu 6 ký tự và chỉ lưu dạng băm (PBKDF2-SHA256 có salt). Không được khóa quản lý cuối cùng. Tài khoản bị khóa không đăng nhập được.", "UC06, UC13"],
  ["BR12", "Mọi thao tác tạo, đổi, hủy, check-in, hoàn thành, vắng mặt đều được ghi nhật ký kèm người thực hiện (nếu là nhân viên).", "UC02 - UC11, UC14"],
  ["BR13", "Chỉ được xóa bàn chưa từng có lượt đặt; chỉ được xóa khu vực không còn bàn.", "UC12"],
];

exports.supp = [
  ["Usability (Khả dụng)", "Giao diện web tự điều chỉnh theo kích thước màn hình (responsive), dùng tốt trên điện thoại. Toàn bộ nội dung bằng tiếng Việt. Khi khách đổi ngày giờ, số người hoặc khu vực, danh sách bàn trống tự cập nhật không cần tải lại trang. Sơ đồ bàn dùng màu phân biệt trạng thái: xanh (trống), vàng (đã đặt), đỏ (đang phục vụ), xám (bảo trì). Thông báo lỗi nêu rõ nguyên nhân và cách khắc phục."],
  ["Reliability (Độ tin cậy)", "Không bao giờ xảy ra đặt trùng bàn (double-booking) kể cả khi nhiều khách thao tác cùng lúc, bằng giao dịch cơ sở dữ liệu và khóa dòng bàn (row-level lock). Tiến trình nền tự quét vắng mặt mỗi 60 giây. Dữ liệu được sao lưu hằng ngày bằng mysqldump."],
  ["Performance (Hiệu năng)", "Đáp ứng đồng thời 100 khách truy cập. Tra cứu bàn trống phản hồi dưới 2 giây. Sử dụng nhóm kết nối (connection pool) và chỉ mục (index) theo bàn - thời gian và theo trạng thái - thời gian. Sơ đồ bàn dùng 2 truy vấn cho toàn bộ bàn (không truy vấn lặp từng bàn). Lưu trữ được 100.000+ khách hàng và 500.000+ lượt đặt."],
  ["Supportability (Khả năng hỗ trợ)", "Mọi tham số nghiệp vụ (giờ mở cửa, thời lượng, thời gian dọn bàn, hạn đổi/hủy, cửa sổ check-in...) nằm tập trung trong một tệp cấu hình, thay đổi không cần sửa mã. Tầng nghiệp vụ tách khỏi giao diện nên kiểm thử tự động được (28 bài kiểm thử pytest)."],
  ["Security (Bảo mật)", "Khách chỉ xem được lượt đặt khi cung cấp đúng mã xác nhận hoặc số điện thoại. Chức năng nhân viên và quản lý yêu cầu đăng nhập và phân quyền theo vai trò. Chống SQL Injection bằng truy vấn tham số hóa; chống XSS bằng mã hóa ký tự đặc biệt khi hiển thị; chống CSRF bằng mã thông báo (token) trên mọi biểu mẫu POST; chống làm ngập dữ liệu bằng giới hạn tối đa 10 lần gửi biểu mẫu mỗi phút cho mỗi địa chỉ IP. Mật khẩu chỉ lưu dạng băm có salt. Cookie phiên đặt HttpOnly và SameSite. Thông báo đăng nhập sai không tiết lộ tài khoản có tồn tại hay không. Địa chỉ chuyển hướng sau đăng nhập được kiểm tra để chống open redirect."],
  ["Design Constraints (Ràng buộc thiết kế)", "Hoạt động trên nền tảng web: HTML5 + CSS3 + JavaScript. Ngôn ngữ lập trình Python 3.10+ với framework Flask. Hệ quản trị CSDL MySQL 8.0 (mã hóa utf8mb4). Chạy được trên Windows và Linux."],
];

exports.desc = [
  ["Xem và tìm kiếm bàn trống:", [
    "Khách hàng có thể tra cứu bàn trống theo ngày giờ đến, số người và khu vực mong muốn. Danh sách bàn được sắp xếp theo sức chứa tăng dần (bàn vừa nhất đứng đầu).",
    "Hệ thống chỉ hiển thị bàn đang hoạt động, đủ chỗ và không trùng lịch với lượt đặt khác (kể cả 15 phút dọn bàn)."]],
  ["Chọn và đặt bàn:", [
    "Mỗi lượt đặt gồm: họ tên và số điện thoại khách (email, ghi chú không bắt buộc), giờ bắt đầu, giờ kết thúc, số người, bàn được xếp và khu vực. Mỗi lượt đặt được cấp một mã xác nhận 8 ký tự và một mã QR để check-in.",
    "Khách có thể tự chọn một bàn trong danh sách bàn trống hoặc để hệ thống tự động xếp bàn nhỏ nhất còn đủ chỗ.",
    "Quy trình đặt bàn: khách nhập ngày giờ, số người; hệ thống kiểm tra quy tắc nghiệp vụ (giờ mở cửa, thời gian đặt trước, số người, thời gian dọn bàn); lưu thông tin khách (định danh bằng số điện thoại); ghi nhận lượt đặt; trả về mã xác nhận và mã QR."]],
  ["Tra cứu, đổi lịch và hủy đặt bàn:", [
    "Khách tra cứu lượt đặt bằng mã xác nhận hoặc số điện thoại.",
    "Khách có thể đổi giờ đến hoặc số người; hệ thống tự chuyển sang bàn khác nếu bàn cũ không còn phù hợp. Khách có thể hủy lượt đặt.",
    "Chỉ được đổi hoặc hủy khi lượt đặt ở trạng thái 'Đã xác nhận' và còn ít nhất 2 giờ trước giờ đặt."]],
  ["Đăng nhập nhân viên:", [
    "Nhân viên và quản lý đăng nhập bằng tên đăng nhập và mật khẩu. Quản lý có toàn bộ quyền của nhân viên."]],
  ["Check-in và phục vụ (dành cho nhân viên):", [
    "Khi khách đến, nhân viên quét mã QR để check-in. Chỉ được check-in từ 15 phút trước đến 15 phút sau giờ đặt; quá hạn, hệ thống tự chuyển lượt đặt sang 'Vắng mặt' và giải phóng bàn.",
    "Nhân viên xem sơ đồ bàn tương tác (Trống, Đã đặt, Đang phục vụ, Bảo trì) tại thời điểm bất kỳ và xem danh sách khách theo ngày.",
    "Sau khi khách dùng bữa xong, nhân viên bấm 'Hoàn thành' để trả bàn."]],
  ["Quản trị hệ thống: Quản lý có các chức năng sau:", [
    "Quản lý bàn và khu vực (thêm, sửa, xóa, bật/tắt bảo trì).",
    "Quản lý tài khoản nhân viên (thêm, khóa/mở khóa, đặt lại mật khẩu).",
    "Xem nhật ký thao tác của các lượt đặt bàn."]],
];

exports.dict = [
  ["khu_vuc", "ma_khu_vuc", "INT, PK, tự tăng", "Mã khu vực"],
  ["", "ten_khu_vuc", "VARCHAR(50), duy nhất", "Tên khu vực"],
  ["", "mo_ta", "VARCHAR(200)", "Mô tả"],
  ["ban", "ma_ban", "INT, PK, tự tăng", "Mã bàn"],
  ["", "ten_ban", "VARCHAR(20), duy nhất", "Tên bàn (A1, B2...)"],
  ["", "ma_khu_vuc", "INT, FK → khu_vuc", "Khu vực của bàn"],
  ["", "suc_chua", "INT, 1-20", "Số chỗ tối đa (BR05)"],
  ["", "vi_tri_x, vi_tri_y", "INT", "Toạ độ trên sơ đồ bàn"],
  ["", "bao_tri", "TINYINT(1)", "1 = đang bảo trì (BR09)"],
  ["khach_hang", "ma_khach", "INT, PK, tự tăng", "Mã khách"],
  ["", "ho_ten", "VARCHAR(100)", "Họ tên"],
  ["", "so_dien_thoai", "VARCHAR(15), duy nhất", "Khóa định danh khách (BR08)"],
  ["", "email", "VARCHAR(100)", "Không bắt buộc"],
  ["", "ngay_tao", "DATETIME", "Thời điểm tạo"],
  ["nhan_vien", "ma_nhan_vien", "INT, PK, tự tăng", "Mã nhân viên"],
  ["", "ten_dang_nhap", "VARCHAR(30), duy nhất", "Tên đăng nhập"],
  ["", "mat_khau_hash", "VARCHAR(255)", "Mật khẩu đã băm (BR11)"],
  ["", "ho_ten", "VARCHAR(100)", "Họ tên"],
  ["", "vai_tro", "ENUM(NHAN_VIEN, QUAN_LY)", "Phân quyền"],
  ["", "kich_hoat", "TINYINT(1)", "0 = tài khoản bị khóa"],
  ["dat_ban", "ma_dat_ban", "INT, PK, tự tăng", "Mã nội bộ"],
  ["", "ma_xac_nhan", "CHAR(8), duy nhất", "Mã xác nhận / nội dung QR (BR10)"],
  ["", "ma_khach", "INT, FK → khach_hang", "Khách đặt"],
  ["", "ma_ban", "INT, FK → ban", "Bàn được xếp"],
  ["", "thoi_gian_bat_dau, thoi_gian_ket_thuc", "DATETIME", "Khung giờ (kết thúc = bắt đầu + 90 phút)"],
  ["", "so_nguoi", "INT, 1-20", "Số người"],
  ["", "ghi_chu", "VARCHAR(200)", "Ghi chú của khách"],
  ["", "trang_thai", "ENUM(DA_XAC_NHAN, DA_CHECK_IN, HOAN_THANH, DA_HUY, VANG_MAT)", "Trạng thái lượt đặt"],
  ["", "gio_check_in", "DATETIME, null", "Giờ check-in thực tế"],
  ["nhat_ky_dat_ban", "ma_nhat_ky", "INT, PK, tự tăng", "Mã nhật ký"],
  ["", "ma_dat_ban", "INT, FK → dat_ban", "Lượt đặt liên quan"],
  ["", "ma_nhan_vien", "INT, FK → nhan_vien, null", "Null = khách hoặc hệ thống"],
  ["", "hanh_dong", "VARCHAR(30)", "TAO, DOI, HUY, CHECK_IN, HOAN_THANH, VANG_MAT"],
  ["", "chi_tiet, thoi_gian", "VARCHAR(255), DATETIME", "Nội dung và thời điểm"],
];

exports.trace = [
  ["UC01", "GET /api/availability", "find_available_tables"],
  ["UC02", "POST /dat-ban", "create_reservation"],
  ["UC03", "GET /xac-nhan/<mã>; /tra-cuu", "get_reservation, find_by_phone"],
  ["UC04", "POST /doi/<mã>", "modify_reservation"],
  ["UC05", "POST /huy/<mã>", "cancel_reservation"],
  ["UC06", "/dang-nhap; POST /dang-xuat", "authenticate"],
  ["UC07", "/nhan-vien; GET /api/so-do-ban", "table_status_map"],
  ["UC08", "/check-in/<mã> (action = check_in)", "check_in"],
  ["UC09", "/check-in/<mã> (action = hoan_thanh)", "complete"],
  ["UC10", "/nhan-vien?ngay=", "guest_list"],
  ["UC11", "run.py (luồng nền); /nhan-vien", "mark_no_shows"],
  ["UC12", "/quan-ly/ban/*; /quan-ly/khu-vuc/*", "list_tables, save_table, set_maintenance, delete_table, add_area, delete_area"],
  ["UC13", "/quan-ly/nhan-su/*", "list_staff, create_staff, set_staff_active, reset_staff_password"],
  ["UC14", "/quan-ly/nhat-ky", "audit_log"],
];

exports.team = [
  ["TV1", "Trưởng nhóm, phân tích nghiệp vụ (BA)", "Business rules, SRS, glossary; UC01, UC03, UC10, UC14"],
  ["TV2", "Thiết kế hệ thống và CSDL", "Sơ đồ lớp, trạng thái, schema MySQL; UC02, UC11, UC12"],
  ["TV3", "Lập trình backend", "Tầng nghiệp vụ Python, bảo mật, đăng nhập; UC04, UC05, UC06, UC13"],
  ["TV4", "Giao diện và kiểm thử (QA)", "Giao diện web, sơ đồ bàn, QR check-in, kiểm thử; UC07, UC08, UC09"],
];
