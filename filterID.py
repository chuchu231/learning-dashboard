import pandas as pd
import dask.dataframe as dd


def assign_idsystem(file_path, conn):
    print("Đang đọc file Excel...")

    # Đọc sheet Student và StudentActivity bằng pandas
    student_excel = pd.read_excel(file_path, sheet_name='Student')
    activity_excel = pd.read_excel(file_path, sheet_name='StudentActivity')

    # Chuyển sang Dask
    student_df = dd.from_pandas(student_excel, npartitions=4)
    activity_df = dd.from_pandas(activity_excel, npartitions=4)

    print("Cột trong sheet Student:", student_df.columns.tolist())
    print("Cột trong sheet StudentActivity:", activity_df.columns.tolist())

    # Trích xuất ID từ Descript
    print("Đang trích xuất ID từ mô tả hoạt động...")
    activity_df['ExtractedID'] = activity_df['Descript'].str.extract(r"The user with id\s*'(\d+)'")[0].astype(float)

    # Tính toán activity_df
    activity_pd = activity_df.compute()

    # Tạo ánh xạ FullName → list ID
    id_mapping = {}
    for name, group in activity_pd.groupby('FullName'):
        if pd.isna(name):
            continue
        ids = group['ExtractedID'].dropna().unique()
        id_mapping[name] = list(ids)

    print("Một vài ánh xạ đầu tiên:")
    for k in list(id_mapping.keys())[:5]:
        print(f"{k} → {id_mapping[k]}")

    # Map IDSystem cho từng sinh viên
    print("Đang gán IDSystem...")
    id_series = pd.Series(id_mapping)

    if 'FullName' not in student_df.columns:
        raise ValueError("Không tìm thấy cột 'FullName' trong dữ liệu Student.")

    student_df['IDSystem'] = student_df['FullName'].map(id_series, meta=('IDSystem', 'object')).apply(
        lambda ids: ids[0] if isinstance(ids, list) and len(ids) > 0 else None,
        meta=('IDSystem', 'float')
    )

    # Tính toán student_df thành pandas để xử lý nhóm
    student_pd = student_df.compute()

    # Giải quyết trùng IDSystem
    def assign_unique_ids(group):
        seen_ids = set()
        group = group.copy()
        mask = group['IDSystem'].notna()
        for idx in group[mask].index:
            current_id = group.at[idx, 'IDSystem']
            if current_id not in seen_ids:
                seen_ids.add(current_id)
            else:
                group.at[idx, 'IDSystem'] = None
        return group

    student_pd = student_pd.groupby('FullName', group_keys=False).apply(assign_unique_ids)

    print("5 dòng đầu sau khi gán IDSystem:")
    cols_to_show = [col for col in ['StudentID', 'FullName', 'IDSystem'] if col in student_pd.columns]
    print(student_pd[cols_to_show].to_string(index=False))

    # Cập nhật vào SQL Server
    print("🔄 Đang cập nhật SQL Server...")
    cursor = conn.cursor()

    cursor.execute("SELECT StudentID FROM Student")
    existing_ids = [row[0] for row in cursor.fetchall()]

    update_data = []
    for _, row in student_pd.iterrows():
        if 'StudentID' not in row or pd.isna(row['StudentID']):
            continue
        try:
            update_row = (
                int(row['IDSystem']) if pd.notna(row['IDSystem']) else None,
                str(row['StudentID']).strip()
            )
            update_data.append(update_row)
        except Exception as e:
            print(f"❌ Lỗi xử lý dòng: {row.to_dict()} → {e}")

    if not update_data:
        print("⚠️ Không có dữ liệu để cập nhật.")
        return

    update_query = """
    UPDATE [dbo].[Student]
    SET IDSystem = ?
    WHERE TRIM(StudentID) = TRIM(?)
    """
    try:
        cursor.executemany(update_query, update_data)
        conn.commit()
        print(f"✅ Đã cập nhật {cursor.rowcount} bản ghi.")
    except Exception as e:
        print(f"❌ Lỗi cập nhật vào SQL Server: {e}")
        raise

    # In kết quả
    try:
        cursor.execute("SELECT TOP 5 StudentID, FullName, IDSystem FROM Student")
        rows = cursor.fetchall()
        print("✅ 5 bản ghi đầu tiên sau cập nhật:")
        for r in rows:
            print(r)
    except:
        print("⚠️ Không thể truy vấn bảng Student để in kết quả.")

