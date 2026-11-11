# Claude Automation Builder — slide tương tác

Trang slide tương tác Tầng 3 (B11–B13), đăng bằng GitHub Pages.

## Thêm slide của một buổi
1. Chép file deck vào `modules/`, tên bắt đầu bằng mã buổi: `B11_ten-buoi.html`
   (hoặc một thư mục `B11_ten-buoi/` có `index.html` bên trong, nếu deck có ảnh/file kèm).
2. GitHub Desktop: viết commit → **Commit to main** → **Push origin**.
3. Khoảng 1 phút sau, trang chủ tự hiện thẻ buổi đó là "Đã mở".

Mô tả trên thẻ lấy từ `<meta name="description" content="...">` trong deck nếu có;
không có thì dùng mô tả mặc định trong `build_index.py`.

## File
- `_template.html`: giao diện trang chủ (sửa ở đây, không sửa `index.html`).
- `build_index.py`: dựng `index.html`. Xem trước trên máy: `python3 build_index.py`.
- `.github/workflows/pages.yml`: GitHub tự dựng và đăng mỗi lần push.
