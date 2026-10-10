# Hồi quy tuyến tính đa biến dự đoán cường độ chịu nén bê tông

## 1. Mục tiêu và dữ liệu

Phân tích sử dụng 1.005 quan sát trong bộ UCI Concrete Compressive Strength đã được làm sạch. Mục tiêu là dự đoán cường độ chịu nén `strength` (MPa) từ thành phần cấp phối và tuổi bê tông. Dữ liệu được chia ngẫu nhiên thành 804 quan sát train (80%) và 201 quan sát test (20%) với `random_state = 42`. Biến `strength_level` không được sử dụng vì được tạo trực tiếp từ biến mục tiêu và sẽ gây rò rỉ dữ liệu.

## 2. Tóm tắt lý thuyết

Hồi quy tuyến tính đa biến có dạng:

$$
y = \beta_0 + \beta_1x_1 + \cdots + \beta_kx_k + \varepsilon.
$$

Hệ số $\beta_j$ biểu diễn mức thay đổi trung bình của biến mục tiêu khi $x_j$ tăng một đơn vị và các biến còn lại được giữ cố định. Phương pháp bình phương tối thiểu OLS chọn các hệ số sao cho tổng bình phương phần dư là nhỏ nhất. Chất lượng mô hình được đánh giá bằng $R^2$, Adjusted $R^2$, RMSE và MAE; ý nghĩa thống kê của từng hệ số được xem xét qua p-value.

Các giả định chính gồm quan hệ gần tuyến tính, phần dư gần phân phối chuẩn, phương sai phần dư không đổi và không có đa cộng tuyến nghiêm trọng. Phân tích sử dụng đồ thị Residuals vs Fitted, Q-Q plot, histogram, kiểm định Jarque–Bera, kiểm định Breusch–Pagan và VIF để kiểm tra các giả định này.

### Ví dụ minh họa bằng dữ liệu thật

Hồi quy mô tả `strength` theo `water` và `cement` trên toàn bộ dữ liệu cho phương trình:

$$
\widehat{strength}=48{,}343-0{,}185\,water+0{,}074\,cement.
$$

Khi giữ lượng xi măng không đổi, tăng 1 kg/m³ nước liên hệ với mức giảm trung bình khoảng 0,185 MPa. Khi giữ lượng nước không đổi, tăng 1 kg/m³ xi măng liên hệ với mức tăng trung bình khoảng 0,074 MPa. Hai hệ số đều có p-value rất nhỏ, nhưng $R^2 = 0{,}297$, cho thấy hai biến này chưa đủ để mô tả đầy đủ cường độ.

## 3. Xây dựng và lựa chọn mô hình

Mô hình 1 sử dụng 7 thành phần cấp phối gồm `cement`, `slag`, `fly_ash`, `water`, `superplasticizer`, `coarse_agg`, `fine_agg` cùng với tuổi thật `age`. Mô hình 2 thay `age` bằng `log_age = ln(age + 1)` để mô tả quá trình tăng cường độ nhanh ở tuổi sớm và chậm dần về sau.

Ở bước đầu của mô hình 2, `w_c = water/cement` được thêm vào đúng theo giả thuyết vật liệu. Tuy nhiên, `cement` có VIF 11,98 và tương quan giữa `cement` với `w_c` bằng -0,878. Do `w_c` chứa lại thông tin của `cement`, phân tích loại `w_c` và giữ `cement` để hệ số nguyên liệu dễ diễn giải. Sau khi loại `w_c`, VIF lớn nhất còn 7,19, dưới ngưỡng 10. Việc bỏ `w_c` chỉ làm $R^2$ test của mô hình ứng viên giảm nhẹ từ khoảng 0,803 xuống 0,800.

### So sánh hai mô hình

| Mô hình | Tập | R² | Adjusted R² | RMSE (MPa) | MAE (MPa) |
|---|---:|---:|---:|---:|---:|
| Mô hình 1: `age` | Train | 0,6098 | 0,6059 | 10,0025 | 7,9606 |
| Mô hình 1: `age` | Test | 0,5801 | 0,5626 | 11,1922 | 8,8960 |
| Mô hình 2: `log_age` | Train | 0,8105 | 0,8086 | 6,9701 | 5,3401 |
| Mô hình 2: `log_age` | Test | 0,8001 | 0,7918 | 7,7215 | 5,8796 |

Mô hình 2 được chọn làm mô hình cuối vì tốt hơn rõ rệt trên tập test: $R^2$ tăng từ 0,5801 lên 0,8001, trong khi RMSE giảm từ 11,1922 MPa xuống 7,7215 MPa. Chênh lệch nhỏ giữa kết quả train và test chưa cho thấy overfitting lớn theo cách chia dữ liệu này.

## 4. Bảng hệ số mô hình cuối

| Biến | Hệ số | Sai số chuẩn | p-value | Khoảng tin cậy 95% |
|---|---:|---:|---:|---:|
| Hệ số chặn | -74,1061 | 20,1951 | 0,000259 | [-113,7481; -34,4642] |
| `cement` | 0,1303 | 0,0064 | < 0,001 | [0,1178; 0,1428] |
| `slag` | 0,1100 | 0,0077 | < 0,001 | [0,0949; 0,1252] |
| `fly_ash` | 0,0924 | 0,0094 | < 0,001 | [0,0739; 0,1109] |
| `water` | -0,1227 | 0,0303 | < 0,001 | [-0,1821; -0,0633] |
| `superplasticizer` | 0,1286 | 0,0713 | 0,0716 | [-0,0113; 0,2684] |
| `coarse_agg` | 0,0265 | 0,0072 | < 0,001 | [0,0125; 0,0406] |
| `fine_agg` | 0,0336 | 0,0081 | < 0,001 | [0,0176; 0,0495] |
| `log_age` | 9,1039 | 0,2330 | < 0,001 | [8,6467; 9,5611] |

Ở mức ý nghĩa 5%, tất cả biến đầu vào trừ `superplasticizer` có ý nghĩa thống kê. Hệ số chặn âm chỉ là tham số giúp định vị mặt phẳng hồi quy; trường hợp mọi thành phần bằng 0 không phải một cấp phối có ý nghĩa thực tế nên không diễn giải hệ số này theo vật liệu.

## 5. Diễn giải hệ số

- Khi giữ các biến khác cố định, tăng 1 kg/m³ xi măng liên hệ với mức tăng khoảng 0,130 MPa. `cement` cũng có hệ số chuẩn hóa lớn nhất về trị tuyệt đối, khoảng 0,846.
- Tăng 1 kg/m³ xỉ lò cao liên hệ với mức tăng khoảng 0,110 MPa; tăng 1 kg/m³ tro bay liên hệ với mức tăng khoảng 0,092 MPa. Dấu dương phù hợp với đóng góp của các vật liệu kết dính bổ sung trong phạm vi dữ liệu.
- Tăng 1 kg/m³ nước liên hệ với mức giảm khoảng 0,123 MPa. Kết quả phù hợp với kiến thức vật liệu vì lượng nước cao, khi các yếu tố khác được giữ cố định, có thể làm tăng độ rỗng của bê tông sau đóng rắn.
- Tăng 1 kg/m³ phụ gia siêu dẻo liên hệ với mức tăng khoảng 0,129 MPa, nhưng p-value 0,0716 nên chưa đủ bằng chứng kết luận hệ số khác 0 ở mức ý nghĩa 5%.
- Tăng 1 kg/m³ cốt liệu thô và cốt liệu mịn lần lượt liên hệ với mức tăng khoảng 0,027 MPa và 0,034 MPa. Các hệ số nhỏ theo đơn vị 1 kg/m³ nhưng đều có ý nghĩa thống kê.
- Tăng một đơn vị `log_age = ln(age + 1)` liên hệ với mức tăng khoảng 9,104 MPa. Cách biến đổi log phù hợp với hiện tượng cường độ tăng nhanh lúc đầu rồi tốc độ tăng giảm dần.

Các diễn giải trên là liên hệ có điều kiện trong mô hình, không phải bằng chứng nhân quả. Việc so sánh trực tiếp độ lớn hệ số gốc giữa `log_age` và các biến kg/m³ cũng không phù hợp vì đơn vị và thang đo khác nhau.

## 6. Chẩn đoán giả định

Kiểm định Jarque–Bera cho thống kê 20,620 và p-value $3,33\times10^{-5}$, nên phần dư không hoàn toàn tuân theo phân phối chuẩn. Kiểm định Breusch–Pagan cho thống kê LM 77,157 và p-value $1,82\times10^{-13}$, cho thấy phương sai phần dư không đồng nhất. Chỉ số Durbin–Watson bằng 1,91, chưa gợi ý tự tương quan bậc một rõ rệt. Tất cả VIF của mô hình cuối đều dưới 10, vì vậy không còn đa cộng tuyến nghiêm trọng theo ngưỡng đã chọn.

## 7. Danh sách hình

1. **`residuals_vs_fitted.png` — Phần dư theo giá trị dự đoán.** Phần dư tập trung quanh đường 0 nhưng độ phân tán tăng ở vùng cường độ dự đoán cao. Hình này, cùng kết quả Breusch–Pagan, cho thấy giả định phương sai không đổi bị vi phạm.

2. **`residuals_qq.png` — Q-Q plot của phần dư.** Phần lớn quan sát ở trung tâm bám tương đối gần đường chuẩn, nhưng hai đuôi lệch khỏi đường chéo, đặc biệt ở đuôi phải. Nhận xét này phù hợp với p-value nhỏ của kiểm định Jarque–Bera.

3. **`residuals_histogram.png` — Histogram và đường mật độ của phần dư.** Phần dư có tâm gần 0 nhưng hơi lệch phải và có đuôi dày hơn phân phối chuẩn. Vì vậy không nên khẳng định giả định chuẩn được thỏa mãn hoàn toàn.

4. **`predicted_vs_actual.png` — Cường độ dự đoán so với thực tế trên tập test.** Phần lớn điểm đi theo đường $y=x$, phù hợp với $R^2$ test bằng 0,8001. Tuy nhiên, mô hình có xu hướng dự đoán thấp ở một số mẫu cường độ cao và vẫn tồn tại một số sai số lớn.

5. **`final_model_coefficients.png` — Hệ số OLS của mô hình cuối.** `log_age` có hệ số gốc lớn nhất do một đơn vị logarit khác hoàn toàn một đơn vị kg/m³. Các hệ số vật liệu kết dính mang dấu dương, còn hệ số nước mang dấu âm; biểu đồ này không được dùng để so sánh tầm quan trọng nếu chưa chuẩn hóa thang đo.

## 8. Giới hạn

- Mô hình chỉ mô tả quan hệ tuyến tính theo các biến đã chọn; tương tác và các dạng phi tuyến khác chưa được xét.
- Dữ liệu chỉ đến từ một bộ thí nghiệm/lab, nên khả năng khái quát sang nguồn vật liệu, điều kiện dưỡng hộ hoặc phòng thí nghiệm khác còn hạn chế.
- Một số dòng có thể thuộc cùng một mẻ trộn và chỉ khác tuổi thử. Chia ngẫu nhiên theo dòng có thể đưa các quan sát liên quan vào cả train và test, làm hai tập không hoàn toàn độc lập.
- Phần dư không hoàn toàn chuẩn và có phương sai thay đổi. Do đó, p-value, khoảng tin cậy và dự đoán ở vùng cường độ cực trị cần được diễn giải thận trọng.
- Không nên ngoại suy cho các cấp phối nằm ngoài phạm vi của bộ dữ liệu và không nên xem hệ số hồi quy quan sát là tác động nhân quả.

## 9. Kết luận

Việc thay `age` bằng `log_age` giúp mô hình tuyến tính mô tả tốt hơn quá trình phát triển cường độ theo tuổi. Mô hình cuối đạt $R^2$ test 0,8001, Adjusted $R^2$ test 0,7918, RMSE 7,7215 MPa và MAE 5,8796 MPa. `cement` là biến có hệ số chuẩn hóa lớn nhất về trị tuyệt đối; `superplasticizer` là biến duy nhất chưa có ý nghĩa thống kê ở mức 5%. Mặc dù khả năng dự đoán được cải thiện rõ so với baseline, các vi phạm về phân phối chuẩn và phương sai không đổi của phần dư cần được nêu rõ khi báo cáo kết quả.
