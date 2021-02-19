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

created_datas = []
sx0 = 139.668636
sx1 = 139.798017
sy0 = 35.607243
sy1 = 35.736624
devidecount=3
scale=pow(2,devidecount)
tweetssum=123594
join_datas=[]
countnum=[]

meancosnum=[]
maxcosnum=[]
mincosnum=[]

meandqnum=[]
maxdqnum=[]
mindqnum=[]

meanaspnum=[]
maxaspnum=[]
minaspnum=[]

meancelldqnum=[]
maxcelldqnum=[]
mincelldqnum=[]

meanvisualnum=[]
maxvisualnum=[]
minvisualnum=[]

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

def make_daynum(format):
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
    count = 0
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
#四角を結合し, data型を返す
def sq_joinmain(d,count,i):
    c=count
    W=make_cosW(d)
    if(count == i):
        global countnum
        countnum=countnum+[count]
        return d
    else:
        s=search_W(W)
        max =s["max"]
        m_sqnumber=s["m_sqnumber"]
        s_sqnumber=s["s_sqnumber"]
        d=sq_join(m_sqnumber,s_sqnumber,d)
        c = count + 1
        #sq_joinmain(d,c)
        return sq_joinmain(d,c,i)

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
    mnum = make_daynum(d[i]["devidetweets"])
    snum = make_daynum(d[j]["devidetweets"])
    m_pow=[]
    s_pow=[]
    naiseki = 0
    for t in range(len(mnum)):
        m_pow.append(mnum[t]*mnum[t])
        s_pow.append(snum[t]*snum[t])
        naiseki = naiseki + mnum[t]*snum[t]
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
                        W[i][j]=calc_dq(d,i,j)
    return W

def calc_dq(d,i,j):
    mnum = make_daynum(d[i]["devidetweets"])
    snum = make_daynum(d[j]["devidetweets"])
    sum = 0
    for t in range(len(mnum)):
        sum = sum +mnum[t]+snum[t]
    if(sum==0):
        return 0
    else:
        return  (tweetssum-sum)/tweetssum

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
    indq=d[i]["include"]
    i_sq=len(d[i]["include"])
    j_sq=len(d[j]["include"])
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
                W[i][j]=calc_celldq(d,i)
    return W

def calc_celldq(d,i):
    tqnum = make_daynum(d[i]["devidetweets"])
    #print(max(tqnum))
    return max(tqnum)


def make_visualW(d):
    ysc=calc_ysc(d)
    global tweetssum
    W=[[ -tweetssum for i in range(len(d))] for j in range(len(d))]
    for i in range(len(W[0])):
        for j in range(len(W[0])):
            if(i==j):
                W[i][j]=calc_visual(d,i,ysc)
    return W

#縦軸の基準yscを求める
def calc_ysc(d):
    ysc = 0
    for i in range(len(d)):
        #四角d[i]のツイート数を日付順にリストに入れたものtqnum作成
        tqnum=make_daynum(d[i]["devidetweets"])
        tqmax=max(tqnum)
        if(ysc<tqmax/(d[i]["gy1"]-d[i]["gy0"])):
            ysc = tqmax/(d[i]["gy1"]-d[i]["gy0"])
    return ysc

def calc_visual(d,i,ysc):
    tqnum = make_daynum(d[i]["devidetweets"])
    tqmax = max(tqnum)
    return tqmax/ysc


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
    dqsim = calc_dq(d,i,j)
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
    b = 1
    c = 1
    #a=64-0.01*count
    #b=64-0.01*count
    #c=1-a-b
    d["a"]=a
    d["b"]=b
    d["c"]=c
    return d

#コサイン類似度の平均を求める
def mean_W(W):
    a = len(W[0])
    sum = 0
    count = 0
    for i in range(a):
        for t in range(a):
            if(W[i][t]!=-tweetssum):
                sum = sum+W[i][t]
                count = count + 1
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
        copyd = copy.deepcopy(d)
        copyd = copyd[i]["include"]
        side = 3
        json=search_include(copyd,t,1,side)
        heightlist.append(json)

#四角d[t]を左になるべく結合させた時の四角をjsonで表し結合
    for t in range(len(heightlist)):
        copylist = copy.deepcopy(heightlist)
        side = 1
        json = search_include(copylist,t,1,side)
        leftlist.append(json)

#四角d[t]を右になるべく結合させた時の四角をjsonで表し結合
    for t in range(len(leftlist)):
        copylist = copy.deepcopy(leftlist)
        side = 2
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
def search_include(d,t,update,side):
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
            three_count(mx0,mx1,my0,my1,sx0,sx1,sy0,sy1)
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




def check(d):
        """
        if(i==44):
            print(i)
            print(d[i]["gx0"])
            print(d[i]["gx1"])
            print(d[i]["gy0"])
            print(d[i]["gy1"])
            pprint.pprint(d[i]["include"])
            print(d[i]["x0num"])
            print("----------")
        if(i==38):
            print(i)
            print(d[i]["x0"])
            print(d[i]["x1"])
            print(d[i]["y0"])
            print(d[i]["y1"])
        """

def regist_sqnumber(d):
    for i in range(len(d)):
        d[i]["sqnumber"]=i
    return d


def matplotall():
    count = np.array(countnum)
    plt.figure(figsize=(20,10))
    #subplot(縦何個，横何個, どこか)
    plt.subplot(2,3,1)
    mean = np.array(meancosnum)
    min = np.array(mincosnum)
    max = np.array(maxcosnum)
    plt.plot(count,max,label="max")
    plt.plot(count,mean,label="mean")
    plt.plot(count,min,label="min")
    plt.title("cossim")
    plt.xlabel("times")
    plt.ylabel("cossim")
    #plt.legend(bbox_to_anchor=(0.8, 0.2), loc='upper left', borderaxespad=0)
    #plt.subplots_adjust(right=0.7)

    plt.subplot(2,3,2)
    mean = np.array(meandqnum)
    min = np.array(mindqnum)
    max = np.array(maxdqnum)
    plt.plot(count,max,label="max")
    plt.plot(count,mean,label="mean")
    plt.plot(count,min,label="min")
    plt.title("two_cell_sum")
    plt.xlabel("times")
    plt.ylabel("dq")
    #plt.legend(bbox_to_anchor=(0.2, 0.2), loc='upper left', borderaxespad=0)
    #plt.subplots_adjust(right=0.7)

    plt.subplot(2,3,3)
    mean = np.array(meanaspnum)
    min = np.array(minaspnum)
    max = np.array(maxaspnum)
    plt.plot(count,max,label="max")
    plt.plot(count,mean,label="mean")
    plt.plot(count,min,label="min")
    plt.title("asp")
    plt.xlabel("times")
    plt.ylabel("asp")

    plt.subplot(2,3,4)
    mean = np.array(meancelldqnum)
    min = np.array(mincelldqnum)
    max = np.array(maxcelldqnum)
    plt.plot(count,max,label="max")
    plt.plot(count,mean,label="mean")
    plt.plot(count,min,label="min")
    plt.title("one_cell_max")
    plt.xlabel("times")
    plt.ylabel("celldq")
    #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    #plt.subplots_adjust(right=0.7)
    plt.subplot(2,3,5)
    mean = np.array(meanvisualnum)
    min = np.array(minvisualnum)
    max = np.array(maxvisualnum)
    plt.plot(count,max,label="max")
    plt.plot(count,mean,label="mean")
    plt.plot(count,min,label="min")
    plt.title("one_cell_max_rate_yaxis")
    plt.xlabel("times")
    plt.ylabel("visual")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    plt.show()

def regist_db(join_datas):
    #apiを公開しやすくするために入れ子構造を作る
    dict = {}
    dict["join"]=join_datas
    list = []
    list.append(dict)
    client = pymongo.MongoClient('localhost',50625)
    col = client['create']["cossim"]
    x = col.delete_many({})
    print(x.deleted_count, "fixdocuments deleted.")
    col = client['create']["cossim"]
    col.insert_many(list)

def main():
    #makedatabase()
    client = pymongo.MongoClient('localhost',50625)
    col = client["dripdatas"]["datas"]
    json_data = {}
    i = 0
    for post in col.find():
        json_data[i]=post
        i = i + 1
    four_devide_tree(sx0,sx1,sy0,sy1,json_data,0)
    for i in range(len(created_datas)-1):
        d=regist_include(created_datas)
        join_dict = {}
        #print(i)
        d = sq_joinmain(d,0,i)
        d = regist_graphloc(d)
        regist_graphnums(d)
        d = regist_sqloc(d)
        d = regist_sqnumber(d)
        join_dict["joincount"+str(i)] = d
        join_datas.append(join_dict)
    regist_db(join_datas)
    matplotall()

def regist_graphnums(d):
        regist_cossim(d)
        regist_dq(d)
        regist_asp(d)
        regist_celldq(d)
        regist_visual(d)

def regist_cossim(d):
    global meancosnum
    global maxcosnum
    global mincosnum
    cosW=make_cosW(d)
    search_cosW=search_W(cosW)
    meancosnum=meancosnum+[mean_W(cosW)]
    maxcosnum=maxcosnum+[search_cosW["max"]]
    mincosnum=mincosnum+[search_cosW["min"]]

def regist_dq(d):
    global meandqnum
    global maxdqnum
    global mindqnum
    dqW=make_dqW(d)
    search_dqW=search_W(dqW)
    meandqnum=meandqnum+[mean_W(dqW)]
    maxdqnum=maxdqnum+[search_dqW["max"]]
    mindqnum=mindqnum+[search_dqW["min"]]

def regist_asp(d):
    global meanaspnum
    global maxaspnum
    global minaspnum
    aspW=make_aspW(d)
    search_aspW=search_W(aspW)
    meanaspnum=meanaspnum+[mean_W(aspW)]
    maxaspnum=maxaspnum+[search_aspW["max"]]
    minaspnum=minaspnum+[search_aspW["min"]]

def regist_celldq(d):
    global meancelldqnum
    global maxcelldqnum
    global mincelldqnum
    celldqW=make_celldqW(d)
    search_celldqW=search_W(celldqW)
    meancelldqnum=meancelldqnum+[mean_W(celldqW)]
    maxcelldqnum=maxcelldqnum+[search_celldqW["max"]]
    #print(search_celldqW["min"])
    mincelldqnum=mincelldqnum+[search_celldqW["min"]]

def regist_visual(d):
    global meanvisualnum
    global maxvisualnum
    global minvisualnum
    visualW=make_visualW(d)
    search_visualW=search_W(visualW)
    meanvisualnum=meanvisualnum+[mean_W(visualW)]
    maxvisualnum=maxvisualnum+[search_visualW["max"]]
    minvisualnum=minvisualnum+[search_visualW["min"]]



if __name__=='__main__':
    main()
