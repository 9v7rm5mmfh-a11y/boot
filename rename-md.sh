#!/usr/bin/env bash
# rename-md.sh — 批量重命名当前目录的 .md 文件:文件名转小写 + 加日期前缀
# 用法: ./rename-md.sh [--dry-run | --apply]    默认 dry-run,仅预览不改动

set -euo pipefail

DRY_RUN=1
PREFIX="$(date +%Y-%m-%d)"
COUNT=0 SKIP=0

case "${1:-}" in
  --apply)   DRY_RUN=0 ;;
  --dry-run|"") DRY_RUN=1 ;;   # 无参数时默认 dry-run
  -h|--help) echo "用法: $0 [--dry-run(默认)|--apply]"; exit 0 ;;
  *) echo "错误: 未知参数 $1" >&2; exit 1 ;;
esac

MODE="DRY-RUN 预览"; [ "$DRY_RUN" -eq 0 ] && MODE="APPLY 实际执行"
echo "== 模式: $MODE | 日期前缀: ${PREFIX}_ =="

shopt -s nullglob    # 目录下没有 .md 文件时,for 循环直接跳过
for file in *.md; do
  base="${file%.md}"                 # 去掉扩展名
  lower="${base,,}"                  # 文件名转小写
  # 已带 YYYY-MM-DD_ 前缀的不重复添加
  if [[ "$lower" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}_ ]]; then
    new="${lower}.md"
  else
    new="${PREFIX}_${lower}.md"
  fi

  [[ "$file" == "$new" ]] && continue            # 已符合规范
  if [[ -e "$new" ]]; then                       # 目标已存在则跳过,防止覆盖
    echo "[跳过] $file -> $new(目标已存在)"
    SKIP=$((SKIP + 1)); continue
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[预览] $file -> $new"
  else
    mv -n -- "$file" "$new"
    echo "[执行] $file -> $new"
  fi
  COUNT=$((COUNT + 1))
done

echo "== 完成: 处理 $COUNT 个,跳过 $SKIP 个 =="
[ "$DRY_RUN" -eq 1 ] && echo "预览无误后,实际执行: $0 --apply"

exit 0
