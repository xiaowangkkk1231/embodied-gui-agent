# 调度器、仲裁与标定（工程实现说明）

> 配套 01 方案书、02 架构图。本文给的是**可直接落地的伪代码与公式**，语言无关（示例用 Python 风格）。

---

## 1. 主状态机

```
                  ┌──────────────────────────────────────────┐
                  │                                          │
   ┌────────┐   ┌─▼───────┐   ┌────────┐   ┌────────┐   ┌───▼────┐
   │  IDLE  │──▶│ OBSERVE │──▶│ GROUND │──▶│ DECIDE │──▶│   ACT  │
   └────────┘   └─────────┘   └────────┘   └────────┘   └───┬────┘
        ▲                                                    │
        │            ┌──────────┐    ┌────────┐              │
        └────────────│  RECOVER │◀───│ VERIFY │◀─────────────┘
                     └──────────┘    └────────┘
                          │
                     ┌────▼────┐
                     │  ABORT  │  ← 安全监视触发（超力 / 急停 / 连续失败）
                     └─────────┘
```

| 状态 | 进入条件 | 退出条件 | 超时 |
|---|---|---|---|
| IDLE | 任务开始 / 上一步成功 | 有未完成子目标 | — |
| OBSERVE | 任一动作后 | 截图 + 力信号窗口落盘 | 1.0 s |
| GROUND | 有截图 | 拿到 ≥1 个候选元素 | 2.0 s |
| DECIDE | 有候选 | 产出 `Action` | 1.5 s |
| ACT | 有 Action | 执行器回报完成 | 2.0 s |
| VERIFY | 动作完成 | success / fail 判决 | 1.0 s |
| RECOVER | 判决 fail | 重试或换执行器 | 3 次 |
| ABORT | 安全阈值 | 人工介入 | — |

**硬约束**：单个任务最长步数（默认 20）、最长墙钟（默认 120s）、连续失败 3 次即 ABORT。

---

## 2. 动作原语接口

```python
@dataclass
class Action:
    kind: str            # key | type | scroll | tap | long_press | swipe | drag
    params: dict         # 见下表
    target: Optional[BBox] = None
    hint: Optional[str] = None   # "hid" | "mech" | None
    timeout_ms: int = 2000

@dataclass
class BBox:
    x: int; y: int; w: int; h: int
    label: str
    responds_to_mouse: bool = True   # 由历史成功率估计，而非静态声明
```

| kind | params | 首选执行器 | 备注 |
|---|---|---|---|
| `key` | `code`（BACK/HOME/APP_SWITCH/ENTER） | HID | 系统键码，零定位 |
| `type` | `text` | HID | 中文需配合输入法/剪贴板 |
| `scroll` | `dy`（像素或档位） | HID | 滚轮；列表页最稳 |
| `tap` | `x,y` | 机械 | 目标 `responds_to_mouse=False` 时强制机械 |
| `long_press` | `x,y,ms` | 机械 | 建议 800ms |
| `swipe` | `points[], ms` | HID（拖拽） | 机械需轨迹规划，优先 HID |
| `drag` | `from,to,ms` | 机械 | 排序类拖拽 |

---

## 3. 仲裁器

目标：在**成功率**与**延迟**之间取帕累托最优。

```python
def choose_effector(a: Action, ctx) -> str:
    # 1) 硬规则：能力不匹配直接排除
    if a.kind in ("key", "type", "scroll"):
        return "hid"
    if a.kind in ("tap", "long_press"):
        if ctx.target and not ctx.target.responds_to_mouse:
            return "mech"
        if ctx.mech_busy and ctx.hid_ok:
            return "hid"          # 退化为视觉伺服点击
        if ctx.recent_mech_fail >= 2 and ctx.hid_ok:
            return "hid"
        return "mech"             # 默认：真触摸更通用
    if a.kind in ("swipe", "drag"):
        return "hid" if a.kind == "swipe" else "mech"
    return "mech"

# 软化版本：用在线估计的成功率/延迟做加权打分
# score(e) = w1 * P_success(e, kind) + w2 * P_success(e, target_label)
#            - w3 * E[latency(e)] - w4 * busy_penalty(e)
# 权重初始 (1.0, 0.6, 0.004/ms, 0.3)，按任务族各训一组
```

**在线更新**：每次动作后按 (kind, target_label, effector) 维护 Beta 后验，`P_success = α/(α+β)`，滑动窗口 200 次。

---

## 4. 动作后验证（VERIFY）

```python
def verify(before, after, expect) -> Verdict:
    if expect.assert_dsl:                 # 结构化断言优先
        return run_assert(expect.assert_dsl, after)
    sim = ssim(before.roi, after.roi)     # 结构相似度兜底
    if sim > 0.98:  return Verdict(False, "no_change")
    if sim < 0.60:  return Verdict(True,  "page_changed")
    return Verdict(True, "element_present") if expect.element in after.elements else Verdict(False, "uncertain")
```

**失败归因**（写入日志，供分析用）：

| 标签 | 判据 |
|---|---|
| `decision_error` | grounding 的框与人工标注 IoU < 0.5 |
| `execution_error` | 框正确但点击后无变化，且力信号显示接触异常 |
| `perception_error` | 截图模糊/遮挡/反光，元素未被检出 |
| `env_error` | 网络、弹窗、权限等外部中断 |
| `unsupported` | 需要多点/手势，硬件不支持 |

---

## 5. 标定

### 5.1 相机内参（离线，一次）

```python
import cv2, numpy as np
# 棋盘格 9x6 内角点，边长 20mm；采 15 张不同姿态
ret, K, dist, _, _ = cv2.calibrateCamera(objp, imgp, gray.shape[::-1], None, None)
# 重投影误差目标 < 0.3 px
```

### 5.2 像素 → 机械坐标（单应矩阵 H）

```python
def calibrate_homography(pairs):          # pairs: [(u,v), (X_mm, Y_mm)]
    src = np.float32([p[0] for p in pairs])
    dst = np.float32([p[1] for p in pairs])
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 3.0)
    err = rms_reprojection(H, src, dst)   # 目标 ≤ 0.5 mm
    return H, err

def px_to_mm(H, u, v):
    p = H @ np.array([u, v, 1.0])
    return p[0]/p[2], p[1]/p[2]
```

**取点方式**：手动示教 4–9 点（触头在屏幕上点出的实际位置），或屏幕显示已知间距的十字阵列自动采集。

### 5.3 触头偏置（tool offset）

```python
# 触头点一下屏幕上的基准点 P，记录机械坐标 (Xm, Ym)
# 相机在该点看到像素 (u, v) → 映射得 (Xc, Yc)
offset = (Xm - Xc, Ym - Yc)      # 之后所有视觉目标都要减去它
```

### 5.4 HID 视觉伺服（解决"相对坐标"问题）

Android 会把鼠标箭头画在屏幕上，因此可以闭环：

```python
def hid_move_to(u_t, v_t, iters=4, tol=3):
    for _ in range(iters):
        img = grab()
        (u_c, v_c) = detect_cursor(img)          # 模板匹配光标箭头
        du, dv = u_t - u_c, v_t - v_c
        if abs(du) <= tol and abs(dv) <= tol:
            return True
        hid.move(dx=gain*du, dy=gain*dv, steps=1) # gain 初值 0.8，按收敛情况调
        sleep(0.06)
    return False
```

> 若机型不渲染鼠标光标（部分定制 ROM），退化为"屏幕四角回零 + 固定步长"的开环方案，需在任务集里单独标注。

### 5.5 在线校验与重标定

```python
def auto_check():
    # 每 30 分钟：机械去基准点 1、2、3 各点一次，读力信号 + 截图确认
    errs = [compare(expected, actual) for expected, actual in baseline_points]
    if max(errs) > 0.5:          # mm
        recalibrate()            # 重跑 5.2 + 5.3，约 5–10 min
```

### 5.6 换机型复用

1. 夹具用**定位销 + 可调挡边**，保证手机左/下边对齐同一基准；
2. 用屏幕尺寸检测（分辨率 + 边框识别）自动换算显示区域；
3. 只需重采 4 个点即可重算 H——目标 **≤10 min**。

---

## 6. 安全

| 项 | 阈值 / 策略 |
|---|---|
| 触头最大接触力 | 2 N（FSR 标定后闭环限幅） |
| 单次下压时长 | ≤ 200 ms |
| 电磁铁占空比 | ≤ 20%（防过热） |
| 机械越界 | 软限位 + 硬限位各一层 |
| 急停 | 物理常闭按钮，切断 12V |
| 看门狗 | 主控 500 ms 无心跳 → 断电回零 |
| 电源时序 | 先逻辑后功率；步进与 BLE 电源分开滤波 |

---

## 7. 日志（详见 06）

每次动作落一行 JSON：`ts, task_id, step, state, action, target, effector, latency_ms, force_peak, force_impulse, verdict, fail_label, screenshot_before, screenshot_after`。
