#!/usr/bin/env python
# coding: utf-8
import warnings
from tables import NaturalNameWarning
warnings.filterwarnings('ignore', category=NaturalNameWarning)
import asyncio
import pandas as pd
import numpy as np
import datetime

from concurrent import futures

import sys
sys.path.append("..")
from lib.ddeclient import DDEClient

import time


class LastNPerfTime:
    def __init__(self, n):
        """
        過去n回の実行時間の合計を尺取り法で記録する
        """
        self.n = n
        self.count = 0
        self.sum_time = 0
        self.times = np.zeros(n)
        
        
    def start(self):
        """
        実行時間の計測を開始する
        """
        self.start_time = time.perf_counter() # timeより正確
        
    def end(self):
        """
        実行時間の計測を終了する
        """
        dtime = time.perf_counter() - self.start_time
        idx = self.count % self.n # self.nが2^xならここをビット論理積にできる
        time_n_before = self.times[idx]
        self.times[idx] = dtime
        #self.count += 1
        self.sum_time += (dtime - time_n_before)
        
    def get_sum_time(self):
        """
        過去n回の実行時間を合計した値を返す
        """
        return self.sum_time
    
    def count_one(self):
        self.count += 1

class ClientHolder():
    def __init__(self, idx, codes, weights,hdffoldername = "./data/"):
        """
        RSSサーバーに接続し、継続的に複数の銘柄の株価を取得する
        
        Parameters
        ----------
        idx: int
        ClientHolderにつける番号
        番号がかぶると同じファイルに書き込むことになる
        
        codes: array_like
        RSSサーバーにリクエストを送る銘柄のコード番号を格納したリスト
        
        """
        hdffilename = hdffoldername + str(idx).zfill(3) + ".hdf5" # 文字列・数値をゼロパディング（ゼロ埋め）するzfill()
        
        self.idx = idx
        self.clients = {}
        self.activate = {}
        self.array=[]
        self.close_value = "現在値" #price_request_str
        self.codes = codes
        self.weights = weights
        self.Boolean = True
        self.codes_attrsafe = 'code_' + np.array(codes).astype('object') # pandasを使ってhdfを作るとき、数字から始まる列名にできない
        
        # RSSサーバーに接続し、127個のDDEClientを作る
        self.connect_all()
        
        # データ保存用のファイルを開く
        self.hdffilename = hdffilename
        self.store = pd.HDFStore(hdffilename)
        self.key_name = "classidx_" + str(self.idx) 
        
        self.firststep = True
        self.checkbox = {}
        
        
        
        
    def connect_all(self):
        """
        RSSサーバーに接続する
        """
        for code in self.codes:
            try:
                self.clients[code] = DDEClient("rss", code)
            except Exception as e:
                print(f"an error occurred at code: {code} while connecting server.")
                pass
            
        return
    
    

    
    
    def get_price(self, code):
        """
        1つの銘柄の株価を取得する
        """ 
        
           
        client = self.clients[code]
        t1 = time.time()
          
        if True:
            val =0
            try:
                val = client.request("現在値").decode("sjis")         
            except Exception :
                with open("shares.txt", "a",encoding="utf-8") as f:
                    f.write(str(code)+ "\n")
                    #f.write(client.request("銘柄名称").decode("sjis")+ "\n")
                pass
            else:
                try:
                    float(val)
                except Exception as e:
                    val = 0
                    with open("shares2.txt", "a",encoding="utf-8") as f:
                        f.write("error"+ "\n")
                

        return val 
        

    
        
       
    
    
    def get_prices(self):
        """
        複数の銘柄の株価を取得し、保存する
        """
        

        temps =[]
        prices = {}
        times = {}
        #times['time_start'] = np.datetime64(datetime.datetime.now())
            

        for i, code in enumerate(self.codes):     
            prices[self.codes_attrsafe[i]] = self.get_price(code)
            
            try:
                pre_code= temps[-1]
            except Exception:
                pass
            else:
                pass
            temps.append(code)
            
        
        #times['time_end'] = np.datetime64(datetime.datetime.now())
        #self.save(prices)
        self.firststep = False
        return prices


    def save(self, data_dict):
        """
        取得した株価を保存する
        """
        self.store.put(self.key_name, pd.DataFrame(data_dict)) #O.K. block0 values
        return

    def time_save(self, data_dict):
        self.store.append("time", pd.DataFrame())
        return    
    
    def get_prices_forever(self):
        """
        継続的に株価を取得して保存し続ける
        """
        
        
        
        while True:
            t1 = time.time()
            try:
                prices= self.get_prices()
            except KeyboardInterrupt:
                break
            except Exception as e:
                raise Exception(e)
            else:
                t2 = time.time()
                v = self.calc(prices)
                
                
                #s2 = s2
                
                dict = {str(int(int(self.idx)/126)): v}
                series = pd.Series(dict)
                """
                time_start, time_end = prices["time_start"], prices["time_end"]
                self.store.append("time",pd.DataFrame({"time_start":time_start, "time_end": time_end},index = [0]))
                """
                #辞書形式でhdf5ファイルに保存
                """
                with pd.HDFStore("./data/504.hdf5") as store:
                    temp =store.get("classidx_504")
                    temp =store.select("classidx_504")
                    print(temp[0]["504~630"])
                    293.65325399999983
                """
                self.save(series)
                
                #index=False
                """
                with pd.HDFStore(self.hdffilename) as store:
                    store.put("restore/"+str(self.idx), series)
                """
                
                break

    def calc(self,prices):
        checkbox = self.checkbox
        num = 0
        
        #prices=itertools.chain.from_iterable(prices)
        for i, code in enumerate(self.codes):
            #num += float(prices[i])* float(weights[i]) 
            val = prices[self.codes_attrsafe[i]]
            try:
                float(val)
            except Exception as e:
                checkbox[self.codes_attrsafe[i]] = self.codes_attrsafe[i]
                self.checkbox = checkbox
                continue
            num += float(val)* float(self.weights[i]) 
        return num
    


if __name__ == '__main__':
    idx = int(sys.argv[1])
    foldername = sys.argv[2]
    codes = sys.argv[3:]
    holder = ClientHolder(idx, codes, foldername)
    
    holder.get_prices_forever()