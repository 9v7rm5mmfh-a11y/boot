#!/usr/bin/env python3
# cloud_legion.py — 云蚁 worker：轮询 boot 仓 legion 分支领单 → 跑 claude → 回报结果
# 部署：/workspaces/boot 下，tmux 会话 legion 常驻。空闲10分钟自退让（机器15min闲置自动休眠）。
import json, subprocess, sys, time
from pathlib import Path

REPO = Path('/workspaces/boot')
BRANCH = 'legion'
POLL_S = 30
IDLE_EXIT_MIN = 10
T0 = time.time()

def log(msg):
    print(f'[{time.strftime("%H:%M:%S")}] {msg}', flush=True)

def git(*a):
    r = subprocess.run(['git', *a], cwd=str(REPO), capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()

def sync_branch():
    git('fetch', 'origin', '--prune')
    rc, out = git('rev-parse', '--verify', f'origin/{BRANCH}')
    if rc != 0:
        rc2, sha = git('rev-parse', 'origin/main')
        if rc2 != 0:
            raise RuntimeError('no origin/main: ' + sha)
        git('branch', BRANCH, sha.strip())
        git('push', 'origin', BRANCH)
        log(f'legion 分支已建档 @{sha.strip()[:7]}')
    git('checkout', '-B', BRANCH, f'origin/{BRANCH}')
    git('pull', '--ff-only', 'origin', BRANCH)

def commit_push(msg):
    git('add', '-A')
    rc, out = git('commit', '-m', msg, '--allow-empty')
    rc, out = git('push', 'origin', BRANCH)
    if rc != 0:
        log('push 失败(重拉重试): ' + out[:200])
        git('pull', '--rebase', '--autostash', 'origin', BRANCH)
        git('push', 'origin', BRANCH)

def run_task(spec):
    tid = str(spec.get('id') or 'task')
    tf = Path(f'/tmp/legion-{tid}.txt'); tf.write_text(spec.get('prompt', ''), encoding='utf-8')
    argv = ['claude', '-p', '--max-turns', str(spec.get('max_turns', 20)),
            '--output-format', 'json']
    t0 = time.time()
    of = Path(f'/tmp/legion-{tid}.out')
    try:
        with open(of, 'wb') as fo:
            subprocess.run(argv, stdin=open(tf, 'rb'), stdout=fo,
                           stderr=subprocess.STDOUT,
                           timeout=int(spec.get('timeout_s', 1500)))
        rc = 0
    except subprocess.TimeoutExpired:
        rc = 124
    except FileNotFoundError:
        of.write_text('[legion] claude 命令不存在'.encode())
        rc = 127
    raw = of.read_text(encoding='utf-8', errors='replace')
    result, usage = raw, None
    try:
        env = json.loads(raw.strip().splitlines()[-1])
        if isinstance(env, dict):
            result = env.get('result', raw)
            u = env.get('usage') or {}
            usage = {'total_tokens': (int(u.get('input_tokens') or 0) + int(u.get('output_tokens') or 0)
                                      + int(u.get('cache_read_input_tokens') or 0)
                                      + int(u.get('cache_creation_input_tokens') or 0)),
                     'via': 'cloud-claude', 'model': str(env.get('model', ''))[:60]} if u else None
    except Exception:
        pass
    if rc == 124:
        result += '\n[legion] TIMEOUT 云侧强杀'
    dt = int(time.time() - t0)
    return rc, result, usage, dt

def main():
    log('云蚁 worker 启动，轮询 legion 分支（空闲%d分钟自退让）' % IDLE_EXIT_MIN)
    last_busy = time.time()
    while True:
        try:
            sync_branch()
            qdir = REPO / 'queue'
            pend = sorted([p for p in qdir.glob('*.json')
                           if json.loads(p.read_text(encoding='utf-8')).get('status') == 'pending'])
            if not pend:
                idle = (time.time() - last_busy) / 60
                if idle > IDLE_EXIT_MIN:
                    log(f'空闲{idle:.0f}分钟，worker 退让休眠（任务在队，下次开窗自取）')
                    return 0
                time.sleep(POLL_S)
                continue
            last_busy = time.time()
            for qf in pend:
                spec = json.loads(qf.read_text(encoding='utf-8'))
                tid = str(spec.get('id') or qf.stem)
                log(f'领单 {tid}: {str(spec.get("prompt",""))[:60]}...')
                spec['status'] = 'running'; spec['claimed_at'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')
                qf.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding='utf-8')
                commit_push(f'legion: claim {tid}')
                rc, result, usage, dt = run_task(spec)
                rp = REPO / 'runs' / f'{tid}.md'
                rp.parent.mkdir(exist_ok=True)
                rp.write_text(f'# 云蚁回报 {tid}\n\n- 时间: {time.strftime("%Y-%m-%d %H:%M:%S")}\n'
                              f'- 云侧 exit: {rc} / 耗时 {dt}s\n\n---\n\n{result}\n', encoding='utf-8')
                spec.update({'status': 'done' if rc == 0 else 'failed',
                             'result_path': f'runs/{tid}.md', 'rc': rc, 'cloud_s': dt,
                             'finished_at': time.strftime('%Y-%m-%dT%H:%M:%S%z')})
                if usage:
                    spec['usage'] = usage
                qf.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding='utf-8')
                commit_push(f'legion: {tid} {"done" if rc == 0 else "failed"} ({dt}s)')
                log(f'回报 {tid} rc={rc} {dt}s')
        except Exception as e:
            log(f'循环异常 {type(e).__name__}: {e}（60s后重试）')
            time.sleep(60)

if __name__ == '__main__':
    sys.exit(main())
