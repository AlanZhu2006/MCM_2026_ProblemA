A_MCM_A – Smartphone Battery Drain (A) / 手机电量耗竭建模（A）

Overview / 概述
- English: Lightweight, extensible Python model for MCM A. Physics-based SOC dynamics with component-wise power decomposition and temperature-dependent capacity. Also outlines a data-driven (training-style) parameter fitting approach without neural networks.
- 中文: 轻量且可扩展的 Python 实现，基于物理的 SOC 动态，结合组件功耗分解与温度依赖容量，并给出非神经网络的参数拟合思路。

Project layout / 目录结构
- battery_model.py: 核心引擎，实现 SOC 更新、温度耦合与分量功耗计算
- demo_run.py: 简单演示脚本，展示两段使用情景并输出 CSV
- README.md: 本文档（本文件）
- output/ 目录（可在运行时自动创建，保存 CSV 输出）

CSV & Visualization outputs / CSV 与可视化输出
- 本仓库支持将仿真轨迹导出为 CSV，字段包括：time_s, SOC, temp_C, P_W, I_A, Q_eff_Ah, brightness, cpu_load, network, gps, background, ambient_T。
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

Extending ideas / 拓展思路
- 增加更细分的硬件分量功耗模型、热模型的改进、以及对器件老化的考虑
- 将拟合过程设计为非神经网络的参数估计，使用最小二乘等常见算法
- 输出 CSV 与静态图共同服务于复现实验与报告撰写
