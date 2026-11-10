# Dashboard PR 11.11 – tự cập nhật mỗi 30 phút

Luồng: cron trên máy → Claude Code + MCP TikTok kéo số liệu → ghi `data.json` vào nhánh `data` của repo
→ trang trên Netlify (nhánh `main`) tự đọc file đó, không cần build lại.

## Cài đặt
1. Chạy `bash setup.sh` (tạo repo `vynguyen-HO/pr-megalive` nếu có GitHub CLI `gh`, đẩy file, tạo nhánh data, đặt cron).
   Không có `gh`: tạo repo PUBLIC rỗng `pr-megalive` trên github.com rồi chạy lại.
2. Netlify: site `pr-1111` → Site configuration → Build & deploy → Continuous deployment → Link repository → chọn repo, nhánh `main`.
3. Cần Claude Code đã cài và đã kết nối MCP TikTok for Business (`claude mcp list`).

## Ghi chú
- Repo phải public để trang đọc được `raw.githubusercontent.com/.../data/data.json`.
- Số liệu là engage của ad (Spark/ads-only), không phải organic.
- Đổi phạm vi video: sửa `start_date` và danh sách kênh trong `REFRESH_PROMPT.md`.
