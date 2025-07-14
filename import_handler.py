
import pandas as pd
import pyodbc
from filterID import assign_idsystem
from io import BytesIO

# import_handler.py

def import_file(uploaded_files):
    try:
        # Kiểm tra nếu không có file nào được upload
        if not uploaded_files:
            return False, "❌ Không có file nào được upload."

        # Hàm kiểm tra file quiz (chỉ chứa sheet QuizActivity)
        def is_quiz_file(file):
            try:
                sheets = pd.read_excel(BytesIO(file.read()), sheet_name=None, engine='openpyxl')
                file.seek(0)  # Đặt lại con trỏ sau khi đọc
                return list(sheets.keys()) == ['QuizActivity']
            except Exception as e:
                print(f"❌ Lỗi khi kiểm tra file quiz: {e}")
                return False

        # Tách file chính và file quiz
        main_file = None
        quiz_files = []
        for file in uploaded_files:
            if is_quiz_file(file):
                quiz_files.append(file)
            else:
                if main_file is None:
                    main_file = file
                else:
                    return False, "❌ Nhiều file chính được phát hiện. Chỉ cho phép một file chứa sheet 'Class'."

        if main_file is None:
            return False, "❌ Không tìm thấy file chính chứa sheet 'Class'."

        # Đọc file chính
        sheets = pd.read_excel(BytesIO(main_file.read()), sheet_name=None, engine='openpyxl')
        main_file.seek(0)  # Đặt lại con trỏ

        # Lấy CourseID và ClassID từ sheet Class trong file chính
        if 'Class' not in sheets:
            return False, "❌ Sheet 'Class' không tồn tại trong file chính."
        class_info = sheets['Class']
        if class_info.shape[0] != 1:
            return False, "❌ Sheet 'Class' trong file chính cần đúng 1 dòng."
        course_id = class_info.loc[0, 'CourseID']
        class_id = class_info.loc[0, 'ClassID']

        # Kết nối SQL Server
        conn = pyodbc.connect(
            "Driver={SQL Server};"
            "Server=LEETHUONG\\MSSQLSERVER2019;"
            "Database=THESIS_SOURCE;"
            "Trusted_Connection=yes;"
        )
        cursor = conn.cursor()
        # Truncate bảng bằng cursor, KHÔNG dùng read_sql
        truncate_sql = """
            TRUNCATE TABLE ClassFeedback;
            TRUNCATE TABLE StudentClassResult;
            TRUNCATE TABLE StudentActivity;
            TRUNCATE TABLE QuizActivity;
            TRUNCATE TABLE Class;
            TRUNCATE TABLE student;
        """
        cursor.execute(truncate_sql)

        # Mapping sheet → bảng
        sheet_table_map = {
            'Class': 'Class',
            'Student': 'Student',
            'StudentClassResult': 'StudentClassResult',
            'ClassFeedback': 'ClassFeedback',
            'QuizActivity': 'QuizActivity',
            'StudentActivity': 'StudentActivity'
        }

        sheets_with_extra = ['Student', 'StudentClassResult', 'ClassFeedback', 'QuizActivity', 'StudentActivity']
        float_columns = {
            'StudentClassResult': ['LAB', 'BONUS', 'AssignmentQuiz', 'FinalExam', 'FinalNote'],
            'ClassFeedback': ['Rating1', 'Rating2', 'Rating3', 'Rating4', 'Rating5', 'Average'],
            'Class': ['Credit']
        }

        # Xử lý các sheet của file chính
        for sheet_name, df in sheets.items():
            if sheet_name not in sheet_table_map:
                print(f"⏭️ Bỏ qua sheet không khớp bảng SQL: {sheet_name}")
                continue

            table_name = sheet_table_map[sheet_name]

            if sheet_name in sheets_with_extra:
                df.insert(0, 'ClassID', class_id)
                df.insert(0, 'CourseID', course_id)
                if sheet_name == 'StudentClassResult':
                    print("📋 DataFrame StudentClassResult sau khi thêm ClassID và CourseID:")
                    print(df.head(10))  # Hiển thị 10 dòng đầu tiên, có thể đổi thành df.to_string(index=False) nếu muốn full bảng


            if sheet_name == 'QuizActivity' and 'ID' in df.columns:
                df = df.drop(columns=['ID'])

            if sheet_name in float_columns:
                for col in float_columns[sheet_name]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

            if sheet_name != 'Class':
                cols_to_check = [col for col in df.columns if col not in ['CourseID', 'ClassID']]
                df = df.dropna(subset=cols_to_check, how='any')

            df = df.loc[:, ~df.columns.duplicated()]

            columns = list(df.columns)
            placeholders = ','.join(['?'] * len(columns))
            col_names = ','.join(columns)
            insert_sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"

            for i, row in df.iterrows():
                try:
                    clean_row = [None if pd.isna(val) else val for val in row]
                    cursor.execute(insert_sql, tuple(clean_row))
                except Exception as e:
                    print(f"❌ Lỗi tại dòng {i} sheet {sheet_name}: {e}")
                    print(f"📌 Cột: {columns}")
                    print(f"📦 Dữ liệu: {tuple(row)}")
                    raise

        # Xử lý các file quiz
        quiz_id = 1
        for quiz_file in quiz_files:
            print(f"🔄 Xử lý file quiz: {quiz_file.name} với ID: {quiz_id}")
            quiz_df = pd.read_excel(BytesIO(quiz_file.read()), sheet_name='QuizActivity', engine='openpyxl')
            quiz_file.seek(0)  # Đặt lại con trỏ

            quiz_df.insert(0, 'ClassID', class_id)
            quiz_df.insert(0, 'CourseID', course_id)
            quiz_df.insert(0, 'ID', quiz_id)

            if 'QuizActivity' in float_columns:
                for col in float_columns['QuizActivity']:
                    if col in quiz_df.columns:
                        quiz_df[col] = pd.to_numeric(quiz_df[col], errors='coerce')

            cols_to_check = [col for col in quiz_df.columns if col not in ['CourseID', 'ClassID', 'ID']]
            quiz_df = quiz_df.dropna(subset=cols_to_check, how='any')

            quiz_df = quiz_df.loc[:, ~quiz_df.columns.duplicated()]

            columns = list(quiz_df.columns)
            placeholders = ','.join(['?'] * len(columns))
            col_names = ','.join(columns)
            insert_sql = f"INSERT INTO QuizActivity ({col_names}) VALUES ({placeholders})"

            for i, row in quiz_df.iterrows():
                try:
                    clean_row = [None if pd.isna(val) else val for val in row]
                    cursor.execute(insert_sql, tuple(clean_row))
                except Exception as e:
                    print(f"❌ Lỗi tại dòng {i} file {quiz_file.name}: {e}")
                    print(f"📌 Cột: {columns}")
                    print(f"📦 Dữ liệu: {tuple(row)}")
                    raise

            quiz_id += 1

        assign_idsystem(main_file, conn)
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"✅ Import thành công {len(uploaded_files)} file ({len(quiz_files)} file quiz)!"

    except Exception as e:
        return False, f"❌ Lỗi khi import: {e}"