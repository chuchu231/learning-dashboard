# ---------------------- app.py (Streamlit gọi Flask API - giữ nguyên layout gốc) ----------------------
import streamlit as st
import streamlit_menu as menu
import uuid
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import pearsonr
import time
import pyodbc
from import_handler import import_file
from streamlit import experimental_rerun
import zipfile
import io
from api import fetch_class_statistics

# Set page config
st.set_page_config("Learning Analytics", layout="wide", page_icon="📊")

# ---------------------- Gọi API ----------------------
BASE_URL = "https://2a6024378dc0.ngrok-free.app/api"


def get_api_data(endpoint, class_id):
    try:
        url = f"{BASE_URL}/{endpoint}/{class_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error(f"❌ API lỗi {response.status_code}: {response.text}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Lỗi khi gọi API: {e}")
        return pd.DataFrame()

import streamlit as st
import streamlit_menu as menu
import uuid
import pandas as pd
from pyadomd import Pyadomd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import pearsonr
import time
import pyodbc
from import_handler import import_file
from streamlit import experimental_rerun
import zipfile
import io
import time


# Set page config
st.set_page_config("Learning Analytics", layout="wide", page_icon="📊")
conn_str = "Provider=MSOLAP;Data Source=LEETHUONG\\MSSQLSERVER2019;Catalog=cube_07062025;Integrated Security=SSPI"

# CSS styles
st.markdown("""
<style>
    /* Sidebar màu xanh lá vừa */
    [data-testid="stSidebar"] {
        background-color: #A5D6A7 !important;  
    }

    /* Font & Text */
    .stMarkdown, .stWrite {
        font-family: 'Arial', sans-serif;
        color: #1B5E20;  /* Xanh lá đậm */
    }

    h1, h2, h3, h4 {
        color: #388E3C;  /* Xanh lá vừa */
    }

    a {
        color: #1B5E20;
    }

    a:hover {
        color: #2E7D32;  /* Xanh lá hover */
    }

    /* Thẻ card / box */
    .card {
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        background-color: #E8F5E9;  /* Xanh pastel */
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #F1F8E9;  /* Nền xanh rất nhạt */
        border-radius: 8px;
        padding: 10px;
    }

    [data-testid="stFileUploader"] label {
        color: #1B5E20 !important;
        font-weight: 500;
    }

    /* Data card */
    .data-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
    }

    .data-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .data-left {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .data-title {
        font-size: 20px;
        font-weight: 600;
        color: #1B5E20;
        margin: 0;
    }

    .data-desc {
        font-size: 15px;
        color: #4B5563;
        margin: 4px 0 0 0;
    }

    /* Hover nút */
    button:hover {
        background-color: #C8E6C9 !important;  /* Xanh nhạt hover */
        color: #1B5E20 !important;
    }

    /* Divider */
    .divider {
        border: none;
        height: 1px;
        background: #C8E6C9;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header configuration
header = {
    "title": "Learning Analytics"
}

# Menu items configuration
menu_items = [
    {"id": 1, "title": "Overview", "icon": "fa-solid fa-chart-line", "children": None},
    {
        "id": 2,
        "title": "Academic Insights",
        "icon": "fa-solid fa-book",
        "children": [
            {"id": 3, "title": "Learning Performance", "icon": "fa-solid fa-comment-dots", "children": None},
            {"id": 4, "title": "Learning Behavior", "icon": "fa-solid fa-graduation-cap", "children": None},
        ],
    },
    {
        "id": 5,
        "title": "Correlation Analysis",
        "icon": "fa-solid fa-user-graduate",
        "children": None,
    },
    {"id": 6, "title": "Data Management", "icon": "fa-solid fa-database", "children": None},
]

# Callback for menu selection
def on_menu_select(widgetkey):
    selected_item = st.session_state.get(widgetkey, {}).get("title", "Overview")
    st.session_state["selected"] = selected_item
    # Handle submenu selections
    if "parent" in st.session_state.get(widgetkey, {}):
        st.session_state["sub_selected"] = selected_item
        st.session_state["selected"] = st.session_state[widgetkey]["parent"]["title"]
    else:
        st.session_state["sub_selected"] = None

# Menu styles
# Wrapper màu sidebar
wrapper_style = {"background_color": "#A5D6A7"}  # Xanh pastel sidebar

# Header
header_style = {
    "items_direction": "column",
    "horizontal_alignment": "center",
    "font_family": "'Arial', sans-serif",
    "font_size": "2rem",
    "height": "6rem",
    "text_color": "#1B5E20",  # Xanh lá đậm
    "logo": {
        "border_radius": "100px",
        "width": "0rem",
        "height": "0rem"
    }
}

# Menu chính
single_menu_style = {
    "color": "#1B5E20",  # Text thường
    "hover": {
        "color": "#2E7D32",  # Xanh hover
        "background_color": "#C8E6C9",  # Nền xanh nhạt
    },
    "active_menu": {
        "color": "#ffffff",
        "background_color": "#66BB6A",  # Xanh lá vừa active
    }
}

# Submenu
submenu_style = {
    "color": "#1B5E20",
    "hover": {
        "color": "#2E7D32",
        "background_color": "#E8F5E9",  # Nhẹ nhàng hơn
    },
    "active_submenu": {
        "color": "#ffffff",
        "background_color": "#66BB6A",
    }
}

# Render menu in sidebar
with st.sidebar:
    menu.st_menu(
        header=header,
        menu_items=menu_items,
        wrapper_style=wrapper_style,
        header_style=header_style,
        single_menu_style=single_menu_style,
        submenu_style=submenu_style,
        divider_between_header_and_body=True,
        is_collapsible=True,
        on_menu_select=on_menu_select,
        args=("sidemenu",)
    )

# Initialize session state
if "selected" not in st.session_state:
    st.session_state["selected"] = "Overview"
if "sub_selected" not in st.session_state:
    st.session_state["sub_selected"] = None

# Main content
selected = st.session_state["selected"]
sub_selected = st.session_state["sub_selected"]

st.markdown(
    f"<h2 style='color: #1F2A44;'>{selected} {('- ' + sub_selected) if sub_selected else ''}</h2>",
    unsafe_allow_html=True
)
def load_class_list():
        conn_sql = pyodbc.connect( 
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=LEETHUONG\\MSSQLSERVER2019;"
                "DATABASE=THESIS_DDS;"
                "Trusted_Connection=yes;"
            )
        df = pd.read_sql("SELECT CL.ClassID + ' - ' + CO.CourseName AS Class FROM dbo.DimClass CL join dbo.DimCourse CO on CL.CourseSK = CO.CourseSK", conn_sql) 
        conn_sql.close() 
        return df["Class"].dropna().tolist()
def run_query(query, columns):
        try:
            with Pyadomd(conn_str) as conn:
                with conn.cursor().execute(query) as cur:
                    data = cur.fetchall()
                    return pd.DataFrame(data, columns=columns) if data else pd.DataFrame()
        except Exception as e:
            st.markdown(f"""
            <div class='info-box'>
                <b>Error:</b> {str(e)}<br>
                <b>Troubleshooting tips:</b><br>
                - Verify SSAS server is running.<br>
                - Ensure database name is correct.<br>
                - Check user permissions.<br>
                - Test MDX in SSMS.
            </div>
            """, unsafe_allow_html=True)
            return pd.DataFrame()


if selected == "Overview":
    st.markdown("""
        <div class='card'>
            <h3 style='color: #1F2A44;'>🔍 Welcome to Learning Analytics</h3>
            <p style='font-size: 16px; color: #4B5563;'>
                Learning Analytics is an intelligent system that helps institutions and instructors monitor, assess, and improve students' academic performance through intuitive and effective visualizations.
            </p>
            <hr style='border-top: 1px solid #E5E7EB;'>
            <h4 style='color: #1F2A44;'>⚙️ Core Features</h4>
            <ul style='font-size: 16px; color: #4B5563;'>
                <li>📊 <b>Overview:</b> Provides a high-level summary of learning data across the entire system.</li>
                <li>📚 <b>Academic Insights:</b> Analyzes academic data from two perspectives:
                    <ul style='margin-top: 4px; margin-bottom: 4px;'>
                        <li>🎯 <b>Academic Performance:</b> Analyzes grades, performance classifications, and pass/fail rates.</li>
                        <li>📈 <b>Learning Behavior:</b> Tracks student behavior including quiz durations and satisfaction levels with each course.</li>
                    </ul>
                </li>
                <li>🔗 <b>Correlation Analysis:</b> Explores the relationship between learning behaviors and academic outcomes.</li>
                <li>🗂️ <b>Data Management:</b> Manages input data (.xlsx) and system sample datasets.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

elif selected == "Learning Performance":
    st.markdown("""
    <style>
        .main {
            background-color: none;
            padding: 2rem;
            font-family: 'Inter', sans-serif;
            color: #1e293b;
        }
        .stMetric {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            text-align: left;
            transition: transform 0.2s;
        }
        .stMetric:hover {
            transform: translateY(-4px);
        }
        .metric-label {
            font-size: 1.1rem;
            font-weight: 500;
            color: #64748b;
            margin-bottom: 0.5rem;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
        }
        .metric-value.avg-value {
            color: #F97316;  /* Orange */
        }
        .metric-value.max-value {
            color: #10B981;  /* Green */
        }
        .metric-value.min-value {
            color: #EF4444;  /* Red */
        }

        .stPlotlyChart {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }
        h1 { color: #111827; font-weight: 700; font-size: 2rem; text-align: center; margin-bottom: 2rem; }
        h2 { color: #1F2937; font-weight: 600; font-size: 1.5rem; margin-bottom: 1rem; }
        h3 { color: #1F2937; font-weight: 500; font-size: 1.25rem; margin-bottom: 0.75rem; }
        .divider {
            border-top: 1px solid #e5e7eb;
            margin: 2rem 0;
        }
        .card {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }
        .info-box {
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            border-radius: 8px;
            padding: 1rem;
            color: #78350f;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        .doughnut-caption {
            text-align: center;
            font-size: 0.9rem;
            color: #64748b;
            margin-top: -0.5rem;
        }
        .footer {
            text-align: center;
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 2rem;
            padding: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

    

    class_list = load_class_list()
    default_index = class_list.index("22CLC01 - Hệ điều hành") if "22CLC01 - Hệ điều hành" in class_list else 0
    selected_class_full = st.selectbox("Select Class", class_list, index=default_index)

    # Lấy phần trước dấu "-"
    selected_class = selected_class_full.split(" - ")[0]


    # Hàm vẽ biểu đồ doughnut
    def draw_doughnut(title, value, color):
        fig = go.Figure(go.Pie(
            values=[value, 100 - value],
            labels=["", ""],
            hole=0.6,
            marker_colors=[color, "#f3f4f6"],
            textinfo='none',
            sort=False,              
            direction='clockwise'
        ))
        fig.update_layout(
            showlegend=False,
            annotations=[dict(text=f"{value:.1f}%", x=0.5, y=0.5, font_size=18, showarrow=False)],
            margin=dict(t=10, b=10, l=10, r=10),
            height=180
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<div class='doughnut-caption'>{title}</div>", unsafe_allow_html=True)

    # # Truy vấn dữ liệu
    # # 1. Average Score
    # query_avg = f"""
    # SELECT NON EMPTY {{ [Measures].[AVG_Overall] }} ON COLUMNS,
    # NON EMPTY {{ [Dim Class].[Class SK].[Class SK].ALLMEMBERS }} 
    # DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    # ON ROWS 
    # FROM [cube_13062025] 
    # WHERE ([Dim Class].[Class ID].[{selected_class}])
    # """
    # df_avg = run_query(query_avg, ["Class SK", "Class SK Dim", "AVG_Overall"])


    # # 2. Performance Rates
    # query_rates = f"""
    # SELECT NON EMPTY {{
    #     [Measures].[Rate_Excellent], [Measures].[Rate_Good], 
    #     [Measures].[Rate_Average], [Measures].[Rate_Poor]
    # }} ON COLUMNS,
    # NON EMPTY {{ [Dim Class].[Class SK].[Class SK].ALLMEMBERS }} 
    # DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    # ON ROWS 
    # FROM [cube_13062025] 
    # WHERE ([Dim Class].[Class ID].[{selected_class}])
    # """
    # df_rates = run_query(query_rates, ["Class SK", "Class SK Dim", "Rate_Excellent", "Rate_Good", "Rate_Average", "Rate_Poor"])

    # # 3. Distribution Ranking Student
    # query_ranks = f"""
    # SELECT 
    # NON EMPTY {{
    #     [Measures].[Count_Rank_1], [Measures].[Count_Rank_2], [Measures].[Count_Rank_3],
    #     [Measures].[Count_Rank_4], [Measures].[Count_Rank_5], [Measures].[Count_Rank_6],
    #     [Measures].[Count_Rank_7], [Measures].[Count_Rank_8], [Measures].[Count_Rank_9],
    #     [Measures].[Count_Rank_10]
    # }} ON COLUMNS,
    # NON EMPTY {{ [Dim Class].[Class SK].[Class SK].ALLMEMBERS }} 
    # DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    # ON ROWS 
    # FROM [cube_13062025]
    # WHERE ([Dim Class].[Class ID].[{selected_class}])
    # """
    
    # df_ranks = run_query(query_ranks, ["Class SK", "Class SK Dim", "Rank_1", "Rank_2", "Rank_3", "Rank_4", "Rank_5", "Rank_6", "Rank_7", "Rank_8", "Rank_9", "Rank_10"])

    # # 4. Performance Distribution
    # query_dist = f"""
    # SELECT NON EMPTY {{ 
    #     [Measures].[Count_Excellent], [Measures].[Count_Good], 
    #     [Measures].[Count_Average], [Measures].[Count_Poor] 
    # }} ON COLUMNS,
    # NON EMPTY {{ [Dim Class].[Class SK].[Class SK].ALLMEMBERS }} 
    # DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    # ON ROWS 
    # FROM [cube_13062025] 
    # WHERE ([Dim Class].[Class ID].[{selected_class}])
    # """
    # df_dist = run_query(query_dist, ["Class SK", "Class SK Dim", "Excellent", "Good", "Average", "Poor"])
    # for col in ["Excellent", "Good", "Average", "Poor"]:
    #     df_dist[col] = pd.to_numeric(df_dist[col], errors="coerce")
    # df_dist = df_dist.dropna()


    # # 5. Max/Min Scores
    # query_scores = f"""
    # SELECT NON EMPTY {{ 
    #     [Measures].[Max Final Note], [Measures].[Min Final Note] 
    # }} ON COLUMNS,
    # NON EMPTY {{ [Dim Class].[Class SK].[Class SK].ALLMEMBERS }} 
    # DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    # ON ROWS 
    # FROM [cube_13062025] 
    # WHERE ([Dim Class].[Class ID].[{selected_class}])
    # """
    # df_scores = run_query(query_scores, ["Class SK", "Class SK Dim", "Max Final Note", "Min Final Note"])
    # df_scores["Max Score"] = pd.to_numeric(df_scores["Max Final Note"], errors="coerce")
    # df_scores["Min Score"] = pd.to_numeric(df_scores["Min Final Note"], errors="coerce")
    # df_scores = df_scores.dropna(subset=["Max Score", "Min Score"])

    # start = time.time()

    # # 6. Pass/Fail Rate
    # query_pass_fail = f"""
    # SELECT NON EMPTY {{ 
    #     [Measures].[Rate_Fail], [Measures].[Rate_Pass] 
    # }} ON COLUMNS,
    # NON EMPTY {{ [Dim Class].[Class SK].[Class SK].ALLMEMBERS }} 
    # DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    # ON ROWS 
    # FROM [cube_13062025] 
    # WHERE ([Dim Class].[Class ID].[{selected_class}])
    # """
    # df_pass_fail = run_query(query_pass_fail, ["Class SK", "Class SK Dim", "Rate_Fail", "Rate_Pass"])
    # end = time.time()
    results = fetch_class_statistics(selected_class)

    # Truy cập từng DataFrame cụ thể
    df_avg = results["avg_score"]
    df_rates = results["performance_rates"]
    df_ranks = results["ranking_distribution"]
    df_dist = results["performance_distribution"]
    df_scores = results["min_max_scores"]
    df_pass_fail = results["pass_fail_rate"]
    # Layout
    # Phần chính: Average Score và Pass/Fail Rate
    col1, col2 = st.columns([1.5, 3])
    with col1:
        if not df_avg.empty and not df_scores.empty:
            df_avg = df_avg.sort_values(by="AVG_Overall", ascending=False)
            df_scores["Max Score"] = pd.to_numeric(df_scores["Max Score"], errors="coerce")
            df_scores["Min Score"] = pd.to_numeric(df_scores["Min Score"], errors="coerce")

            avg_score = df_avg.iloc[0]["AVG_Overall"]
            max_score = df_scores.iloc[0]["Max Score"]
            min_score = df_scores.iloc[0]["Min Score"]

            st.markdown("<h3>Overview Class Score</h3>", unsafe_allow_html=True)
            st.markdown("🔸 Average Score", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='stMetric'>
                    <div class='metric-value avg-value'>{avg_score:.1f}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("🔺 Max Score", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='stMetric'>
                    <div class='metric-value max-value'>{max_score:.1f}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("🔻 Min Score", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='stMetric'>
                    <div class='metric-value min-value'>{min_score:.1f}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='info-box'>No average score data available.</div>", unsafe_allow_html=True)

    with col2:
        
        if not df_pass_fail.empty:
            class_data = df_pass_fail.iloc[0]
            fig_pass_fail = go.Figure(data=[go.Pie(
                labels=["Pass", "Fail"],
                values=[
                    round(class_data.get("Rate_Pass", 0) * 100, 2),
                    round(class_data.get("Rate_Fail", 0) * 100, 2)
                ],
                hole=0.4,
                marker=dict(colors=["#66BB6A", "#EF5350"]),  # Green pastel for Pass, Red pastel for Fail
                hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
                sort=False,
                direction="clockwise"
            )])

            st.markdown("<h3>Pass/Fail Rate</h3>", unsafe_allow_html=True)
            fig_pass_fail.update_layout(
                height=430,
                plot_bgcolor='white',
                margin=dict(l=40, r=40, t=80, b=60),
                font=dict(size=12, color='#1e293b')
            )
            st.plotly_chart(fig_pass_fail, use_container_width=True)
        else:
            st.markdown("<div class='info-box'>No pass/fail data available.</div>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Max/Min Scores
    st.markdown("<h2>Max–Min Score Gap</h2>", unsafe_allow_html=True)
    if not df_scores.empty:
        class_id = df_scores["Class SK"].iloc[0]
        fig_scores = go.Figure()
        fig_scores.add_trace(go.Bar(
            y=[class_id], x=[df_scores["Max Score"].iloc[0]], name='Max Score',
            orientation='h', marker_color="#4CAF50",  # Green pastel for Max Score
            hovertemplate='Class: %{y}<br>Max Score: %{x}<extra></extra>'
        ))
        fig_scores.add_trace(go.Bar(
            y=[class_id], x=[df_scores["Min Score"].iloc[0]], name='Min Score',
            orientation='h', marker_color='#EF5350',  # Red pastel for Min Score
            hovertemplate='Class: %{y}<br>Min Score: %{x}<extra></extra>'
        ))
        fig_scores.update_layout(
            barmode='group', xaxis_title="Score", yaxis_title="Class",
            title=None, plot_bgcolor='white',
            height=200, hovermode='closest',
            legend=dict(x=1, y=1.1, xanchor='right'),
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(size=12, color='#1e293b')
        )
        st.plotly_chart(fig_scores, use_container_width=True)
    else:
        st.markdown("<div class='info-box'>No max/min score data available.</div>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Distribution Rank Student
    st.markdown("<h2>Distribution of Scores Across the Entire Course</h2>", unsafe_allow_html=True)
    if not df_ranks.empty:
        class_id = df_scores["Class SK"].iloc[0]
        df_plot = pd.DataFrame({
            "Score Range": [f"{i}-{i+1}" for i in range(10)],
            "Number of students": df_ranks.iloc[0, 2:].values
        })

        fig_ranks = px.bar(
            df_plot,
            x="Score Range",
            y="Number of students",
            text_auto=True,
            labels={"Number of students": "Số sinh viên"},
            color_discrete_sequence=["#4CAF50"]  # Blue pastel for neutral distribution
        )

        fig_ranks.update_layout(
            height=450,
            margin=dict(t=60, b=60, l=40, r=40),
            xaxis_title="Score Range",
            yaxis_title="Number of Students",
            font=dict(size=14),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig_ranks, use_container_width=True)
    else:
        st.markdown("<div class='info-box'>No Scores Across data available.</div>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Performance Rates (Doughnut Charts)
    st.markdown("<h2>Performance Rates</h2>", unsafe_allow_html=True)
    if not df_rates.empty:
        try:
            rates = df_rates.iloc[0]
            col3, col4, col5, col6 = st.columns(4)
            with col3:
                draw_doughnut("Excellent", rates["Rate_Excellent"] * 100, "#388E3C")  # Dark Green pastel for Excellent
            with col4:
                draw_doughnut("Good", rates["Rate_Good"] * 100, "#66BB6A")  # Green pastel for Good
            with col5:
                draw_doughnut("Average", rates["Rate_Average"] * 100, "#FFCA28")  # Yellow pastel for Average
            with col6:
                draw_doughnut("Poor", rates["Rate_Poor"] * 100, "#EF5350")  # Red pastel for Poor
        except Exception as e:
            st.markdown(f"<div class='info-box'>Error processing performance rates: {str(e)}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='info-box'>No performance rate data available.</div>", unsafe_allow_html=True)

    # Performance Distribution
    st.markdown("<h2>Student Performance Distribution</h2>", unsafe_allow_html=True)
    if not df_dist.empty:
        class_id = df_dist["Class SK"].iloc[0]
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Bar(y=[class_id], x=[df_dist["Excellent"].iloc[0]],
            name="Excellent", orientation='h', marker_color="#388E3C",  # Dark Green pastel for Excellent
            hovertemplate="Excellent: %{x}<extra></extra>"))
        fig_dist.add_trace(go.Bar(y=[class_id], x=[df_dist["Good"].iloc[0]],
            name="Good", orientation='h', marker_color="#66BB6A",  # Green pastel for Good
            hovertemplate="Good: %{x}<extra></extra>"))
        fig_dist.add_trace(go.Bar(y=[class_id], x=[df_dist["Average"].iloc[0]],
            name="Average", orientation='h', marker_color="#FFCA28",  # Yellow pastel for Average
            hovertemplate="Average: %{x}<extra></extra>"))
        fig_dist.add_trace(go.Bar(y=[class_id], x=[df_dist["Poor"].iloc[0]],
            name="Poor", orientation='h', marker_color="#EF5350",  # Red pastel for Poor
            hovertemplate="Poor: %{x}<extra></extra>"))
        fig_dist.update_layout(
            barmode='group', title=None,
            xaxis_title="Number of Students", yaxis_title="Class",
            height=350, plot_bgcolor='white', hovermode='closest',
            legend=dict(x=1, y=1.1, xanchor='right'),
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(size=12, color='#1e293b'),
            bargap=0.3,
            bargroupgap=0.3
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.markdown("<div class='info-box'>No performance distribution data available.</div>", unsafe_allow_html=True)

    # Cuộn về đầu trang
    st.markdown("""
        <script>
            window.scrollTo(0, 0);
        </script>
    """, unsafe_allow_html=True)
 
elif selected == "Learning Behavior":
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        .main {
            background-color: none;
            padding: 2rem;
            font-family: 'Inter', sans-serif;
            color: #1e293b;
        }
        .stApp { color: #111827; }
        .card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
            border: 1px solid #E5E7EB;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }
        .stMetric {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            text-align: left;
            transition: transform 0.2s;
        }
        .stMetric:hover {
            transform: translateY(-4px);
        }
        .metric-label {
            font-size: 1.1rem;
            font-weight: 500;
            color: #64748b;
            margin-bottom: 0.5rem;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
        }
        .metric-value.avg-value {
            color: #F97316;  /* Orange */
        }
        .metric-value.max-value {
            color: #10B981;  /* Green */
        }
        .metric-value.min-value {
            color: #EF4444;  /* Red */
        }
        h1 { color: #111827; font-weight: 700; font-size: 2rem; text-align: center; margin-bottom: 2rem; }
        h2 { color: #1F2937; font-weight: 600; font-size: 1.5rem; margin-bottom: 1rem; }
        h3 { color: #1F2937; font-weight: 500; font-size: 1.25rem; margin-bottom: 0.75rem; }

        .stRadio > div { flex-direction: row; gap: 1rem; }
        .stMetric { font-size: 1.25rem; color: #111827; }
        
        .divider {
            border-top: 1px solid #e5e7eb;
            margin: 2rem 0;
        }
        .stPlotlyChart {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    class_list = load_class_list()
    default_index = class_list.index("22CLC01 - Hệ điều hành") if "22CLC01 - Hệ điều hành" in class_list else 0
    selected_class_full = st.selectbox("Select Class", class_list, index=default_index)

    # Lấy phần trước dấu "-"
    selected_class = selected_class_full.split(" - ")[0]

    
    # --- Section 1: Class Overview ---
    st.markdown("<h2>Class Performance Overview</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("<h3>Average Quiz Time</h3>", unsafe_allow_html=True)
        mdx_avg_time = f"""
        SELECT 
            {{ [Measures].[AVG_QuizTime] }} ON COLUMNS 
        FROM [cube_13062025] 
        WHERE ([Dim Class].[Class ID].[{selected_class}])
        """
        df_avg_time = run_query(mdx_avg_time, ["AVG_QuizTime"])
        if not df_avg_time.empty:
            df_avg_time["AVG_QuizTime"] = pd.to_numeric(df_avg_time["AVG_QuizTime"], errors="coerce")
            avg_val = df_avg_time["AVG_QuizTime"].mean()
            fig1 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=avg_val,
                title={"text": "Average Time (s)", "font": {"size": 14}},
                gauge={
                    'axis': {'range': [0, max(30, avg_val * 1.5)]},
                    'bar': {'color': "#388E3C"},
                    'steps': [
                        {'range': [0, avg_val], 'color': "#C8E6C9"},
                        {'range': [avg_val, avg_val * 1.5], 'color': "#FFF59D"}
                    ]
                }
            ))
            fig1.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=200, plot_bgcolor="white")
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("<h3>Quiz Completion Rate</h3>", unsafe_allow_html=True)
        mdx_completion = f"""
        SELECT 
        NON EMPTY {{ 
            [Measures].[Rate_QuizCompleted], 
            [Measures].[Rate_QuizNotCompleted] 
        }} ON COLUMNS
        FROM [cube_13062025] 
        WHERE ([Dim Class].[Class ID].[{selected_class}])
        """
        df_completion = run_query(mdx_completion, ["Rate_QuizCompleted", "Rate_QuizNotCompleted"])
        if not df_completion.empty:
            d = df_completion.iloc[0]
            fig2 = go.Figure(data=[go.Pie(
                labels=["Completed", "Not Completed"],
                values=[round(d["Rate_QuizCompleted"]*100, 1), round(d["Rate_QuizNotCompleted"]*100, 1)],
                hole=0.4,
                marker=dict(colors=["#66BB6A", "#EF5350"]),
                hovertemplate="%{label}: %{value:.1f}%<extra></extra>"
            )])
            fig2.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=200, plot_bgcolor="white", font=dict(size=12, color="#111827"))
            st.plotly_chart(fig2, use_container_width=True)

    # --- Section 2: Student Performance ---
    st.markdown("<h2>Student Performance Analysis</h2>", unsafe_allow_html=True)
    st.markdown("<h3>Quiz Time Distribution</h3>", unsafe_allow_html=True)
    mdx_quiz_time = f"""
    SELECT NON EMPTY {{ [Measures].[AVG_QuizTime] }} ON COLUMNS, 
    NON EMPTY {{ 
        [Dim Student].[Student ID].[Student ID].ALLMEMBERS 
    }} 
    DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    ON ROWS 
    FROM [cube_13062025] 
    WHERE ([Dim Class].[Class ID].[{selected_class}]) 
    CELL PROPERTIES VALUE
    """
    df_quiz_time = run_query(mdx_quiz_time, ["Student ID", "Student ID Dim", "Time Taken"])
    if not df_quiz_time.empty:
        df = df_quiz_time.copy()
        df["Time Taken"] = pd.to_numeric(df["Time Taken"], errors="coerce")
        df["Class ID"] = selected_class  
        chart_type = st.radio("Select chart type", ["Box Plot", "Violin Plot"], horizontal=True)
        df_for_plot = df.reset_index()
        if chart_type == "Box Plot":
            fig3 = px.box(df_for_plot, x="Class ID", y="Time Taken", color_discrete_sequence=["#66BB6A"])
        else:
            fig3 = px.violin(df_for_plot, x="Class ID", y="Time Taken", box=True, color_discrete_sequence=["#66BB6A"])
        fig3.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=400, plot_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)

    # --- Top 10 Most / Least Active Students ---
    col1, col2 = st.columns(2)
    mdx_activities = f"""
    SELECT NON EMPTY {{ [Measures].[Sum_NumOfActivity] }} ON COLUMNS, 
    NON EMPTY {{ [Dim Student].[Student ID].[Student ID].ALLMEMBERS }} 
    DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
    ON ROWS 
    FROM [cube_13062025] 
    WHERE ([Dim Class].[Class ID].[{selected_class}])
    """
    df_activities = run_query(mdx_activities, ["Student ID", "Student ID Dim", "Sum_NumOfActivity"])
    if not df_activities.empty:
        df_activities.rename(columns={"Sum_NumOfActivity": "Activity Count"}, inplace=True)
        df_activities["Activity Count"] = pd.to_numeric(df_activities["Activity Count"], errors="coerce")

        with col1:
            df_top10_max = df_activities.sort_values("Activity Count", ascending=False).head(10)
            df_sorted_max = df_top10_max.sort_values("Activity Count", ascending=True)
            fig_max = go.Figure()
            for _, row in df_sorted_max.iterrows():
                fig_max.add_trace(go.Scatter(x=[0, row["Activity Count"]], y=[row["Student ID"]]*2, mode='lines',
                                            line=dict(color="#A5D6A7", width=2), showlegend=False))
                fig_max.add_trace(go.Scatter(x=[row["Activity Count"]], y=[row["Student ID"]]*2, mode='markers',
                                            marker=dict(color="#2E7D32", size=8), showlegend=False))
            fig_max.update_layout(title="Top 10 Most Active Students", height=500,
                                margin=dict(l=20, r=20, t=40, b=5), plot_bgcolor="white")
            st.plotly_chart(fig_max, use_container_width=True)
            avg_count = df_sorted_max["Activity Count"].mean()
            st.markdown(
                f"""
                <div style='text-align:center; font-size:16px; margin-top:1px;'>
                    <b>Avg activity count:</b> {avg_count:.2f}
                </div>
                """,
                unsafe_allow_html=True
            )


        with col2:
            df_top10_min = df_activities.sort_values("Activity Count", ascending=True).head(10)
            df_sorted_min = df_top10_min.sort_values("Activity Count", ascending=True)
            fig_min = go.Figure()
            for _, row in df_sorted_min.iterrows():
                fig_min.add_trace(go.Scatter(x=[0, row["Activity Count"]], y=[row["Student ID"]]*2, mode='lines',
                                            line=dict(color="#FFCCBC", width=2), showlegend=False))
                fig_min.add_trace(go.Scatter(x=[row["Activity Count"]], y=[row["Student ID"]]*2, mode='markers',
                                            marker=dict(color="#EF5350", size=8), showlegend=False))
            fig_min.update_layout(title="Top 10 Least Active Students", height=500,
                                margin=dict(l=20, r=20, t=40, b=5), plot_bgcolor="white")
            st.plotly_chart(fig_min, use_container_width=True)
            avg_count_min = df_sorted_min["Activity Count"].mean()
            st.markdown(f"""
                <div style='text-align:center; font-size:16px; margin-top:1px;'>
                        <b>Avg activity count:</b> {avg_count_min:.2f}
                </div>
            """, unsafe_allow_html=True)

    # --- Section 3: Course Feedback ---
    st.markdown("<h2>Course Feedback</h2>", unsafe_allow_html=True)
    col3, col4 = st.columns([1, 3])

    with col3:
        st.markdown("<h3>Rating Summary</h3>", unsafe_allow_html=True)
        mdx_rating = f"""
        SELECT 
            {{ [Measures].[AVG_Rating] }} ON COLUMNS
        FROM [cube_13062025] 
        WHERE ([Dim Class].[Class ID].[{selected_class}])
        """
        df_rating = run_query(mdx_rating, ["AVG_Rating"])

        mdx_avg_question = f"""
        SELECT 
            NON EMPTY {{ [Measures].[AVG_Rating] }} ON COLUMNS, 
            NON EMPTY {{ [Dim Question].[Question ID].[Question ID].ALLMEMBERS }} 
            DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
        ON ROWS 
        FROM [cube_13062025]
        WHERE ([Dim Class].[Class ID].[{selected_class}])
        """
        df_avg_question = run_query(mdx_avg_question, ["Question ID", "Question ID Dim", "AVG_Rating"])

        if not df_rating.empty and not df_avg_question.empty:
            df_rating["AVG_Rating"] = pd.to_numeric(df_rating["AVG_Rating"], errors="coerce")
            df_avg_question["AVG_Rating"] = pd.to_numeric(df_avg_question["AVG_Rating"], errors="coerce")

            avg_rating = df_rating["AVG_Rating"].mean()
            max_rating = df_avg_question["AVG_Rating"].max()
            min_rating = df_avg_question["AVG_Rating"].min()

            st.markdown("🔸 Average Rating", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='stMetric'>
                    <div class='metric-value avg-value'>{avg_rating:.2f}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("🔺 Max Rating", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='stMetric'>
                    <div class='metric-value max-value'>{max_rating:.2f}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("🔻 Min Rating", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='stMetric'>
                    <div class='metric-value min-value'>{min_rating:.2f}</div>
                </div>
            """, unsafe_allow_html=True)

    with col4:
        st.markdown("<h3>Average Rating per Question</h3>", unsafe_allow_html=True)
        df_avg_question = run_query(mdx_avg_question, ["Question ID", "Question ID Dim", "AVG_Rating"])
        if not df_avg_question.empty:
            df_avg_question["AVG_Rating"] = pd.to_numeric(df_avg_question["AVG_Rating"], errors="coerce")
            df_avg_question["Question ID"] = pd.to_numeric(df_avg_question["Question ID"], errors="coerce")
            df_avg_question = df_avg_question.sort_values("Question ID", ascending=True)
            fig_rating = px.scatter(
                df_avg_question,
                x="Question ID",
                y="AVG_Rating",
                size_max=10,
                hover_data=["Question ID", "AVG_Rating"],
                labels={"AVG_Rating": "Average Rating", "Question ID": "Question"},
                color_discrete_sequence=["#66BB6A"]
            )
            fig_rating.update_traces(marker=dict(size=6, line=dict(width=1, color="#1B5E20")))
            fig_rating.update_layout(
                height=430,
                xaxis_title="Question ID",
                yaxis_title="Average Rating",
                margin=dict(l=40, r=40, t=40, b=40),
                plot_bgcolor="white",
                title=None
            )
            st.plotly_chart(fig_rating, use_container_width=True)

    # Average Rating by Category
    st.markdown("<h3>Average Rating by Category</h3>", unsafe_allow_html=True)
    mdx_avg_category = f"""
    SELECT NON EMPTY {{ [Measures].[AVG_Rating] }} ON COLUMNS, 
    NON EMPTY {{ ([Dim Question].[Question ID].[Question ID].ALLMEMBERS ) }} 
    DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME ON ROWS 
    FROM [cube_13062025] WHERE ([Dim Class].[Class ID].[{selected_class}])
    """
    df_avg_category = run_query(mdx_avg_category, ["Question ID", "Question ID Dim", "AVG_Rating"])
    if not df_avg_category.empty:
        df_avg_category["Question ID"] = pd.to_numeric(df_avg_category["Question ID"], errors="coerce")
        df_avg_category["AVG_Rating"] = pd.to_numeric(df_avg_category["AVG_Rating"], errors="coerce")
        question_group_map = {
            "Course Materials": [1, 2, 3],
            "Course Usefulness": [4, 5],
            "Teaching Methods": [6, 7, 8, 9, 10, 11, 19, 20],
            "Student Interaction": [12, 13, 21],
            "Assessment and Exams": [14, 15, 16, 17, 18],
            "Overall Satisfaction": [22, 23, 24, 25]
        }
        def map_category(qid):
            for category, ids in question_group_map.items():
                if qid in ids:
                    return category
            return "Other"
        df_avg_category["Category"] = df_avg_category["Question ID"].apply(map_category)
        df_category_avg = df_avg_category.groupby("Category", as_index=False)["AVG_Rating"].mean().round(2)
        df_category_avg = df_category_avg.sort_values("AVG_Rating", ascending=False)
        fig = px.bar(
            df_category_avg,
            x="AVG_Rating",
            y="Category",
            orientation="h",
            text="AVG_Rating",
            color="AVG_Rating",
            color_continuous_scale=["#FFCA28", "#4CAF50"],
            labels={"AVG_Rating": "Average Rating", "Category": "Category"},
        )
        fig.update_traces(
            texttemplate='<b>%{text:.2f}</b>',
            textposition='outside',
            marker_line_width=0.5,
            hovertemplate="%{y}<br>⭐ %{x:.2f}<extra></extra>"
        )
        fig.update_layout(
            xaxis=dict(range=[4.5, 4.8], title=""),
            yaxis=dict(title="", tickfont=dict(size=14)),
            coloraxis_showscale=False,
            height=350,
            margin=dict(l=30, r=30, t=50, b=30),
            plot_bgcolor="#ffffff",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Scroll to top
    st.markdown("""
        <script>
            window.scrollTo(0, 0);
        </script>
    """, unsafe_allow_html=True)

elif selected == "Correlation Analysis":
    col, col2 = st.columns(2)
    with col:
        class_list = load_class_list()
        default_index = class_list.index("22CLC01 - Hệ điều hành") if "22CLC01 - Hệ điều hành" in class_list else 0
        selected_class_full = st.selectbox("Select Class", class_list, index=default_index)

        # Lấy phần trước dấu "-"
        selected_class = selected_class_full.split(" - ")[0]
    with col2:
        category = st.selectbox(
            "Select Analysis Category",
            options=[
                "Student Activity Summary",
                "Quiz Time",
                "Quiz Score",
                "Lab Score",
                "Final Exam Score",
                "Bonus Score"
            ],
            index=0
        )

    mdx_quiz = f"""
    SELECT 
        NON EMPTY {{ [Measures].[AVG_QuizTime], [Measures].[AVG_Overall] }} ON COLUMNS,
        NON EMPTY {{ 
            ([Dim Student].[Student SK].[Student SK].ALLMEMBERS) 
        }}
        DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME ON ROWS
    FROM [cube_13062025] 
    WHERE ([Dim Class].[Class ID].[{selected_class}])
    """


    mdx_activity = f"""
    SELECT 
        NON EMPTY {{ [Measures].[AVG_Overall], [Measures].[Sum_NumOfActivity] }} ON COLUMNS,
        NON EMPTY {{ 
            ([Dim Student].[Student SK].[Student SK].ALLMEMBERS) 
        }} 
        DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME ON ROWS 
    FROM [cube_13062025] 
    WHERE ([Dim Class].[Class ID].[{selected_class}])
    """

    mdx_lab= f"""
    SELECT 
        NON EMPTY {{ [Measures].[AVG_Score], [Measures].[AVG_Overall] }} ON COLUMNS,
        NON EMPTY {{ 
            ([Dim Student].[Student ID].[Student ID].ALLMEMBERS 
            * {{ [DimType Point].[Type Name].&[Quiz] }}) 
        }} 
        DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
        ON ROWS 
    FROM [cube_13062025] 
    WHERE ([Dim Class].[Class ID].[{selected_class}])
    """
    mdx_quiz_score = f"""
    SELECT 
        NON EMPTY {{ [Measures].[AVG_Score], [Measures].[AVG_Overall] }} ON COLUMNS,
        NON EMPTY {{ 
            ([Dim Student].[Student ID].[Student ID].ALLMEMBERS 
            * {{ [DimType Point].[Type Name].&[Quiz] }}) 
        }} 
        DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
        ON ROWS 
    FROM [cube_13062025] 
    WHERE ([Dim Class].[Class ID].[{selected_class}])
    """

    mdx_final_ex= f"""
    SELECT 
        NON EMPTY {{ [Measures].[AVG_Score], [Measures].[AVG_Overall] }} ON COLUMNS,
        NON EMPTY {{ 
            ([Dim Student].[Student ID].[Student ID].ALLMEMBERS 
            * {{ [DimType Point].[Type Name].&[Final exam] }}) 
        }} 
        DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
        ON ROWS 
    FROM [cube_13062025] 
    WHERE ([Dim Class].[Class ID].[{selected_class}])
    """
    mdx_bonus= f"""
    SELECT 
        NON EMPTY {{ [Measures].[AVG_Score], [Measures].[AVG_Overall] }} ON COLUMNS,
        NON EMPTY {{ 
            ([Dim Student].[Student ID].[Student ID].ALLMEMBERS 
            * {{ [DimType Point].[Type Name].&[Bonus] }}) 
        }} 
        DIMENSION PROPERTIES MEMBER_CAPTION, MEMBER_UNIQUE_NAME 
        ON ROWS 
    FROM [cube_13062025] 
    WHERE ([Dim Class].[Class ID].[{selected_class}])
    """

    # --- Run queries ---
    queries = {
        "Quiz Time": (mdx_quiz, ["Student SK", "Student SK Dim", "AVG_QuizTime", "AVG_Overall"]),
        "Student Activity Summary": (mdx_activity, ["Student SK", "Student SK Dim", "AVG_Overall", "Sum_NumOfActivity"]),
        "Quiz Score": (mdx_quiz_score, ["Student ID", "Student ID Dim", "Type Name", "Type Name Dim", "AVG_Score", "AVG_Overall"]),
        "Lab Score": (mdx_lab, ["Student ID", "Student ID Dim", "Type Name", "Type Name Dim", "AVG_Score", "AVG_Overall"]),
        "Final Exam Score": (mdx_final_ex, ["Student ID", "Student ID Dim", "Type Name", "Type Name Dim", "AVG_Score", "AVG_Overall"]),
        "Bonus Score": (mdx_bonus, ["Student ID", "Student ID Dim", "Type Name", "Type Name Dim", "AVG_Score", "AVG_Overall"]),
    }

    results = {}
    for key, (mdx, cols) in queries.items():
        results[key] = run_query(mdx, cols)

    # --- Visualization logic ---
    def render_scatter_chart(df, x_col, y_col, hover_col, x_label, y_label, title):
        x = pd.to_numeric(df[x_col], errors="coerce")
        y = pd.to_numeric(df[y_col], errors="coerce")
        hover = df[hover_col]

        fig = px.scatter(
            x=x,
            y=y,
            hover_name=hover,
            color_discrete_sequence=["#66BB6A"],  # Harmonized green tone
            labels={"x": x_label, "y": y_label},
            title=title
        )
        corr, _ = pearsonr(x.dropna(), y.dropna())
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"**Pearson Correlation Coefficient (r):** `{corr:.3f}`")
        st.markdown("---")

    # --- Chart rendering ---
    if category == "Quiz Time":
        df = results["Quiz Time"]
        if not df.empty:
            render_scatter_chart(
                df,
                "AVG_QuizTime",
                "AVG_Overall",
                "Student SK Dim",
                "Average Quiz Time",
                "Final Score",
                "Quiz Time vs Final Score"
            )

    elif category == "Student Activity Summary":
        df = results["Student Activity Summary"]
        if not df.empty:
            render_scatter_chart(
                df,
                "Sum_NumOfActivity",
                "AVG_Overall",
                "Student SK Dim",
                "Total Interactions",
                "Final Score",
                "Interaction Count vs Final Score"
            )

    elif category in ["Quiz Score", "Lab Score", "Final Exam Score", "Bonus Score"]:
        df = results[category]
        if not df.empty:
            render_scatter_chart(
                df,
                "AVG_Score",
                "AVG_Overall",
                "Student ID Dim",
                f"{category}",
                "Final Score",
                f"{category} vs Final Score"
            )

elif selected == "Data Management":
    col1, col2 = st.columns([7, 1])  

    with col1:
        st.markdown("""
            <div style='background-color: #ffff; padding: 16px; border-radius: 0px; border: 0px solid #e5e7eb;'>
                <div style='display: flex; gap: 12px; align-items: center;'>
                    <img src='https://cdn-icons-png.flaticon.com/512/5415/5415206.png' width='48'>
                    <div>
                        <p style='font-size: 20px; font-weight: 600; margin: 0; color: #1F2A44;'>Data Management</p>
                        <p style='font-size: 16px; color: #4B5563; margin: 4px 0;'>Import data using system-provided sample templates.</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


    with col2:
    # Tạo file zip trong bộ nhớ
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.write("Sample_Data.xlsx", arcname="Sample_Data.xlsx")
            zip_file.write("Sample_Quiz.xlsx", arcname="Sample_Quiz.xlsx")

        zip_buffer.seek(0)

        st.download_button(
            label="Download sample",
            data=zip_buffer,
            file_name="sample_files.zip",
            mime="application/zip"
        )


    st.markdown("</div></div></div>", unsafe_allow_html=True)

    # File uploader
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = "multi_file_uploader"

    uploaded_files = st.file_uploader(
        "📁 Upload Excel files (XLSX):",
        type=["xlsx"],
        accept_multiple_files=True,
        key=st.session_state.uploader_key
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} files uploaded successfully.")
        st.markdown("<div style='text-align: right; margin-top: 10px;'>", unsafe_allow_html=True)
        if st.button("⬆️ Import All"):
            success, message = import_file(uploaded_files)
            if success:
                st.success(message)
                st.session_state.uploader_key = f"multi_file_uploader_{uuid.uuid4()}"
                time.sleep(1.5)
                experimental_rerun()
            else:
                st.error(f"❌ {message}")
        st.markdown("</div>", unsafe_allow_html=True)
