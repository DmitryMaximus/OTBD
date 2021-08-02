import requests


def send_statistic(robot_id: int, oper_count: int):
    """
    Функция отправляет информацию на сервер //A105512 и формируент дэшшборд http://a105512/reports/powerbi/RobotsEffects
    """
    try:
        response = requests.get('http://172.25.100.210:86/Statistic/Add', params={'rid': int(robot_id), 'oc': int(oper_count)},timeout=2)
        return response.content.decode('UTF-8') if response.ok else 'Connection error'
    except:
        print("Статистику записать не удалось")
