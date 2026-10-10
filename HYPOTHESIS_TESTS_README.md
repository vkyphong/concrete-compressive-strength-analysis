# Phần 3 — Kiểm định giả thuyết cường độ chịu nén bê tông

## Nội dung

- `analysis/hypothesis_tests.py`: mã phân tích hai câu hỏi và minh họa Chi-square.
- `analysis/reporting.py`: kiểm tra tính nhất quán của CSV, hình, dữ liệu và liên kết trong Markdown.
- `analysis/build_report.py`: dựng Word trực tiếp từ Markdown chuẩn (cần cài pandoc).
- `notebooks/04_hypothesis_tests.ipynb`: notebook nêu rõ hai câu hỏi, H₀/H₁ và kết luận ở những hình/bảng quan trọng; đã lưu bảng và hình, có thể chạy lại.
- `data/hypothesis_tests/cleaned.csv`: bản dữ liệu 1.005 dòng dành riêng cho phần 3; không ghi đè dữ liệu của EDA khi ghép dự án.
- `tables/hypothesis_tests/`: 13 bảng CSV, ánh xạ cụm và thông tin lần chạy.
- `figures/hypothesis_tests/`: 7 hình PNG.
- `report/`: báo cáo Markdown, Word và PDF của phần 3.

## Chạy lại

Từ thư mục gốc vừa giải nén, dùng Python 3.11 trở lên:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-hypothesis.txt
python analysis/hypothesis_tests.py
python analysis/reporting.py
python analysis/build_report.py  # cần cài pandoc trước
```

Để chạy notebook, cài thêm `python -m pip install -r requirements-notebook.txt`, chọn kernel của `.venv` và dùng **Run All**. Mã tìm dữ liệu theo vị trí tệp Python nên không phụ thuộc thư mục hiện hành của terminal. Word và PDF trong gói được dựng từ cùng Markdown chuẩn; khi sửa lời văn, chạy `build_report.py` rồi xuất PDF từ DOCX để hai bản thống nhất. Khi thay `cleaned.csv`, cần tính lại bảng/hình và rà soát toàn bộ câu chữ, DOCX/PDF; `reporting.py` kiểm tra tính nhất quán nội bộ thay vì khóa cứng các con số của bản dữ liệu hiện tại.

## Phương pháp

1. Câu hỏi 1 dùng paired t-test để ước lượng mức tăng MPa của cùng cấp phối từ 7 đến 28 ngày.
2. Câu hỏi 2 dùng Welch ANOVA và Games–Howell để so cường độ quan sát được của bốn kiểu SCM ở 28 ngày.
3. Chi-square minh họa liên hệ giữa kiểu SCM và việc dùng phụ gia siêu dẻo, hai biến phân loại sẵn có.

Đơn vị là cấp phối; ngưỡng gộp chính 1 kg/m³ ở bảy thành phần vật liệu. Bảng độ nhạy xét ngưỡng 0; 0,5; 1; 2. So sánh ở vùng xi măng 220–340 kg/m³ là thăm dò mức chồng lấn, không phải chứng cứ nhân quả.

Gói này là phần kiểm định để tích hợp vào dự án của nhóm; báo cáo tổng thể và gói nộp theo mã số sinh viên được hoàn thiện sau khi các phần còn lại thống nhất dữ liệu.

## Nếu notebook báo AttributeError DATA_PATH

Đó là lỗi của notebook được chỉnh sửa trên máy trước khi cập nhật bản này: mô-đun v3 khai báo `DATA`, không khai báo `DATA_PATH`. Mã mới hỗ trợ cả hai tên. Sau khi giải nén bản này, trong VS Code chọn **Restart Kernel → Run All**; nếu còn một bản notebook đang mở và có dấu chấm chưa lưu, hãy mở lại tệp trong gói này.
