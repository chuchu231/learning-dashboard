import pandas as pd

def assign_idsystem(file_path, conn):
    print("📥 Đang đọc file Excel...")

    # Đọc dữ liệu từ file Excel bằng pandas
    student_df = pd.read_excel(file_path, sheet_name='Student')
    activity_df = pd.read_excel(file_path, sheet_name='StudentActivity')

    print("📄 Cột trong sheet Student:", student_df.columns.tolist())
    print("📄 Cột trong sheet StudentActivity:", activity_df.columns.tolist())

    # Trích xuất ID từ mô tả
    print("🔍 Đang trích xuất ID từ mô tả hoạt động...")
    activity_df['ExtractedID'] = activity_df['Descript'].str.extract(r"The user with id\s*'(\d+)'")[0].astype(float)

    # Tạo ánh xạ FullName → list các ID duy nhất
    print("🔄 Tạo ánh xạ từ FullName sang IDSystem...")
    id_mapping = activity_df.dropna(subset=['FullName']) \
                            .groupby('FullName')['ExtractedID'] \
                            .apply(lambda x: list(x.dropna().unique()))

    # Gán IDSystem vào student_df
    student_df['IDSystem'] = student_df['FullName'].map(id_mapping) \
        .apply(lambda ids: ids[0] if isinstance(ids, list) and len(ids) > 0 else None)

    # Giải quyết trùng lặp IDSystem trong cùng một FullName
    print("🔄 Kiểm tra và loại bỏ IDSystem trùng trong cùng nhóm...")
    def assign_unique_ids(group):
        seen_ids = set()
        for idx in group.index:
            current_id = group.at[idx, 'IDSystem']
            if pd.notna(current_id) and current_id in seen_ids:
                group.at[idx, 'IDSystem'] = None
            else:
                seen_ids.add(current_id)
        return group

    student_df = student_df.groupby('FullName', group_keys=False).apply(assign_unique_ids)

    print("📊 5 dòng đầu sau khi gán IDSystem:")
    cols = [c for c in ['StudentID', 'FullName', 'IDSystem'] if c in student_df.columns]
    print(student_df[cols].head().to_string(index=False))

    # Cập nhật vào SQL Server
    print("💾 Đang cập nhật vào SQL Server...")
    cursor = conn.cursor()

    cursor.execute("SELECT StudentID FROM Student")
    existing_ids = {row[0] for row in cursor.fetchall()}

    update_data = []
    for _, row in student_df.iterrows():
        sid = row.get('StudentID')
        ids = row.get('IDSystem')
        if pd.isna(sid) or str(sid).strip() not in existing_ids:
            continue
        try:
            update_data.append((
                int(ids) if pd.notna(ids) else None,
                str(sid).strip()
            ))
        except Exception as e:
            print(f"❌ Lỗi xử lý dòng {row.to_dict()} → {e}")

    if not update_data:
        print("⚠️ Không có dòng hợp lệ để cập nhật.")
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
        print(f"❌ Lỗi khi cập nhật vào SQL Server: {e}")

    # In 5 dòng đầu sau cập nhật
    try:
        cursor.execute("SELECT TOP 5 StudentID, FullName, IDSystem FROM Student")
        print("✅ 5 bản ghi đầu tiên sau cập nhật:")
        for r in cursor.fetchall():
            print(r)
    except:
        print("⚠️ Không thể truy vấn bảng Student để in kết quả.")
