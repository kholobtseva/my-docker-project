import requests
import time
import json

def wait_for_graylog():
    """Ждем пока Graylog станет доступен"""
    print("⏳ Ожидаем запуск Graylog...")
    for i in range(60):
        try:
            response = requests.get("http://graylog:9000/api", timeout=5)
            if response.status_code == 200:
                print("✅ Graylog готов!")
                return True
        except:
            pass
        time.sleep(3)
    print("❌ Graylog не запустился за 3 минуты")
    return False

def setup_graylog_input():
    """Создаем и запускаем GELF UDP Input"""
    
    try:
        # Заголовки для CSRF защиты
        headers = {
            "Content-Type": "application/json",
            "X-Requested-By": "graylog-setup-script"
        }
        
        # Получаем список Inputs
        response = requests.get(
            "http://graylog:9000/api/system/inputs",
            auth=("admin", "admin"),
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            inputs = response.json()['inputs']
            gelf_input = None
            
            # Ищем существующий GELF Input
            for input in inputs:
                if input['type'] == 'org.graylog2.inputs.gelf.udp.GELFUDPInput':
                    gelf_input = input
                    break
            
            if gelf_input:
                print("✅ GELF Input найден")
                # Проверяем статус через отдельный запрос
                status_response = requests.get(
                    f"http://graylog:9000/api/system/inputs/{gelf_input['id']}",
                    auth=("admin", "admin"),
                    headers=headers
                )
                
                if status_response.status_code == 200:
                    input_status = status_response.json()
                    if not input_status['attributes']['running']:
                        # Запускаем если остановлен
                        start_response = requests.post(
                            f"http://graylog:9000/api/system/inputs/{gelf_input['id']}/start",
                            auth=("admin", "admin"),
                            headers=headers
                        )
                        if start_response.status_code == 204:
                            print("✅ GELF Input запущен!")
                        else:
                            print(f"❌ Ошибка запуска: {start_response.status_code}")
                    else:
                        print("✅ GELF Input уже запущен")
                else:
                    print("❌ Не удалось получить статус Input")
            else:
                # СОЗДАЕМ новый Input
                print("🔄 Создаем новый GELF Input...")
                input_data = {
                    "title": "Python Apps Logs",
                    "type": "org.graylog2.inputs.gelf.udp.GELFUDPInput",
                    "configuration": {
                        "bind_address": "0.0.0.0",
                        "port": 12201,
                        "recv_buffer_size": 262144
                    },
                    "global": True
                }
                
                create_response = requests.post(
                    "http://graylog:9000/api/system/inputs",
                    json=input_data,
                    auth=("admin", "admin"),
                    headers=headers,
                    timeout=10
                )
                
                if create_response.status_code == 201:
                    print("✅ GELF Input создан и запущен!")
                else:
                    print(f"❌ Ошибка создания: {create_response.status_code} - {create_response.text}")
                    
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    if wait_for_graylog():
        setup_graylog_input()