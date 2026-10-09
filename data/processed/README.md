# Dữ liệu bê tông đã xử lý

`cleaned.csv` được tạo từ `data/raw/Concrete_Data.xls` bởi notebook `notebooks/01_eda.ipynb`.

## Quy mô và quy tắc làm sạch

- Dữ liệu gốc: 1.030 dòng, 9 cột.
- Xóa 25 dòng trùng hoàn toàn; dữ liệu cuối: 1.005 dòng.
- Không có NaN và không có giá trị không dương ở cement, water, coarse_agg, fine_agg, age, strength.
- Giữ số 0 ở slag, fly_ash, superplasticizer vì có nghĩa là không sử dụng.
- Không xóa/winsorize ngoại lai; giữ nguyên giá trị thí nghiệm và thêm cờ theo dòng.

## Các cột

- `cement`, `slag`, `fly_ash`, `water`, `superplasticizer`, `coarse_agg`, `fine_agg`: kg/m³.
- `age`: tuổi mẫu, ngày.
- `strength`: cường độ chịu nén, MPa.
- `log_age`: `log(1 + age)`.
- `w_c`: `water / cement`.
- `age_group`: 1–7 ngày; 8–28 ngày; >28 ngày.
- `scm_type`: không SCM; chỉ slag; chỉ fly ash; cả slag và fly ash.
- `strength_level`: thấp ≤ 23.524 MPa; trung bình (23.524, 44.868] MPa; cao > 44.868 MPa.
- `outlier_iqr_any`, `outlier_zscore_any`, `outlier_mad_any`: cờ ngoại lai ở ít nhất một biến chính theo từng phương pháp.

## Lưu ý

Modified Z-score không áp dụng riêng cho `fly_ash` vì MAD bằng 0. Các cờ ngoại lai dùng để phân tích độ nhạy, không phải nhãn lỗi dữ liệu.
