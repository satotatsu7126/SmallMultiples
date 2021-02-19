#!/home/tatsuyasato/anaconda3/bin/python
# -*- coding: utf-8 -*-
from eve import Eve
app = Eve()
if __name__=='__main__':
    app.run(host='127.0.0.1', port=50503, debug=True) #このAPIの起動IPとポート番号
