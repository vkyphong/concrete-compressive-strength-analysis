"""Kiểm tra cấu trúc đầu ra và nhất quán nội bộ, không khóa vào số của một CSV.

Chạy sau `python analysis/hypothesis_tests.py`. Khi đổi dữ liệu, bản báo cáo
vẫn phải được người viết rà soát trước khi dựng Word/PDF.
"""
from pathlib import Path
import hashlib
import json
import re

import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables" / "hypothesis_tests"
FIGURES = ROOT / "figures" / "hypothesis_tests"
DATA = ROOT / "data" / "hypothesis_tests" / "cleaned.csv"
REPORT = ROOT / "report" / "hypothesis_tests_report.md"
REQUIRED = [
    "cap_ghep_7_28.csv", "cau_1_paired_t.csv", "cap_phoi_28.csv",
    "cau_2_mo_ta_nhom.csv", "cau_2_welch.csv", "cau_2_games_howell.csv",
    "cau_2_vung_xi_mang_chung.csv", "cau_2_welch_vung_chung.csv",
    "chi_square_bang_cheo.csv", "chi_square_ket_qua.csv",
    "do_nhay_gop_cap_phoi.csv", "anh_xa_cap_phoi_gan_trung.csv",
    "ty_so_28_7_theo_nhom.csv",
]


def main() -> None:
    for name in REQUIRED:
        if not (TABLES / name).is_file():
            raise FileNotFoundError(TABLES / name)
    metadata = json.loads((TABLES / "run_metadata.json").read_text())
    if metadata["source_sha256"] != hashlib.sha256(DATA.read_bytes()).hexdigest():
        raise ValueError("CSV nguồn đã thay đổi sau lần chạy phân tích; hãy chạy lại.")
    pairs = pd.read_csv(TABLES / "cap_ghep_7_28.csv")
    recipes = pd.read_csv(TABLES / "cap_phoi_28.csv")
    q1 = pd.read_csv(TABLES / "cau_1_paired_t.csv").iloc[0]
    q2 = pd.read_csv(TABLES / "cau_2_welch.csv").iloc[0]
    chi = pd.read_csv(TABLES / "chi_square_ket_qua.csv").iloc[0]
    if not (len(pairs) == metadata["n_pairs"] == q1["n"]):
        raise ValueError("Số cặp tuổi không nhất quán.")
    if len(recipes) != metadata["n_recipes_28"] or not 0 <= q2["p"] <= 1:
        raise ValueError("Bảng Welch hoặc số cấp phối không nhất quán.")
    if chi["min_expected"] < 5:
        raise ValueError("Chi-square cần xem lại vì có tần số kỳ vọng < 5.")

    body = REPORT.read_text(encoding="utf-8")
    links = re.findall(r"!\[[^]]*\]\(([^)]+\.png)\)", body)
    if not links:
        raise ValueError("Báo cáo Markdown chưa dẫn hình.")
    for link in links:
        if not (REPORT.parent / link).is_file():
            raise FileNotFoundError(f"Hình dẫn trong báo cáo bị thiếu: {link}")
    images = sorted(FIGURES.glob("*.png"))
    if len(images) != len(set(links)):
        raise ValueError("Số hình trong báo cáo và thư mục đầu ra không khớp.")
    for path in images:
        with Image.open(path) as image:
            image.load()
            if image.width < 500 or path.stat().st_size < 5000:
                raise ValueError(f"Hình không hợp lệ: {path}")
    print(f"Đã kiểm tra {len(REQUIRED)} CSV, {len(images)} PNG và dữ liệu đầu vào.")


if __name__ == "__main__":
    main()
