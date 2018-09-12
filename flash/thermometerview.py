from m5stack import lcd
import math

class ThermometerView:
    def __init__(self, x, y, min_value=-15, max_value=50, color=lcd.RED, background_color=lcd.WHITE, label='`C'):
        # 描画領域の左上の座標
        self.x, self.y = x, y
        
        # 描画領域の横幅と高さ
        self.width, self.height = 64, 220
        
        # 温度計の縦棒の左のx座標
        self.bar_x = self.x + 40
        
        # 温度計の縦棒の横幅
        self.bar_width = 9
        
        # 温度計の液溜めの円の半径
        self.circle_radius = 12
        
        # 温度計の液溜めの円の中心の座標
        self.circle_x = self.bar_x + int(round(self.bar_width / 2))
        self.circle_y = self.y + self.height - self.circle_radius
        
        # 温度計のラベルの文字列
        self.label=label
        
        # 液体の色
        self.color = color
        
        # 背景色
        self.background_color = background_color
        
        # ラベルや目盛りの色
        self.axis_color = lcd.BLACK
        
        # 温度計の目盛りの最小値と最大値 (摂氏度)
        self.min_value = min_value
        self.max_value = max_value
        
        # 1度あたりのピクセル数
        self.scale = ((self.circle_y - self.circle_radius) - self.y - 20) / (self.max_value - self.min_value)
        
        # 原点(摂氏0度)のy座標
        self.y0 = self.circle_y - self.circle_radius + int(round(self.scale * self.min_value))
        
        # 温度計の縦棒の差分更新用の変数
        self.prev_y1 = self.circle_y
        
    def _calc_y(self, value):
        '''温度をy座標に変換する'''
        return int(round(self.y0 - self.scale * value))
        
    def init(self):
        self._draw_once()
    
    def _draw_once(self):
        '''最初に一度だけ描画する処理'''
        # 枠を表示 (デバッグ用)
        #lcd.rect(0, 0, self.width + 1, self.height + 1, lcd.BLACK)
        
        # 温度計の液溜め部分(正式には「球部」)の円を描画
        lcd.circle(self.circle_x, self.circle_y, self.circle_radius, self.color, self.color)
        
        # 目盛りの間隔 (摂氏度)
        tick = 10
        
        # 目盛りとグラフの隙間のピクセル数
        m = 2
        
        # 目盛りの長さ (ピクセル)
        l = 8
        
        # 目盛りと軸の数字の隙間のピクセル数
        m2 = 4
        
        # フォントの設定
        lcd.font(lcd.FONT_Default, color=self.axis_color, transparent=True)
        
        # TODO: ラベルを描画
        label_x = self.bar_x - m - l - m2 - lcd.textWidth(self.label)
        label_y = self.y
        lcd.text(label_x, label_y, self.label)
        
        # フォントの設定
        lcd.font(lcd.FONT_Default, color=self.axis_color, transparent=True)
        
        # フォントサイズ
        font_width, font_height = lcd.fontSize()
        half_font_height = int(round(font_height / 2))
        
        min_ylabel = int(math.ceil(self.min_value / 10)) * 10
        for i in range(min_ylabel, self.max_value+1, tick):
            y1 = self._calc_y(i)
            
            # 目盛り (左)
            lcd.line(
                self.bar_x - m - l, y1,
                self.bar_x - m, y1,
                self.axis_color
            )
            
            # 目盛り (右)
            lcd.line(
                self.bar_x + self.bar_width + m, y1,
                self.bar_x + self.bar_width + m + l, y1,
                self.axis_color
            )
            
            # 目盛りラベル
            tick_label = '{}'.format(i)
            lcd.print(
                tick_label,
                self.bar_x - m - l - m2 - lcd.textWidth(tick_label),
                y1 - half_font_height,
                self.axis_color
            )
        
    def update(self, value):
        '''温度計の表示値を再描画する。
        '''
        
        # 温度計の縦棒の一番上のy座標を計算する
        y1 = self._calc_y(value)
        
        # 描画する
        lcd.rect(self.bar_x, y1, self.bar_width, self.circle_y - y1, self.color, self.color)
        lcd.rect(self.bar_x, self.y, self.bar_width, y1 - self.y, self.background_color, self.background_color)
        