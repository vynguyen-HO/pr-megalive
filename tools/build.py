"""Ghép số liệu TikTok vào .data-wt/data.json.

Cách dùng: python3 tools/build.py <thư mục input>
Thư mục input chứa 3 file (ngăn cách bằng TAB hoặc khoảng trắng):
  ads.tsv         ad_id  item_id          (mọi ad của 12 kênh, kể cả ad 0 impression)
  metrics.tsv     ad_id  impressions plays view6s likes comments shares follows visits spend   (ad có impressions > 0; spend = chi phí, VND)
  new_videos.tsv  identity_id <TAB> item_id <TAB> duration <TAB> caption   (video chưa có trong data.json; có thể rỗng)
Không đạt kiểm tra thì thoát mã 1 và KHÔNG ghi file.
"""
import json, sys, datetime as dt
from collections import Counter
from pathlib import Path

CH = {
 "4be674d5-ce42-5850-abd4-5a8f1bc1646e": ("Mua gì xài đó", "mua.g.xi"),
 "9fcd14d6-55bf-5c7a-b33e-58f64b6078d2": ("Càng soi càng sáng", "cng.soi.cng.sng97"),
 "48e2834e-9b5b-5130-a264-7a538a728d3b": ("Hóng gì mua đó", "hng.g.mua"),
 "0d08ac1d-ba07-5003-8c5b-4025c14b869f": ("Sống có phúc, di chúc có tên", "dungcosoitmetvcl"),
 "51b52b95-eb91-5270-98fc-0b6138ce455a": ("Lê Lý Hà Linh", "lelyhalinh"),
 "667b55db-c8ca-5f19-a73b-482385a670d3": ("noidzido", "noidzido"),
 "fd05cdb3-2067-56c4-93fc-ec21649a5d23": ("Ngọc Hằng", "ngc.hng9074"),
 "a8b96abf-54d6-5181-a05a-12c1a790c185": ("Thích săn sale", "hu.dit.deal.sc"),
 "0467f433-fe65-5567-b609-3831d3a3d333": ("Hà My", "lc.ci.lc.khc"),
 "d82973bb-b6bb-573e-9e53-ddd97b801181": ("Hà vy05", "_nguyenthitramy3"),
 "862e9eb0-beac-5d1e-9c5b-edae9408d52c": ("ChanLee", "chanlee4449"),
 "75798885-07d2-5b9e-8420-0dbd4da857b3": ("pynchi", "pynpynemly"),
}
START = "2026-11-09"
K = ["impressions", "plays", "view6s", "likes", "comments", "shares", "follows", "visits", "spend"]
N = len(K)
VN = dt.timezone(dt.timedelta(hours=7))
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / ".data-wt" / "data.json"


def die(msg):
    print("LỖI:", msg); sys.exit(1)


def rows(p):
    p = Path(p)
    return [l.rstrip("\n") for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


inp = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
ad2item = dict(l.split()[:2] for l in rows(inp / "ads.tsv"))
metrics = {p[0]: [round(float(x)) for x in p[1:1 + N]] + [0] * (N + 1 - len(p)) for p in (l.split() for l in rows(inp / "metrics.tsv"))}
if not ad2item:
    die("ads.tsv rỗng")
if set(metrics) - set(ad2item):
    die(f"metrics có ad không nằm trong ads.tsv: {sorted(set(metrics) - set(ad2item))[:5]}")

old = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {"videos": []}
old_tot = sum(v.get("impressions") or 0 for v in old["videos"])
vids = {v["item_id"]: dict(v) for v in old["videos"]}

for l in rows(inp / "new_videos.tsv"):
    ident, iid, dur, cap = l.split("\t", 3)
    if ident not in CH:
        die(f"identity lạ: {ident}")
    posted = dt.datetime.fromtimestamp(int(iid) >> 32, VN)
    if posted.strftime("%Y-%m-%d") < START or iid in vids:
        continue
    name, user = CH[ident]
    cap = " ".join(cap.split())
    vids[iid] = dict(channel=name, username=user, item_id=iid,
                     url=f"https://www.tiktok.com/@{user}/video/{iid}",
                     posted=posted.strftime("%Y-%m-%dT%H:%M"), caption=cap,
                     tag="Có" if "#megalive" in cap.lower() else "Không",
                     duration=round(float(dur), 1))

agg = {}
for a, i in ad2item.items():
    s = agg.setdefault(i, [0] * N)
    for n, x in enumerate(metrics.get(a, [0] * N)):
        s[n] += x

unknown = sorted(set(agg) - set(vids))
if unknown:
    die(f"ad trỏ tới video chưa có thông tin, cần thêm vào new_videos.tsv: {unknown}")

for iid, v in vids.items():
    s = agg.get(iid)
    v["ad_status"] = "Chưa có ad" if s is None else ("Đã chạy ad" if s[0] > 0 else "Chưa delivery")
    for k, n in zip(K, range(N)):
        v[k] = None if s is None else s[n]

out = sorted(vids.values(), key=lambda v: v["posted"], reverse=True)
tot = sum(v["impressions"] or 0 for v in out)
if old_tot and tot < old_tot * 0.8:
    die(f"tổng impression giảm bất thường {old_tot} -> {tot}")

now = dt.datetime.now(VN).replace(microsecond=0).isoformat()
DATA.write_text(json.dumps({"updated_at": now, "start_date": START, "videos": out},
                           ensure_ascii=False, indent=1), encoding="utf-8")
print(f"OK {len(out)} video, impression {old_tot} -> {tot}, {dict(Counter(v['ad_status'] for v in out))}")
