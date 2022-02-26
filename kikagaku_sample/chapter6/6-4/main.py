from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from janome.tokenizer import Tokenizer
from gensim import corpora, matutils
from summpy.summpy.lexrank import summarize
import requests
import joblib
import json
import time

# - - - - - - - - - 
# グローバル変数
# - - - - - - - - - 

# 辞書と訓練済みモデルの読み込み
dictionary = joblib.load('dictionary.pkl')
clf = joblib.load('document_classifier.pkl')
n_words = len(dictionary)  # 辞書内の単語数

# 形態素解析を行うTokenizerをインスタンス化
tagger = Tokenizer(wakati=True)


# - - - - - - - - - 
# 関数
# - - - - - - - - - 

# テキストの前処理（クリーニング＋形態素解析）
def preprocessing(text):
    text = text.replace('\u3000', '')
    text = text.replace('\n', '')
    words = tagger.tokenize(text)
    return words

# BoW形式を取得
def get_bow(words):
    bow_id = dictionary.doc2bow(words)
    bow = matutils.corpus2dense([bow_id], n_words).T
    return bow

# Slackの本文
def get_slack_text(title, url, sentences):
    text = '''記事のタイトル：
    {}
    
    記事のURL：
    {}
    
    記事の要約：
    ・{}
    ・{}
    ・{}
    '''.format(title, url, sentences[0], sentences[1], sentences[2])
    return text 

# Slackへテキストを通知
def send_text(text):
    slack_url = 'https://hooks.slack.com/services/XXXXXX/XXXXXX/XXXXXX'
    data = json.dumps({
        'username': 'bot',
        'text': text
    })
    requests.post(slack_url, data=data)


# - - - - - - - - - 
# メイン関数
# - - - - - - - - - 
if __name__ == '__main__':

    # HeadlessなChromeの設定
    options = Options()
    options.binary_location = '/app/.apt/usr/bin/google-chrome'
    options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)

    # Topページへアクセス
    browser.get('https://sandbox.kikagaku.co.jp/blog/')

    # ブログのURLを取得
    elems = browser.find_elements_by_class_name('stretched-link')
    urls = [elem.get_attribute('href') for elem in elems]

    # 各ブログ記事にアクセス
    for url in urls:
        browser.get(url)
        title = browser.find_element_by_class_name('blog-post-title').text
        text = browser.find_element_by_class_name('newsContent_inner').text
        words = preprocessing(text)
        x = get_bow(words)
        y = clf.predict(x)[0]

        # ITカテゴリーであれば Slack へ通知
        if y == 1:
            # 文書要約
            sentences, debug_info = summarize(
                text, sent_limit=3, continuous=True, debug=True
            )
            # Slack へ通知用の文章作成
            text = get_slack_text(title, url, sentences)
            # Slack へ通知
            send_text(text)
        
        # 3秒待機
        time.sleep(3)

    # ブラウザを閉じる
    browser.quit()
        
