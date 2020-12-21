import board
import time
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
import adafruit_bme280
import datetime
import random

# Zdefiniowanie liczby znakow na LCD
lcd_columns = 16
lcd_rows = 2

# Inicjalizacja magistrali I2C
i2c = busio.I2C(board.SCL, board.SDA)
# Inicjalizacja klasy LCD
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
# Inicjalizacja czujnika bme280
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# Deklaracja zmiennej sterujacej kliknieciem przycisku
press_control = False
# Numer poczatkowo wyswietlanego parametru
par_number = 0
# Liczba wyswietlanych parametrow
par_count = 3

# Deklaracja parametrow pomiarowych
par = [[1, "Temperatura:\n%0.1f C\n", bme280.temperature],
        [2, "Wilgotnosc:\n%0.1f %%\n", bme280.humidity],
        [3, "Cisnienie:\n%0.1f hPa\n", bme280.pressure]]
		#4, "Nazwa pomiaru:\n%0.1f\n", odczyt_pomiaru]]
        
# Funkcja odczytu parametrow
def read_parameter(params):
    return {
        1: bme280.temperature,
        2: bme280.humidity,
        3: bme280.pressure,
        #4: odczyt_parametru,
        }[params]

# Funkcja zapisu parametrow
def write_parameter(params):
    # Otwarcie i ustawienie trybu zapisu pliku
    f = open("/home/pi/SensorData/data.txt", "a")
    # Odczyt czasu
    now = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S\n"))
    
    # Zapis czasu pomiaru
    f.write(now)
    i = 0
    # Zapis parametrow
    while i < par_count:
        line = params[i][1] % params[i][2]
        f.write(line)
        i += 1
    f.write("\n")
    f.close()

# Tryb zapisu parametrow
def lcd_write(pressed, num):
    # Wyswietlenie odpowiedniego komunikatu o trybie zapisu
    lcd.clear()
    lcd.color = [75, 25, 75]
    lcd.message = "Tryb zapisu\nparametrow"
    time.sleep(2)
    
    while not pressed:
        lcd.message = "SELECT - zapis\nDOWN - anuluj"
        #Zapis parametru i powrot do trybu wyswietlania parametru
        if lcd.select_button:
            write_parameter(par)
            lcd.clear()
            lcd.message = "Zapisano dane!"
            time.sleep(2)
            pressed = True
        # Powrot do trybu wyswietlania parametru
        elif lcd.down_button:
            pressed = True
    # Ustawienie wcisniecie przycisku jako zakonczone
    pressed = False
    lcd_parameter(pressed, num)

# Tryb wyswietlania dowolnego parametru
def lcd_parameter(pressed, num):
    
    # Czyszczenie i ustawienie koloru LCD
    lcd.clear()
    rgb_color(num)
    
    while not pressed:
        # Odczyt parametru w czasie rzeczywistym
        par[num][2] = read_parameter(par[num][0])
        # Wyswietlenie parametru
        lcd.message = par[num][1] % par[num][2]
        # Warunek sprawdzajacy czy wcisnieto przycisk
        if (lcd.right_button or lcd.left_button or  lcd.up_button):
            pressed = True
    # Ustawienie wcisniecie przycisku jako zakonczone
    pressed = False
    
    # Wybor trybu wyswietlania w zaleznosci od wcisnietego przycisku
    if lcd.right_button:
        if num != (par_count - 1):
            num += 1
            lcd_parameter(pressed, num)
        elif num == (par_count - 1):
            num = 0
            lcd_parameter(pressed, num)
    elif lcd.left_button:
        if num == 0:
            num = (par_count - 1)
            lcd_parameter(pressed, num)
        elif num != 0:
            num -= 1
            lcd_parameter(pressed, num)
    elif lcd.up_button:
        lcd_write(pressed, num)

# Funkcja zmieniajaca kolor RGB LCD
def rgb_color(num):
    if num > 2:
        num = 0
    if num == 0:
        lcd.color = [100, 0, 0]
    if num == 1:
        lcd.color = [0, 0, 100]
    if num == 2:
        lcd.color = [0, 100, 0] 
    
# Ekran startowy
lcd.color = [50, 25, 25]
lcd.message = "Stacja\nmonitorujaca"

# Glowna petla programu
while True:
    if lcd.select_button == True:
        lcd_parameter(press_control, par_number)

