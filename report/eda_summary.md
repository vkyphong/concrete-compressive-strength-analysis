# Tóm tắt phân tích khám phá dữ liệu cường độ chịu nén bê tông

## 1. Tổng quan dữ liệu

Bộ dữ liệu Concrete Compressive Strength của UCI do Prof. I-Cheng Yeh cung cấp, gồm kết quả thí nghiệm cường độ chịu nén của bê tông theo thành phần cấp phối và tuổi mẫu. Tệp nguồn có 1.030 quan sát và 9 biến: bảy thành phần vật liệu tính theo kg/m³, tuổi mẫu tính theo ngày và cường độ chịu nén tính theo MPa. Tám biến đầu là biến giải thích định lượng; `strength` là biến mục tiêu định lượng. Dữ liệu gốc không có biến phân loại và không có giá trị thiếu.

Tuổi mẫu chỉ nhận 14 mốc: 1, 3, 7, 14, 28, 56, 90, 91, 100, 120, 180, 270, 360 và 365 ngày. Do đó, `age` là biến số rời rạc theo lịch thí nghiệm, không phải đại lượng liên tục được lấy mẫu đều. Riêng mốc 28 ngày có 419/1.005 quan sát sau làm sạch, tương đương 41,7%.

## 2. Kết quả làm sạch

| Bước | Số dòng trước | Số dòng loại | Số dòng sau | Lý do |
|---|---:|---:|---:|---|
| Nạp dữ liệu gốc | 1.030 | 0 | 1.030 | Giữ nguyên toàn bộ bản ghi khi đọc tệp nguồn. |
| Xóa dòng trùng hoàn toàn | 1.030 | 25 | 1.005 | Các dòng giống nhau ở cả 9 cột và không có mã mẫu để phân biệt. |
| Kiểm tra giá trị thiếu | 1.005 | 0 | 1.005 | Không có NaN; không cần điền khuyết hoặc loại dòng. |
| Kiểm tra giá trị không dương bất hợp lý | 1.005 | 0 | 1.005 | Không có `cement`, `water`, `coarse_agg`, `fine_agg`, `age` hoặc `strength` nhỏ hơn hay bằng 0. |
| Xác nhận số 0 hợp lệ ở vật liệu tùy chọn | 1.005 | 0 | 1.005 | Số 0 ở `slag`, `fly_ash`, `superplasticizer` có nghĩa là không sử dụng, không phải thiếu dữ liệu. |
| Xử lý ngoại lai | 1.005 | 0 | 1.005 | Không có bằng chứng lỗi nhập; giữ nguyên giá trị phòng thí nghiệm và thêm cờ theo ba phương pháp. |

Sau khử trùng, tỷ lệ bằng 0 là 46,3% với slag, 53,8% với fly ash và 37,6% với superplasticizer. Các giá trị này được giữ nguyên vì thể hiện cấu trúc cấp phối. Dữ liệu cuối có 1.005 dòng và 17 cột, gồm 9 biến gốc, 5 biến phụ trợ và 3 cờ ngoại lai.

## 3. Biến phụ trợ

- `log_age = log(1 + age)` được tạo để giảm độ lệch phải của tuổi. Skewness giảm từ 3,254 ở `age` xuống 0,006 ở `log_age`.
- `w_c = water / cement` biểu diễn tỷ lệ nước/xi măng. Trung vị là 0,690 và khoảng tứ phân vị là 0,547–0,938.
- `age_group` gồm ba nhóm: sớm (1–7 ngày), tiêu chuẩn (8–28 ngày) và dài ngày (>28 ngày). Số quan sát tương ứng là 253, 481 và 271.
- `scm_type` gồm không SCM, chỉ slag, chỉ fly ash, cả slag và fly ash. Quy mô tương ứng là 231, 310, 234 và 230 quan sát.
- `strength_level` được chia theo Q1 = 23,524 MPa và Q3 = 44,868 MPa: thấp, trung bình và cao. Số quan sát tương ứng là 252, 502 và 251.

## 4. Thống kê mô tả chính

| Biến | Count | Mean | Median | Std | Min | Q1 | Q3 | Max | Skewness |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cement` (kg/m³) | 1.005 | 278,629 | 265,000 | 104,345 | 102,000 | 190,680 | 349,000 | 540,000 | 0,565 |
| `water` (kg/m³) | 1.005 | 182,074 | 185,700 | 21,341 | 121,750 | 166,610 | 192,940 | 247,000 | 0,034 |
| `age` (ngày) | 1.005 | 45,857 | 28,000 | 63,735 | 1,000 | 7,000 | 56,000 | 365,000 | 3,254 |
| `strength` (MPa) | 1.005 | 35,250 | 33,798 | 16,285 | 2,332 | 23,524 | 44,868 | 82,599 | 0,396 |
| `w_c` | 1.005 | 0,756 | 0,690 | 0,314 | 0,267 | 0,547 | 0,938 | 1,882 | 0,940 |

Cường độ chịu nén có phân phối lệch phải nhẹ: trung bình 35,250 MPa cao hơn trung vị 33,798 MPa. Tuổi lệch phải rất mạnh do phần lớn quan sát nằm ở các mốc nhỏ và chỉ một số ít ở 180–365 ngày. Water gần đối xứng, trong khi cement và tỷ lệ nước/xi măng lệch phải ở mức vừa đến rõ.

## 5. Danh sách hình và diễn giải

| Tên file | Loại biểu đồ | Lý do chọn | Caption đề xuất | Nhận xét chính |
|---|---|---|---|---|
| `01_hist_kde_main_variables.png` | Histogram kết hợp KDE | Thể hiện đồng thời tần suất theo khoảng và hình dạng phân phối trơn. | Phân phối của cường độ, nước, xi măng và tuổi mẫu sau làm sạch. | Strength lệch phải nhẹ; water gần đối xứng; cement lệch phải vừa; age tập trung mạnh ở 28 ngày và có đuôi đến 365 ngày. |
| `02_boxplot_components.png` | Boxplot nhiều ô | So sánh trung vị, IQR và điểm vượt râu cho từng thành phần mà không để chênh lệch thang đo che khuất biến nhỏ. | Phân bố các thành phần cấp phối bê tông. | Slag, fly ash và superplasticizer có nhiều số 0. Water có 15 điểm ngoài râu IQR, superplasticizer có 10 và fine aggregate có 5. |
| `03_boxplot_strength_by_age_group.png` | Boxplot theo nhóm | So sánh vị trí và độ phân tán của strength giữa các giai đoạn dưỡng hộ. | Cường độ chịu nén theo nhóm tuổi mẫu. | Trung vị tăng từ 17,575 MPa ở 1–7 ngày lên 33,088 MPa ở 8–28 ngày và 45,368 MPa ở >28 ngày; các nhóm vẫn chồng lấp. |
| `04_boxplot_strength_by_scm_type.png` | Boxplot theo nhóm | So sánh toàn bộ phân phối strength giữa bốn cách dùng SCM. | Cường độ chịu nén theo kiểu sử dụng vật liệu bổ sung xi măng. | Trung vị cao nhất ở nhóm chỉ slag (38,554 MPa), sau đó là cả hai SCM (36,394 MPa), chỉ fly ash (31,478 MPa) và không SCM (30,571 MPa). Không diễn giải nhân quả từ so sánh thô này. |
| `05_bar_age_counts.png` | Bar chart tần suất | `age` chỉ có 14 mốc rời rạc, vì vậy cột biểu diễn chính xác quy mô từng mốc. | Số quan sát tại từng mốc tuổi mẫu. | Mốc 28 ngày có 419 quan sát; các mốc 1, 120 và 360 ngày chỉ có 2, 3 và 6 quan sát. |
| `06_bar_scm_usage.png` | Bar chart tỷ lệ | So sánh trực tiếp tỷ lệ bốn nhóm SCM. | Tỷ lệ các kiểu sử dụng SCM trong dữ liệu. | 77,0% cấp phối dùng ít nhất một SCM; nhóm chỉ slag lớn nhất với 30,8%. |
| `07_scatter_strength_relationships.png` | Scatter plot kèm đường xu hướng | Giữ từng quan sát và cho thấy chiều quan hệ, độ phân tán và khả năng phi tuyến. | Quan hệ giữa strength với water, cement, log_age và tỷ lệ nước/xi măng. | Spearman với strength là −0,284 cho water, 0,461 cho cement, 0,605 cho log_age và −0,504 cho w_c. |
| `08_heatmap_spearman.png` | Heatmap tương quan | Spearman phù hợp với biến lệch, nhiều số 0 và quan hệ đơn điệu; heatmap cho phép xem đồng thời mọi cặp biến. | Ma trận tương quan Spearman của các biến số. | Strength liên hệ mạnh nhất với age/log_age; age và log_age có tương quan thứ hạng bằng 1 nên không nên cùng xuất hiện trong mô hình tuyến tính. Cement và w_c có tương quan rất mạnh theo chiều âm (ρ = −0,96) do w_c chứa cement ở mẫu số. |
| `09_bar_outlier_comparison.png` | Bar chart nhóm | So sánh độ nhạy của ba phương pháp ngoại lai trên từng biến. | Số quan sát bị gắn cờ theo biến và phương pháp. | Modified Z-score gắn cờ 301 giá trị slag, cho thấy phương pháp này nhạy với phân phối nhiều số 0; IQR và Z-score bảo thủ hơn. |

## 6. Kết quả ngoại lai

| Biến | IQR | Z-score | Modified Z-score | Đánh giá |
|---|---:|---:|---:|---|
| `cement` | 0 | 0 | 0 | Không phát hiện ngoại lai. |
| `slag` | 2 | 4 | 301 | Giá trị cao đến 359,4 kg/m³ có thể là cấp phối thật; Modified Z-score gắn cờ nhiều do phân phối zero-inflated. |
| `fly_ash` | 0 | 0 | Không áp dụng | MAD bằng 0 vì hơn một nửa giá trị bằng 0. |
| `water` | 15 | 2 | 0 | Phạm vi 121,75–247 kg/m³ đều dương và hợp lý về logic cấp phối. |
| `superplasticizer` | 10 | 10 | 0 | Liều cao đến 32,2 kg/m³ hiếm nhưng không mâu thuẫn dữ liệu. |
| `coarse_agg` | 0 | 0 | 0 | Không phát hiện ngoại lai. |
| `fine_agg` | 5 | 0 | 0 | Mức cao đến 992,6 kg/m³ vẫn là lượng cốt liệu mịn hợp lệ. |
| `age` | 59 | 33 | 59 | Các mốc 180–365 ngày là lịch thí nghiệm chủ đích. |
| `strength` | 8 | 0 | 0 | Các giá trị 77,297–82,599 MPa phù hợp nhóm bê tông cường độ cao. |
| `w_c` | 18 | 8 | 18 | Giá trị cao 1,655–1,882 được tính từ nước và xi măng dương; cần theo dõi nhưng không phải lỗi phép chia. |

Theo mức dòng, IQR gắn cờ 110/1.005 dòng (10,9%), Z-score gắn cờ 57 dòng (5,7%) và Modified Z-score gắn cờ 347 dòng (34,5%). Có 634 dòng không bị phương pháp nào gắn cờ. Không phát hiện giá trị âm, tuổi ngoài 1–365 ngày, thành phần bắt buộc bằng 0 hoặc dấu hiệu rõ ràng của lỗi nhập. Vì vậy, phân tích giữ toàn bộ 1.005 dòng và thêm ba cờ ngoại lai để kiểm tra độ nhạy ở các bước sau; không xóa và không winsorize.

## 7. Các phát hiện chính

1. Dữ liệu có chất lượng tốt về độ đầy đủ, nhưng 25 dòng trùng hoàn toàn cần loại để không lặp trọng số trong thống kê.
2. Thiết kế thí nghiệm mất cân bằng mạnh theo tuổi: 41,7% quan sát ở 28 ngày, còn một số mốc dài ngày có rất ít mẫu. Các so sánh theo tuổi phải kèm quy mô nhóm.
3. Cường độ chịu nén trung bình là 35,250 MPa và biến thiên rộng từ 2,332 đến 82,599 MPa, cho thấy bộ dữ liệu bao phủ nhiều loại cấp phối và giai đoạn dưỡng hộ.
4. Tuổi là biến có quan hệ đơn điệu mạnh nhất với strength (ρ = 0,605). Trung vị strength tăng 27,793 MPa từ nhóm sớm lên nhóm dài ngày.
5. Tỷ lệ nước/xi măng liên hệ âm đáng kể với strength (ρ = −0,504), mạnh hơn quan hệ của water riêng lẻ (ρ = −0,284). Điều này cho thấy tỷ lệ cấp phối có ý nghĩa mô tả tốt hơn lượng nước tuyệt đối.
6. 77,0% cấp phối sử dụng ít nhất một SCM. Nhóm chỉ slag có strength trung vị cao nhất, nhưng khác biệt thô có thể bị nhiễu bởi tuổi, xi măng, nước và các thành phần khác.
7. Các phương pháp ngoại lai cho kết quả rất khác nhau trên biến zero-inflated. Ngoại lai thống kê không đồng nghĩa với lỗi nhập, đặc biệt đối với slag, tuổi dài ngày và bê tông cường độ cao.

## 8. Lưu ý cho các bước tiếp theo

- Khi chia tập huấn luyện và kiểm tra, cần tránh để các dòng có cấp phối gần giống hoặc các bản ghi lặp về công thức rơi vào hai tập theo cách gây rò rỉ thông tin.
- Nên dùng `log_age` thay cho `age` nếu mô hình giả định quan hệ gần tuyến tính; không dùng đồng thời cả hai mà không kiểm tra đa cộng tuyến.
- Cần kiểm tra cả `cement` và `w_c` trong mô hình vì hai biến có tương quan Spearman rất mạnh theo chiều âm; lựa chọn biến hoặc chuẩn hóa không tự giải quyết hoàn toàn đa cộng tuyến.
- Với slag, fly ash và superplasticizer, nên cân nhắc thêm chỉ báo có/không sử dụng bên cạnh lượng vật liệu, vì số 0 mang ý nghĩa cấu trúc.
- Nên đánh giá độ nhạy của kết quả với các dòng được gắn cờ, nhưng không loại chúng mặc định. Nếu cần loại, phải có quy tắc kỹ thuật hoặc đối chiếu nguồn thí nghiệm.
- Các so sánh strength theo `scm_type` hiện chỉ mang tính mô tả. Phân tích sau cần kiểm soát tuổi và toàn bộ cấp phối trước khi đưa ra kết luận về hiệu quả của SCM.
