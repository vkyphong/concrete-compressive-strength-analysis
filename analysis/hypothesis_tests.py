"""Phần 3: hai câu hỏi nghiên cứu trên Concrete Compressive Strength.

Chạy từ thư mục gốc: python analysis/hypothesis_tests.py
Đọc data/hypothesis_tests/cleaned.csv; ghi bảng và hình trong thư mục phần 3.
Các cấp phối gần giống được gộp chỉ theo bảy thành phần, không dùng strength.
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
import json
import hashlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
from scipy import stats
from scipy.cluster.hierarchy import fcluster, linkage

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "hypothesis_tests" / "cleaned.csv"
# Tên tương thích với notebook từng dùng DATA_PATH.
DATA_PATH = DATA
TABLES = ROOT / "tables" / "hypothesis_tests"
FIGURES = ROOT / "figures" / "hypothesis_tests"
MATERIALS = ["cement", "slag", "fly_ash", "water", "superplasticizer", "coarse_agg", "fine_agg"]
SCM = ["Không SCM", "Chỉ xỉ", "Chỉ tro bay", "Cả hai"]
COLORS = ["#667085", "#2875B9", "#D77830", "#318677"]


def load_data() -> pd.DataFrame:
    """Đọc bản CSV riêng của phần 3 và kiểm tra các cột, giá trị bắt buộc.

    Các giá trị 0 của vật liệu tùy chọn là hợp lệ; chỉ xi măng, nước,
    tuổi và cường độ cần dương để tránh dữ liệu vật lý bất hợp lý.
    """
    if not DATA.is_file():
        raise FileNotFoundError(f"Thiếu dữ liệu: {DATA}. Xem tệp nguồn trong gói nộp.")
    df = pd.read_csv(DATA)
    required = MATERIALS + ["age", "strength"]
    absent = set(required) - set(df)
    if absent:
        raise ValueError(f"Thiếu cột: {sorted(absent)}")
    if df[required].isna().any().any():
        raise ValueError("Các cột dùng để kiểm định có dữ liệu thiếu.")
    if (df[["cement", "water", "age", "strength"]] <= 0).any().any():
        raise ValueError("Có giá trị không dương bất hợp lý trong dữ liệu.")
    return df


def recipes(df: pd.DataFrame, threshold: float = 1.0) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Gộp công thức gần trùng dựa trên bảy vật liệu, không dùng cường độ.

    Khoảng cách Chebyshev là độ lệch lớn nhất trong bảy vật liệu;
    complete linkage giữ độ lệch của mọi cặp cùng cụm không vượt ngưỡng.
    Kết quả trả về cường độ trung bình mỗi cụm-tuổi và vật liệu trung bình
    mỗi cụm, để mỗi cấp phối chỉ góp một quan sát vào kiểm định.
    """
    unique = df[MATERIALS].drop_duplicates().sort_values(MATERIALS).reset_index(drop=True)
    if threshold == 0:
        unique["recipe_id"] = np.arange(len(unique))
    else:
        # Complete linkage bảo đảm mọi cặp trong cụm lệch <= threshold ở từng vật liệu.
        tree = linkage(unique.to_numpy(), method="complete", metric="chebyshev")
        unique["recipe_id"] = fcluster(tree, t=threshold, criterion="distance")
    marked = df.merge(unique, on=MATERIALS, validate="many_to_one")
    mix = marked.groupby("recipe_id")[MATERIALS].mean()
    mix["scm"] = np.select(
        [mix.slag.gt(0) & mix.fly_ash.gt(0), mix.slag.gt(0), mix.fly_ash.gt(0)],
        ["Cả hai", "Chỉ xỉ", "Chỉ tro bay"], default="Không SCM")
    by_age = marked.groupby(["recipe_id", "age"], as_index=False).strength.mean()
    return by_age, mix


def recipe_mapping(df: pd.DataFrame, threshold: float = 1.0) -> pd.DataFrame:
    """Ánh xạ kiểm toán từng tổ hợp vật liệu sang cụm được dùng để phân tích."""
    unique = df[MATERIALS].drop_duplicates().sort_values(MATERIALS).reset_index(drop=True)
    tree = linkage(unique.to_numpy(), method="complete", metric="chebyshev")
    unique["recipe_id"] = fcluster(tree, t=threshold, criterion="distance")
    return unique


def paired(by_age: pd.DataFrame, mix: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Ghép hai tuổi theo mã cấp phối rồi kiểm định trung bình chênh lệch.

    Paired t tương đương t một mẫu trên d = MPa(28) − MPa(7).
    KTC của tỷ số dùng log(28/7) rồi biến đổi ngược để luôn dương.
    """
    pair = by_age.pivot(index="recipe_id", columns="age", values="strength")[[7, 28]].dropna()
    pair.columns = ["mpa_7", "mpa_28"]
    pair = pair.join(mix[["scm"]]).reset_index()
    pair["difference_mpa"] = pair.mpa_28 - pair.mpa_7
    pair["ratio_28_7"] = pair.mpa_28 / pair.mpa_7
    d = pair.difference_mpa.to_numpy()
    test = stats.ttest_1samp(d, 0)
    ci = test.confidence_interval()
    log_ratio = np.log(pair.ratio_28_7)
    log_ci = stats.ttest_1samp(log_ratio, 0).confidence_interval()
    result = dict(n=len(d), mean_7=pair.mpa_7.mean(), mean_28=pair.mpa_28.mean(),
                  mean_difference=d.mean(), ci_low=ci.low, ci_high=ci.high,
                  t=test.statistic, df=len(d)-1, p=test.pvalue,
                  dz=d.mean()/d.std(ddof=1), n_increase=int((d > 0).sum()),
                  geometric_ratio=np.exp(log_ratio.mean()),
                  ratio_ci_low=np.exp(log_ci.low), ratio_ci_high=np.exp(log_ci.high),
                  shapiro_p=stats.shapiro(d).pvalue, wilcoxon_p=stats.wilcoxon(d).pvalue)
    return pair, result


def welch(samples: list[np.ndarray]) -> dict:
    """Welch ANOVA cho các nhóm độc lập có phương sai, cỡ mẫu khác nhau.

    Trọng số w_j = n_j/s_j²; lam = Σ(1−w_j/Σw)²/(n_j−1).
    F hiệu chỉnh mẫu số theo lam, df2 = (k²−1)/(3lam), p theo F(df1,df2).
    Công thức này là kiểm định tổng thể; không cho biết cặp nhóm nào khác.
    """
    n = np.array([len(x) for x in samples], dtype=float)
    means = np.array([x.mean() for x in samples])
    variances = np.array([x.var(ddof=1) for x in samples])
    weights = n / variances
    weighted_mean = np.dot(weights, means) / weights.sum()
    k = len(samples)
    lam = np.sum((1-weights/weights.sum())**2/(n-1))
    f = (np.sum(weights*(means-weighted_mean)**2)/(k-1)
         / (1+2*(k-2)*lam/(k*k-1)))
    df2 = (k*k-1)/(3*lam)
    return dict(F=f, df1=k-1, df2=df2, p=stats.f.sf(f, k-1, df2))


def games_howell(samples: list[np.ndarray]) -> pd.DataFrame:
    """Đối chiếu sáu cặp với phương sai riêng và điều chỉnh đa so sánh.

    Mỗi cặp dùng sai số chuẩn √(s1²/n1+s2²/n2), bậc tự do
    Welch–Satterthwaite và phân phối studentized range của k nhóm.
    KTC và p đã điều chỉnh theo cùng phân phối, tránh so sáu p thô với 0,05.
    """
    rows = []
    for i, j in combinations(range(len(samples)), 2):
        a, b = samples[i], samples[j]
        va, vb = a.var(ddof=1)/len(a), b.var(ddof=1)/len(b)
        se = np.sqrt(va+vb)
        df = (va+vb)**2/(va**2/(len(a)-1)+vb**2/(len(b)-1))
        diff = a.mean()-b.mean()
        q = abs(diff)/se*np.sqrt(2)
        half = stats.studentized_range.ppf(.95, 4, df)*se/np.sqrt(2)
        rows.append(dict(nhom_1=SCM[i], nhom_2=SCM[j], chenhlech_mpa=diff,
                         ci_low=diff-half, ci_high=diff+half,
                         p_adjusted=stats.studentized_range.sf(q, 4, df)))
    return pd.DataFrame(rows)


def scm_analysis(by_age: pd.DataFrame, mix: pd.DataFrame):
    """Chọn 28 ngày, mô tả bốn kiểu SCM và tính Welch cùng hậu kiểm."""
    a28 = by_age.loc[by_age.age.eq(28)].set_index("recipe_id").join(mix).reset_index()
    samples = [a28.loc[a28.scm.eq(g), "strength"].to_numpy() for g in SCM]
    if min(map(len, samples)) < 2:
        raise ValueError("Không đủ cấp phối ở một trong bốn nhóm SCM.")
    desc = pd.DataFrame([dict(nhom=g, n=len(v), mean_mpa=v.mean(), sd_mpa=v.std(ddof=1),
                              mean_cement=a28.loc[a28.scm.eq(g), "cement"].mean(),
                              mean_water=a28.loc[a28.scm.eq(g), "water"].mean(),
                              mean_sp=a28.loc[a28.scm.eq(g), "superplasticizer"].mean())
                         for g, v in zip(SCM, samples)])
    total = np.concatenate(samples)
    ssb = sum(len(v)*(v.mean()-total.mean())**2 for v in samples)
    ssw = sum(((v-v.mean())**2).sum() for v in samples)
    eta2 = ssb / sum((total-total.mean())**2)
    msw = ssw/(len(total)-len(samples))
    omega2 = max(0., (ssb-(len(samples)-1)*msw)/(ssb+ssw+msw))
    diagnostics = {
        "brown_forsythe_p": stats.levene(*samples, center="median").pvalue,
        "omega2_descriptive": omega2,
    }
    diagnostics.update({f"shapiro_p_{j+1}": stats.shapiro(v).pvalue
                        for j, v in enumerate(samples)})
    return a28, desc, {**welch(samples), "eta2_descriptive": eta2, **diagnostics}, games_howell(samples)


def common_cement_range(a28: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Thăm dò vùng xi măng 220–340 sau khi xem dữ liệu, có CI theo nhóm.

    Đây là phép đối chiếu mô tả độ nhạy, không phải kiểm định xác nhận
    độc lập với Welch chính và không kiểm soát đồng thời nước/phụ gia.
    """
    # Khoảng dùng cho kiểm tra thăm dò vì cả bốn nhóm đều có đủ cấp phối trong đó.
    # Đây không phải ghép mẫu hoặc kiểm soát đồng thời nước và phụ gia.
    subset = a28.loc[a28.cement.between(220, 340)].copy()
    samples = [subset.loc[subset.scm.eq(g), "strength"].to_numpy() for g in SCM]
    desc = pd.DataFrame([dict(nhom=g, n=len(v), mean_strength=v.mean(),
                              ci_low=stats.t.interval(.95, len(v)-1, loc=v.mean(),
                                                      scale=stats.sem(v))[0],
                              ci_high=stats.t.interval(.95, len(v)-1, loc=v.mean(),
                                                       scale=stats.sem(v))[1],
                              mean_cement=subset.loc[subset.scm.eq(g), "cement"].mean(),
                              mean_water=subset.loc[subset.scm.eq(g), "water"].mean(),
                              mean_sp=subset.loc[subset.scm.eq(g), "superplasticizer"].mean())
                         for g, v in zip(SCM, samples)])
    return subset, desc, welch(samples)


def chi_square(a28: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Kiểm định liên hệ SCM × trạng thái dùng phụ gia trên cấp phối 28 ngày."""
    a28 = a28.copy()
    a28["co_phu_gia"] = np.where(a28.superplasticizer.gt(0), "Có", "Không")
    table = pd.crosstab(a28.scm, a28.co_phu_gia).reindex(index=SCM, columns=["Không", "Có"])
    test = stats.chi2_contingency(table, correction=False)
    v = np.sqrt(test.statistic/(table.to_numpy().sum()*min(np.array(table.shape)-1)))
    return table, dict(chi2=test.statistic, df=test.dof, p=test.pvalue,
                       min_expected=test.expected_freq.min(), cramer_v=v)


def sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    """Đối chiếu ngưỡng gộp 0; 0,5; 1; 2 kg/m³ theo cùng quy trình."""
    rows = []
    for threshold in [0, .5, 1., 2.]:
        age, mix = recipes(df, threshold)
        pair, q1 = paired(age, mix)
        a28, _, q2, gh = scm_analysis(age, mix)
        specific = gh.loc[gh.nhom_1.eq("Không SCM") & gh.nhom_2.eq("Chỉ tro bay"), "p_adjusted"].iloc[0]
        rows.append(dict(nguong_kg_m3=threshold, n_cap_7_28=len(pair), delta_mpa=q1["mean_difference"],
                         n_cap_28=len(a28), p_welch=q2["p"], p_gh_khong_scm_chi_tro=specific))
    return pd.DataFrame(rows)


def _format_axis(ax, *, axis="y") -> None:
    """Định dạng dấu phẩy thập phân và lưới nhạt để dễ đọc khi in."""
    formatter = FuncFormatter(lambda value, _: f"{value:g}".replace(".", ","))
    if axis == "y":
        ax.yaxis.set_major_formatter(formatter)
        ax.grid(axis="y", color="#E3E8EF", linewidth=.7)
    else:
        ax.xaxis.set_major_formatter(formatter)
        ax.grid(axis="x", color="#E3E8EF", linewidth=.7)
    ax.set_axisbelow(True)


def _save(fig, filename: str) -> None:
    # Ghi vào tệp tạm rồi thay thế nguyên tử để notebook không thấy PNG rỗng.
    target = FIGURES / filename
    temporary = target.with_name(target.name + ".tmp")
    fig.savefig(temporary, format="png", dpi=240, bbox_inches="tight",
                facecolor="white")
    if temporary.stat().st_size < 5000:
        raise OSError(f"Hình xuất ra không hợp lệ: {temporary}")
    temporary.replace(target)
    plt.close(fig)


def figures(pair: pd.DataFrame, a28: pd.DataFrame, desc: pd.DataFrame,
            gh: pd.DataFrame, support: pd.DataFrame, table: pd.DataFrame) -> None:
    """Vẽ bảy hình có nhãn, dùng dữ liệu đã gộp ở cấp phối."""
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10.5,
        "axes.titlesize": 12.5, "axes.titleweight": "bold",
        "axes.labelcolor": "#243447", "text.color": "#243447",
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.constrained_layout.use": True,
    })
    blue, orange, teal, slate = COLORS[1], COLORS[2], COLORS[3], COLORS[0]

    # Đường mảnh giữ liên hệ trong từng cấp phối; điểm lớn cho thấy
    # dịch chuyển trung bình mà không che sự phân tán giữa các cấp phối.
    fig, ax = plt.subplots(figsize=(8.5, 5))
    for row in pair.itertuples():
        ax.plot([7, 28], [row.mpa_7, row.mpa_28], color=blue, alpha=.16, lw=.85)
    means = [pair.mpa_7.mean(), pair.mpa_28.mean()]
    ax.plot([7, 28], means, "o-", color=orange, ms=9, lw=3,
            label="Trung bình 109 cấp phối", zorder=5)
    for x, y in zip([7, 28], means):
        ax.annotate(f"{y:.1f}".replace(".", ",") + " MPa", (x, y),
                    xytext=(9, 8), textcoords="offset points", weight="bold")
    ax.text(.5, .03, "Mức tăng trung bình: 13,10 MPa  ·  KTC 95%: 12,00–14,20",
            transform=ax.transAxes, ha="center", va="bottom", color="#264F6D",
            bbox={"boxstyle": "round,pad=.4", "fc": "#EAF3FA", "ec": "none"})
    ax.set(xticks=[7, 28], xlim=(4, 31), xlabel="Tuổi bê tông (ngày)",
           ylabel="Cường độ chịu nén (MPa)",
           title="Câu 1  ·  Cùng cấp phối ở 7 và 28 ngày")
    _format_axis(ax)
    ax.legend(loc="upper left", frameon=False)
    _save(fig, "hinh_3_1_cap_phoi_ghep.png")

    # Kiểm tra phân phối của chênh lệch theo cặp, không phải hai cột tuổi riêng.
    d = pair.difference_mpa.to_numpy()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5))
    axes[0].hist(d, bins=15, density=True, color=blue, alpha=.74,
                 edgecolor="white", label="Chênh lệch quan sát")
    xx = np.linspace(d.min(), d.max(), 250)
    axes[0].plot(xx, stats.norm.pdf(xx, d.mean(), d.std(ddof=1)),
                 color=orange, lw=2.2, label="Đường chuẩn tham chiếu")
    axes[0].axvline(d.mean(), color="#243447", ls="--", lw=1.3)
    axes[0].set(title="Phân bố mức tăng", xlabel="28 ngày − 7 ngày (MPa)",
                ylabel="Mật độ")
    axes[0].legend(frameon=False, fontsize=8)
    stats.probplot(d, dist="norm", plot=axes[1])
    axes[1].get_lines()[0].set(color=blue, markersize=4)
    axes[1].get_lines()[1].set(color=orange, linewidth=2)
    axes[1].set(title="Q–Q của chênh lệch", xlabel="Phân vị chuẩn lý thuyết",
                ylabel="Chênh lệch quan sát (MPa)")
    _format_axis(axes[0], axis="x")
    _format_axis(axes[1])
    _save(fig, "hinh_3_1b_chan_doan_chenh_lech.png")

    values = [a28.loc[a28.scm.eq(group), "strength"].to_numpy()
              for group in SCM]
    fig, ax = plt.subplots(figsize=(9, 5))
    boxes = ax.boxplot(values, patch_artist=True, showfliers=True,
                       medianprops={"color": "#172B4D", "linewidth": 2},
                       flierprops={"marker": ".", "markersize": 3,
                                   "alpha": .35, "markerfacecolor": slate})
    for patch, color in zip(boxes["boxes"], COLORS):
        patch.set(facecolor=color, alpha=.45, edgecolor=color)
    for i, value in enumerate(values, 1):
        ax.scatter(i, value.mean(), marker="D", s=55, color="#B04A35", zorder=4)
    ax.scatter([], [], marker="D", color="#B04A35", label="Trung bình")
    ax.set(xticks=np.arange(1, 5), xticklabels=[f"{g}\n(n = {n})"
           for g, n in zip(SCM, desc.n)], ylabel="Cường độ 28 ngày (MPa)",
           title="Câu 2  ·  Phân bố cường độ theo kiểu dùng SCM")
    _format_axis(ax)
    ax.legend(loc="upper right", frameon=False)
    _save(fig, "hinh_3_2_scm_28.png")

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    for i, (value, color) in enumerate(zip(values, COLORS)):
        half = stats.t.ppf(.975, len(value)-1)*stats.sem(value)
        ax.errorbar(i, value.mean(), yerr=half, fmt="o", color=color,
                    capsize=6, ms=9, lw=2.3)
        ax.text(i, value.mean()+half+1.1,
                f"{value.mean():.1f}".replace(".", ","), ha="center", weight="bold")
    ax.set(xticks=np.arange(4), xticklabels=[f"{g}\nn = {n}"
           for g, n in zip(SCM, desc.n)], ylim=(20, 53),
           ylabel="Trung bình cường độ (MPa)",
           title="Cường độ trung bình và khoảng tin cậy 95% ở 28 ngày")
    _format_axis(ax)
    _save(fig, "hinh_3_2b_trung_binh_ci.png")

    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    y = np.arange(len(gh))[::-1]
    for yi, row in zip(y, gh.itertuples()):
        significant = row.p_adjusted < .05
        color = blue if significant else slate
        ax.plot([row.ci_low, row.ci_high], [yi, yi], color=color, lw=2.4)
        ax.plot(row.chenhlech_mpa, yi, "o", color=color, ms=7)
        p_text = "< 0,001" if row.p_adjusted < .001 else f"{row.p_adjusted:.3f}".replace(".", ",")
        ax.text(16.7, yi, "p = " + p_text, va="center", fontsize=9, color=color)
    ax.axvline(0, color="#243447", ls="--", lw=1)
    ax.set(xlim=(-17, 23), yticks=y,
           yticklabels=[f"{row.nhom_1} − {row.nhom_2}" for row in gh.itertuples()],
           xlabel="Chênh lệch trung bình (MPa)  ·  KTC Games–Howell 95%",
           title="Hậu kiểm sáu cặp nhóm ở 28 ngày")
    ax.text(.02, -.22, "Khoảng tin cậy cắt qua 0: chưa đủ bằng chứng khác biệt ở mức 5%.",
            transform=ax.transAxes, fontsize=9, color="#536477")
    _format_axis(ax, axis="x")
    _save(fig, "hinh_3_3_games_howell.png")

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.8))
    left = axes[0]
    left.bar(np.arange(4), desc.mean_cement, color=COLORS, alpha=.8)
    left.axhspan(220, 340, color="#D7EBDF", alpha=.5, zorder=0)
    left.set(xticks=np.arange(4), xticklabels=SCM, ylabel="Xi măng TB (kg/m³)",
             title="Toàn bộ 308 cấp phối")
    left.tick_params(axis="x", rotation=18)
    _format_axis(left)
    right = axes[1]
    right.bar(np.arange(4), support.mean_strength, color=COLORS, alpha=.8)
    for i, row in enumerate(support.itertuples()):
        right.errorbar(i, row.mean_strength,
                       yerr=[[row.mean_strength-row.ci_low],
                             [row.ci_high-row.mean_strength]],
                       fmt="none", ecolor="#25364A", capsize=4, lw=1.4)
        right.text(i, row.ci_high+1, f"n={row.n}", ha="center", fontsize=8)
    right.set(xticks=np.arange(4), xticklabels=SCM,
              ylabel="Cường độ TB (MPa) và KTC 95%",
              title="Vùng xi măng 220–340 kg/m³  ·  n = 120")
    right.tick_params(axis="x", rotation=18)
    right.set_ylim(0, max(support.ci_high)+8)
    _format_axis(right)
    _save(fig, "hinh_3_4_kiem_tra_xi_mang.png")

    fig, ax = plt.subplots(figsize=(9, 4.8))
    pct = table.div(table.sum(axis=1), axis=0)*100
    y = np.arange(4)
    ax.barh(y, pct["Không"], color=slate, label="Không dùng phụ gia")
    ax.barh(y, pct["Có"], left=pct["Không"], color=blue, label="Có dùng phụ gia")
    for i, group in enumerate(SCM):
        share_without = pct.loc[group, "Không"]
        if share_without < 8:
            # Một công thức tạo đoạn cột quá hẹp: đặt nhãn ở mép ngoài.
            ax.text(-1.5, i, f"{int(table.loc[group,'Không'])}",
                    ha="right", va="center", color=slate, weight="bold")
        else:
            ax.text(share_without/2, i, f"{int(table.loc[group,'Không'])}",
                    ha="center", va="center", color="white")
        ax.text(pct.loc[group, "Không"]+pct.loc[group, "Có"]/2, i,
                f"{int(table.loc[group,'Có'])}", ha="center", va="center", color="white")
    ax.set(xlim=(-6, 100), yticks=y, yticklabels=[f"{g}  (n={table.loc[g].sum()})"
           for g in SCM], xlabel="Tỷ lệ trong nhóm (%) — số đếm ghi trên cột",
           title="Kiểu SCM và việc dùng phụ gia siêu dẻo ở 28 ngày")
    ax.invert_yaxis()
    _format_axis(ax, axis="x")
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.18), ncol=2, frameon=False)
    _save(fig, "hinh_3_5_chi_square.png")


def main() -> None:
    """Chạy toàn bộ phân tích, xuất bảng, hình và thông tin tái lập."""
    TABLES.mkdir(parents=True,exist_ok=True)
    FIGURES.mkdir(parents=True,exist_ok=True)
    df=load_data()
    age,mix=recipes(df)
    pair,q1=paired(age,mix)
    a28,desc,q2,gh=scm_analysis(age,mix)
    restricted,common,q2_common=common_cement_range(a28)
    table,chi=chi_square(a28)
    pair.to_csv(TABLES/"cap_ghep_7_28.csv",index=False)
    pd.DataFrame([q1]).to_csv(TABLES/"cau_1_paired_t.csv",index=False)
    a28.to_csv(TABLES/"cap_phoi_28.csv",index=False)
    desc.to_csv(TABLES/"cau_2_mo_ta_nhom.csv",index=False)
    pd.DataFrame([q2]).to_csv(TABLES/"cau_2_welch.csv",index=False)
    gh.to_csv(TABLES/"cau_2_games_howell.csv",index=False)
    common.to_csv(TABLES/"cau_2_vung_xi_mang_chung.csv",index=False)
    pd.DataFrame([q2_common]).to_csv(TABLES/"cau_2_welch_vung_chung.csv",index=False)
    table.to_csv(TABLES/"chi_square_bang_cheo.csv")
    pd.DataFrame([chi]).to_csv(TABLES/"chi_square_ket_qua.csv",index=False)
    sensitivity(df).to_csv(TABLES/"do_nhay_gop_cap_phoi.csv",index=False)
    recipe_mapping(df).to_csv(TABLES/"anh_xa_cap_phoi_gan_trung.csv",index=False)
    pair.groupby("scm").ratio_28_7.agg(["size","mean","median","std"]).to_csv(
        TABLES/"ty_so_28_7_theo_nhom.csv")
    (TABLES/"run_metadata.json").write_text(json.dumps({
        "source_file":"data/hypothesis_tests/cleaned.csv",
        "source_sha256":hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "n_rows":int(len(df)),"n_pairs":int(len(pair)),"n_recipes_28":int(len(a28)),
        "cluster_threshold_kg_per_m3":1.0,"scipy":stats.__version__ if hasattr(stats,"__version__") else __import__("scipy").__version__
    },ensure_ascii=False,indent=2),encoding="utf-8")
    figures(pair,a28,desc,gh,common,table)
    print(f"Đã tạo {len(list(TABLES.glob('*.csv')))} bảng, {len(list(FIGURES.glob('*.png')))} hình")
    print(f"Q1: n={q1['n']}, Δ={q1['mean_difference']:.3f} MPa, p={q1['p']:.3g}")
    print(f"Q2: n={len(a28)}, Welch F={q2['F']:.3f}, p={q2['p']:.3g}")
    print(f"Vùng xi măng chung: n={len(restricted)}, Welch p={q2_common['p']:.3g}")


if __name__ == "__main__":
    main()
