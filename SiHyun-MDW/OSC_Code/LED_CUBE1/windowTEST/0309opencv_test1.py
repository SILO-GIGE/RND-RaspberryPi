import cv2
import time
import os
from pythonosc import dispatcher, osc_server, udp_client

Main_port_num = 5557  # Window 포트번호
Server1_port_num = 4206  # 라즈베리파이 포트번호

# LED 설정
# pixel_pin = 18  # GPIO 18에 연결된 LED
num_pixels = 2304  # 1280 + 1024 픽셀
# ORDER = neopixel.GRB

# OSC 클라이언트 설정
client_ip = '192.168.50.191'  # Window IP 주소
client_port = Main_port_num
osc_client = udp_client.SimpleUDPClient(client_ip, client_port)

# OSC 서버 설정
ip = '0.0.0.0'  # 모든 IP 주소에서 수신
port = Server1_port_num

# OSC 메시지 처리를 위한 콜백 함수
def receive_osc_message(address, *args):
    global num_iterations
    if address == "/SILOKSH" and args[0] == 1:
        print(f"Received OSC message from {address}: {args}")  # 수신한 메세지를 출력.
        start_time = time.time()
        for i in range(num_iterations):
            show_image(*image_pixels_list[i % len(image_pixels_list)])
            time.sleep(interval)
        end_time = time.time()
        execution_time = end_time - start_time
        print("TIME    :", execution_time, "sec")
        #pixels.fill((0, 0, 0))
        #pixels.show()
        osc_client.send_message("/Rasp1", 3)
        print("Sent OSC message: /Rasp1 3")
    elif address == "/SILOKSH" and args[0] == 0:
        print(f"Received OSC message from {address}: {args}")  # 수신한 메세지를 출력.
        #pixels.fill((0, 0, 0))
        #pixels.show()

# OSC 디스패처 설정
dispatcher = dispatcher.Dispatcher()
dispatcher.set_default_handler(receive_osc_message)

# OSC 서버 시작
server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
print(f"OSC server listening on {ip}:{port}")

# LED 초기화 및 밝기 설정
pixels = [(0, 0, 0)] * num_pixels
# 이미지 파일이 있는 디렉토리 경로
directory_path = "C:/Users/sihyu/Desktop/Composition2/"
save_directory = "C:/Users/sihyu/Desktop/crop/"
# 이미지 파일들의 경로를 저장할 배열
image_paths = [os.path.join(directory_path, filename) for filename in sorted(os.listdir(directory_path)) if
               filename.endswith(".png")]

# 이미지각각 마다 이미지 영역을 자르고 픽셀 배열로 변환하는 함수
def image_to_pixels(image_path):
    image = cv2.imread(image_path)  # 이미지를 RGB색상모드로 변환
    image_name = os.path.splitext(os.path.basename(image_path))[0]  # 이미지 파일명 추출
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # BGR -> RGB로 변환
    image_pixel_lists = []
    image_index = 0  # 이미지 순서를 나타내는 변수 초기화'
    start_time = time.time()
    for x in range(0, 80, 16):
        image_piece = image[:, x:x + 16, :]
        cv2.imwrite(os.path.join("C:/Users/sihyu/Desktop/crop/",f"{image_name}_piece_{x}_{image_index}.png"), image_piece)  # 이미지 저장
        image_piece = cv2.flip(image_piece, 0)  # 이미지를 상하반전
        #if image_index % 2 == 1:  # 짝수 행인 경우에만 좌우 반전
        #    image_piece = image_piece[:, ::-1, :]  # 열을 역순으로 배치하여 좌우 반전
        image_pixel_lists.append(list(image_piece.reshape(-1, 3)))
        image_index += 1  # 이미지 순서 증가
    end_time = time.time()
    execution_time = end_time - start_time
    print("TIME    :", execution_time, "sec")
    with open("C:/Users/sihyu/Desktop/combined_pixels1.txt", "w") as file:           
        file.write(f"{image_pixel_lists}\n")
    return image_pixel_lists

# 최종 image_pixelx_list
image_pixels_list = [image_to_pixels(image_path) for image_path in image_paths]
print("DoneE!!!!!!!!!!!")

# 이미지를 1/30초 간격으로 송출
interval = 1 / 30  # 1/30초 간격
total_time = 10  # 10초
num_iterations = int(total_time / interval)  # 이미지 출력 개수

# 이미지 출력 함수
def show_image(*image_pixels):
    combined_pixels = []
    for pixels in image_pixels:
        combined_pixels.extend(pixels)
    with open("C:/Users/sihyu/Desktop/combined_pixels.txt", "w") as file:
        for pixel_value in combined_pixels:
            file.write(f"{pixel_value}\n")
    for i, pixel_value in enumerate(combined_pixels):
        if i < 1280:
            # NumPy 배열을 리스트로 변환하여 각 채널을 스케일링하여 정수로 변환
            r = int(pixel_value[0] * 1)
            g = int(pixel_value[1] * 0.9)
            b = int(pixel_value[2] * 0.5)
            combined_pixels[i] = (r, g, b)
            #pixels[i] = (int(pixel_value[0] * 1), int(pixel_value[1] * 0.9), int(pixel_value[2] * 0.5))
    #pixels.show()

# OSC 메시지 수신 대기`
try:
    while True:
        for i in range(1280, num_pixels):
            pixels[i] = (int(150), int(140), int(90))  # 화이트 설정
        print("OSC 대기중!!")
        server.handle_request()
except KeyboardInterrupt:
    server.server_close()
