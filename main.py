# ================================================

#  숨으로 조작하는 게임 컨트롤러

# Raspberry Pi Pico + 가스센서 (MQ-2/MQ-135)

# Thonny IDE용 MicroPython 코드

# ================================================

 

from machine import ADC, Pin

import time

import utime

 

# ------------------------------------------------

#  핀 설정

# ------------------------------------------------

gas_sensor = ADC(26)        # 가스센서 → GP26 (ADC0)

led_strong = Pin(15, Pin.OUT)  # 강하게 불기 LED

led_weak   = Pin(14, Pin.OUT)  # 약하게 불기 LED

# ------------------------------------------------

 

# ------------------------------------------------

#  기준값 설정 (이 값들을 조절하세요!)

# ------------------------------------------------

BASELINE    = 0       # 초기 기준값 (자동 설정됨)

WEAK_THRESHOLD   = 2000   # 약하게 불기 감지 기준

STRONG_THRESHOLD = 5000   # 강하게 불기 감지 기준

CALIBRATION_TIME = 3      # 기준값 측정 시간 (초)

# ------------------------------------------------

 

# ------------------------------------------------

#  게임 명령어 정의

# ------------------------------------------------

CMD_IDLE   = "대기중"

CMD_WEAK   = "약한 바람 → [점프!]"

CMD_STRONG = "강한 바람 → [대시!]"

# ------------------------------------------------

 

 

def read_gas():

    """가스센서 값 읽기 (0 ~ 65535)"""

    return gas_sensor.read_u16()

 

 

def calibrate():

    """

     기준값 자동 보정

    - 처음 3초 동안 공기 상태를 측정해서

      기준값(BASELINE)을 자동으로 설정합니다

    """

    global BASELINE

    

    print("=" * 40)

    print(" 기준값 측정 중...")

    print(f"   {CALIBRATION_TIME}초 동안 센서 앞에서")

    print("   아무것도 하지 마세요!")

    print("=" * 40)

    

    # LED 점멸로 측정 중 표시

    total = 0

    samples = 20  # 샘플 횟수

    

    for i in range(samples):

        total += read_gas()

        

        # LED 깜빡임

        led_strong.toggle()

        led_weak.toggle()

        

        # 진행상황 출력

        progress = int((i + 1) / samples * 100)

        print(f"   측정중... {progress}%")

        

        time.sleep(CALIBRATION_TIME / samples)

    

    BASELINE = total // samples

    

    # LED 끄기

    led_strong.off()

    led_weak.off()

    

    print(f"\n 기준값 설정 완료! → {BASELINE}")

    print("=" * 40)

    time.sleep(1)

 

 

def get_command(sensor_value):

    """

     센서값을 게임 명령어로 변환

    - 기준값보다 얼마나 증가했는지로 판단

    """

    diff = sensor_value - BASELINE  # 기준값과의 차이

    

    if diff >= STRONG_THRESHOLD:

        return CMD_STRONG, "강함", diff

    

    elif diff >= WEAK_THRESHOLD:

        return CMD_WEAK, "약함", diff

    

    else:

        return CMD_IDLE, "없음", diff

 

 

def show_led(command):

    """ 명령어에 따라 LED 제어"""

    

    if command == CMD_STRONG:

        led_strong.on()

        led_weak.on()    # 강하면 둘 다 켜짐

        

    elif command == CMD_WEAK:

        led_strong.off()

        led_weak.on()    # 약하면 하나만

        

    else:

        led_strong.off()

        led_weak.off()   # 대기중엔 꺼짐

 

 

def print_status(value, diff, level, command):

    """ 상태를 보기 좋게 출력"""

    

    # 바람 세기 시각화 바

    bar_length = min(int(diff / 500), 30)  # 최대 30칸

    bar = "█" * bar_length + "░" * (30 - bar_length)

    

    print(f"센서값: {value:5d} | 차이: {diff:5d} | 세기: [{bar}] | 명령: {command}")

 

 

def game_controller():

    """

     메인 게임 컨트롤러 루프

    - 계속 센서를 읽으면서 게임 명령어 출력

    """

    print("\n 게임 컨트롤러 시작!")

    print("━" * 60)

    print(" 약하게 불기  →  점프!")

    print(" 강하게 불기 →  대시!")

    print("━" * 60)

    print("(Thonny 터미널에서 확인하세요)")

    print("━" * 60)

    

    last_command = CMD_IDLE

    

    while True:

        try:

            # 1. 센서값 읽기

            value = read_gas()

            

            # 2. 명령어 판단

            command, level, diff = get_command(value)

            

            # 3. LED 제어

            show_led(command)

            

            # 4. 명령이 바뀔 때만 출력 (터미널 깔끔하게)

            if command != last_command:

                if command != CMD_IDLE:

                    print(f"\n [{command}] 감지!")

                    print_status(value, diff, level, command)

                else:

                    print(f"   대기중... (센서값: {value})")

                

                last_command = command

            

            # 5. 0.1초마다 반복

            time.sleep(0.1)

            

        except KeyboardInterrupt:

            # Ctrl+C로 종료 시

            print("\n\n 컨트롤러 종료!")

            led_strong.off()

            led_weak.off()

            break

 

 

# ================================================

#  프로그램 시작!

# ================================================

print("╔══════════════════════════════════════╗")

print("║   가스센서 게임 컨트롤러 v1.0      ║")

print("║  Raspberry Pi Pico + MQ 센서         ║")

print("╚══════════════════════════════════════╝")

 

# 1단계: 기준값 보정

calibrate()

 

# 2단계: 게임 컨트롤러 실행

game_controller()
