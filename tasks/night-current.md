<!-- ================================================================ -->
<!-- 军团云夜航 · 任务书投递协议 + 首单任务书                            -->
<!-- 云端位置：boot 仓 tasks/night-current.md                           -->
<!-- 本工程位置：夜航工程/night-current.md（本文件）                     -->
<!-- 云端 claude 会读到全文，但协议已声明「只执行下方正文任务」，         -->
<!-- 因此整文件原样投递也安全；讲究做法是只投 `---` 之后的正文。          -->
<!-- ================================================================ -->

# 云夜航 · 任务书投递协议（投递员/Hermes 读）

## 文件与流向
- 唯一入口：boot 仓 `tasks/night-current.md`。云端每晚北京时间 22:33 自动读取执行。
- 投递方式：Hermes（或人类）每晚 push 覆盖该文件。云端只管执行，不做任何确认回执。
- 投递即生效：当天 push 的任务书，当晚 22:33 就跑。
- 空跑：文件不存在或为空 → 当晚不启动 claude，run 绿色退出 0（无任务≠失败）。
- 一次一单：一晚只投一个任务；跨晚大活请在任务书里自己写清「分几晚、每晚做什么」。

## 任务书正文格式（约定）
- Markdown 纯文本，`claude -p` 把全文当 prompt 直接吃。
- 必含三段：
  - `任务`：做什么，写到可执行（改哪个文件、写什么内容）
  - `约束`：红线。**必须显式写「只许改 X、禁改 Y」**——云端跑在
    `--dangerously-skip-permissions` 下，边界全靠任务书约束
  - `产出判定`：怎么算完成（diff 范围 + 验收点）
- 云端跑完由 workflow 统一 commit+push（作者 cloud-ant），任务书里要写明「无需自行 push」。
- token/耗时结算由 workflow 的「结算」步骤自动回填到最新 `docs/night-log-*.md`，
  任务书不必要求云端自报 token（它自己看不到自己的 json 输出）。

## 结果查看
- 仓库新 commit（作者 cloud-ant）= 产物本体
- Actions run 页 → Artifacts = result.json + stderr 尾部（留档 14 天）
- run 页 Summary = 机器结算表

---

# 首单任务书（R1 · 第 1 轮 · 2026-09-30）

（以下正文 = 投递到 boot 仓 `tasks/night-current.md` 的内容）

## 任务

1. 给 boot 仓 `README.md` 追加一个「军团云夜航」章节，中文，说清四件事：
   - 夜航是什么：每晚 GitHub Actions 无人值守跑 claude headless 干编码任务，产物自动 commit 回仓
   - 怎么触发：每晚北京时间 22:33 自动跑；Actions 页也可手动 Run workflow
   - 产物在哪看：本仓 commit（作者 cloud-ant）+ Actions run 页的 Artifacts
   - 成本 0：public 仓 Actions 分钟免费无限，模型算力走自有 GLM 网关，GitHub 侧零成本
2. 新建 `docs/night-log-0930.md`，记录本次夜航元数据：
   - 触发时间、轮次（R1 第 1 轮）、开始/结束时间、耗时
   - token 用量：取 claude `--output-format json` 输出里的字段
     （usage.input_tokens / usage.output_tokens / total_cost_usd / num_turns / duration_ms）；
     取不到真实值的字段先写「待结算回填」，workflow 的结算步骤会自动补上

## 约束（红线）

- 只许修改 `README.md`，只许新建 `docs/night-log-0930.md`
- 禁止改动/删除其他任何文件（含 .github/、tasks/、已有文档）
- 禁止在任何文件里写入密钥或 token
- 完成后正常结束即可，无需自行 push（收尾步骤统一 commit+push）

## 产出判定

- `README.md` 出现「军团云夜航」章节，四要素（是什么/怎么触发/产物在哪/成本 0）齐全
- `docs/night-log-0930.md` 存在且含元数据表
- 仓库 diff 只涉及上述两个文件
