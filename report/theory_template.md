## 3.1. Cơ sở lý thuyết

### 3.1.1. Quy trình chung

Một phép kiểm định gồm: câu hỏi → đơn vị phân tích → giả thuyết H₀/H₁ → điều kiện áp dụng → thống kê kiểm định và p-value → độ lớn chênh lệch và kết luận. Chọn mức ý nghĩa **α = 0,05**. Nếu p < α, bác bỏ H₀; nếu p ≥ α, chưa đủ bằng chứng bác bỏ H₀. P-value phản ánh mức độ bất tương thích với H₀ trong mô hình kiểm định, còn ý nghĩa thực tiễn được đọc qua MPa và khoảng tin cậy.

**Khoảng tin cậy 95% (CI)** thể hiện độ bất định của ước lượng theo phương pháp lấy mẫu. **SD** mô tả mức phân tán giữa các quan sát. **Kích thước hiệu ứng** mô tả độ lớn khác biệt; không thể thay thế nó bằng một p-value nhỏ.

### 3.1.2. t-test: so sánh hai trung bình

**Hai mẫu độc lập — Welch t-test.** Dùng khi mỗi quan sát chỉ thuộc một trong hai nhóm và các đơn vị quan sát độc lập. Ký hiệu $\bar x_j$, $s_j$, $n_j$ lần lượt là trung bình, độ lệch chuẩn và số quan sát nhóm j:

$$t=\frac{\bar x_1-\bar x_2}{\sqrt{s_1^2/n_1+s_2^2/n_2}},\qquad
\nu=\frac{(s_1^2/n_1+s_2^2/n_2)^2}{(s_1^2/n_1)^2/(n_1-1)+(s_2^2/n_2)^2/(n_2-1)}.$$

Giả thuyết hai phía: $H_0:\mu_1=\mu_2$ và $H_1:\mu_1\ne\mu_2$. Welch cho phép phương sai và số quan sát hai nhóm khác nhau. Với mẫu nhỏ, cần xem hình dạng phân phối và ngoại lai.

**Ví dụ giả lập:** hai nhóm độc lập đều có n = 20; trung bình 32 và 36 MPa, SD là 5 và 6 MPa. Khi đó $t=(32-36)/\sqrt{25/20+36/20}\approx-2,29$. Ví dụ chỉ minh họa công thức; đây không phải số liệu của dự án.

**Hai mẫu ghép — paired t-test.** Dùng khi có quy tắc ghép cặp hợp lý. Đặt $d_i=x_{i,28}-x_{i,7}$:

$$t=\frac{\bar d}{s_d/\sqrt n},\quad df=n-1,\qquad
CI_{95\%}=\bar d\pm t_{0,975;n-1}\frac{s_d}{\sqrt n}.$$

Các cặp cần đủ độc lập với nhau. Điều kiện phân phối được xét trên **chênh lệch d**, vì kiểm định thực chất là t-test một mẫu trên d. Cohen’s $d_z=\bar d/s_d$ chuẩn hóa chênh lệch theo độ lệch chuẩn của d.

**Ví dụ giả lập:** năm chênh lệch [2, 3, 4, 5, 6] có $\bar d=4$, $s_d=\sqrt{2,5}$, nên $t=5,657$ với 4 bậc tự do. Trong bài, ghép theo thành phần cấp phối và đo cường độ của các mẫu ở hai tuổi; không cần coi đó là cùng một mẫu vật được nén hai lần.

### 3.1.3. Chi-square: liên hệ giữa hai biến phân loại

$H_0$: hai biến phân loại độc lập; $H_1$: chúng có liên hệ. Với bảng r hàng, c cột và tổng N:

$$E_{ij}=\frac{n_{i\cdot}n_{\cdot j}}{N},\qquad
\chi^2=\sum_{i=1}^{r}\sum_{j=1}^{c}\frac{(O_{ij}-E_{ij})^2}{E_{ij}},\qquad df=(r-1)(c-1).$$

$O_{ij}$ là số đếm quan sát; $E_{ij}$ là số đếm kỳ vọng nếu H₀ đúng. Mỗi đơn vị chỉ đóng góp vào một ô, các đơn vị độc lập, và tần số kỳ vọng phải đủ lớn. Ở phần minh họa của bài, mọi tần số kỳ vọng đều ít nhất bằng 5. Hệ số Cramér’s $V=\sqrt{\chi^2/[N\min(r-1,c-1)]}$ mô tả độ lớn liên hệ.

**Ví dụ giả lập:** hai nhóm A/B có số lượng đạt/không đạt lần lượt [30, 20] và [20, 30]. Bốn tần số kỳ vọng đều bằng 25; χ² = 4 và df = 1 khi không dùng hiệu chỉnh liên tục. Đây là một bảng số đếm, không dùng trực tiếp các giá trị MPa làm tần số.

### 3.1.4. ANOVA: so sánh từ ba trung bình

$H_0:\mu_1=\cdots=\mu_k$; $H_1$: có ít nhất một trung bình khác. Với N quan sát:

$$SSB=\sum_{j=1}^k n_j(\bar x_j-\bar x)^2,\qquad
SSW=\sum_{j=1}^k\sum_{i=1}^{n_j}(x_{ij}-\bar x_j)^2,$$

$$F=\frac{MSB}{MSW}=\frac{SSB/(k-1)}{SSW/(N-k)}.$$

ANOVA thông thường giả định độc lập, sai số có hình dạng phân phối phù hợp và phương sai tương đương. **Ví dụ giả lập:** A = [1,2,3], B = [4,5,6], C = [7,8,9] cho SSB = 54, SSW = 6 và F(2,6) = 27.

**Welch’s ANOVA** dùng trọng số $w_j=n_j/s_j^2$ và trung bình có trọng số, điều chỉnh thống kê F cùng bậc tự do theo phương sai từng nhóm. Bài chọn Welch từ thiết kế vì số mẫu và mức phân tán giữa nhóm khác nhau. Welch vẫn cần xem xét tính độc lập và ngoại lai. Nếu kiểm định tổng thể có ý nghĩa, **Games–Howell** so sánh từng cặp, cho phép phương sai khác nhau và điều chỉnh cho nhiều so sánh. Với bốn nhóm có sáu cặp.

Chỉ số $\eta^2=SSB/(SSB+SSW)$ trong bài là thống kê **mô tả phân tán giữa nhóm** theo công thức ANOVA thông thường. Kết luận kiểm định dựa trên Welch; ý nghĩa thực tiễn ưu tiên chênh lệch MPa và CI của Games–Howell.

