import pandas as pd

INPUT_CSV = "comments.csv"
OUTPUT_CSV = "comments_clean_utf8.csv"
TEXT_COL = "content"

def fix_utf8_mojibake(s):
    """
    修复典型：UTF-8 被当成 latin1 读取后产生的乱码
    例如：'ÐòºÅ' -> '序号'
    """
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin1").decode("utf-8")
    except Exception:
        return s

def clean_content(s: pd.Series) -> pd.Series:
    """
    对 content 列做基础清洗：
    - NaN -> ""
    - 转 str
    - 去首尾空格
    - 去掉常见不可见字符（可选但推荐）
    """
    s = s.fillna("").astype(str)
    s = s.str.replace("\u200b", "", regex=False)  # 零宽空格
    s = s.str.replace("\ufeff", "", regex=False)  # BOM
    s = s.str.strip()
    return s

def main():
    # 1) 用 latin1 兜底读取：保证不报编码错（把字节原样搬进来）
    print("① 用 latin1 读取原始 CSV（兜底不报错）…")
    df = pd.read_csv(INPUT_CSV, encoding="latin1", low_memory=False)

    # 2) 对所有“文本列”尝试修复 UTF-8 乱码
    print("② 尝试修复 UTF-8->latin1 造成的乱码（所有 object 列）…")
    obj_cols = [c for c in df.columns if df[c].dtype == object]
    for c in obj_cols:
        df[c] = df[c].map(fix_utf8_mojibake)

    # 3) content 列进一步清洗
    if TEXT_COL not in df.columns:
        raise KeyError(f"找不到列 '{TEXT_COL}'，当前列名：{list(df.columns)}")

    print("③ 清洗 content 列（空值、空格、不可见字符）…")
    df[TEXT_COL] = clean_content(df[TEXT_COL])

    # 4) 输出为 UTF-8-SIG（WPS/Excel 直接正常）
    print("④ 导出为 UTF-8-SIG：", OUTPUT_CSV)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    # 5) 打印前几行做验证
    print("\n✅ 完成！下面是清洗后 content 前 5 条：")
    for i, x in enumerate(df[TEXT_COL].head(5).tolist(), 1):
        print(f"{i}. {x}")

    print(f"\n✅ 已生成干净文件：{OUTPUT_CSV}")

if __name__ == "__main__":
    main()
