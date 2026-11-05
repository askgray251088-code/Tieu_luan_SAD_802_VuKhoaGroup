import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle

plt.rcParams["font.family"] = "DejaVu Sans"
fig, ax = plt.subplots(figsize=(12.4, 11.4))
ax.set_xlim(0, 12.4); ax.set_ylim(0, 11.4); ax.axis("off")
W, H = 3.15, 1.0
BORDER, FILL, LINE = "#b08900", "#fdf1c7", "#7a1f3d"

ax.add_patch(Rectangle((2.0, 0.1), 7.9, 10.8, fill=False, ls="--", ec="#888", lw=1.2))
ax.text(5.95, 10.5, "Hệ thống đặt bàn nhà hàng Hương Việt", ha="center", fontsize=13, fontweight="bold")

UC = {}
def uc(code, vi, en, x, y):
    UC[code] = (x, y)
    ax.add_patch(Ellipse((x, y), W, H, fc=FILL, ec=BORDER, lw=1.3, zorder=3))
    ax.text(x, y + 0.27, code, ha="center", va="center", fontsize=9.5, fontweight="bold", color="#8a6a00", zorder=4)
    ax.text(x, y + 0.02, vi, ha="center", va="center", fontsize=12.5, fontweight="bold", zorder=4)
    ax.text(x, y - 0.27, en, ha="center", va="center", fontsize=10, color="#444", zorder=4)

# cột khách (trái)
uc("UC02", "Đặt bàn", "Book table", 4.1, 9.7)
uc("UC01", "Tra cứu bàn trống", "Search table", 4.1, 8.4)
uc("UC05", "Hủy đặt bàn", "Cancel booking", 4.1, 7.1)
uc("UC03", "Tra cứu lượt đặt", "View booking", 4.1, 5.8)
uc("UC04", "Đổi lịch", "Modify booking", 4.1, 4.5)
# cột nhân viên (phải)
uc("UC07", "Xem sơ đồ bàn", "View table map", 7.8, 9.7)
uc("UC06", "Đăng nhập", "Login", 7.8, 8.4)
uc("UC08", "Check-in bằng QR", "Check-in", 7.8, 7.1)
uc("UC09", "Hoàn thành / trả bàn", "Complete booking", 7.8, 5.8)
uc("UC10", "Xem danh sách khách", "View guest list", 7.8, 4.5)
# hàng dưới
uc("UC11", "Đánh dấu vắng mặt", "Mark no-show", 4.1, 2.2)
uc("UC12", "Quản lý bàn, khu vực", "Manage tables", 7.8, 3.2)
uc("UC13", "Quản lý nhân viên", "Manage staff", 7.8, 1.9)
uc("UC14", "Xem nhật ký", "View audit log", 7.8, 0.6)

def edge_pt(code, tx, ty):
    cx, cy = UC[code]; dx, dy = tx - cx, ty - cy
    t = 1 / math.sqrt((dx / (W / 2)) ** 2 + (dy / (H / 2)) ** 2)
    return cx + dx * t, cy + dy * t

def actor(name, sub, x, y):
    ax.add_patch(plt.Circle((x, y + 0.62), 0.15, fc="white", ec="#444", lw=1.5, zorder=3))
    for (x1, y1, x2, y2) in [(x, y + 0.47, x, y), (x - 0.3, y + 0.3, x + 0.3, y + 0.3), (x, y, x - 0.22, y - 0.42), (x, y, x + 0.22, y - 0.42)]:
        ax.plot([x1, x2], [y1, y2], color="#444", lw=1.5, zorder=3)
    ax.text(x, y - 0.62, name, ha="center", fontsize=12, fontweight="bold")
    ax.text(x, y - 0.95, sub, ha="center", fontsize=10, color="#555")

def bus(codes, side, bus_x, act_x, act_y):
    ys = [UC[c][1] for c in codes] + [act_y]
    ax.plot([bus_x, bus_x], [min(ys), max(ys)], color=LINE, lw=1.1, zorder=2)
    for c in codes:
        x, y = UC[c]
        ex = x - W / 2 if side == "L" else x + W / 2
        ax.plot([bus_x, ex], [y, y], color=LINE, lw=1.1, zorder=2)
    ax.plot([bus_x, act_x], [act_y, act_y], color=LINE, lw=1.1, zorder=2)

def arrow(src, dst, label, dashed=True, col=LINE):
    (x1, y1), (x2, y2) = UC[src], UC[dst]
    p1 = edge_pt(src, x2, y2); p2 = edge_pt(dst, x1, y1)
    ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="-|>", color=col, lw=1.1, ls="--" if dashed else "-"), zorder=2)
    ax.text((p1[0] + p2[0]) / 2 + 0.08, (p1[1] + p2[1]) / 2, label, fontsize=10, color=col, ha="left", va="center",
            bbox=dict(fc="white", ec="none", pad=0.6), zorder=5)

GX, GY = 0.9, 6.9
actor("Khách", "Guest", GX, GY)
bus(["UC01", "UC02", "UC03", "UC04", "UC05"], "L", 2.35, GX + 0.3, GY + 0.3)
SX, SY = 11.4, 7.2
actor("Nhân viên", "Staff", SX, SY)
bus(["UC06", "UC07", "UC08", "UC09", "UC10"], "R", 9.65, SX - 0.3, SY + 0.3)
AX, AY = 11.4, 2.0
actor("Quản lý", "Admin", AX, AY)
bus(["UC12", "UC13", "UC14"], "R", 9.65, AX - 0.3, AY + 0.3)
TX, TY = 0.9, 1.9
actor("Bộ hẹn giờ", "Scheduler", TX, TY)
ax.plot([TX + 0.3, UC["UC11"][0] - W / 2], [TY + 0.3, UC["UC11"][1]], color=LINE, lw=1.1, zorder=2)
# Admin kế thừa Staff
ax.annotate("", xy=(SX, SY - 1.1), xytext=(AX, AY + 0.8), arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.2, fc="white"), zorder=2)
ax.text(SX + 0.12, 4.6, "kế thừa", fontsize=10, color="#333", ha="left")

arrow("UC02", "UC01", "«extend»")
arrow("UC05", "UC03", "«extend»")
arrow("UC04", "UC03", "«extend»")
arrow("UC07", "UC06", "«include»")
arrow("UC08", "UC06", "«include»")
arrow("UC09", "UC08", "«extend»")
plt.savefig("usecase_tongquan.png", dpi=170, bbox_inches="tight", facecolor="white")
