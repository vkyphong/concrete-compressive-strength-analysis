# Dữ liệu kèm phần kiểm định

- Nguồn gốc: I-Cheng Yeh, Concrete Compressive Strength, UCI Machine Learning Repository: https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength
- Bộ gốc UCI được phát hành theo CC BY 4.0; trích dẫn Yeh, I. (1998), DOI: 10.24432/C5PK67.
- Nguồn CSV đã làm sạch của nhóm: https://github.com/vkyphong/concrete-compressive-strength-analysis/blob/main/data/processed/cleaned.csv
- Bản dữ liệu kèm gói: 1.005 dòng, 17 cột; bộ gốc UCI có 1.030 dòng. Quy trình của nhóm đã loại 25 dòng trùng hoàn toàn và tạo thêm biến. Phần kiểm định dùng chín cột gốc bên dưới, giữ ngoại lai.
- SHA-256 CSV kèm gói: `220dde6aff061a71630280993add035370fd20f2f201a0ad25557a2a44d59cd9`.

| Cột | Ý nghĩa | Đơn vị |
|---|---|---|
| cement | Xi măng | kg/m³ |
| slag | Xỉ lò cao | kg/m³ |
| fly_ash | Tro bay | kg/m³ |
| water | Nước | kg/m³ |
| superplasticizer | Phụ gia siêu dẻo | kg/m³ |
| coarse_agg | Cốt liệu thô | kg/m³ |
| fine_agg | Cốt liệu mịn | kg/m³ |
| age | Tuổi mẫu | ngày |
| strength | Cường độ chịu nén | MPa |

Các biến dẫn xuất trong CSV được giữ để tương thích dự án; mã phần này tự tạo nhóm SCM từ `slag`/`fly_ash` và trạng thái dùng phụ gia từ `superplasticizer`. Không dùng nhãn `strength_level` có sẵn.

Cần phân biệt công thức giống hệt, công thức gần nhau và mã thí nghiệm: bộ dữ liệu không cung cấp mã mẻ/lô để xác nhận độc lập. Các ánh xạ phân cụm được xuất riêng, không thay thế hay xóa dòng trong CSV nguồn.

Bản CSV được đặt trong `data/hypothesis_tests/` để khi ghép vào dự án không ghi đè `data/processed/cleaned.csv` do thành viên EDA quản lý.
