#!/usr/bin/python
# coding: UTF-8


# Flask などの必要なライブラリをインポートする

from flask import Flask, render_template, request, redirect, url_for

#Cookieのsecret_key生成
import os

#login/out用
import urllib.parse
from authlib.flask.client import OAuth
from functools import wraps
from flask import session

from six.moves.urllib.parse import urlencode

#アクセストークンを取得するためにAuth0 Management APIとつなぐ
import http.client
import requests
import json


#アクセストークンを取得するためにAuth0 Management APIとつなぐ
import http.client
#auth0とつなぐ
import flask_oauthlib.client


#####loopを入れる###############
from jinja2 import Environment

#### 必要な情報を整理しやすいよう外部ファイル化####

import info_val

#####自作の外部関数の読み込み########
import azure_negaposi_function

#str型（文字列）をdict型に変換
import ast
#####CSRF 対策(stateを生成)########
import uuid

client_id=info_val.client_id
client_secret=info_val.client_secret
domain=info_val.domain
#facebook_user_id=info_val.facebook_user_id
insta_id=info_val.insta_id
subscription_key = info_val.subscription_key
text_analytics_base_url = info_val.text_analytics_base_url
heroku_domain=info_val.heroku_domain


# 自身の名称を app という名前でインスタンス化する
app = Flask(__name__)

##########azure_negaposi_functionに外部化するとうまくいかなかった関数###############
def request_form():
    if request.method == 'POST':
        # リクエストフォームからname「access_token」を取得
        HASHTAG_NAME = str(request.form['hashtag_name'])
    else:
        HASHTAG_NAME = str(request.args.get('hashtag_name'))
    return(HASHTAG_NAME)

#############################################
#{{azure_json}}を使い回すため、POST and GETでフォームを使って投稿を取得したいハッシュタグ名を取得
#############################################

def request_form_azure_json():
    HASHTAG_POSTS = request.form['user_name']
    HASHTAG_NAME = request.args.get('hashtag_name')
    hashtag_error_message = request.args.get('hashtag_error_message')
    hashtag_error_message_negaposi= request.args.get('hashtag_error_message_negaposi')
    print('hashtag_error_message')
    print(hashtag_error_message)
    print('hashtag_error_message_negaposi')
    print(hashtag_error_message_negaposi)

    return(HASHTAG_POSTS,HASHTAG_NAME,hashtag_error_message,hashtag_error_message_negaposi)
##########azure_negaposi_functionに外部化するとうまくいかなかった関数###############


#Cookieの暗号化に使うキー
#推奨はランダム生成だが、herokuにアップする場合固定値でないとerrorのため固定値にする
app.secret_key = 'ninino_koteich_20190811'


#########login#####################
#auth0とつなぐ  Auth0とはoauthでやりとりするので、主にそのあたりの設定
#なお、Auth0とのAPIをつなぐには、下記だけでなくhttps://manage.auth0.com/?のGUI上での設定も必要

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=client_id,
    client_secret=client_secret,
    api_base_url=domain,
    access_token_url=domain+'/oauth/token',
    authorize_url=domain+'/authorize',
    client_kwargs={
        'scope': 'openid profile',
        #GUI操作ではできない、hashtagの取得に必要なscopeの設定  manage_pages pages_show_listもinstagarm 　id抽出の為に使用
        'connection_scope':'instagram_basic business_management instagram_manage_insights manage_pages pages_show_list'

    },
)

#########login#####################
# ここからウェブアプリケーション用のルーティングを記述

#ログインページ
@app.route('/login')
def login():
    print('loginボタン押下')
    if(session.get('profile')):
        return redirect('/dashboard')
    else:
        #csrf token error対策(stateをセット)
        session['_auth0_authlib_state_'] = str(uuid.uuid4().hex.strip())

        #local
        #stateを付与
        return auth0.authorize_redirect(redirect_uri='http://0.0.0.0:5000/callback', audience=domain+'/userinfo',state=session['_auth0_authlib_state_'])
        
        #本番  https://×××××××××.herokuapp.com/
        #stateを付与
        #return auth0.authorize_redirect(redirect_uri=heroku_domain+'/callback', audience=domain+'/userinfo',state=session['_auth0_authlib_state_'])
        
#callback 

# Here we're using the /callback route.
@app.route('/callback',methods=['GET'])
def callback_handling():
    global client_id
    global client_secret
    global domain
    #global facebook_user_id
    #前回のセッションの保存を取得
    session['_auth0_authlib_state_']=str(request.args.get('state').strip())
    #local
    session['_auth0_authlib_callback_']='http://0.0.0.0:5000/callback'
    #本番
    #session['_auth0_authlib_callback_']=heroku_domain+'/callback'

 #user（情報）の特定
    token_params=auth0.authorize_access_token(state=session['_auth0_authlib_state_'])

    resp = auth0.get('userinfo')
    userinfo = resp.json()
    #ここで今までのセッションがなくなっているので セッションにデータを入れる
    session['_auth0_authlib_state_']=str(request.args.get('state').strip())
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
        }
    facebook_user_id=session['profile']['user_id']


    #Auth0 API アクセストークンを取得
    headers = {
        'content-type': 'application/json',
    }

    data = '{\"client_id\":\"'+client_id+'\",\"client_secret\":\"'+client_secret+'\",\"audience\":\"'+domain+"/api/v2/"+'\",\"grant_type\":\"client_credentials\"}'

    response = requests.post(domain+'/oauth/token', headers=headers, data=data)
    auth0_api_token=response.json()


    #facebook 全ての情報を取得　　
    #必要な情報　　ユーザー特定のためのFB　USER_ID
    #userが特定できていれば、その後、繰り返し取得可能

    api_token_auth=auth0_api_token['access_token']

    headers = {
         'Authorization': 'Bearer '+str(api_token_auth)
        }
    response = requests.get(domain+'/api/v2/users/'+facebook_user_id, headers=headers)
    userinfo=response.json()

    fb_access_token= userinfo['identities'][0]['access_token']

    user_name=userinfo['name']
    
    return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    #Flask session is empty after redirect対策
    if('profile' not in session):
        print('profileが存在しない場合、topへ')
        return redirect('/')
    else:
        print('profileが存在するので、実行')
        print(session)
        facebook_user_id=session['profile']['user_id']
        fb_access_token= azure_negaposi_function.fb_access_token(facebook_user_id)
        if(fb_access_token==None):
            #Noneの場合logout
            return redirect('/logout')
        else:
            id_name_json_dict=azure_negaposi_function.hashtag_names(fb_access_token)
            len_id_name_json_dict=len(id_name_json_dict)
            return render_template('dashboard_post_before.html',
                                    id_name_json_dict=id_name_json_dict,
                                    len_id_name_json_dict=len_id_name_json_dict,
                                    userinfo=session['profile'])

#logoutをauth0に伝える
@app.route('/logout')
def logout():
    global client_id
    # セッションをクリアし、データを削除する
    session.clear()
    #ログアウト時の場所を指定
    params = {'returnTo': url_for('index', _external=True), 'client_id': client_id}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

#
#トップページ(login page)
@app.route('/')
def index():
    print('top。rootのセッション確認')
    if(session.get('profile')):
        return redirect('/dashboard')
    else:    
        return render_template('index.html')


@app.route('/post', methods=['GET', 'POST'])
def post():
    global insta_id
    print('post処理入った')
    if('profile' not in session):
        print('profileが存在しない場合、topへ')
        return redirect('/')
    else:
        facebook_user_id=session['profile']['user_id']
        #Pハッシュタグ名を取得
        HASHTAG_NAME=request_form()
        hashtag_error_message_negaposi= request.args.get('hashtag_error_message_negaposi')

        ##ハッシュタグidを取得##  
        #nstagram_business_account ID
        insta_id=insta_id

        print('fb_access_token取得を開始')
        fb_access_token= azure_negaposi_function.fb_access_token(facebook_user_id)
        print('fb_access_token取得完了')
        #画面上で変更
        #HASHTAG_NAME='任意のハッシュタグ'
        url = 'https://graph.facebook.com/v3.0/ig_hashtag_search/?user_id='+insta_id+'&q='+HASHTAG_NAME+'&access_token='+fb_access_token
        r= requests.get(url)
        #instagram graph APIのステータス確認(アップレート制限対策)
        if(r.status_code is not requests.codes.ok):
            if (str(r.status_code) == 'ステータスコード：403'):
                print( 'ステータスコード：'+str(r.status_code))
                print('403＝アプリレベルのレート制限に達したため、３０分程度検索を控える')
                print( 'ステータスコード：'+str(r.status_code))
                print('200じゃないので終了')
                hashtag_error_message='Facebookアプリの検索上限に達したため、３０分程度検索をお控えください'
                return render_template('dashboard_post_before.html',hashtag_error_message=hashtag_error_message,userinfo=session['profile']) 

            else:
                print( 'ステータスコード：'+str(r.status_code))
                print('200じゃないので終了')
                hashtag_error_message='hashtagが存在しないか、投稿がありません。別のキーワードで検索してください'
                return render_template('dashboard_post_after.html',hashtag_error_message=hashtag_error_message,hashtag_name=HASHTAG_NAME,userinfo=session['profile'])        
                
        else:    
            #instagram graphAPIからハッシュタグの投稿を取得
            fb_access_token= azure_negaposi_function.fb_access_token(facebook_user_id)
            single_json_content_list=azure_negaposi_function.fb_graph_hashtag(HASHTAG_NAME,fb_access_token)
            if (single_json_content_list==None):
                print('single_json_content_listが空なので終了')
                hashtag_error_message='hashtagが存在しないか、投稿がありません。別のキーワードで検索してください'
                return render_template('dashboard_post_after.html',hashtag_error_message=hashtag_error_message,hashtag_name=HASHTAG_NAME,userinfo=session['profile'])        
         
            else:
                azure_json=azure_negaposi_function.azure_json_transform(single_json_content_list)

                #azure apiのレスポンスを判定（azureの無料枠を超えていたら、200以外が返る）
                response=azure_negaposi_function.nega_posi_azure_is_ok(azure_json)
                if(response.status_code is not requests.codes.ok):
                    print('200じゃないので終了')
                    hashtag_error_message_negaposi='ネガポジ分析の件数が30日の上限5000に達しました'
                    return render_template('dashboard_post_after.html',hashtag_error_message_negaposi=hashtag_error_message_negaposi,azure_json=azure_json['documents'],hashtag_name=HASHTAG_NAME,userinfo=session['profile'])
                else:
                    negaposi_azure_json=azure_negaposi_function.nega_posi_azure(azure_json)
                    return render_template('dashboard_post_after.html',azure_json=negaposi_azure_json['documents'],hashtag_name=HASHTAG_NAME,userinfo=session['profile'])

@app.route('/post_good', methods=['GET', 'POST'])
def post_good():
    print(session)
    if('profile' not in session):
        print('profileが存在しない場合、topへ')
        print(session)
        return redirect('/')
    else:    
       #azure apiのレスポンスを判定（azureの無料枠を超えていたら、200以外が返る） HASHTAG_POSTS_GOOD
       #Pハッシュタグ名を取得
        HASHTAG_POSTS,HASHTAG_NAME,hashtag_error_message,hashtag_error_message_negaposi=request_form_azure_json()
        azure_json = ast.literal_eval(HASHTAG_POSTS)
        HASHTAG_POSTS_GOOD=True    
       #azure apiのレスポンスを判定（azureの無料枠を超えていたら、200以外が返る）
        if(hashtag_error_message_negaposi):
            print('hashtag_error_message_negaposiあり')
            return render_template('dashboard_post_after.html',HASHTAG_POSTS_GOOD=HASHTAG_POSTS_GOOD,hashtag_error_message_negaposi=hashtag_error_message_negaposi,azure_json=azure_json,hashtag_name=HASHTAG_NAME,userinfo=session['profile'])
        else:
            return render_template('dashboard_post_after.html',HASHTAG_POSTS_GOOD=HASHTAG_POSTS_GOOD,azure_json=azure_json,hashtag_name=HASHTAG_NAME,userinfo=session['profile'])

@app.route('/post_nega', methods=['GET', 'POST'])
def post_nega():
    if('profile' not in session):
        print('profileが存在しない場合、topへ')
        return redirect('/')
    else:     
        #Pハッシュタグ名を取得
        HASHTAG_POSTS,HASHTAG_NAME,hashtag_error_message,hashtag_error_message_negaposi=request_form_azure_json()
        azure_json = ast.literal_eval(HASHTAG_POSTS)
        HASHTAG_POSTS_NEGA=True    
        #azure apiのレスポンスを判定（azureの無料枠を超えていたら、200以外が返る）
        if(hashtag_error_message_negaposi):
            print('hashtag_error_messageあり')
            return render_template('dashboard_post_after.html',HASHTAG_POSTS_NEGA=HASHTAG_POSTS_NEGA,hashtag_error_message_negaposi=hashtag_error_message_negaposi,azure_json=azure_json,hashtag_name=HASHTAG_NAME,userinfo=session['profile'])
        else:
            return render_template('dashboard_post_after.html',HASHTAG_POSTS_NEGA=HASHTAG_POSTS_NEGA,azure_json=azure_json,hashtag_name=HASHTAG_NAME,userinfo=session['profile'])

@app.route('/post_posi', methods=['GET', 'POST'])
def post_posi():
    if('profile' not in session):
        print('profileが存在しない場合、topへ')
        return redirect('/')
    else:        
       #Pハッシュタグ名を取得
        HASHTAG_POSTS,HASHTAG_NAME,hashtag_error_message,hashtag_error_message_negaposi=request_form_azure_json()
        azure_json = ast.literal_eval(HASHTAG_POSTS)
        HASHTAG_POSTS_POSI=True    
       #azure apiのレスポンスを判定（azureの無料枠を超えていたら、200以外が返る）
        if(hashtag_error_message_negaposi):
            print('hashtag_error_messageあり')
            return render_template('dashboard_post_after.html',HASHTAG_POSTS_POSI=HASHTAG_POSTS_POSI,hashtag_error_message_negaposi=hashtag_error_message_negaposi,azure_json=azure_json,hashtag_name=HASHTAG_NAME,userinfo=session['profile'])
        else:
            return render_template('dashboard_post_after.html',HASHTAG_POSTS_POSI=HASHTAG_POSTS_POSI,azure_json=azure_json,hashtag_name=HASHTAG_NAME,userinfo=session['profile'])

def debug(text):
  print(text)
  return ''


if __name__ == '__main__':
#直接実行された場合の時のみ、実行という意味
#モジュールを作成中のテストや、現在はモジュール化するつもりはないが、モジュール化したときに無駄な処理を行わないようにしたい場合などに使われます
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.jinja_env.filters['debug']=debug

    # debugモード/どこからでもアクセス可能に
    app.run(debug=True, host='0.0.0.0') 
