import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import googlemaps
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import plotly.express as px
import sqlite3
from datetime import datetime, timedelta

# --- 1. 初期設定 & データベース準備 ---
st.set_page_config(page_title="次世代物流シミュレーター", layout="wide")

def init_db():
    conn = sqlite3.connect('logistics_v2.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, vehicle_id TEXT, 
         route_summary TEXT, total_distance REAL, status TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- 2. 最適化ロジック (OR-Tools) ---
def solve_tsp(dist_matrix):
    manager = pywrapcp.RoutingIndexManager(len(dist_matrix), 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    def distance_callback(from_index, to_index):
        return dist_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(search_parameters)
    
    route = []
    if solution:
        index = routing.Start(0)
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))
    return route

# --- 3. メインUI (サイドバー & タブ) ---
st.sidebar.title("🛠 設定パネル")
api_key = st.sidebar.text_input("Google Maps API Key", type="password")
vehicle_id = st.sidebar.selectbox("車両選択", ["Truck-01", "Truck-02", "Van-05"])

tab1, tab2 = st.tabs(["🚀 ルート計画・実行", "📊 運行実績分析"])

# --- タブ1: ルート計画 ---
with tab1:
    st.header("配送ルートの最適化")
    address_input = st.text_area("配送先リスト (1行に1つ、最初はデポ)", 
                                 "東京駅\n新宿駅\n浅草寺\n品川駅", height=120)
    
    if st.button("最適化シミュレーション開始"):
        if not api_key:
            st.error("APIキーが必要です")
        else:
            gmaps = googlemaps.Client(key=api_key)
            with st.spinner("データを取得中..."):
                addresses = [a.strip() for a in address_input.split("\n") if a.strip()]
                
                # ジオコーディング & 距離行列取得
                geo_data = [gmaps.geocode(addr)[0]['geometry']['location'] for addr in addresses]
                matrix_res = gmaps.distance_matrix(addresses, addresses, mode='driving')
                
                dist_matrix = []
                for row in matrix_res['rows']:
                    dist_matrix.append([el['distance']['value'] for el in row['elements']])
                
                # 最適化実行
                optimized_indices = solve_tsp(dist_matrix)
                
                # 結果表示
                col_left, col_right = st.columns([2, 1])
                
                with col_left:
                    m = folium.Map(location=[geo_data[0]['lat'], geo_data[0]['lng']], zoom_start=12)
                    route_coords = [[geo_data[i]['lat'], geo_data[i]['lng']] for i in optimized_indices]
                    folium.PolyLine(route_coords, color="blue", weight=5).add_to(m)
                    for i, idx in enumerate(optimized_indices[:-1]):
                        folium.Marker(route_coords[i], tooltip=addresses[idx], 
                                      icon=folium.Icon(color="red" if i==0 else "blue")).add_to(m)
                    st_folium(m, width=700, height=500)

                with col_right:
                    st.subheader("配送スケジュール")
                    total_dist_km = sum(dist_matrix[optimized_indices[i]][optimized_indices[i+1]] for i in range(len(optimized_indices)-1)) / 1000
                    st.write(f"**総走行距離:** {total_dist_km:.2f} km")
                    
                    # ログ保存ボタン
                    if st.button("このルートで確定・保存"):
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO logs (date, vehicle_id, route_summary, total_distance, status) VALUES (?, ?, ?, ?, ?)",
                                       (datetime.now().strftime("%Y-%m-%d"), vehicle_id, " -> ".join(addresses), total_dist_km, "正常"))
                        conn.commit()
                        st.success("実績をデータベースに記録しました！")

# --- タブ2: 分析ダッシュボード ---
with tab2:
    st.header("運行データ分析")
    df = pd.read_sql_query("SELECT * FROM logs", conn)
    
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig_dist = px.bar(df, x='date', y='total_distance', color='vehicle_id', title="日別走行距離推移")
            st.plotly_chart(fig_dist)
        with c2:
            fig_pie = px.pie(df, names='vehicle_id', title="車両別稼働比率")
            st.plotly_chart(fig_pie)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("実績データがありません。")
