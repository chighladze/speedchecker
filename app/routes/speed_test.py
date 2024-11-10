# speedchecker/app/routes/speed_test.py
from flask import Blueprint, jsonify, request, render_template
import speedtest

sp = Blueprint('sp', __name__, template_folder='../templates/speedtest')


@sp.route('/', methods=['GET'])
def index():
    # Отображаем HTML-шаблон
    return render_template('index.html')


@sp.route('/servers', methods=['GET'])
def get_servers():
    try:
        print("Initializing Speedtest client...")
        st = speedtest.Speedtest()

        print("Retrieving servers...")
        st.get_servers()  # Загружаем все доступные серверы
        servers = st.servers

        if not servers:
            print("No servers found.")
            return jsonify({"error": "No servers found"}), 500

        server_list = []

        # Преобразуем серверы в удобный формат JSON
        for server in servers.values():
            for s in server:
                server_list.append({
                    'id': s['id'],
                    'name': s['name'],
                    'country': s['country'],
                    'sponsor': s['sponsor'],
                    'distance': s['d']
                })

        print(f"Total servers found: {len(server_list)}")

        # Сортируем серверы по расстоянию
        server_list = sorted(server_list, key=lambda x: x['distance'])

        return jsonify(server_list)
    except Exception as e:
        print(f"Error retrieving servers: {e}")  # Отладочный вывод
        return jsonify({"error": str(e)}), 500


@sp.route('/run', methods=['POST'])
def run_speedtest():
    try:
        data = request.json
        server_id = data.get('server_id')

        st = speedtest.Speedtest()

        # Устанавливаем сервер, если он был выбран
        if server_id:
            st.get_servers([server_id])
            st.get_best_server()
        else:
            st.get_best_server()  # Автоматически выбираем ближайший

        download_speed = st.download() / 1_000_000  # Мбит/с
        upload_speed = st.upload() / 1_000_000  # Мбит/с
        ping = st.results.ping

        return jsonify({
            "download_speed": round(download_speed, 2),
            "upload_speed": round(upload_speed, 2),
            "ping": ping
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sp.route('/test', methods=['GET'])
def test_speedtest():
    try:
        st = speedtest.Speedtest()
        st.get_servers()
        print("Servers retrieved:", st.servers)
        return jsonify({"status": "Servers retrieved"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
