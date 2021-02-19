import pymongo
import time
from datetime import datetime
import json
import requests
import pprint
import math

location = []
sx0 = 139.668636
sx1 = 139.798017
sy0 = 35.607243
sy1 = 35.736624

#範囲内のデータの数
def range_datas_quantities(x0,x1,y0,y1,json_data):
    keyList = json_data.keys()
    #print(keyList)
    i = 0
    for name in keyList:
        if( (x0 <= json_data[name]["lon"]) and (json_data[name]["lon"] <= x1)):
            if( (y0 <= json_data[name]["lat"]) and (json_data[name]["lat"] <= y1)):
                i+=1

    return i


#範囲内のデータを返す
def range_datas(x0,x1,y0,y1,json_data):
    indatas={}
    keyList = json_data.keys()
    samedata_count = 0
    #valList = json_data.values()
    for name in keyList:
        if( (x0  <= json_data[name]["lon"]) and (json_data[name]["lon"] <= x1 )):
            if( (y0 <= json_data[name]["lat"]) and (json_data[name]["lat"] <= y1 )):
            #nameがあるため、上書きされずに済んでいる
                indatas[name] = {
                        'lon':json_data[name]["lon"],
                        'lat':json_data[name]["lat"],
                        "text":json_data[name]["text"],
                        "timestamp_ms":json_data[name]["timestamp_ms"],
                        #"created_at":json_data[name]["created_at"]
                        }
    #print(indatas)
    #print(samedata_count)
    return indatas


#範囲内のツイートを変数formatに格納
def make_format(json_data):
    loccount = 0
    format = {"month":{"m7":{"day":{
                    "d16":{"tweets":[]},
                    "d17":{"tweets":[]},
                    "d18":{"tweets":[]},
                    "d19":{"tweets":[]},
                    "d20":{"tweets":[]},
                    "d21":{"tweets":[]},
                    "d22":{"tweets":[]},
                    "d23":{"tweets":[]},
                    "d24":{"tweets":[]},
                    "d25":{"tweets":[]},
                    "d26":{"tweets":[]},
                    "d27":{"tweets":[]},
                    "d28":{"tweets":[]},
                    "d29":{"tweets":[]}
                     }
                     }
                     }
                     }
    #print(len(json_data.keys())) #これの合計値も可笑しい
    for name in json_data.keys():
        t=json_data[name]["timestamp_ms"]
        t = int(t)
        day = datetime.fromtimestamp(t/1000)
        sm=str(day.month)
        sd=str(day.day)
        #print(json_data[name].keys())
        format["month"]["m"+sm]["day"]["d"+sd]["tweets"].append(
        {
            "text":json_data[name]["text"],
            "lon":json_data[name]["lon"],
            "lat":json_data[name]["lat"],
            "timestamp_ms":json_data[name]["timestamp_ms"],
            #"created_at":json_data[name]["created_at"]
        }
        )
        loccount = loccount + 1
    #print(loccount) #これの合計値がおかしい
    return format

#四分木
def four_devide_tree(x0,x1,y0,y1,json_data,count):
    #keyList = json_data.keys()
    #if(count == 1):
        #print(len(json_data.keys()))
    count = count + 1
        #分割しない条件
    if(range_datas_quantities(x0,x1,y0,y1,json_data)<10000):
        #d1 = range_datas(x0,x1,y0,y1,json_data)
        #print(len(json_data.keys())) #ここの合計が足りてない.
        d = make_format(json_data)
        #pprint.pprint(d)
        #for day in d["month"]["m7"]["day"].keys():
            #print(len(d["month"]["m7"]["day"][day]["tweets"]))
        location.append({
        'x0':x0,
        'x1':x1,
        'y0':y0,
        'y1':y1,
        'width':x1-x0,
        'height':y1-y0,
        "devidetweets":d
        })
        #print("x0:"+str(x0))
        #print("x1:"+str(x1))
        #print("y0:"+str(y0))
        #print("y1:"+str(y1))
        #print("(x0+x1)/2:"+str((x0+x1)/2))
        #print("(y0+y1)/2:"+str((y0+y1)/2))
        #print("-------")
        #print(location)
    else:
        #左上
        lu=range_datas(x0,(x1+x0)/2,(y0+y1)/2,y1,json_data)
        four_devide_tree(x0,(x1+x0)/2,(y0+y1)/2,y1,lu,count)
        #右上
        ru=range_datas((x0+x1)/2,x1,(y0+y1)/2,y1,json_data)
        four_devide_tree((x0+x1)/2,x1,(y0+y1)/2,y1,ru,count)
        #左下
        ld=range_datas(x0,(x1+x0)/2,y0,(y1+y0)/2,json_data)
        four_devide_tree(x0,(x1+x0)/2,y0,(y1+y0)/2,ld,count)
        #右下
        rd=range_datas((x0+x1)/2,x1,y0,(y1+y0)/2,json_data)
        four_devide_tree((x0+x1)/2,x1,y0,(y1+y0)/2,rd,count)

#番号をデータにふる
def regist_sqnumber(location):
    sqdatas = []
    for t in range(len(location)):
        sqdatas.append({
    #    'name':name,
    #    'lon':json_data[name]["lon"],
    #    'lat':json_data[name]["lat"],
        'sqnumber':t,
        'x0':location[t]["x0"],
        'x1':location[t]["x1"],
        'y0':location[t]["y0"],
        'y1':location[t]["y1"],
        'width':location[t]["width"],
        'height':location[t]["height"],
        'devidetweets':location[t]["devidetweets"]
        }
        )
    return sqdatas

def makedatabase():
    datas = []
    i = 0
    client = pymongo.MongoClient('localhost',50625)
    col = client['ex5']['japan'] #データベース指定, 適宜変える。

    for post in col.find(): #db.collection.find()で出てくるデータの総当たり
        #lonが経度, latが緯度
        #地理的に範囲内かどうか
        if((sx0<=post["geo"]["coordinates"][1])and(post["geo"]["coordinates"][1]<=sx1)):
            if((sy0<=post["geo"]["coordinates"][0])and(post["geo"]["coordinates"][0]<=sy1)):
            #日付的に範囲内かどうか
                t = post["timestamp_ms"]
                t = int(t)
                day = datetime.fromtimestamp(t/1000)
                if(day.year == 2018):
                    print(day.month)
                    if(day.month == 7):
                        d=day.day
                        print(d)
                        if((15<day.day) and (day.day<30)):
                            #データ登録
                            """
                            tweet["text"]=post["text"]
                            tweet["geo"]=post["geo"]
                            tweet["timestamp_ms"]=post["timestamp_ms"]
                            tweet["created_at"] = post["created_at"]
                            """
                            #print(tweet)
                            #i = str(i)
                            datas.append({
                                "text":post["text"],
                                "lon":post["geo"]["coordinates"][1],
                                "lat":post["geo"]["coordinates"][0],
                            #"geo":post["geo"]    ,
                                "timestamp_ms":post["timestamp_ms"],
                                "created_at": post["created_at"]
                                })
                            i = i + 1
                            print(i)
        #for文抜け出すためのもの
        #if(i==166939):
            #break
    #print(datas)
    #登録
    #return datas
    col = client["dripdatas"]["datas"]
    x = col.delete_many({})
    print(x.deleted_count, "dropdocuments deleted.")
    col = client["dripdatas"]["datas"]
    col.insert_many(datas)

def main():
    #makedatabase()
    client = pymongo.MongoClient('localhost',50625)
    col = client["dripdatas"]["datas"]
    json_data = {}
    i = 0
    for post in col.find():
        json_data[i]=post
        i = i + 1
    print(i)

    #print(json_data)
    #while x0 < x1:
        #while y0 < y1:
    #print(json_data.keys())
    four_devide_tree(sx0,sx1,sy0,sy1,json_data,0)
    d = regist_sqnumber(location)
    """
    count = 0
    for i in range(N):
        for t in range(N):
            q = range_datas_quantities(x0,x0+lont,y0,y0+latt,json_data)
            count = count + q
            print(x0)
            d = range_datas(x0,x0+lont,y0,y0+latt,json_data)
            #範囲内のデータdをindatasに加える=make_format
            indatas = make_format(indatas, d)
            location.append({
            'x0':x0,
            'x1':x0+lont,
            'y0':y0,
            'y1':y0+latt,
            'width':lont,
            'height':latt,
            "devidetweets":indatas
            })
            y0 = y0 + latt
        x0 = x0 + lont
        y0 = kalat
    print(count)
    """
    #make_daynum(json_data)
    #print(calc_cos_sim())
    col = client['create']["quant"]
    x = col.delete_many({})
    print(x.deleted_count, "fixdocuments deleted.")
    col = client['create']["quant"]
    col.insert_many(d)
    #"""
    #pprint.pprint(d)
    #print(json_data[192])
    #データ番号192がcoordinatesのまま.
    #print(col.findOne())
    #lonが経度, latが緯度
    #json_data = json.load(f) #json形式で読み込む
    #print(json.dumps(json_data,sort_keys = True, indent = 4)) json形式のデータプリント
    #keyList = json_data.keys()
    #print("{}", keyList) ABCD....
    #valList = json_data.values()
    #print(valList) #全ての緯度と経度
    #print(len(valList)) 緯度と経度の組み合わせが26個あると確認できる
    #d=range_datas(139.9,140,35.9,36,json_data)
    #d1 = make_format(json_data)
    #four_devide_tree(kulon,kalon,kalat,kulat,json_data,lont,latt)
    #d2 = regist_location_number(location)
    #print(location)
    #print(len(location))
    #print(json.dump(d, indent =2))
    #datas["datas"]["tweets"]=d1
    #datas["datas"]["locate"]=d2
    #print(datas)
    #print(location[1]["y1"])
    #print(json.dumps(location,indent = 2))
    #print(json.d\umps(d1, indent =2))
    #print(d2)
    #print(valList["lon"])
    #print(datas)
    #print(json.dumps(datas, indent =2))
    #client = pymongo.MongoClient(host='localhost',port=50625)
    #print(col.find_one())


if __name__=='__main__':
    main()
