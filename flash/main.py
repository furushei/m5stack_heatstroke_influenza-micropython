from m5stack import lcd, buttonC
from dht12 import DHT12
from thermometerview import ThermometerView
import utime
import uos
import ujson

########## 設定 ##########
# 前景色 (文字の色等)
color = lcd.BLACK
# 背景色
background_color = lcd.WHITE

# JSONファイルのパス
wbgt_table_path = '/sd/data/th_wbgt_table.json'

# 画像のパス
image_path_kiken = '/sd/assets/heatstroke_kiken.jpg'
image_path_genjukeikai = '/sd/assets/heatstroke_genjukeikai.jpg'
image_path_keikai = '/sd/assets/heatstroke_keikai.jpg'
image_path_influenza = '/sd/assets/influenza.jpg'

# 画像の表示位置の左上の座標
image_x, image_y = 160, 80

# 画像のサイズ
image_width, image_height = 150, 150

# 表示の更新間隔 (秒)
interval = 2


def load_wbgt_table():
    '''温度、湿度とWBGT値との対応関係を格納したテーブルをファイルから読み込む'''
    with open(wbgt_table_path, 'r') as f:
        data = ujson.load(f)
    return data


_wbgt_table = None
def get_wbgt_table():
    '''温度、湿度とWBGT値との対応関係を格納したテーブルを取得する。
    
    最初の呼び出し時はファイルから読み込む。2回目以降はそのまま返す。
    '''
    global _wbgt_table
    if _wbgt_table is None:
        _wbgt_table = load_wbgt_table()
    return _wbgt_table


def calc_wbgt(temperature, humidity):
    '''温度、湿度と対応するWBGTの推定値を返す'''
    table = get_wbgt_table()
    temperature = int(round(temperature))
    humidity = int(round(humidity / 5) * 5)
    key = '{},{}'.format(temperature, humidity)
    try:
        wbgt_value = table[key]
    except KeyError:
        raise ValueError('out of table')
    return wbgt_value


def main():
    ########## 初期化 ##########
    # 液晶画面を初期化する
    lcd.setColor(color, background_color)
    lcd.clear()
    
    # センサーを初期化する
    sensor = DHT12()
    
    # 温度計、湿度計の表示を初期化する
    temperature_view = ThermometerView(10, 10, min_value=-15, max_value=45)
    humidity_view = ThermometerView(80, 10, min_value=0, max_value=100, color=lcd.BLUE, label='%')
    
    # SDカードのマウント
    uos.mountsd()
    
    # 背景の描画
    temperature_view.init()
    humidity_view.init()
    
    ########## 無限ループ ##########
    while not buttonC.isPressed():
        # センサーで温度と湿度を計測する
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        
        # デバッグ用
        print("Temperature: {} `C, Humidity: {} %".format(temperature, humidity))
        
        # 温度計、湿度計の表示を更新する
        temperature_view.update(temperature)
        humidity_view.update(humidity)
        
        # WBGT値を求める
        try:
            wbgt = calc_wbgt(temperature, humidity)
        except ValueError:
            wbgt = None
        
        # WBGT値を画面に表示する
        lcd.font(lcd.FONT_Default, color=color, transparent=False)
        lcd.textClear(160, 30, 'WBGT: Unknown')
        if wbgt is not None:
            lcd.text(160, 30, 'WBGT: {}'.format(wbgt))
        else:
            lcd.text(160, 30, 'WBGT: Unknown')
        
        image_path = None
        
        # WBGT値に応じて画像を描画する
        # 31度以上          : 危険
        # 28度以上31度未満  : 厳重警戒
        # 25度以上28度未満  : 警戒
        # 25度未満          : 注意
        if temperature >= 21 and wbgt is not None:
            if wbgt >= 31:
                # 危険
                image_path = image_path_kiken
            elif wbgt >= 28:
                # 厳重警戒
                image_path = image_path_genjukeikai
            elif wbgt >= 25:
                # 警戒
                image_path = image_path_keikai
        
        # 湿度に応じてインフルエンザ注意情報を表示する
        # 湿度40%未満 : インフルエンザ感染注意
        if humidity < 40:
            image_path = image_path_influenza
        
        if image_path is not None:
            # 画像を描画する
            lcd.image(image_x, image_y, image_path)
        else:
            # 画像を描画した領域を背景色で塗りつぶす
            lcd.rect(image_x, image_y, image_width, image_height, background_color, background_color)
        
        # 表示の更新間隔
        utime.sleep(interval)

try:
    main()
except Exception as e:
    import sys
    import uio
    f = uio.StringIO()
    sys.print_exception(e, f)
    lcd.text(0, 0, f.getvalue(), color=lcd.RED)
    sys.exit(1)
