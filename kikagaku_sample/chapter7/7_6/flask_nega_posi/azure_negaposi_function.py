#!/usr/bin/python
# coding: UTF-8

############azure nega-posi############
import requests
import json
import time
#Pythonの標準ライブラリであるpprintモジュールを使うと、リスト（list型）や辞書（dict型）などのオブジェクトをきれいに整形して出力・表示したり
#文字列（str型オブジェクト）に変換したりすることができる。pprintは「pretty-print」の略。
from pprint import pprint

#str型（文字列）をdict型に変換
import ast
############azure nega-posi############

#### 必要な情報を整理しやすいよう外部ファイル化####
import info_val

client_id=info_val.client_id
client_secret=info_val.client_secret
domain=info_val.domain
#facebook_user_id=info_val.facebook_user_id
insta_id=info_val.insta_id
subscription_key = info_val.subscription_key
text_analytics_base_url = info_val.text_analytics_base_url
heroku_domain=info_val.heroku_domain

#############################################
#FB access tokenの取得
#############################################

def fb_access_token(facebook_user_id):
    global client_id
    global client_secret
    global domain

    facebook_user_id=facebook_user_id

    ##fb access tokenの取得
    headers = {
        'content-type': 'application/json',
    }

    data = '{\"client_id\":\"'+client_id+'\",\"client_secret\":\"'+client_secret+'\",\"audience\":\"'+domain+"/api/v2/"+'\",\"grant_type\":\"client_credentials\"}'

    response = requests.post(domain+'/oauth/token', headers=headers, data=data)

    auth0_api_token=response.json()


    #facebook 全ての情報を取得s　　
    #必要な情報　　ユーザー特定のためのFB　USER_ID
    #userが特定できていれば、その後、繰り返し取得可能

    api_token_auth=auth0_api_token['access_token']

    headers = {
         'Authorization': 'Bearer '+str(api_token_auth)
        }

    response = requests.get(domain+'/api/v2/users/'+facebook_user_id, headers=headers)
    userinfo=response.json()

    #200じゃない時にはlogoutさせる（fb_access_token＝Noneを入れる）
    if(response.status_code is not requests.codes.ok):
        print('200じゃないので終了')
        fb_access_token=None
        return(fb_access_token)

    else:
        fb_access_token= userinfo['identities'][0]['access_token']
        return(fb_access_token)

#############################################
##FB graphAPIから、取得
############################################

def fb_graph_hashtag(HASHTAG_NAME,fb_access_token):
    #FB access tokenの取得
    global insta_id
    # #nstagram_business_account ID取得リクエスト
    # #instagram ビジネスアカウントを取得。前節で紹介したように取得には特別なパーミッションが必要
 
    ##ハッシュタグidを取得##
    #instagram_business_account ID
    insta_id=insta_id
    

    #画面上で変更
    #HASHTAG_NAME='任意のハッシュタグ'
    url = 'https://graph.facebook.com/v3.0/ig_hashtag_search/?user_id='+insta_id+'&q='+HASHTAG_NAME+'&access_token='+fb_access_token
    r= requests.get(url)
    json_dict = json.loads(r.text)
    hash_tag_id=json_dict['data'][0]['id']

    ##人気のハッシュタグ投稿１００件まで取得
    #APIへのアクセスが多い場合、アクセス制限がかかることもある。その場合は、1時間に200回までしかコールできない/60件程度しか取得できない場合も。

    contents_list=[]
    #top_media　　で、直近の人気投稿を抽出　recent_mediaで最新の投稿を抽出
    url = 'https://graph.facebook.com/v3.2/'+hash_tag_id+'/top_media/?user_id='+insta_id+'&fields=id,media_type,caption,comments_count,like_count,media_url,children{media_url},permalink&limit=50&access_token='+fb_access_token
    r = requests.get(url)
    
    if(r.status_code is not requests.codes.ok):
        print( 'ステータスコード：'+str(r.status_code))
        print('200じゃないので終了')
    else:
        #空のjsondataか空じゃないかを判定
        json_dict = json.loads(r.text)
        if(json_dict['data']==[]):
            print('１回目リクエスト：dataが　空なので[アクセスレート制限の可能性高い]')
            single_json_content_list=None
            return(single_json_content_list)
        #status code 200で空dataでもない場合、コンテンツリストに格納し、ループを回す
        else:
            contents_list.append(json_dict)
            try:
                while(json_dict['paging']['next']):
                    next_hash=str(json_dict['paging']['next'])
                    r_next = requests.get(next_hash)                
                #status code 200　じゃない場合
                    if(r_next.status_code is not requests.codes.ok):        
                        print( 'ステータスコード：'+str(r_next.status_code))
                        print('200じゃないので終了')
                        break
                    else:
                        json_dict = json.loads(r_next.text)
                        #空のjsondataか空じゃないかを判定、からの場合はループを止める
                        if(json_dict['data']==[]):
                            print('２回目以降リクエスト：dataが　空なので[アクセスレート制限の可能性高い]')
                            break
                #status code 200で、空dataでもない場合は、contents_listに格納
                        else:
                            contents_list.append(json_dict)
        #ループを抜けた後の処理
                            print('コンテンツリストの合計'+str(len(contents_list)))
                #１秒アクセスルール
                            time.sleep(1)
                #最大１００件取得まで取得したら抜ける
                            num=int(0)
                            for json_dict_test in enumerate(contents_list):
                                json_dict_num=len(json_dict_test[1]['data'])
                                num=num+json_dict_num
                            print('合計'+str(num))
                            if(int(num)>=100):
                                print('100以上なので、抜ける')
                                break
                        #ループを抜けたら、最後にjsonlist内に入ってるコンテンツを、全てシングルコンテンツにして格納する
                print("json_dictの格納（orループ処理)は完了しました。")
                single_json_content_list=[]
                for json_content in contents_list:
                    for single_json_content in json_content['data']:
                        single_json_content_list.append(single_json_content)
                        #シングルコンテンツの件数
                len_of_single_contents=len(single_json_content_list)
                print('コンテンツの件数は'+str(len_of_single_contents)+'件です')
                return(single_json_content_list)


            #KeyError: 'paging'対策
            except:
                print("paging 対策:json_dictの格納（orループ処理)は完了しました。")
                single_json_content_list=[]
                for json_content in contents_list:
                    for single_json_content in json_content['data']:
                        single_json_content_list.append(single_json_content)
                        #シングルコンテンツの件数
                len_of_single_contents=len(single_json_content_list)
                print('コンテンツの件数は'+str(len_of_single_contents)+'件です')
                return(single_json_content_list)



################################################################
##最近検索したハッシュタグの取得
################################################################

def hashtag_names(fb_access_token):

    global insta_id
    insta_id=insta_id
    id_name_json_dict=[]
    #最近検索したハッシュタグを入れる　　/recently_searched_hashtags?limit=30
    url = 'https://graph.facebook.com/v3.0/'+insta_id+'/recently_searched_hashtags?limit=30'+'&access_token='+fb_access_token
    r= requests.get(url)
    if(r.status_code is not requests.codes.ok):
        print( 'ステータスコード：'+str(r.status_code))
        print('200じゃないので終了')
    else:
        json_dict = json.loads(r.text)        
        #hash_tag_idから、ハッシュタグ名を検索
        #最近検索したハッシュタグを逆検索
        #17843829121032086=ゴルフ  json_dict['data'][0]['id']
        for hashtag_id in json_dict['data']:
            url_id_name = 'https://graph.facebook.com/v3.0/'+hashtag_id['id']+'?fields=id,name&access_token='+fb_access_token
            id_name= requests.get(url_id_name)
            if(id_name.status_code is not requests.codes.ok):
                print( 'ステータスコード：'+str(id_name.status_code))
                print('200じゃないので終了')
            else:
                id_name_json_dict.append(json.loads(id_name.text))
    return(id_name_json_dict)

################################################################
#####APIで感情分析する対象のテキストをjson形式で作成し、dict型に変換
################################################################
def azure_json_transform(single_json_content_list):
    azure_json=''
    for single_json_for_azure in single_json_content_list:

#キャプションがありの場合は以下
        if 'caption' in single_json_for_azure:
#ある場合は以下を実行する
            #カルーセルかどうか？
            if single_json_for_azure['media_type']=='CAROUSEL_ALBUM':
                
                try:
                    azure_json_single=str({'id': single_json_for_azure['id'],'language': 'ja','text':single_json_for_azure['caption'],'media_type':single_json_for_azure['media_type'],'comments_count':single_json_for_azure['comments_count'],'like_count':single_json_for_azure['like_count'],'permalink':single_json_for_azure['permalink'],'media_url':single_json_for_azure['children']['data'][0]['media_url']})
                    azure_json +=azure_json_single+','
                except:
                    try:
                        #とりあえず、一個づつtry exceptで行ってみて、３回やってもアクセスできないものはスキップすることにする
                        azure_json_single=str({'id': single_json_for_azure['id'],'language': 'ja','text':single_json_for_azure['caption'],'media_type':single_json_for_azure['media_type'],'comments_count':single_json_for_azure['comments_count'],'like_count':single_json_for_azure['like_count'],'permalink':single_json_for_azure['permalink'],'media_url':single_json_for_azure['children']['data'][1]['media_url']})
                        azure_json +=azure_json_single+','
                    except:
                        try:
                            azure_json_single=str({'id': single_json_for_azure['id'],'language': 'ja','text':single_json_for_azure['caption'],'media_type':single_json_for_azure['media_type'],'comments_count':single_json_for_azure['comments_count'],'like_count':single_json_for_azure['like_count'],'permalink':single_json_for_azure['permalink'],'media_url':single_json_for_azure['children']['data'][1]['media_url']})
                            azure_json +=azure_json_single+','
                        except:
                            try:
                                azure_json_single=str({'id': single_json_for_azure['id'],'language': 'ja','text':single_json_for_azure['caption'],'media_type':single_json_for_azure['media_type'],'comments_count':single_json_for_azure['comments_count'],'like_count':single_json_for_azure['like_count'],'permalink':single_json_for_azure['permalink'],'media_url':single_json_for_azure['children']['data'][1]['media_url']})
                                azure_json +=azure_json_single+','
                            except:
                                print('スキップ')

            #ビデオの場合
            elif single_json_for_azure['media_type']=='VIDEO':
                azure_json_single=str({'id': single_json_for_azure['id'],'language': 'ja','text':single_json_for_azure['caption'],'media_type':single_json_for_azure['media_type'],'comments_count':single_json_for_azure['comments_count'],'like_count':single_json_for_azure['like_count'],'permalink':single_json_for_azure['permalink'],'media_url':single_json_for_azure['media_url']})
                azure_json +=azure_json_single+','

            #イメージの場合
            elif single_json_for_azure['media_type']=='IMAGE':
                azure_json_single=str({'id': single_json_for_azure['id'],'language': 'ja','text':single_json_for_azure['caption'],'media_type':single_json_for_azure['media_type'],'comments_count':single_json_for_azure['comments_count'],'like_count':single_json_for_azure['like_count'],'permalink':single_json_for_azure['permalink'],'media_url':single_json_for_azure['media_url']})
                azure_json +=azure_json_single+','

#メディアなし？
            else:
                azure_json_single=str({'id': single_json_for_azure['id'],'language': 'ja','text':single_json_for_azure['caption'],'media_type':single_json_for_azure['media_type'],'comments_count':single_json_for_azure['comments_count'],'like_count':single_json_for_azure['like_count'],'permalink':single_json_for_azure['permalink']})
                azure_json +=azure_json_single+','

#キャプションがない場合は以下を実行する
        else:
            single_json_for_azure['caption']="キャプション無し"
            #カルーセルかどうか？
            if single_json_for_azure['media_type']=='CAROUSEL_ALBUM':
                try:
                    azure_json_single=str({'id': single_json_for_azure['id'],'language': 'ja','text':single_json_for_azure['caption'],'media_type':single_json_for_azure['media_type'],'comments_count':single_json_for_azure['comments_count'],'like_count':single_json_for_azure['like_count'],'permalink':single_json_for_azure['permalink'],'media_url':single_json_for_azure['children']['data'][0]['media_url']})
                    azure_json +=azure_json_single+','
                except:
                    azure_json_single=str({'id': single_json_for_azure['id'],'language': 'ja','text':single_json_for_azure['caption'],'media_type':single_json_for_azure['media_type'],'comments_count':single_json_for_azure['comments_count'],'like_count':single_json_for_azure['like_count'],'permalink':single_json_for_azure['permalink'],'media_url':single_json_for_azure['children']['data'][1]['media_url']})
                    azure_json +=azure_json_single+','
            #ビデオの場合
            elif single_json_for_azure['media_type']=='VIDEO':
                azure_json_single=str({'id': single_json_for_azure['id'],'language': 'ja','text':single_json_for_azure['caption'],'media_type':single_json_for_azure['media_type'],'comments_count':single_json_for_azure['comments_count'],'like_count':single_json_for_azure['like_count'],'permalink':single_json_for_azure['permalink'],'media_url':single_json_for_azure['media_url']})
                azure_json +=azure_json_single+','
            
            #イメージの場合
            elif single_json_for_azure['media_type']=='IMAGE':
                azure_json_single=str({'id': single_json_for_azure['id'],'language': 'ja','text':single_json_for_azure['caption'],'media_type':single_json_for_azure['media_type'],'comments_count':single_json_for_azure['comments_count'],'like_count':single_json_for_azure['like_count'],'permalink':single_json_for_azure['permalink'],'media_url':single_json_for_azure['media_url']})
                azure_json +=azure_json_single+','                

#キャプション無しでメディアなし　はあり得ない？
            else:
                azure_json_single=str({'id': single_json_for_azure['id'],'language': 'ja','text':single_json_for_azure['caption'],'media_type':single_json_for_azure['media_type'],'comments_count':single_json_for_azure['comments_count'],'like_count':single_json_for_azure['like_count'],'permalink':single_json_for_azure['permalink']})
                azure_json +=azure_json_single+','

    #最後だけカンマ抜く
    azure_json=azure_json[:-1]
    azure_json="{'documents' : ["+ azure_json+"]}"
    azure_json=ast.literal_eval(azure_json)
    return(azure_json)

################################################################
    #取得したデータに、ネガポジをつけ、json形式で保存
    #保存の際はキャッシュ対策にcash_bastingを画面側で行う
    ################################################################

def nega_posi_azure(azure_json):
    global subscription_key
    global text_analytics_base_url
    #APIキー
    subscription_key = subscription_key
    assert subscription_key

    #APIのエンドポイントの基盤を入力する
    text_analytics_base_url = text_analytics_base_url

    #感情分析を行うAPIのエンドポイントをセット
    sentiment_api_url = text_analytics_base_url + "sentiment"

    #ドキュメントのセンチメント スコアを0 ?1 の間で取得（高いスコアは肯定的なセンチメントを示します。）
    headers   = {"Ocp-Apim-Subscription-Key": subscription_key}
    response  = requests.post(sentiment_api_url, headers=headers, json=azure_json)
    sentiments = response.json()

    #念のため、ID順に、azure_json['documents']とsentiments['documents']をソートする
    sentiments['documents'].sort(key=lambda x: x['id'], reverse=False)
    azure_json['documents'].sort(key=lambda x: x['id'], reverse=False)

    print(len(sentiments['documents']))
    print(len(azure_json['documents']))

    #azure_jsonにネガポジスコアを格納
    for num,sentiments_single in enumerate(sentiments['documents']):
        #print(azure_json['documents'][num])
        azure_json['documents'][num]['score']=sentiments['documents'][num]['score']
    
    return(azure_json)


################################################################
    #azure apiのレスポンスを判定（azureの無料枠を超えていたら、200以外が返る）
    ################################################################
def nega_posi_azure_is_ok(azure_json):
    global subscription_key
    global text_analytics_base_url    
    #azure negaposi分析(まずは、free tierを超えてなないか確認)
    subscription_key = subscription_key
    assert subscription_key

    #APIのエンドポイントの基盤を入力する
    text_analytics_base_url = text_analytics_base_url

    #感情分析を行うAPIのエンドポイントをセット
    sentiment_api_url = text_analytics_base_url + "sentiment"

    #ドキュメントのセンチメント スコアを0 ?1 の間で取得（高いスコアは肯定的なセンチメントを示します。）
    headers   = {"Ocp-Apim-Subscription-Key": subscription_key}
    response  = requests.post(sentiment_api_url, headers=headers, json=azure_json)
    return(response)