A_MCM_A – Smartphone Battery Drain (A) / 手机电量耗竭建模（A）

- Changelog / 变更记录
- 2026-01-30: 初始正式技术文档模板，包含中英对照、公式区块、字段表、使用示例；CSV 输出字段扩展以包含分量功耗。新增 notebook 路径指引。
- 2026-01-31: 增添 Notebook HTML 导出的一键脚本方案（Python 脚本 ci_export_notebook_html.py、Shell 脚本 run_and_export.sh、Windows batch run_and_export.bat），方便 CI/CD 自动化导出 HTML。

Overview / 概述
- English: Lightweight, extensible Python model for MCM A. Physics-based SOC dynamics with component-wise power decomposition and temperature-dependent capacity. Also outlines a data-driven (training-style) parameter fitting approach without neural networks.
- 中文: 轻量且可扩展的 Python 实现，基于物理的 SOC 动态，结合组件功耗分解与温度依赖容量，并给出非神经网络的参数拟合思路。

Project layout / 目录结构
- battery_model.py: 核心引擎，实现 SOC 更新、温度耦合与分量功耗计算
- demo_run.py: 简单演示脚本，展示两段使用情景并输出 CSV
- noteboooks/ or notebooks/: 相关 Notebook（如 battery_csv_demo.ipynb）
- README.md: 本文档（本文件）
- output/ 目录（可在运行时自动创建，保存 CSV 输出）

CSV & Visualization outputs / CSV 与可视化输出
- 本仓库支持将仿真轨迹导出为 CSV，字段包括：time_s, SOC, temp_C, P_W, I_A, Q_eff_Ah, brightness, cpu_load, network, gps, background, ambient_T。
- 现在还扩展了分量功耗字段：P_screen_W, P_CPU_W, P_network_W, P_GPS_W, P_background_W，便于细粒度分析。
- 也支持生成简单的静态可视化图（如 SOC/温度/功耗随时间的曲线）作为后续分析的入口。

Usage / 使用
- 运行演示：
  python A_MCM_A/demo_run.py
- CSV 导出：在演示脚本中，仿真结果将自动导出到 A_MCM_A/output/trajectory_demo.csv。
- 自定义参数：通过 BatteryModel 的构造函数参数进行调整，关键参数包括 Q_Ah、V_nom、温度相关常数等。
- 使用情景：通过 usage_schedule 与 ambient_schedule 传入多段使用情景与环境温度。

API 与接口 / API 与接口
- BatteryModel(
    Q_Ah=3.8, V_nom=3.85, T_ref=25.0, k_temp=0.02,
    P_base=0.20, P_screen_base=0.30, P_cpu_idle=0.10, P_cpu_peak=0.90,
    P_network=0.25, P_gps=0.04, P_background=0.05,
    C_th=600.0, h=5.0, T_env_init=25.0
  )
- simulate(duration_s, dt_s, usage_schedule, ambient_schedule=None) -> trajectory dict
- export_csv(trajectory, filename) -> None
- reset(soc=1.0, T=None) -> None
- report_summary() -> str

Usage customization / 使用定制
- usage_schedule: list of segments; each segment is a dict with keys: start, end, usage
- usage: dict with keys brightness, cpu_load, network, gps, background
- ambient_schedule: list or dict describing ambient_T over time
- 轨迹输出包含 per-step inputs，便于 CSV 导出分析

Formula blocks / 公式区块
- Physics & Equations / 物理与方程
  - SOC dynamics: dSOC/dt = - I(t) / C_total
  - I(t) decomposition: I(t) = sum of component currents; P(t) = V_nom * I(t)
  - Temperature & capacity coupling: C_total(T) = C_Ah * exp(-k_temp * (T - T_ref))
  - Temperature dynamics: dT/dt = (P(t) - h*(T - T_env)) / C_th

- Component power models / 分量功耗模型
  - P_screen = P_screen_base * (brightness ** P_screen_exp)
  - P_CPU = P_cpu_idle + (P_cpu_peak - P_cpu_idle) * (cpu_load ** P_cpu_exp)
  - P_network, P_GPS, P_background as availability-based constants
  - P(t) = P_base + P_screen + P_CPU + P_network + P_GPS + P_background

Note: This template supports easy extension with aging or non-linear effects as needed.

Data & CSV Output / 数据与 CSV 输出
- Fields (current):
- time_s, SOC, temp_C, P_W, I_A, Q_eff_Ah, brightness, cpu_load, network, gps, background, ambient_T
- Expanded fields (per-step components):
- P_screen_W, P_CPU_W, P_network_W, P_GPS_W, P_background_W
- CSV header example is provided in the Notebook and code comments.

Notebook & Demo / Notebook & 演示
 - Notebooks path: A_MCM_A/notebooks/battery_csv_demo.ipynb
- Path resolution for CSV in Notebook
- You can override CSV path via environment variable A_MCM_A_CSV_PATH, e.g.:
  - Windows: set A_MCM_A_CSV_PATH=C:\path\to\trajectory_demo.csv
  - Linux/macOS: export A_MCM_A_CSV_PATH=/path/to/trajectory_demo.csv
- Or rely on the internal resolver (battery_csv_path_utils.resolve_csv_path) which looks for the default path A_MCM_A/output/trajectory_demo.csv under your repo, with a safety fallback.
- If you patch the notebook (option B) using the provided update_notebook_path.py, the path resolver will be used automatically.
- This notebook demonstrates CSV loading, visualization (SOC, temp, total and component powers) and simple energy metrics.
- Notebook HTML Export (CI/CD) / Notebook HTML 导出（CI/CD）
- One-click HTML export options:
-  - Python: python A_MCM_A/scripts/ci_export_notebook_html.py
-  - Shell (Linux/macOS): A_MCM_A/scripts/run_and_export.sh
-  - Windows: A_MCM_A/scripts/run_and_export.bat
- Prerequisite: nbconvert should be installed in your Python environment.
- How it works: the script first runs the CSV generator (demo_run.py) to ensure data exists, then executes the notebook and exports to HTML.
- Quick manual alternative: generate CSV via "python A_MCM_A/demo_run.py" and then run "jupyter nbconvert --to html --execute A_MCM_A/notebooks/battery_csv_demo.ipynb --output A_MCM_A/notebooks/battery_csv_demo.html --ExecutePreprocessor.timeout=600".

API Reference / API 参考
- BatteryModel constructor parameters (selected):
  - Q_Ah, V_nom, T_ref, k_temp, P_base, P_screen_base, P_screen_exp, P_cpu_idle, P_cpu_peak,
    P_network, P_gps, P_background, P_cpu_exp, C_th, h, T_env_init
- Methods:
  - simulate(duration_s, dt_s, usage_schedule, ambient_schedule=None) -> trajectory dict
  - export_csv(trajectory, filename) -> None
  - reset(soc=1.0, T=None) -> None
  - report_summary() -> str

Usage Examples / 使用示例
```python
from A_MCM_A.battery_model import BatteryModel

model = BatteryModel()
duration_s = 2 * 60 * 60
dt_s = 60
usage = [{"start":0, "end":3600, "usage": {"brightness":0.8, "cpu_load":0.7, "network":True, "gps":True, "background":True}} ,
         {"start":3600, "end":duration_s, "usage": {"brightness":0.3, "cpu_load":0.3, "network":True, "gps":False, "background":True}}]
trajectory = model.simulate(duration_s, dt_s, usage)
model.export_csv(trajectory, "A_MCM_A/output/trajectory_demo.csv")
```

Visualization Guidance / 可视化建议
- 使用 Notebook 中的 notebook_demo 来将 CSV 导出与绘图结合起来，或自行用 Pandas/Matplotlib 绘制。

Contributing & Notes / 贡献与说明
- 保持接口兼容性，新增字段时尽量保持向后兼容；CSV 列表在文档中更新即可。请在 PR/提交信息中注明新字段的用途与影响。

References / 参考资料
- 常见电池物理、温度对容量的影响、设备功耗建模文献等（按需补充到这里）。

Appendix: Notation & Glossary / 附录：符号与术语
- SOC: State of Charge，电池剩余容量比
- P: 功率，单位 W
- I: 电流，单位 A
- C_th: 热容（J/K）
- h: 热传导系数（W/K）
