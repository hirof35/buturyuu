
🚚 Next-Gen Logistics Simulator
~ Google OR-Tools と Streamlit による配送ルート最適化プラットフォーム ~
Next-Gen Logistics Simulator は、複雑な配送経路を数秒で最適化し、リアルタイムな運行管理と実績分析を可能にする、物流DXのための統合型シミュレーションツールです。

🌟 プロジェクトの概要
現代の物流現場において、経験則に頼ったルート作成はコストと環境負荷を増大させます。
本プロジェクトでは、Googleの OR-Tools を活用した巡回セールスマン問題（TSP）の解決と、Google Maps Platform の距離行列APIを連携させることで、渋滞や道路情報を考慮した「最短・最速」のルートを動的に生成します。

✨ 主な機能
インテリジェント・ルート計画 (TSP):

Google OR-Tools による最適解の算出。

地名入力だけで座標（Geocoding）と移動コスト（Distance Matrix）を自動取得。

対話型マップ・ビジュアライザー:

folium を用いたインタラクティブな地図表示。

最適化された巡回ルートを地図上にポリラインで即座に描画。

運行データ管理システム:

SQLiteによる軽量・高速なデータベース管理。

車両ID、日付、総距離、ルート概要を永続化。

分析ダッシュボード:

Plotly を用いたグラフィカルな分析。

日別の走行距離推移や車両稼働率を視覚化し、フリート（車両群）の最適化を支援。

🛠 技術スタック
Frontend: Streamlit

Optimization Engine: Google OR-Tools (Constraint Solver)

API Integration: Google Maps Platform (Geocoding / Distance Matrix)

Visualization: Folium, Plotly Express

Database: SQLite3

Language: Python 3.10+

🚀 セットアップ
APIキーの取得: Google Maps Platform からAPIキーを取得してください。

依存ライブラリのインストール:

Bash
pip install streamlit pandas googlemaps ortools folium streamlit-folium plotly
アプリケーションの起動:

Bash
streamlit run main.py
📈 シミュレーションの流れ
サイドバーで Google Maps API Key を入力。

配送先リストを入力（1行目がデポ/出発点になります）。

「最適化シミュレーション開始」をクリック。

生成されたルートを地図で確認し、問題なければ「確定・保存」を実行。

分析タブ で、蓄積されたデータの傾向を確認。

📜 ライセンス
MIT License

「物流の最適化は、世界の構造を書き換える。」
