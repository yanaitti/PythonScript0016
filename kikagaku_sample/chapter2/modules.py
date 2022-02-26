# coding: utf-8

# 返り値が複数個ある関数
def hello(name1='Kikagaku', name2='Python'):
    result1 = 'Hello, ' + name1
    result2 = 'Hello, ' + name2
    return result1, result2

# 模擬的な機械学習のクラス
class Model:

    def __init__(self, x, t):
        self.x = x
        self.t = t
        self.w = None  # 初期状態は値なし
        
    # モデルの訓練を行うメソッド（模擬）
    def fit(self):
        self.w = self.x + self.t
        
    # モデルの検証を行うメソッド（模擬）
    def score(self):
        print(self.w)