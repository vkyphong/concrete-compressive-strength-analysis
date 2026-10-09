# Báo cáo phân tích tương quan giữa các biến trong dữ liệu cường độ chịu nén bê tông

**Học phần:** Phân tích và trực quan hóa dữ liệu  
**Phần việc:** Phân tích tương quan giữa các biến  
**Notebook thực hiện:** [02_correlation_analysis.ipynb](../notebooks/02_correlation_analysis.ipynb)  
**Nguồn dự án:** [concrete-compressive-strength-analysis](https://github.com/vkyphong/concrete-compressive-strength-analysis)

## 1. Mục tiêu và phạm vi

Phân tích nhằm xác định chiều và mức độ liên hệ giữa các thành phần cấp phối, tuổi mẫu và cường độ chịu nén bê tông. Ba câu hỏi chính gồm:

1. Những biến đầu vào nào có tương quan lớn với cường độ chịu nén?
2. Các biến đầu vào tương quan với nhau như thế nào?
3. Kết quả thay đổi ra sao khi xét tuổi mẫu, biến dẫn xuất và các cờ ngoại lai?

Báo cáo tiếp nối phần EDA của nhóm, sử dụng đúng dữ liệu đã làm sạch. Kết quả mang tính mô tả và thăm dò, không phải mô hình dự đoán hoặc bằng chứng nhân quả.

## 2. Dữ liệu sử dụng

Dữ liệu được đọc từ `data/processed/cleaned.csv` tại commit `cd7509dc0d1734cf8c9382b5127c4bfbcd769e44`. Theo quy trình trong `01_eda.ipynb`, dữ liệu gốc có 1.030 dòng; sau khi loại 25 dòng trùng hoàn toàn, còn **1.005 quan sát**. Không có giá trị thiếu trong 9 biến gốc. Nhóm giữ các giá trị ngoại lai và bổ sung cờ để kiểm tra độ nhạy.

| Biến | Ý nghĩa | Đơn vị | Vai trò |
| --- | --- | --- | --- |
| `cement` | Xi măng | kg/m³ | Đầu vào |
| `slag` | Xỉ lò cao nghiền mịn | kg/m³ | Đầu vào |
| `fly_ash` | Tro bay | kg/m³ | Đầu vào |
| `water` | Nước trộn | kg/m³ | Đầu vào |
| `superplasticizer` | Phụ gia siêu dẻo | kg/m³ | Đầu vào |
| `coarse_agg` | Cốt liệu thô | kg/m³ | Đầu vào |
| `fine_agg` | Cốt liệu mịn | kg/m³ | Đầu vào |
| `age` | Tuổi mẫu khi thử nén | ngày | Đầu vào |
| `strength` | Cường độ chịu nén | MPa | Mục tiêu |

Các giá trị 0 ở `slag`, `fly_ash` và `superplasticizer` biểu thị không sử dụng vật liệu, không phải dữ liệu thiếu. Tuổi mẫu chỉ có 14 mốc và phân bố không đều; riêng 28 ngày có 419 mẫu, chiếm 41,7%.

Ma trận chính sử dụng 9 biến gốc. Hai biến dẫn xuất `log_age = log(1 + age)` và `w_c = water / cement` được phân tích riêng. Không đưa các biến phân nhóm hoặc cờ ngoại lai vào ma trận chính. Đặc biệt, `strength_level` được tạo từ `strength`, nên không được xem là một biến giải thích độc lập.

## 3. Phương pháp phân tích

### 3.1. Pearson và Spearman

**Pearson (r)** đo mức độ liên hệ tuyến tính trên các giá trị gốc. **Spearman (ρ)** đo liên hệ đơn điệu thông qua thứ hạng; các giá trị bằng nhau được gán hạng trung bình. Cả hai hệ số nằm trong đoạn [−1, 1]. Dấu của hệ số biểu thị chiều liên hệ; trị tuyệt đối biểu thị độ mạnh theo thước đo đang dùng.

Báo cáo sử dụng đồng thời hai phương pháp vì tuổi mẫu lệch phải, một số vật liệu có nhiều số 0 và quan hệ với cường độ có thể không tuyến tính. Spearman giảm ảnh hưởng của độ lớn cực trị, nhưng không tự giải quyết mọi vấn đề về ngoại lai hay các giá trị đồng hạng. Không cần chuẩn hóa đơn vị trước khi tính tương quan.

Không áp dụng cứng một ngưỡng để kết luận “mạnh” hoặc “yếu”. Hệ số gần 0 không loại trừ quan hệ phi tuyến hoặc tương tác; hệ số lớn không chứng minh nhân quả.

### 3.2. Kiểm định và trực quan hóa

Notebook thực hiện kiểm định hai phía với giả thuyết hệ số tương quan bằng 0 và hiệu chỉnh Benjamini–Hochberg (BH) riêng cho 8 kiểm định Pearson và 8 kiểm định Spearman với mục tiêu. P-value Spearman được tính theo xấp xỉ của SciPy.

Các kiểm định chỉ mang tính tham khảo: nhiều mẫu có thể thuộc cùng công thức cấp phối được thử ở các tuổi khác nhau, nên giả định độc lập giữa các dòng chưa được đảm bảo. Báo cáo ưu tiên độ lớn hệ số, biểu đồ phân tán và kiểm tra độ nhạy.

Heatmap dùng để quan sát toàn bộ ma trận; biểu đồ thanh so sánh Pearson–Spearman; scatter plot kiểm tra hình dạng và độ phân tán. Các đường hồi quy tuyến tính trên scatter plot chỉ hỗ trợ mô tả xu hướng.

## 4. Kết quả phân tích

### 4.1. Tương quan với cường độ chịu nén

Bảng được sắp theo trị tuyệt đối của Spearman giảm dần. Các số được làm tròn đến ba chữ số thập phân; dấu chấm là dấu thập phân.

| Biến | Pearson r | Spearman ρ |
| --- | --- | --- |
| age | 0.337 | 0.605 |
| cement | 0.488 | 0.461 |
| superplasticizer | 0.344 | 0.322 |
| water | -0.270 | -0.284 |
| fine_agg | -0.186 | -0.193 |
| coarse_agg | -0.145 | -0.163 |
| slag | 0.103 | 0.139 |
| fly_ash | -0.081 | -0.056 |

**Tuổi mẫu:** `age` có Spearman cao nhất trong 8 đầu vào gốc (ρ = 0.605), trong khi Pearson chỉ đạt 0.337. Điều này cho thấy liên hệ theo thứ hạng rõ hơn liên hệ tuyến tính trên tuổi gốc. Biểu đồ cho thấy tuổi phân bố rời rạc và độ phân tán cường độ lớn tại cùng một mốc tuổi.

**Xi măng:** `cement` có Pearson cao nhất trong các đầu vào gốc (r = 0.488), đồng thời Spearman dương (ρ = 0.461). Trong dữ liệu quan sát, lượng xi măng lớn hơn có xu hướng đi cùng cường độ cao hơn, nhưng chưa giữ cố định nước, tuổi và các thành phần khác.

**Phụ gia siêu dẻo và nước:** `superplasticizer` liên hệ dương với cường độ (ρ = 0.322), còn `water` liên hệ âm (ρ = −0.284). Đây là tương quan biên trên toàn mẫu, chưa thể diễn giải thành hiệu quả riêng của từng vật liệu.

**Cốt liệu, xỉ và tro bay:** hai loại cốt liệu có tương quan âm với cường độ; xỉ có hệ số dương nhỏ; tro bay có hệ số âm gần 0. Không thể từ đó kết luận xỉ hoặc tro bay không ảnh hưởng đến cường độ, vì quan hệ có thể phụ thuộc tuổi và sự phối hợp các vật liệu.

Sau hiệu chỉnh BH, cả 8 kiểm định Pearson có p < 0.05; với Spearman, `fly_ash` có p hiệu chỉnh khoảng 0.074 và không đạt ngưỡng này. Sự khác biệt nhấn mạnh rằng ý nghĩa thống kê phụ thuộc thước đo, không thay thế đánh giá độ lớn quan hệ. Không bác bỏ giả thuyết hệ số bằng 0 cũng không chứng minh hai biến hoàn toàn không liên hệ.

Hệ số 0.605 **không có nghĩa tuổi giải thích 60,5% cường độ**. Bình phương Spearman cũng không phải R² của hồi quy tuyến tính trên dữ liệu gốc.

### 4.2. Quan hệ của các biến dẫn xuất

| Biến | Pearson với strength | Spearman với strength |
| --- | --- | --- |
| age | 0.337 | 0.605 |
| log_age | 0.560 | 0.605 |
| water | -0.270 | -0.284 |
| cement | 0.488 | 0.461 |
| w_c | -0.489 | -0.504 |

Khi dùng `log_age` thay cho `age`, Pearson với cường độ tăng từ 0.337 lên 0.560. Phép biến đổi này giúp liên hệ gần tuyến tính hơn trong dữ liệu đang xét. Spearman giữ nguyên 0.605 vì hàm log tăng nghiêm ngặt và không thay đổi thứ hạng của tuổi.

Tỷ lệ nước/xi măng (`w_c`) có Spearman −0.504 với cường độ, lớn hơn về trị tuyệt đối so với nước riêng lẻ (−0.284). Như vậy, tỷ lệ này mô tả liên hệ với cường độ rõ hơn lượng nước tuyệt đối theo thước đo Spearman.

Tuy nhiên, Spearman giữa `cement` và `w_c` xấp xỉ −0.957, một phần do xi măng nằm ở mẫu số của tỷ lệ. Không xem các biến này là các nguồn bằng chứng độc lập. Tương tự, Spearman bằng 1 giữa `age` và `log_age` phản ánh trùng thứ hạng, không có nghĩa chúng là tổ hợp tuyến tính chính xác của nhau.

### 4.3. Tương quan giữa các biến đầu vào

Trong 28 cặp đầu vào khác nhau, năm cặp có |Spearman| lớn nhất là:

| Biến 1 | Biến 2 | Pearson r | Spearman ρ |
| --- | --- | --- | --- |
| water | superplasticizer | -0.647 | -0.672 |
| fly_ash | superplasticizer | 0.414 | 0.502 |
| cement | fly_ash | -0.386 | -0.407 |
| slag | coarse_agg | -0.278 | -0.341 |
| water | fine_agg | -0.445 | -0.338 |

Cặp `water`–`superplasticizer` nổi bật với r = −0.647 và ρ = −0.672. Kết quả phù hợp với giả thuyết các cấp phối dùng nhiều phụ gia siêu dẻo có thể sử dụng ít nước hơn, nhưng tương quan không đủ để xác nhận cơ chế này.

Tro bay có tương quan dương với phụ gia siêu dẻo và âm với xi măng. Các mối liên hệ có thể phản ánh những cách lựa chọn hoặc thay thế vật liệu trong cấp phối. Vì các thành phần không biến đổi độc lập, cần thận trọng khi diễn giải từng hệ số với cường độ.

Tương quan cặp là bước sàng lọc sự phụ thuộc giữa các đầu vào. Hệ số cặp nhỏ không đảm bảo không có đa cộng tuyến giữa nhiều biến; hệ số lớn cũng không tự động là lý do loại biến khỏi mô hình.

## 5. Phân tích theo tuổi mẫu

### 5.1. So sánh toàn mẫu với nhóm 28 ngày

Nhóm 28 ngày có 419 quan sát. Vì tuổi không đổi trong nhóm này, chỉ tính tương quan của các vật liệu với cường độ.

| Biến | Spearman toàn mẫu | Spearman ở 28 ngày |
| --- | --- | --- |
| cement | 0.461 | 0.647 |
| slag | 0.139 | 0.154 |
| fly_ash | -0.056 | -0.223 |
| water | -0.284 | -0.350 |
| superplasticizer | 0.322 | 0.184 |
| coarse_agg | -0.163 | -0.143 |
| fine_agg | -0.193 | -0.188 |

Ba thay đổi đáng chú ý gồm:

- `cement`: Spearman tăng từ 0.461 lên 0.647.
- `fly_ash`: hệ số chuyển từ −0.056 xuống −0.223.
- `superplasticizer`: hệ số giảm từ 0.322 xuống 0.184.

Các kết quả cho thấy tương quan toàn mẫu có thể che khuất khác biệt khi xét cùng tuổi. Tuy nhiên, việc giới hạn ở 28 ngày đồng thời thay đổi tập cấp phối quan sát; không được diễn giải chênh lệch hệ số như tác động thuần túy của việc kiểm soát tuổi.

### 5.2. Tương quan Pearson riêng phần theo log tuổi

Để bổ sung phân tích phân tầng, hồi quy từng biến vật liệu lên hằng số và `log_age`, làm tương tự với `strength`, rồi tính Pearson giữa hai phần dư.

| Biến | Pearson biên | Pearson riêng phần theo log_age |
| --- | --- | --- |
| cement | 0.488 | 0.585 |
| slag | 0.103 | 0.138 |
| fly_ash | -0.081 | -0.082 |
| water | -0.270 | -0.448 |
| superplasticizer | 0.344 | 0.447 |
| coarse_agg | -0.145 | -0.146 |
| fine_agg | -0.186 | -0.148 |

Sau điều chỉnh tuyến tính theo log tuổi, Pearson của xi măng với cường độ tăng từ 0.488 lên 0.585. Hệ số của nước âm rõ hơn, từ −0.270 xuống −0.448; hệ số của phụ gia siêu dẻo tăng từ 0.344 lên 0.447.

Đây chỉ là điều chỉnh tuyến tính theo `log_age`. Phương pháp chưa kiểm soát toàn bộ cấp phối, không loại bỏ mọi nhiễu và không biến kết quả thành quan hệ nhân quả. Phân tích riêng phần trên toàn mẫu và phân tích nhóm 28 ngày trả lời các câu hỏi khác nhau, nên không nhất thiết cho cùng chiều thay đổi hệ số.

## 6. Kiểm tra độ nhạy với ngoại lai

Kết quả chính giữ toàn bộ 1.005 quan sát theo quyết định làm sạch của nhóm. Ba kịch bản bổ sung chỉ loại tạm thời các dòng có cờ để so sánh:

| Kịch bản | Số mẫu còn lại | Số mẫu bị loại trong kịch bản |
| --- | --- | --- |
| Toàn mẫu | 1.005 | 0 |
| Bỏ cờ IQR | 895 | 110 |
| Bỏ cờ Z-score | 948 | 57 |
| Bỏ cờ Modified Z-score/MAD | 658 | 347 |

Hệ số Spearman với cường độ trong từng kịch bản:

| Biến | Toàn mẫu | Bỏ cờ IQR | Bỏ cờ Z-score | Bỏ cờ MAD |
| --- | --- | --- | --- | --- |
| cement | 0.461 | 0.412 | 0.436 | 0.439 |
| slag | 0.139 | 0.169 | 0.161 | 0.291 |
| fly_ash | -0.056 | -0.007 | -0.034 | -0.042 |
| water | -0.284 | -0.330 | -0.312 | -0.355 |
| superplasticizer | 0.322 | 0.349 | 0.342 | 0.337 |
| coarse_agg | -0.163 | -0.165 | -0.158 | -0.167 |
| fine_agg | -0.193 | -0.161 | -0.181 | -0.146 |
| age | 0.605 | 0.614 | 0.608 | 0.603 |
| w_c | -0.504 | -0.477 | -0.492 | -0.515 |

Chiều của các hệ số trong bảng được giữ qua ba kịch bản. Tuổi luôn có Spearman khoảng 0.60–0.61 và tỷ lệ nước/xi măng luôn liên hệ âm, khoảng −0.48 đến −0.51. Tuy nhiên, không phải mọi độ lớn đều ổn định: hệ số của `slag` tăng từ 0.139 lên 0.291 khi bỏ cờ MAD, chênh khoảng 0.152.

Cờ ngoại lai được tạo từ nhiều biến, có cả `strength`. Loại các dòng này có thể gây thiên lệch chọn mẫu và làm mất các tuổi dài ngày hoặc cấp phối hiếm. Đặc biệt, phương pháp MAD nhạy với cấu trúc nhiều số 0; trong bước EDA, nhóm không áp dụng Modified Z-score riêng cho tro bay vì MAD bằng 0. Do đó, các kịch bản trên không phải căn cứ để khuyến nghị xóa toàn bộ ngoại lai.

## 7. Các hình trực quan đi kèm

Bảy hình được lưu trực tiếp trong [notebook phân tích](../notebooks/02_correlation_analysis.ipynb), có thể xem cùng mã và kết quả:

| Hình | Nội dung | Mục đích |
| --- | --- | --- |
| 1 | Hai heatmap Pearson và Spearman của 9 biến gốc | So sánh cấu trúc tương quan và khác biệt giữa hai thước đo |
| 2 | Biểu đồ thanh tương quan với `strength` | Xếp hạng và so sánh chiều, độ lớn hệ số |
| 3 | Scatter plot của 8 đầu vào với cường độ | Quan sát độ phân tán, cụm số 0 và khả năng phi tuyến |
| 4 | Scatter plot cho `age`, `log_age`, `w_c` | Minh họa biến đổi log và tỷ lệ nước/xi măng |
| 5 | Scatter plot của 3 cặp đầu vào nổi bật | Xem hình dạng liên hệ giữa các thành phần |
| 6 | Tương quan toàn mẫu so với nhóm 28 ngày | Minh họa sự thay đổi khi phân tầng theo tuổi |
| 7 | Heatmap độ nhạy theo các cờ ngoại lai | Kiểm tra sự ổn định của hệ số khi thay đổi tập mẫu |

Báo cáo Markdown dùng bảng để giữ đầy đủ số liệu ngay cả khi đọc độc lập. Muốn xuất hình PNG và bảng CSV từ notebook, đặt `EXPORT = True` ở ô thiết lập rồi chạy toàn bộ; kết quả được lưu vào thư mục `correlation_outputs` trong thư mục làm việc.

## 8. Kết luận và đề xuất

Phân tích cho thấy **tuổi mẫu có liên hệ đơn điệu lớn nhất với cường độ trong các đầu vào gốc**, trong khi **xi măng có liên hệ tuyến tính lớn nhất**. Quan hệ tuổi–cường độ được mô tả tuyến tính rõ hơn khi dùng log tuổi. Tỷ lệ nước/xi măng liên hệ âm với cường độ và có |Spearman| lớn hơn nước riêng lẻ.

Các vật liệu cũng tương quan với nhau, nổi bật là quan hệ âm giữa nước và phụ gia siêu dẻo. Kết quả thay đổi khi xét riêng tuổi 28 ngày, điều chỉnh log tuổi hoặc lọc cờ ngoại lai. Vì vậy, không thể xem hệ số biên là tác động riêng của từng vật liệu hoặc chọn biến chỉ dựa trên p-value.

Đối với phần mô hình hóa tiếp theo, nhóm nên:

1. Cân nhắc `log_age`, đồng thời kiểm tra đa cộng tuyến trên tập biến thực sự đưa vào mô hình; tránh coi `age` và `log_age` là hai nguồn thông tin độc lập.
2. Kiểm tra thêm quan hệ phi tuyến và tương tác giữa tuổi với các vật liệu bổ sung xi măng.
3. Giữ nguyên dữ liệu ngoại lai khi chưa có bằng chứng lỗi; sử dụng phân tích độ nhạy để đánh giá ảnh hưởng của các quan sát hiếm.
4. Khi chia dữ liệu huấn luyện và kiểm tra, xem xét các dòng cùng hoặc gần giống cấp phối xuất hiện ở nhiều tuổi để hạn chế đánh giá quá lạc quan.

**Giới hạn:** Dữ liệu mất cân bằng theo tuổi, chưa có mã thí nghiệm độc lập và có thể chứa các phép đo liên quan với nhau. Các mối liên hệ tìm được chỉ phản ánh tập dữ liệu hiện có. Tương quan không chứng minh nhân quả; hệ số nhỏ không loại trừ quan hệ phi tuyến hoặc tác động phụ thuộc bối cảnh cấp phối.

## 9. Nguồn và khả năng tái lập

- [Repo tại commit được phân tích](https://github.com/vkyphong/concrete-compressive-strength-analysis/tree/cd7509dc0d1734cf8c9382b5127c4bfbcd769e44).
- [Dữ liệu làm sạch](../data/processed/cleaned.csv) và [mô tả quy trình làm sạch](../data/processed/README.md).
- [Báo cáo EDA của nhóm](eda_summary.md), [từ điển dữ liệu](../tables/data_dictionary.csv) và [bảng Spearman gốc](../tables/spearman_correlation.csv).
- [Notebook thực hiện phân tích tương quan](../notebooks/02_correlation_analysis.ipynb). Ma trận Spearman của 9 biến gốc đã được đối chiếu và khớp bảng EDA của nhóm.
- Nguồn dữ liệu gốc theo `Concrete_Readme.txt`: Prof. I-Cheng Yeh. Yeh, I.-C. (1998). *Modeling of strength of high performance concrete using artificial neural networks*. Cement and Concrete Research, 28(12), 1797–1808. Giữ ghi nhận tác giả và công trình này khi tái sử dụng dữ liệu.

SHA-256 của CSV dùng trong báo cáo: `220dde6aff061a71630280993add035370fd20f2f201a0ad25557a2a44d59cd9`.

Các số liệu trong báo cáo được tính từ đúng snapshot trên. Nếu nhóm thay đổi dữ liệu, cần chạy lại notebook và cập nhật cả bảng lẫn nhận xét. Các liên kết tương đối hoạt động khi đặt file báo cáo này trong thư mục `report/` của repo.
