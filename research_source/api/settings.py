#!/home/tatsuyasato/anaconda3/bin/python
MONGO_URI = 'mongodb://localhost:50625/create'  # 接続先MongoDBの //ドメイン:ポート番号/DB名
X_DOMAINS = '*'               # このAPIへのアクセス許可ドメイン
HATEOAS = False               # Restfulの拡張
PAGINATION = False            # ページ送り
URL_PREFIX = 'api'            # このAPIのURL接頭辞 http://localhost:50503/api
DOMAIN ={
    'fix1616':{    # 公開するmongodbコレクション名
    'item_title': 'fix1616',  # 返されるjsonファイルにおけるkey
    'url':'fix1616',          # 公開用のURL http://localhost:50503/api/fixdevide
    'schema':{
        'sqnumber':{'type':"stringify"},
        'x0':{'type':'float'},  # 以降，jsonファイルに含めるmongodbのフィールド(キー)名と型
        'x1':{'type':'float'},
        'y0':{'type':'float'},
        'y1':{'type': 'float'},
        'width':{'type':'float'},
        'height':{'type':'float'},
        'devidetweets':{},
            }
        },
    'fix88':{    # 公開するmongodbコレクション名
    'item_title': 'fix88',  # 返されるjsonファイルにおけるkey
    'url':'fix88',          # 公開用のURL http://localhost:50503/api/fixdevide
    'schema':{
        'sqnumber':{'type':"stringify"},
        'x0':{'type':'float'},  # 以降，jsonファイルに含めるmongodbのフィールド(キー)名と型
        'x1':{'type':'float'},
        'y0':{'type':'float'},
        'y1':{'type': 'float'},
        'width':{'type':'float'},
        'height':{'type':'float'},
        'devidetweets':{}
            }
        },
    'quant':{    # 公開するmongodbコレクション名
    'item_title': 'quant',  # 返されるjsonファイルにおけるkey
    'url':'quant',          # 公開用のURL http://localhost:50503/api/fixdevide
    'schema':{
        'sqnumber':{'type':"stringify"},
        'x0':{'type':'float'},  # 以降，jsonファイルに含めるmongodbのフィールド(キー)名と型
        'x1':{'type':'float'},
        'y0':{'type':'float'},
        'y1':{'type': 'float'},
        'width':{'type':'float'},
        'height':{'type':'float'},
        'devidetweets':{}
            }
        },
    'cossim':{    # 公開するmongodbコレクション名
    'item_title': 'cossim',  # 返されるjsonファイルにおけるkey
    'url':'cossim',          # 公開用のURL http://localhost:50503/api/fixdevide
    'schema':{"join":[]
            }
        },
    'quantsim':{    # 公開するmongodbコレクション名
    'item_title': 'quantsim',  # 返されるjsonファイルにおけるkey
    'url':'quantsim',          # 公開用のURL http://localhost:50503/api/fixdevide
    'schema':{"join":[]
            }
        },
    'prop':{    # 公開するmongodbコレクション名
    'item_title': 'prop',  # 返されるjsonファイルにおけるkey
    'url':'prop',          # 公開用のURL http://localhost:50503/api/fixdevide
    'schema':{"join":[]
            }
        }
    }
