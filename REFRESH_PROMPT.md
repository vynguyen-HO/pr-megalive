# Prompt cập nhật dashboard PR 11.11 (dùng MCP TikTok for Business)

Dán nguyên phần trong khung dưới vào tác vụ định kỳ (30 phút). Thay `<REPO_PATH>` bằng đường dẫn repo trên máy.

---

Bạn cập nhật số liệu cho dashboard PR 11.11. Chỉ dùng MCP TikTok for Business (chỉ đọc), tuyệt đối không tạo/sửa/bật/tắt/xoá ad, campaign hay bất cứ thứ gì trên TikTok. Làm việc trong repo `<REPO_PATH>`.

## Cấu hình
- advertiser_id: 7239635595482415105 (HannahOlala - Affiliate)
- identity_authorized_bc_id: 7199957727395741697, identity_type: BC_AUTH_TT
- start_date: 2026-11-09 (chỉ lấy video đăng từ ngày này, giờ Việt Nam UTC+7)
- 12 kênh (channel | username | identity_id):
  1. Mua gì xài đó | mua.g.xi | 4be674d5-ce42-5850-abd4-5a8f1bc1646e
  2. Càng soi càng sáng | cng.soi.cng.sng97 | 9fcd14d6-55bf-5c7a-b33e-58f64b6078d2
  3. Hóng gì mua đó | hng.g.mua | 48e2834e-9b5b-5130-a264-7a538a728d3b
  4. Sống có phúc, di chúc có tên | dungcosoitmetvcl | 0d08ac1d-ba07-5003-8c5b-4025c14b869f
  5. Lê Lý Hà Linh | lelyhalinh | 51b52b95-eb91-5270-98fc-0b6138ce455a
  6. noidzido | noidzido | 667b55db-c8ca-5f19-a73b-482385a670d3
  7. Ngọc Hằng | ngc.hng9074 | fd05cdb3-2067-56c4-93fc-ec21649a5d23
  8. Thích săn sale | hu.dit.deal.sc | a8b96abf-54d6-5181-a05a-12c1a790c185
  9. Hà My | lc.ci.lc.khc | 0467f433-fe65-5567-b609-3831d3a3d333
  10. Hà vy05 | _nguyenthitramy3 | d82973bb-b6bb-573e-9e53-ddd97b801181
  11. ChanLee | chanlee4449 | 862e9eb0-beac-5d1e-9c5b-edae9408d52c
  12. pynchi | pynpynemly | 75798885-07d2-5b9e-8420-0dbd4da857b3

## Các bước
1. Chuẩn bị nhánh data: thư mục `<REPO_PATH>/.data-wt` là git worktree của nhánh `data`. Nếu chưa có: `git fetch origin data`; nếu nhánh tồn tại thì `git worktree add .data-wt data`, nếu chưa thì `git worktree add --orphan -b data .data-wt` (hoặc tạo nhánh orphan tương đương). Đọc `.data-wt/data.json` cũ (nếu có) làm bộ nhớ đệm.
2. Danh sách video:
   - Nếu phút hiện tại < 30 (lần chạy đầu mỗi giờ) hoặc chưa có data.json: gọi `identity_video_get` cho từng kênh (count 20, bỏ qua video có ngày đăng < start_date). Ngày đăng = timestamp trong item_id: `(int(item_id) >> 32)` đổi sang giờ UTC+7. Nếu `has_more` và cần trang tiếp mà tham số cursor bị lỗi, bỏ qua, trang đầu là đủ.
   - Nếu phút >= 30: dùng lại danh sách video trong data.json cũ, và chỉ thêm video mới tìm thấy qua ad (bước 4).
3. Metrics theo ad: `report_integrated_get`, report_type BASIC, data_level AUCTION_AD, dimensions ["ad_id"], metrics ["impressions","video_play_actions","engaged_view","likes","comments","shares","follows","profile_visits"], start_date = start_date, end_date = hôm nay (giờ VN), order_field impressions DESC, page_size 1000. Đọc các trang cho đến khi gặp ad có impressions = 0.
4. Ghép ad → video: dùng `tool_execute` với `ad_get` (advertiser_id, fields ["ad_id","tiktok_item_id","identity_id"], filtering {"ad_ids": [...]} tối đa 100 id mỗi lần) cho các ad có impressions > 0. Nếu muốn nhận diện ad chưa delivery, thử thêm filtering {"creation_filter_start_time": "<start_date> 00:00:00"}; nếu lỗi thì bỏ qua.
5. Gộp: cộng metrics của mọi ad có cùng tiktok_item_id. Với mỗi video:
   - có impressions > 0 → ad_status "Đã chạy ad"
   - có ad nhưng impressions = 0 → "Chưa delivery", mọi số = 0
   - không thấy ad nào → "Chưa có ad", các số để null
6. Ghi `.data-wt/data.json` đúng schema:
   `{"updated_at": "<ISO giờ VN, ví dụ 2026-11-10T21:30:00+07:00>", "start_date": "2026-11-09", "videos": [ ... ]}`
   Mỗi video: `channel, username, item_id (chuỗi), url ("https://www.tiktok.com/@<username>/video/<item_id>"), posted ("YYYY-MM-DDTHH:MM" giờ VN), caption, tag ("Có" nếu caption chứa #megalive, ngược lại "Không"), duration (giây), ad_status, impressions, plays (video_play_actions), view6s (engaged_view), likes, comments, shares, follows, visits (profile_visits)`. Sắp xếp theo `posted` giảm dần. Số là số nguyên, không phải chuỗi.
7. Kiểm tra nhanh: tổng impressions hợp lý so với lần trước (không giảm mạnh bất thường), JSON hợp lệ. Nếu một bước gọi MCP lỗi, KHÔNG ghi đè data.json bằng dữ liệu thiếu; giữ nguyên file cũ và dừng.
8. Commit và push: trong `.data-wt`: `git add data.json && git commit -m "data <giờ>" && git push origin data`. Nếu không có thay đổi ngoài updated_at thì vẫn commit bình thường.

Đừng in ra toàn bộ kết quả API; chỉ tóm tắt cuối cùng một dòng: số video, tổng impression, trạng thái push.

---

## Cài đặt cách 1: Claude Code chạy nền bằng cron (ổn định nhất)
Cần: Claude Code đã đăng nhập, MCP TikTok for Business đã kết nối trong Claude Code, repo đã clone, quyền đọc ghi file và git trong repo.
Lưu phần prompt ở trên vào `~/pr-1111-refresh.txt`, rồi thêm vào crontab (`crontab -e`):

```
*/30 * * * * cd <REPO_PATH> && claude -p "$(cat ~/pr-1111-refresh.txt)" --allowedTools "Bash(git:*)" "Read" "Write" "Edit" "mcp__TikTok_for_Business__*" >> ~/pr-1111-refresh.log 2>&1
```
(Tên tool MCP và cờ `--allowedTools` có thể khác theo bản Claude Code, kiểm tra bằng `claude --help` và `/mcp`.)
Trên macOS có thể dùng launchd thay cron.

## Cài đặt cách 2: tác vụ định kỳ trong app
Nếu app Claude của bạn (Claude Code desktop / Cowork) có "Scheduled tasks": tạo tác vụ mới, lặp 30 phút, thư mục làm việc là repo, dán prompt ở trên, bật cho phép tool TikTok MCP và git.
