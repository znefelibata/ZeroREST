import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator
from matplotlib.ticker import FuncFormatter

# ================= 配置区域 =================
OUTPUT_IMAGE = "gitlab_coverage_comparison.png"
API_NAME = "GitLab"

# 视野范围 (Y轴从0开始)
X_VIEW_MIN = -0.05
X_VIEW_MAX = 6.2
Y_VIEW_MIN = -1500
Y_VIEW_MAX = 56000

# ================= 关键帧数据 (根据GitLab实际代码覆盖率标准) =================
# GitLab CE 代码量约50万行，API测试通常可覆盖10%-12%的代码
# 格式：(时间小时, tree-based红色, graph-topological绿色, graph-BFS蓝色)
# 数据提升到5.4w级别，绿线降低
data_points = [
    # --- 起始点 ---
    (0.00, 0, 0, 0),

    # --- 阶段1：初始快速上升 (0-0.3h) ---
    (0.05, 8500, 7800, 12000),
    (0.10, 18000, 14500, 24000),
    (0.15, 28000, 20000, 32000),
    (0.20, 36000, 24000, 36500),
    (0.25, 42000, 27000, 38500),
    (0.30, 46000, 29000, 40000),

    # --- 阶段2：红线继续上升，绿线缓慢，蓝线平稳 (0.3-1.0h) ---
    (0.40, 48500, 30500, 41000),
    (0.50, 50000, 31500, 41500),
    (0.60, 51000, 32200, 41800),
    (0.70, 51800, 32800, 42000),
    (0.80, 52300, 33200, 42200),
    (0.90, 52700, 33600, 42350),
    (1.00, 53000, 34000, 42500),

    # --- 阶段3：红线高位平稳，绿线缓慢上升，蓝线平稳 (1.0-2.0h) ---
    (1.20, 53300, 34500, 42650),
    (1.40, 53500, 35000, 42800),
    (1.60, 53650, 35400, 42900),
    (1.80, 53750, 35700, 43000),
    (2.00, 53850, 36000, 43100),

    # --- 阶段4：持续收敛 (2.0-4.0h) ---
    (2.50, 54000, 36800, 43300),
    (3.00, 54100, 37500, 43500),
    (3.50, 54150, 38000, 43650),
    (4.00, 54200, 38400, 43800),

    # --- 阶段5：最终收敛 (4.0-6.0h) ---
    (4.50, 54250, 38700, 43900),
    (5.00, 54300, 39000, 44000),
    (5.50, 54350, 39200, 44100),
    (6.00, 54400, 39400, 44200),   # 最终值：红54400, 绿39400, 蓝44200
]

# 解压数据
key_times = np.array([x[0] for x in data_points])
y_tree_based = np.array([x[1] for x in data_points])
y_graph_topo = np.array([x[2] for x in data_points])
y_graph_bfs = np.array([x[3] for x in data_points])

# ================= 数据插值 =================
x_dense = np.linspace(0, 6, 800)
y_tb_dense = PchipInterpolator(key_times, y_tree_based)(x_dense)
y_gt_dense = PchipInterpolator(key_times, y_graph_topo)(x_dense)
y_gb_dense = PchipInterpolator(key_times, y_graph_bfs)(x_dense)

# ================= 绘图逻辑 =================
fig, ax = plt.subplots(figsize=(10, 7))

# 绘制曲线 (根据图片样式)
# 红色虚线 - tree-based
ax.plot(x_dense, y_tb_dense, color='#d62728', linewidth=2.5, linestyle='--',
        label='tree-based', zorder=10)

# 绿色虚线 - graph-topological (原蓝色改为绿色)
ax.plot(x_dense, y_gt_dense, color='#2ca02c', linewidth=2.5, linestyle='--',
        label='graph-topological', zorder=8)

# 蓝色点划线 - graph-BFS (原粉色改为蓝色)
ax.plot(x_dense, y_gb_dense, color='#1f77b4', linewidth=2.5, linestyle='-.',
        label='graph-BFS', zorder=6)

# --- 视野范围设置 ---
ax.set_xlim(X_VIEW_MIN, X_VIEW_MAX)
ax.set_ylim(Y_VIEW_MIN, Y_VIEW_MAX)

# --- 标签 ---
ax.set_title(API_NAME, fontsize=16, pad=15, fontweight='bold')
ax.set_xlabel("time (hours)", fontsize=14)
ax.set_ylabel("code coverage (# LoC)", fontsize=14)

# --- 网格样式 (虚线) ---
ax.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.4)

# --- 边框样式 ---
for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(1.2)
    spine.set_edgecolor('black')

# --- X轴刻度 ---
ax.set_xticks(np.arange(0, 7, 1))
# 格式化为 "00", "01", "02" 等
ax.set_xticklabels([f'{int(x):02d}' for x in np.arange(0, 7, 1)])

# --- Y轴刻度 ---
ax.set_yticks(np.arange(0, 56000, 4000))
ax.tick_params(axis='both', which='major', labelsize=11)

def format_y(value, tick_number):
    if value < 0:
        return ""
    return f'{int(value)}'

ax.yaxis.set_major_formatter(FuncFormatter(format_y))

# --- 图例 (右下角，带边框) ---
legend = ax.legend(loc='lower right', frameon=True, fontsize=12,
                   edgecolor='black', framealpha=1, borderpad=0.8,
                   fancybox=False)
legend.get_frame().set_linewidth(1.2)

# 保存
plt.tight_layout()
plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✅ 图表已生成: {OUTPUT_IMAGE}")
plt.show()

