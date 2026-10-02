# LEGION — 云蚁自立运行手册（boot 仓常驻文件）

云机 = GitHub Codespaces「turbo meme」。军团经 legion 分支 git 队列派单，云蚁领单跑 claude 回报。

## 开窗启动（每次进云机终端粘贴一行）

```bash
cd /workspaces/boot && git pull --ff-only && tmux new-session -d -s legion 'python3 legion/cloud_legion.py 2>&1 | tee -a /tmp/legion.log' && echo 云蚁已上岗
```

（看岗：`tmux attach -t legion`，分离按 Ctrl+B 再按 D。闲10分钟自退让省核时，别手动stop机器。）

## 协议

- 任务：`queue/<id>.json` = `{id, prompt, max_turns, timeout_s, status: pending→running→done/failed}`
- 回报：`runs/<id>.md` 结果全文；queue json 回写 status/rc/usage（预算官上账）
- 派单端：harness executor=`codespace`（本地 D:\AI军团\harness，需 PAT 见 keys.json 军团-云蚁-Codespaces）

## 红线

- 月额度 120 核时；worker 空闲自退，机器 15min 闲置自动休眠
- 收工三律照旧：结果必 push（worker自动）；老板收工可 stop；不用不删仓
