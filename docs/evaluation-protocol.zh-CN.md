# 评测协议与指标定义

> 配套 01 方案书。目标：让"物理执行 vs 软件注入"的对比**可复现、可统计、可被第三方重跑**。

---

## 1. 任务模板（YAML）

```yaml
id: C5-03
category: C5_restricted      # C1_导航 C2_输入 C3_弹窗 C4_手势 C5_受限
title: 在安全键盘中完成支付密码输入
app: open_source_demo_app    # 只用自建/开源 App
initial_state:
  activity: PayActivity
  reset: cold_start          # cold_start | warm | 指定 deep link
goal:
  assert:
    - type: text_present
      value: "支付成功"
    - type: activity_changed
      to: ResultActivity
  max_steps: 15
  timeout_s: 90
randomization:
  - list_order: shuffle      # 列表项顺序随机
  - start_offset: random     # 起始滚动位置随机
notes: 安全键盘屏蔽 ADB 与无障碍，物理执行为唯一通路
```

## 2. 任务集（5 类 × 12 = 60）

| 类别 | 任务示例（各 12 个） | 设计意图 |
|---|---|---|
| **C1 导航** | 返回上一页、切换底部 Tab、进入二级列表、打开设置、关闭权限页 | 基础可控性，验证执行链路 |
| **C2 输入** | 搜索框输入英文、输入数字、切换输入框、清空输入、提交表单 | HID 优势区 |
| **C3 弹窗/中断** | 关闭插屏广告、处理网络错误重试、允许权限弹窗、处理升级提示 | 鲁棒性与恢复能力 |
| **C4 手势** | 长按弹出菜单、拖拽排序、双指缩放地图、上滑下拉刷新、连续滚动 | 能力边界（预期部分失败） |
| **C5 受限界面** | 安全键盘输入、只认触摸的自绘控件、DRM 播放控制、防截屏页面（截图会黑屏）、无障碍被禁用的页面 | **RQ1 核心：物理执行的价值证明** |

> 每个任务都必须能被**自动断言**判定，否则不入集。

## 3. 运行协议

| 项 | 规定 |
|---|---|
| 冷/热启动 | 每个任务前 `force-stop` + 清缓存，固定冷启动 |
| 预热 | 每台设备开机后先跑 3 个不计分任务，稳定系统状态 |
| 重复次数 | 每任务 **5 次**（二值指标），连续指标取 5 次均值 |
| 随机化 | 任务顺序、列表顺序、起始滚动位置三者都随机，种子记录在案 |
| 环境 | 固定光照（照度计读数）、固定电量区间（40–80%）、飞行模式 + 固定 WiFi、关闭自动亮度 |
| 隔离 | 同一时段只跑一台设备，避免蓝牙/网络互相干扰 |
| 人工介入 | 只允许在 ABORT 后可人工复位，介入行为记录为 `human_intervention=true` 并单独统计 |
| 数据留存 | 截图、力信号原始序列、动作日志、视频（可选）全部落盘，保留 30 天 |

**重跑成本**：单设备单组 60 任务 × 5 次 × 平均 45s ≈ 3.8 小时；5 组对照 ≈ 19 小时/轮。

## 4. 指标定义

| 指标 | 公式 / 口径 |
|---|---|
| **TSR**（任务成功率） | `通过断言次数 / 总运行次数`，二值，严格判定 |
| 严格子集 TSR | 仅 C5 类，用于 RQ1 |
| **Steps** | `动作数 / 成功任务数`（失败任务不计入，另列） |
| **T_task** | 从首个 OBSERVE 到断言通过/超时的墙钟，中位数 + IQR |
| **RetryRate** | `重试动作数 / 总动作数` |
| **EffectorMix** | `hid_actions : mech_actions : injected_actions` 占比 |
| **ForceAUC** | 力判别器在"点击被接收 / 未被接收"二分类上的 ROC-AUC |
| ForceF1 / 判定延迟 | F1@0.5；从接触开始到输出判决的毫秒数 |
| **CalibErr** | 标定点重投影 RMS（mm），每次开机测一次 |
| **RecalTime** | 换机型后从开始到 CalibErr ≤ 0.5mm 的耗时（min） |
| **CrossDeviceDrop** | `(TSR_机型A − TSR_机型B) / TSR_机型A`，测 2–3 台不同品牌/分辨率 |
| 安全事件数 | 超力、越界、急停、屏幕压痕（目检）次数，**必须为 0** |

## 5. 统计方法

- 二值（成功/失败）：配对 **McNemar 检验**（同任务同随机种子），报告 p 值与效应量（odds ratio）。
- 连续指标：任务级配对 bootstrap（10,000 次），报告 95% CI。
- 多组比较：Holm–Bonferroni 校正，α = 0.05。
- 报告规范：`mean ± std`（或中位数[IQR]），附 n，附失败归因分布。

## 6. 日志 Schema（每动作一行 CSV / JSONL）

| 字段 | 类型 | 说明 |
|---|---|---|
| `run_id` | str | 一次运行的唯一 id（含种子） |
| `task_id` | str | 对应任务模板 |
| `group` | str | B1/B2/B3/B4/Ours |
| `device` | str | 机型 + 系统版本 + 分辨率 |
| `step` | int | 步序 |
| `state` | str | 状态机状态 |
| `action_kind` | str | key/type/scroll/tap/long_press/swipe/drag |
| `effector` | str | hid / mech / adb / a11y |
| `target_bbox` | str | `x,y,w,h` |
| `target_label` | str | 元素语义 |
| `latency_ms` | int | 动作端到端耗时 |
| `force_peak` | float | 牛顿（标定后） |
| `force_impulse` | float | N·ms |
| `contact_ms` | int | 接触时长 |
| `verdict` | bool | 动作后验证结果 |
| `fail_label` | str | 见 [`scheduler-and-calibration.zh-CN.md`](scheduler-and-calibration.zh-CN.md) 的归因表 |
| `screenshot_before` | str | 文件路径 |
| `screenshot_after` | str | 文件路径 |
| `human_intervention` | bool | 是否人工介入 |

## 7. 基线公平性（必须遵守）

1. **同一任务、同一随机种子、同一设备**下比较；
2. 所有组使用**相同的 grounding 模型**（否则差异归因于决策而非执行）；
3. 所有组的**决策预算相同**（相同步数上限、相同 VLM 调用次数）；
4. 软件注入组使用官方 API（`adb shell input` / `AccessibilityService`），不用 hack；
5. 报告**失败归因分布**而非只报 TSR——否则无法区分"执行不行"和"决策不行"。

## 8. 预期结果形态（用于判断实验是否正常）

| 假设 | 预期 |
|---|---|
| H1（RQ1） | C5 类上，Ours 显著 > B1/B2（例如 70% vs 10%），其他类别差距小 |
| H2（RQ2） | 力判别 AUC ≥ 0.85，判定延迟 ≤ 100ms，比截图验证快 3–10 倍 |
| H3（RQ3） | 阈值仲裁比固定机械策略耗时低 20–35%，TSR 下降 < 3% |
| H4（RQ4） | 跨机型 TSR 降幅 < 10%，重标定 ≤ 10min |
| H5（RQ5） | 手势覆盖约 60–70%，C4 类 TSR 明显低于其他类（预期 30–50%） |

若 H1 不成立（物理执行没有优势），这本身也是一个有意义的负结果——说明瓶颈在决策层，应转向 grounding 研究。
