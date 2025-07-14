# ---------------------- api.py (Flask API để cung cấp dữ liệu cho Streamlit) ----------------------
from flask import Flask, jsonify
import clr
import sys
import os
import pandas as pd
from flask_cors import CORS


# ---------------------- Khởi tạo Flask ----------------------
app = Flask(__name__)
CORS(app)  # Cho phép gọi từ domain khác (Streamlit Cloud)

# ---------------------- Kết nối ADOMD.NET ----------------------

dll_path = r"D:\Final_app\Microsoft.AnalysisServices.AdomdClient.dll"
if not os.path.exists(dll_path):
    raise FileNotFoundError("❌ DLL path không tồn tại")

# Thêm thư mục chứa DLL vào sys.path
sys.path.append(os.path.dirname(dll_path))

# Load DLL
clr.AddReference(dll_path)

# Import từ namespace sau khi load DLL
from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand


# ---------------------- Thông tin kết nối SSAS ----------------------
connection_string = r"Provider=MSOLAP;Data Source=LEETHUONG\\MSSQLSERVER2019;Catalog=cube_07062025;Integrated Security=SSPI"


def run_query(query, columns):
    """Thực hiện truy vấn MDX và trả DataFrame"""
    try:
        conn = AdomdConnection(connection_string)
        conn.Open()
        cmd = AdomdCommand(query, conn)
        reader = cmd.ExecuteReader()
        data = []
        while reader.Read():
            row = [reader.GetValue(i) for i in range(reader.FieldCount)]
            data.append(row)
        reader.Close()
        conn.Close()
        return pd.DataFrame(data, columns=columns) if data else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})


@app.route("/api/statistics/<class_id>")
def fetch_class_statistics(class_id):
    """Trả về toàn bộ thống kê học tập của lớp học dưới dạng JSON"""

    # 1. Average Score
    query_avg = f"""
    SELECT NON EMPTY {{ [Measures].[AVG_Overall] }} ON COLUMNS,
           NON EMPTY {{ [Dim Class].[Class SK].[Class SK].ALLMEMBERS }} 
           DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    ON ROWS 
    FROM [cube_13062025] 
    WHERE ([Dim Class].[Class ID].[{class_id}])
    """
    df_avg = run_query(query_avg, ["Class SK", "Class SK Dim", "AVG_Overall"])

    # 2. Performance Rates
    query_rates = f"""
    SELECT NON EMPTY {{
        [Measures].[Rate_Excellent], [Measures].[Rate_Good], 
        [Measures].[Rate_Average], [Measures].[Rate_Poor]
    }} ON COLUMNS,
    NON EMPTY {{ [Dim Class].[Class SK].[Class SK].ALLMEMBERS }} 
    DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    ON ROWS 
    FROM [cube_13062025] 
    WHERE ([Dim Class].[Class ID].[{class_id}])
    """
    df_rates = run_query(query_rates, ["Class SK", "Class SK Dim", 
                                       "Rate_Excellent", "Rate_Good", 
                                       "Rate_Average", "Rate_Poor"])

    # 3. Distribution Ranking Student
    query_ranks = f"""
    SELECT 
    NON EMPTY {{
        [Measures].[Count_Rank_1], [Measures].[Count_Rank_2], [Measures].[Count_Rank_3],
        [Measures].[Count_Rank_4], [Measures].[Count_Rank_5], [Measures].[Count_Rank_6],
        [Measures].[Count_Rank_7], [Measures].[Count_Rank_8], [Measures].[Count_Rank_9],
        [Measures].[Count_Rank_10]
    }} ON COLUMNS,
    NON EMPTY {{ [Dim Class].[Class SK].[Class SK].ALLMEMBERS }} 
    DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    ON ROWS 
    FROM [cube_13062025]
    WHERE ([Dim Class].[Class ID].[{class_id}])
    """
    df_ranks = run_query(query_ranks, ["Class SK", "Class SK Dim",
                                       "Rank_1", "Rank_2", "Rank_3", "Rank_4", "Rank_5",
                                       "Rank_6", "Rank_7", "Rank_8", "Rank_9", "Rank_10"])

    # 4. Performance Distribution
    query_dist = f"""
    SELECT NON EMPTY {{ 
        [Measures].[Count_Excellent], [Measures].[Count_Good], 
        [Measures].[Count_Average], [Measures].[Count_Poor] 
    }} ON COLUMNS,
    NON EMPTY {{ [Dim Class].[Class SK].[Class SK].ALLMEMBERS }} 
    DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    ON ROWS 
    FROM [cube_13062025] 
    WHERE ([Dim Class].[Class ID].[{class_id}])
    """
    df_dist = run_query(query_dist, ["Class SK", "Class SK Dim", "Excellent", "Good", "Average", "Poor"])
    for col in ["Excellent", "Good", "Average", "Poor"]:
        df_dist[col] = pd.to_numeric(df_dist[col], errors="coerce")
    df_dist = df_dist.dropna()

    # 5. Max/Min Scores
    query_scores = f"""
    SELECT NON EMPTY {{ 
        [Measures].[Max Final Note], [Measures].[Min Final Note] 
    }} ON COLUMNS,
    NON EMPTY {{ [Dim Class].[Class SK].[Class SK].ALLMEMBERS }} 
    DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    ON ROWS 
    FROM [cube_13062025] 
    WHERE ([Dim Class].[Class ID].[{class_id}])
    """
    df_scores = run_query(query_scores, ["Class SK", "Class SK Dim", "Max Final Note", "Min Final Note"])
    df_scores["Max Score"] = pd.to_numeric(df_scores["Max Final Note"], errors="coerce")
    df_scores["Min Score"] = pd.to_numeric(df_scores["Min Final Note"], errors="coerce")
    df_scores = df_scores.dropna(subset=["Max Score", "Min Score"])

    # 6. Pass/Fail Rate
    query_pass_fail = f"""
    SELECT NON EMPTY {{ 
        [Measures].[Rate_Fail], [Measures].[Rate_Pass] 
    }} ON COLUMNS,
    NON EMPTY {{ [Dim Class].[Class SK].[Class SK].ALLMEMBERS }} 
    DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    ON ROWS 
    FROM [cube_13062025] 
    WHERE ([Dim Class].[Class ID].[{class_id}])
    """
    df_pass_fail = run_query(query_pass_fail, ["Class SK", "Class SK Dim", "Rate_Fail", "Rate_Pass"])

    return jsonify({
        "avg_score": df_avg.to_dict(orient="records"),
        "performance_rates": df_rates.to_dict(orient="records"),
        "ranking_distribution": df_ranks.to_dict(orient="records"),
        "performance_distribution": df_dist.to_dict(orient="records"),
        "min_max_scores": df_scores.to_dict(orient="records"),
        "pass_fail_rate": df_pass_fail.to_dict(orient="records")
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
