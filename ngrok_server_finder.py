import threading
from mcstatus import JavaServer
from datetime import datetime
from difflib import get_close_matches
import os
from version_protocols import version_protocols

ip_range = range(0, 8)
port_range = (10000, 30000)


def find_most_similar_words(input_word, possible_words=version_protocols.keys(), n=7):
    closest_matches = get_close_matches(input_word, possible_words, n=n)
    return closest_matches


def check_server(ip: str, port_range, min_protocol: float, max_protocol: float, file_name, semaphore) -> None:
    for port in port_range:
        with semaphore:
            try:
                server = JavaServer.lookup(address=f"{ip}:{port}", timeout=0.5).status()
                if min_protocol <= server.version.protocol <= max_protocol:
                    with open(file_name, "a+") as writer:
                        message = f"{ip}:{port} | {server.version.name} | {server.players.online}/{server.players.max}\n"
                        writer.write(message)
                        print(message, end='')
            except:
                pass


def server_finder(min_protocol: float, max_protocol: float) -> None:
    if not os.path.exists("ngrok_server_finder"):
        os.makedirs("ngrok_server_finder")
    file_name = f"ngrok_server_finder/servers.{datetime.today().strftime('%Y_%m_%d_%H_%M_%S')}.txt".replace(" ", "_")
    print("Запись в файл:", file_name)
    print("Сканирование запущено. Если сканер вам кажется медленным, то за более быстрый вас забанит ngrok.")

    semaphore = threading.Semaphore(10)  # Создаем семафор с максимальным количеством потоков

    for ip in ip_range:
        port_start = port_range[0]
        while port_start < port_range[1]:
            port_end = min(port_start + 500, port_range[1])
            threading.Thread(target=check_server, args=(f"{ip}.tcp.eu.ngrok.io", range(port_start, port_end), min_protocol, max_protocol, file_name, semaphore)).start()
            port_start = port_end  


print("Введите версии из https://minecraft.wiki/w/Protocol_version#Java_Edition_2")
print("Работают только версии, которые на Майнкрафт Вики имеют точный числовой код, то есть 756, 342 и т.д.")

while True:
    min_version_input = input("Минимальная версия (оставьте пустым для поиска с самой старой возможной версии): ").strip()
    if min_version_input == "":
        min_version = float("-inf")
        break
    try:
        min_version = version_protocols[min_version_input]
        break
    except KeyError:
        print("Минимальная версия введена неверно")
        possible_versions = find_most_similar_words(min_version_input)
        if possible_versions:
            print("Возможно вы имели ввиду: ", ", ".join(possible_versions))

while True:
    max_version_input = input("Максимальная версия (оставьте пустым для поиска с самой новой возможной версии): ").strip()
    if max_version_input == "":
        max_version = float("inf")
        break
    try:
        max_version = version_protocols[max_version_input]
        break
    except KeyError:
        print("Максимальная версия введена неверно")
        possible_versions = find_most_similar_words(max_version_input)
        if possible_versions:
            print("Возможно вы имели ввиду:", ", ".join(possible_versions))

server_finder(min_version, max_version)
