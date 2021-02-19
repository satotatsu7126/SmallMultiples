import pymongo
import time
from datetime import datetime
import json
import requests
import pprint
import math
import matplotlib.pyplot as plt
import numpy as np
import copy
import sys
import resource

#実際の地理空間上の緯度経度，ツイッターの情報抽出に用いる
sx0 = 139.668636
sx1 = 139.798017
sy0 = 35.607243
sy1 = 35.736624

#グリッドに分けるための値
devidecount=3
scale=pow(2,devidecount)
tweetssum=123594
all_dispowsum = 0
created_datas = []
forjoinmain=[]
join_datas=[]
countlist=[]

mean_coslist=[]
max_coslist=[]
min_coslist=[]

mean_dqlist=[]
max_dqlist=[]
min_dqlist=[]

mean_asplist=[]
max_asplist=[]
min_asplist=[]

mean_celldqlist=[]
max_celldqlist=[]
min_celldqlist=[]

mean_visuallist=[]
max_visuallist=[]
min_visuallist=[]

mean_fillinglist=[]
max_fillinglist=[]
min_fillinglist=[]

Flist=[]

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
                        #"text":json_data[name]["text"],
                        "timestamp_ms":json_data[name]["timestamp_ms"],
                        #"created_at":json_data[name]["created_at"]
                        }
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
    for name in json_data.keys():
        t=json_data[name]["timestamp_ms"]
        t = int(t)
        day = datetime.fromtimestamp(t/1000)
        sm=str(day.month)
        sd=str(day.day)
        format["month"]["m"+sm]["day"]["d"+sd]["tweets"].append(
        {
            #"text":json_data[name]["text"],
            "lon":json_data[name]["lon"],
            "lat":json_data[name]["lat"],
            "timestamp_ms":json_data[name]["timestamp_ms"],
            #"created_at":json_data[name]["created_at"]
        }
        )
    for month in format["month"].keys():
        for day in format["month"][month]["day"].keys():
            tq = len(format["month"][month]["day"][day]["tweets"])
            format["month"][month]["day"][day]["tweets"] = tq
    return format

#四分木
def four_devide_tree(x0,x1,y0,y1,json_data,count):
    if(count == devidecount):
        format = make_format(json_data)
        created_datas.append({
        'x0':(x0-sx0)/(sx1-sx0)*scale,
        'x1':(x1-sx0)/(sx1-sx0)*scale,
        'y0':(y0-sy1)/(sy1-sy0)*scale,
        'y1':(y1-sy1)/(sy1-sy0)*scale,
        "devidetweets":format
        })
    else:
        count = count + 1
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


#番号をデータにふり, "include"の初期化
def regist_include(d):
    sqdatas = []
    for t in range(len(d)):
        sqdatas.append({
        'devidetweets':d[t]["devidetweets"],
        "include":[{
            "devidetweets":d[t]["devidetweets"],
            "sqnumber":t,
            "x0":d[t]["x0"],
            "x1":d[t]["x1"],
            "y0":d[t]["y0"],
            "y1":d[t]["y1"],
            "height":d[t]["y1"]-d[t]["y0"]
            }]
        })
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
                            datas.append({
                                #"text":post["text"],
                                "lon":post["geo"]["coordinates"][1],
                                "lat":post["geo"]["coordinates"][0],
                            #"geo":post["geo"]    ,
                                "timestamp_ms":post["timestamp_ms"],
                                "created_at": post["created_at"]
                                })
                            i = i + 1
                            print(i)
    col = client["dripdatas"]["datas"]
    x = col.delete_many({})
    print(x.deleted_count, "dropdocuments deleted.")
    col = client["dripdatas"]["datas"]
    col.insert_many(datas)

def make_daylist(format):
    list = []
    #i = 0
    for day in format["month"]["m7"]["day"].keys():
        if(format["month"]["m7"]["day"][day]["tweets"]!=0):
            list.append(format["month"]["m7"]["day"][day]["tweets"])
        else:
            list.append(0)
    return list

def three_count(mx0,mx1,my0,my1,sx0,sx1,sy0,sy1):
    if((my0==sy0) and (my1 == sy1)):
        if(mx0 == sx0 and mx1 == sx1):
            return 0
        if(mx0 == sx1):
            return 1 #l
        if(mx1 == sx0):
            return 2 #r
    if(mx0 == sx0 and mx1 == sx1):
        if(my1 == sy0):
            return 3 #u
        if(my0 == sy1):
            return 4 #d
    return 0

def sq_side(i,j,d):
    include_m=d[i]["include"]
    include_s=d[j]["include"]
    ret = 0
    for t in range(len(include_m)):
        for q in range(len(include_s)):
            mx0=include_m[t]["x0"]
            mx1=include_m[t]["x1"]
            my0=include_m[t]["y0"]
            my1=include_m[t]["y1"]
            sx0=include_s[q]["x0"]
            sx1=include_s[q]["x1"]
            sy0=include_s[q]["y0"]
            sy1=include_s[q]["y1"]
            if((three_count(mx0,mx1,my0,my1,sx0,sx1,sy0,sy1))!=0):
                ret = 1
                break;
    return ret


def sq_includeside(i,j,d):
    include_m=d
    include_s=d
    ret = 0
    mx0=include_m[i]["x0"]
    mx1=include_m[i]["x1"]
    my0=include_m[i]["y0"]
    my1=include_m[i]["y1"]
    sx0=include_s[j]["x0"]
    sx1=include_s[j]["x1"]
    sy0=include_s[j]["y0"]
    sy1=include_s[j]["y1"]
    if((three_count(mx0,mx1,my0,my1,sx0,sx1,sy0,sy1))!=0):
        ret = 1
    return ret

#四角を結合し, data型を返す
def sq_joinmain(ds,joinmax):
    d = ds
    global all_dispowsum
    global scale
    all_dispowsum =calc_alldispowsum(d)
    forjoinmain=[0]*(joinmax+1)
    for c in range(joinmax+1):
        forjoinmain[c]=d
        global countlist
        countlist=countlist+[c]
        forjoinmain[c] = regist_graphloc(forjoinmain[c])
        forjoinmain[c] = regist_sqloc(forjoinmain[c])
        forjoinmain[c] = regist_sqnumber(forjoinmain[c])
        #c回結合したものをjoin_datasに格納
        join_countdict = {}
        join_countdict["joincount"+str(c)] = d[:]
        join_datas.append(join_countdict)
        #celldq,visual,は1領域に対する計算

        print("結合回数"+str(c))
        regist_eval_celldq(forjoinmain[c])
        regist_eval_visual(forjoinmain[c])
        regist_eval_filling(forjoinmain[c])
        if(c!=0 and c!=scale*scale-1 and c > 14):
            regist_eval_F(forjoinmain[c],c)
        if(c == joinmax):
            #このとき,全て結合されている.
            break;
        #cossim,dq,aspは2領域間の計算
        regist_cossim(forjoinmain[c])
        regist_dq(forjoinmain[c])
        regist_asp(forjoinmain[c])
        W=make_propW(forjoinmain[c],c)
        s=search_W(W)
        max =s["max"]
        if(max==0):
            print("a")
            break;
        m_sqnumber=s["m_sqnumber"]
        s_sqnumber=s["s_sqnumber"]
        forjoinmain[c+1]=sq_join(m_sqnumber,s_sqnumber,forjoinmain[c])
        print("-----------")

#コサイン類似度行列W作成
def make_cosW(d):
    #64×64の行列が必要（四角が64個だから)
    global tweetssum
    W=[[-tweetssum for i in range(len(d))] for j in range(len(d))]
    for i in range(len(W[0])):
        for j in range(len(W[0])):
            #count = count + 1
            if(j != i):
                if(sq_side(i,j,d)!=0):
                    if(W[j][i]==-tweetssum):
                        W[i][j]=calc_cossim(d,i,j)
    return W

#cos類似度の計算
def calc_cossim(d,i,j):
    mlist = make_daylist(d[i]["devidetweets"])
    slist = make_daylist(d[j]["devidetweets"])
    m_pow=[]
    s_pow=[]
    naiseki = 0
    for t in range(len(mlist)):
        m_pow.append(mlist[t]*mlist[t])
        s_pow.append(slist[t]*slist[t])
        naiseki = naiseki + mlist[t]*slist[t]
    m_sum_root=math.sqrt(sum(m_pow))
    s_sum_root=math.sqrt(sum(s_pow))
    t = m_sum_root * s_sum_root
    if(t==0):
        return 0
    else:
        return(naiseki/t)

#ツイート数行列W1
def make_dqW(d):
    #64×64の行列が必要（四角が64個だから)
    global tweetssum
    W=[[ -tweetssum for i in range(len(d))] for j in range(len(d))]
    for i in range(len(W[0])):
        for j in range(len(W[0])):
            #count = count + 1
            if(j !=i ):
                if(sq_side(i,j,d)!=0):
                    if(W[j][i]==-tweetssum):
                        W[i][j]=calc_newdq(d,i,j)
    return W

"""
def calc_dq(d,i,j):
    mlist = make_daylist(d[i]["devidetweets"])
    slist = make_daylist(d[j]["devidetweets"])
    sum = 0
    for t in range(len(mlist)):
        sum = sum +mlist[t]+slist[t]
    if(sum==0):
        return 0
    else:
        return  (tweetssum-sum)/tweetssum
"""
def calc_newdq(d,i,j):
    global tweetssum
    visualrate=0.2
    mintqmax= tweetssum+20
    ysclist = []
    d = regist_graphloc(d)
    #結合前のyscを計算など下準備
    for t in range(len(d)):
        a = len(d)
        tqmax=calc_onecell_dqmax(d,t)
        ysclist=ysclist+[tqmax/(d[t]["gy1"]-d[t]["gy0"])]
        if(mintqmax>tqmax):
            mintqmax=tqmax
            mintqmaxsqnum = t
    ysc=max(ysclist)
    for t in range(len(ysclist)):
        if(ysclist[t]==ysc):
            yscsqnum=t
            del ysclist[t]
            break;
    #yscの候補
    before_ysc = max(ysclist)
    #各分割領域の最大値の中の最小値が，yscに対して一定以上なら0を返す．
    if(mintqmax>ysc*visualrate):
        return 0

    #初期化
    mlist = make_daylist(d[i]["devidetweets"])
    slist = make_daylist(d[j]["devidetweets"])
    resultlist=[0]*len(mlist)
    for l in range(len(mlist)):
        resultlist[l] = mlist[l]+slist[l]

    #縦に結合する場合
    by_yaxis=0
    include_m=d[i]["include"]
    include_s=d[j]["include"]
    new_d = [{}]
    #yscとなっている四角が関係しているかどうか
    if(yscsqnum==i or yscsqnum == j):
        for l in range(len(include_m)):
            for q in range(len(include_s)):
                mx0=include_m[l]["x0"]
                mx1=include_m[l]["x1"]
                my0=include_m[l]["y0"]
                my1=include_m[l]["y1"]
                sx0=include_s[q]["x0"]
                sx1=include_s[q]["x1"]
                sy0=include_s[q]["y0"]
                sy1=include_s[q]["y1"]
                #上下に隣接していたら
                if((three_count(mx0,mx1,my0,my1,sx0,sx1,sy0,sy1)>2)):
                    new_d[0]["include"]=include_m+include_s
                    #print("calc")
                    g = make_g(new_d,0)
                    new_ysc = max(resultlist)/(g["y1"]-g["y0"])
                    #結合してyscとなる四角が違う四角になったら
                    if(before_ysc<new_ysc):
                        #print("new")
                        ysc = new_ysc
                    else:
                        #print("before")
                        ysc = before_ysc
                    #最小の分割領域が結合して最小じゃなくなったら
                    if(i==mintqmaxsqnum or j == mintqmaxsqnum):
                        #最大値の中の最小値を結合後の最大値で初期化
                        mintqmax=max(resultlist)
                        #最小の値探しなおし
                        for t in range(len(d)):
                            #結合する前の分割領域を除く
                            if(t!=i or t!=j):
                                tqmax=calc_onecell_dqmax(d,t)
                                if(mintqmax>tqmax):
                                    mintqmax=tqmax
                    if((1-mintqmax/ysc)>0):
                        #print(mintqmax)
                        by_yaxis = 1-mintqmax/ysc

    #ツイート数を足す場合
    by_sum = 0
    #二つの分割領域のどちらかでも見えていない場合
    if(max(mlist)<ysc*visualrate or max(slist)<ysc*visualrate):
        by_sum=1-max(resultlist)/ysc

    #print("by_sum")
    #print(by_sum)
    #print("by_yaxis")
    #print(by_yaxis)
    #print("---------")
    if(by_sum<by_yaxis):
        #print("winaxis")
        #print(by_yaxis)
        return by_yaxis
    if(by_sum>by_yaxis):
        #print("winsum")
        #print(by_sum)
        return by_sum
    return 0

def make_aspW(d):
    global tweetssum
    W=[[ -tweetssum for i in range(len(d))] for j in range(len(d))]
    for i in range(len(W[0])):
        for j in range(len(W[0])):
            #count = count + 1
            if(j!=i):
                if(sq_side(i,j,d)!=0):
                    if(W[j][i]==-tweetssum):
                        W[i][j]=calc_asp(d,i,j)
    return W

def calc_asp(d,i,j):
    i_sq=len(d[i]["include"])
    j_sq=len(d[j]["include"])
    minx = 8
    maxx = 0
    miny = 0
    maxy = -8
    indq=d[i]["include"]
    for t in range(len(indq)):
        if(minx>indq[t]["x0"]):
            minx = indq[t]["x0"]
        if(maxx<indq[t]["x1"]):
            maxx = indq[t]["x1"]
        if(miny>indq[t]["y0"]):
            miny = indq[t]["y0"]
        if(maxy<indq[t]["y1"]):
            maxy = indq[t]["y1"]
    indq=d[j]["include"]
    for t in range(len(indq)):
        if(minx>indq[t]["x0"]):
            minx = indq[t]["x0"]
        if(maxx<indq[t]["x1"]):
            maxx = indq[t]["x1"]
        if(miny>indq[t]["y0"]):
            miny = indq[t]["y0"]
        if(maxy<indq[t]["y1"]):
            maxy = indq[t]["y1"]
    height = maxy-miny
    width = maxx-minx
    if(height<width):
        all_insidesq=width*width
    else:
        all_insidesq=height*height
    sum_insidesq=i_sq+j_sq
    asp=sum_insidesq/all_insidesq
    return asp

def make_celldqW(d):
    global tweetssum
    W=[[ -tweetssum for i in range(len(d))] for j in range(len(d))]
    for i in range(len(W[0])):
        for j in range(len(W[0])):
            #count = count + 1
            if(j==i):
                W[i][j]=calc_onecell_dqmax(d,i)
    return W

def calc_onecell_dqmax(d,i):
    tqlist = make_daylist(d[i]["devidetweets"])
    return max(tqlist)

def make_visualW(d):
    global tweetssum
    W=[[ -tweetssum for i in range(len(d))] for j in range(len(d))]
    for i in range(len(W[0])):
        for j in range(len(W[0])):
            if(i==j):
                W[i][j]=calc_visual(d,i)
    return W

def calc_visual(d,i):
    ysc=calc_ysc(d)
    tqmax = calc_onecell_dqmax(d,i)
    return tqmax/ysc

#縦軸の基準yscを求める
def calc_ysc(d):
    ysc = 0
    for i in range(len(d)):
        tqmax=calc_onecell_dqmax(d,i)
        if(ysc<tqmax/(d[i]["gy1"]-d[i]["gy0"])):
            ysc = tqmax/(d[i]["gy1"]-d[i]["gy0"])
    return ysc


def make_propW(d,count):
    global tweetssum
    W=[[ -tweetssum for i in range(len(d))] for j in range(len(d))]
    for i in range(len(W[0])):
        for j in range(len(W[0])):
            #count = count + 1
            if(j!=i):
                if(sq_side(i,j,d)!=0):
                    if(W[j][i]==-tweetssum):
                        W[i][j]=calc_prop(d,i,j,count)
    return W

def calc_prop(d,i,j,count):
    cossim = calc_cossim(d,i,j)
    dqsim = calc_newdq(d,i,j)
    #print(dqsim)
    asp = calc_asp(d,i,j)
    coes=calc_coes(count)
    a = coes["a"]
    b = coes["b"]
    c = coes["c"]
    prop = (a*cossim)+(b*dqsim)+(c*asp)
    return prop

def calc_coes(count):
    d = {}
    a = 1
    b = 0
    c = 0
    #a=64-0.01*count
    #b=64-0.01*count
    #c=1-a-b
    d["a"]=a
    d["b"]=b
    d["c"]=c
    return d

#行列Wの平均を求める
def mean_W(W):
    a = len(W[0])
    sum = 0
    count = 0
    for i in range(a):
        for t in range(a):
            if(W[i][t]!=-tweetssum):
                sum = sum+W[i][t]
                count = count + 1
    if(count==0):
        mean = 0
    else:
        mean = sum/count
    return mean

#Wから最大値と、最大値を取る二つの四角の番号,最小値を取り出す
def search_W(W):
    a = len(W[0])
    max = 0
    min = tweetssum*2
    m_sqnumber = 0
    s_sqnumber = 0
    for i in range(a):
        for t in range(a):
            if(max<W[i][t]):
                max = W[i][t]
                m_sqnumber = i
                s_sqnumber = t
            if(min>W[i][t]):
                if(W[i][t]>=0):
                    min = W[i][t]
    d={}
    d["max"]=max
    d["min"]=min
    d["m_sqnumber"]=m_sqnumber
    d["s_sqnumber"]=s_sqnumber
    return d

#i番の四角とj番の四角を統合したdata型を返す
def sq_join(i,j,d):
    data = d
    after_d = {"month":{"m7":{"day":{
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
    include = d[i]["include"]+d[j]["include"]
    i_daytweets =  d[i]["devidetweets"]["month"]["m7"]["day"]
    j_daytweets = d[j]["devidetweets"]["month"]["m7"]["day"]
    for day in after_d["month"]["m7"]["day"].keys():
        join_daytweets=i_daytweets[day]["tweets"]+j_daytweets[day]["tweets"]
        after_d["month"]["m7"]["day"][day]["tweets"]=join_daytweets
    if(i<j):
        del data[j]
        del data[i]
    else:
        del data[i]
        del data[j]
    data.append({
        #"sqnumber":after_sqnumber,
        "devidetweets":after_d,
        "include":include
        })
    return data

#棒グラフの位置を登録
def regist_graphloc(d):
    for i in range(len(d)):
        if(len(d[i].keys())!=6):
            #print("reg")
            g = make_g(d,i)
            d[i]["gy0"]=g["y0"]
            d[i]["gy1"]=g["y1"]
            d[i]["gx0"]=g["x0"]
            d[i]["gx1"]=g["x1"]
    return d

def make_g(d,i):
    heightlist=[]
    leftlist=[]
    rightlist=[]
#四角d[t]を上になるべく結合させた時の四角をjsonで表し結合
    for t in range(len(d[i]["include"])):
        copyd = copy.deepcopy(d[i]["include"])
        side = 3
        #print("a")
        json=search_include(copyd,t,1,side)
        heightlist.append(json)

#四角d[t]を左になるべく結合させた時の四角をjsonで表し結合
    for t in range(len(heightlist)):
        copylist =heightlist
        side = 1
        #print("b")
        json = search_include(copylist,t,1,side)
        leftlist.append(json)

#四角d[t]を右になるべく結合させた時の四角をjsonで表し結合
    for t in range(len(leftlist)):
        copylist = leftlist
        side = 2
        #print("c")
        json = search_include(copylist,t,1,side)
        rightlist.append(json)

    height = 0
    width = 0
    for t in range(len(rightlist)):
        x0=rightlist[t]["x0"]
        x1=rightlist[t]["x1"]
        y0=rightlist[t]["y0"]
        y1=rightlist[t]["y1"]
        if((y1-y0)>height):
            height = y1-y0
            width = x1-x0
            maxjson=rightlist[t]
        elif((y1-y0)==height):
            if((x1-x0)>width):
                width=x1-x0
                maxjson=rightlist[t]
    return maxjson

#sideで指定される方向になるべく結合, 結合されたらupdateを1にして結合の有無を再度判断
def search_include(data,t,update,side):
    d = data
    for j in range(len(d)+1):
        if(update==0):
            json ={
                "sqnumber":d[t]["sqnumber"],
                "x0":d[t]["x0"],
                "x1":d[t]["x1"],
                "y0":d[t]["y0"],
                "y1":d[t]["y1"]
                }
            return json
        else:
            #print("a")
            #pprint.pprint(d)
            mx0=d[t]["x0"]
            mx1=d[t]["x1"]
            my0=d[t]["y0"]
            my1=d[t]["y1"]
            for s in range(len(d)):
                update = 0
                sx0=d[s]["x0"]
                sx1=d[s]["x1"]
                sy0=d[s]["y0"]
                sy1=d[s]["y1"]
                if(s!=t):
                    if(three_count(mx0,mx1,my0,my1,sx0,sx1,sy0,sy1)==side):
                        if(side==3):
                            tmp = d[t]["y1"]
                            d[t]["y1"]=d[s]["y1"]
                            d[s]["y1"]=tmp
                            update = 1
                            break
                        elif(side==2):
                            tmp = d[t]["x1"]
                            d[t]["x1"]=d[s]["x1"]
                            d[s]["x1"]=tmp
                            update = 1
                            break
                        elif(side==1):
                            tmp = d[t]["x0"]
                            d[t]["x0"]=d[s]["x0"]
                            d[s]["x0"]=tmp
                            update = 1
                            break

    """
    if(update==0):
        json ={
                "sqnumber":d[t]["sqnumber"],
                "x0":d[t]["x0"],
                "x1":d[t]["x1"],
                "y0":d[t]["y0"],
                "y1":d[t]["y1"]
            }
        return json
    else:
        update = 0
        mx0=d[t]["x0"]
        mx1=d[t]["x1"]
        my0=d[t]["y0"]
        my1=d[t]["y1"]
        for s in range(len(d)):
            sx0=d[s]["x0"]
            sx1=d[s]["x1"]
            sy0=d[s]["y0"]
            sy1=d[s]["y1"]
            if(s!=t):
                if(three_count(mx0,mx1,my0,my1,sx0,sx1,sy0,sy1)==side):
                    if(side==3):
                        tmp = d[t]["y1"]
                        d[t]["y1"]=d[s]["y1"]
                        d[s]["y1"]=tmp
                        update = 1
                        break
                    if(side==2):
                        tmp = d[t]["x1"]
                        d[t]["x1"]=d[s]["x1"]
                        d[s]["x1"]=tmp
                        update = 1
                        break
                    if(side==1):
                        tmp = d[t]["x0"]
                        d[t]["x0"]=d[s]["x0"]
                        d[s]["x0"]=tmp
                        update = 1
                        break
        return search_include(d,t,update,side)
        """

def regist_sqloc(d):
    for i in range(len(d)):
        lineloc = make_lineloc(d,i)
        d[i]["lineloc"]=lineloc
    return d

def make_lineloc(d,i):
    lineloc=[]
    lineloc_child = []
    loc = {}
    for t in range(len(d[i]["include"])):
        mx0=d[i]["include"][t]["x0"]
        mx1=d[i]["include"][t]["x1"]
        my0=d[i]["include"][t]["y0"]
        my1=d[i]["include"][t]["y1"]
        lineloc_child=[{
                "x0":mx0,
                "y0":my0,
                "y1":my1,
                "side":0},
                {
                "x1":mx1,
                "y0":my0,
                "y1":my1,
                "side":1},
                {
                "x0":mx0,
                "x1":mx1,
                "y1":my1,
                "side":2},
                {
                "x0":mx0,
                "x1":mx1,
                "y0":my0,
                "side":3}
                ]
        for q in range(len(d[i]["include"])):
            sx0=d[i]["include"][q]["x0"]
            sx1=d[i]["include"][q]["x1"]
            sy0=d[i]["include"][q]["y0"]
            sy1=d[i]["include"][q]["y1"]
            if(q !=t):
                judge = three_count(mx0,mx1,my0,my1,sx0,sx1,sy0,sy1)
                if(judge != 0):
                    for s in range(len(lineloc_child)):
                        if(lineloc_child[s]["side"]==judge-1):
                            del lineloc_child[s]
                            break
        lineloc = lineloc + lineloc_child
    return  lineloc


def regist_sqnumber(d):
    for i in range(len(d)):
        d[i]["sqnumber"]=i
    return d

def matplotall():
    count_for_onecell = np.array(countlist)
    count_for_twocell = np.array(range(len(countlist)-1))
    """
    plt.figure(figsize=(20,10))
    #subplot(縦何個，横何個, どこか)
    plt.subplot(3,3,1)
    mean = np.array(mean_coslist)
    min = np.array(min_coslist)
    max = np.array(max_coslist)
    plt.plot(count_for_twocell,max,label="max")
    plt.plot(count_for_twocell,mean,label="mean")
    plt.plot(count_for_twocell,min,label="min")
    plt.title("cossim")
    plt.xlabel("times")
    plt.ylabel("cossim")
    #plt.legend(bbox_to_anchor=(0.8, 0.2), loc='upper left', borderaxespad=0)
    #plt.subplots_adjust(right=0.7)

    plt.subplot(3,3,2)
    mean = np.array(mean_dqlist)
    min = np.array(min_dqlist)
    max = np.array(max_dqlist)
    plt.plot(count_for_twocell,max,label="max")
    plt.plot(count_for_twocell,mean,label="mean")
    plt.plot(count_for_twocell,min,label="min")
    plt.title("two_cell_sum")
    plt.xlabel("times")
    plt.ylabel("dq")
    #plt.legend(bbox_to_anchor=(0.2, 0.2), loc='upper left', borderaxespad=0)
    #plt.subplots_adjust(right=0.7)
    plt.subplot(3,3,3)
    mean = np.array(mean_asplist)
    min = np.array(min_asplist)
    max = np.array(max_asplist)
    plt.plot(count_for_twocell,max,label="max")
    plt.plot(count_for_twocell,mean,label="mean")
    plt.plot(count_for_twocell,min,label="min")
    plt.title("asp")
    plt.xlabel("times")
    plt.ylabel("asp")

    plt.subplot(2,2,1)
    mean = np.array(mean_celldqlist)
    min = np.array(min_celldqlist)
    max = np.array(max_celldqlist)
    plt.plot(count_for_onecell,max,label="max")
    plt.plot(count_for_onecell,mean,label="mean")
    plt.plot(count_for_onecell,min,label="min")
    plt.title("one_cell_max")
    plt.xlabel("times")
    plt.ylabel("celldq")
    #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    #plt.subplots_adjust(height=0.7)
    """
    global Flist
    t=[0]*len(Flist)
    for s in range(len(Flist)):
        t[s]=s+1+14
    #plt.subplot(2,2,1)
    plt.plot(t,Flist,label="F")
    plt.title("pseudo-connectF")
    plt.xlabel("jointimes")
    plt.ylabel("pseudo-connectF")
    #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    plt.show()

    #plt.subplot(2,2,2)
    mean = np.array(mean_visuallist)
    min = np.array(min_visuallist)
    max = np.array(max_visuallist)
    plt.plot(count_for_onecell,mean,label="mean")
    plt.plot(count_for_onecell,max,label="max")
    plt.plot(count_for_onecell,min,label="min")
    plt.title("visual")
    plt.xlabel("jointimes")
    plt.ylabel("visual")
    plt.legend(bbox_to_anchor=(1, 1), loc='upper left', borderaxespad=0)
    plt.show()

    #plt.subplot(1,1,1)
    mean = np.array(mean_fillinglist)
    min = np.array(min_fillinglist)
    max = np.array(max_fillinglist)
    plt.plot(count_for_onecell,mean,label="mean")
    plt.plot(count_for_onecell,max,label="max")
    plt.plot(count_for_onecell,min,label="min")
    plt.xlabel("jointimes")
    plt.title("filling")
    plt.ylabel("filling")
    plt.legend(bbox_to_anchor=(1, 1), loc='upper left', borderaxespad=0)
    plt.show()

def regist_db(join_datas):
    #apiを公開しやすくするために入れ子構造を作る
    dict = {}
    dict["join"]=join_datas
    list = []
    list.append(dict)
    client = pymongo.MongoClient('localhost',50625)
    col = client['create']["prop"]
    x = col.delete_many({})
    print(x.deleted_count, "fixdocuments deleted.")
    col = client['create']["prop"]
    col.insert_many(list)

def main():
    #makedatabase()
    #sys.setrecursionlimit(100000)
    #resource.setrlimit(resource.RLIMIT_STACK,(-1,1024))
    client = pymongo.MongoClient('localhost',50625)
    col = client["dripdatas"]["datas"]
    json_data = {}
    i = 0
    for post in col.find():
        json_data[i]=post
        i = i + 1
    four_devide_tree(sx0,sx1,sy0,sy1,json_data,0)
    d=regist_include(created_datas)
    joincount=len(d)-1
    sq_joinmain(d,joincount)
    regist_db(join_datas)
    matplotall()

def regist_cossim(d):
    global mean_coslist
    global max_coslist
    global min_coslist
    cosW=make_cosW(d)
    search_cosW=search_W(cosW)
    mean_coslist=mean_coslist+[mean_W(cosW)]
    max_coslist=max_coslist+[search_cosW["max"]]
    min_coslist=min_coslist+[search_cosW["min"]]

def regist_dq(d):
    global mean_dqlist
    global max_dqlist
    global min_dqlist
    dqW=make_dqW(d)
    search_dqW=search_W(dqW)
    mean_dqlist=mean_dqlist+[mean_W(dqW)]
    max_dqlist=max_dqlist+[search_dqW["max"]]
    min_dqlist=min_dqlist+[search_dqW["min"]]

def regist_asp(d):
    global mean_asplist
    global max_asplist
    global min_asplist
    aspW=make_aspW(d)
    search_aspW=search_W(aspW)
    mean_asplist=mean_asplist+[mean_W(aspW)]
    max_asplist=max_asplist+[search_aspW["max"]]
    min_asplist=min_asplist+[search_aspW["min"]]


def regist_eval_celldq(d):
    global mean_celldqlist
    global max_celldqlist
    global min_celldqlist
    celldqW=make_celldqW(d)
    search_celldqW=search_W(celldqW)
    mean_celldqlist=mean_celldqlist+[mean_W(celldqW)]
    max_celldqlist=max_celldqlist+[search_celldqW["max"]]
    min_celldqlist=min_celldqlist+[search_celldqW["min"]]

def regist_eval_visual(d):
    global mean_visuallist
    global max_visuallist
    global min_visuallist
    visualW=make_visualW(d)
    search_visualW=search_W(visualW)
    mean_visuallist=mean_visuallist+[mean_W(visualW)]
    max_visuallist=max_visuallist+[search_visualW["max"]]
    min_visuallist=min_visuallist+[search_visualW["min"]]
    print("グラフの見かけ上の高さの評価")
    print("平均値:"+str(mean_W(visualW)))
    print("最大値:"+str(search_visualW["max"]))
    print("最小値："+str(search_visualW["min"]))

def regist_eval_filling(d):
    global mean_fillinglist
    global max_fillinglist
    global min_fillinglist
    fillingW=make_fillingW(d)
    search_fillingW=search_W(fillingW)
    mean_fillinglist=mean_fillinglist+[mean_W(fillingW)]
    max_fillinglist=max_fillinglist+[search_fillingW["max"]]
    min_fillinglist=min_fillinglist+[search_fillingW["min"]]
    print("充填率の評価")
    print("平均値:"+str(mean_W(fillingW)))
    print("最大値:"+str(search_fillingW["max"]))
    print("最小値："+str(search_fillingW["min"]))

def make_fillingW(d):
    global tweetssum
    W=[[ -tweetssum for i in range(len(d))] for j in range(len(d))]
    for i in range(len(W[0])):
        for j in range(len(W[0])):
            if(i==j):
                W[i][j]=calc_filling(d,i)
    return W

def regist_eval_F(d,c):
    global Flist
    F = calc_F(d,c)
    Flist = Flist +[F]
    print("F値:"+str(F))

def calc_F(d,c):
    global all_dispowsum
    global scale
    inside_dispowsum=calc_insidedispow(d)
    allsq=scale*scale
    bunbo = inside_dispowsum/(allsq-allsq+c)
    bunshi = (all_dispowsum-inside_dispowsum)/(allsq-c-1)
    F=bunshi/bunbo
    print("クラスタ内二乗和:"+str(inside_dispowsum))
    print("全サンプル数ークラスタ数:"+str(allsq-allsq+c))
    print("分母:"+str(bunbo))
    print("全クラスタ二乗和:"+str(all_dispowsum))
    print("全クラスタ二乗和－クラスタ内二乗和:"+str(all_dispowsum-inside_dispowsum))
    print("クラスタ数-1:"+str(allsq-c-1))
    print("分子:"+str(bunshi))
    print(F)
    return F

def calc_insidedispow(d):
    global tweetssum
    sum = 0
    for i in range(len(d)):
        W=[[ -tweetssum for t in range(len(d[i]["include"]))] for j in range(len(d[i]["include"]))]
        insq=d[i]["include"]
        insqsum=0
        for a in range(len(W[0])):
            for b in range(len(W[0])):
                if(a != b):
                    if(sq_includeside(a,b,insq)!=0):
                        if(W[b][a]==-tweetssum):
                            #pprint.pprint(insq)
                            #print("----")
                            #print(insq[a]["sqnumber"])
                            #print(make_daylist(insq[a]["devidetweets"]))
                            #print(insq[b]["sqnumber"])
                            #print(make_daylist(insq[b]["devidetweets"]))
                            #print(i)
                            #print("-----")
                            score = 1-calc_cossim(insq,a,b)
                            W[a][b]=score*score
                            insqsum=insqsum+score*score
        sum = sum +insqsum
    return sum

def calc_alldispowsum(d):
    global tweetssum
    W=[[-tweetssum for i in range(len(d))] for j in range(len(d))]
    sum = 0
    for i in range(len(W[0])):
        for j in range(len(W[0])):
            #count = count + 1
            if(j != i):
                if(sq_side(i,j,d)!=0):
                    if(W[j][i]==-tweetssum):
                        score = 1-calc_cossim(d,i,j)
                        print(score)
                        W[i][j]=score*score
                        sum = sum + score*score
    return sum

def calc_filling(d,i):
    indq=d[i]["include"]
    i_sq=len(d[i]["include"])
    minx = 8
    maxx = 0
    miny = 0
    maxy = -8
    for t in range(len(indq)):
        if(minx>indq[t]["x0"]):
            minx = indq[t]["x0"]
        if(maxx<indq[t]["x1"]):
            maxx = indq[t]["x1"]
        if(miny>indq[t]["y0"]):
            miny = indq[t]["y0"]
        if(maxy<indq[t]["y1"]):
            maxy = indq[t]["y1"]
    height = maxy-miny
    width = maxx-minx
    if(height<width):
        all_insidesq=width*width
    else:
        all_insidesq=height*height
    filling = i_sq/all_insidesq
    return filling

if __name__=='__main__':
    main()
