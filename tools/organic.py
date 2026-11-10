"""Gộp số view công khai TikTok vào .data-wt/organic.json.

Cách dùng: python3 tools/organic.py <file.json>
<file.json> dạng {"<item_id>": [playCount, diggCount, commentCount, shareCount, collectCount], ...}
(chuỗi JSON mà đoạn JS lấy trong Chrome trả về). Video không có trong file mới giữ số lần trước.
Số mới nhỏ hơn số cũ quá 5% (bất thường) thì giữ số cũ.
"""
import json, sys, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / ".data-wt" / "organic.json"
VN = dt.timezone(dt.timedelta(hours=7))

new = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"items": {}}
items = dict(old.get("items", {}))
upd = kept = 0
for iid, v in new.items():
    v = [int(x) for x in v[:5]]
    prev = items.get(iid)
    if prev and v[0] < prev[0] * 0.95:
        kept += 1
        continue
    items[iid] = v
    upd += 1
if not upd:
    print("LỖI: không có video nào được cập nhật"); sys.exit(1)
now = dt.datetime.now(VN).replace(microsecond=0).isoformat()
OUT.write_text(json.dumps({"updated_at": now, "items": items}, separators=(",", ":")), encoding="utf-8")
print(f"OK cập nhật {upd} video, giữ số cũ {kept}, tổng {len(items)} video, tổng view {sum(v[0] for v in items.values())}")
