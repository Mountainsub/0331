
import pandas as pd
import numpy as np
import time 
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))




if __name__ == "__main__":
    t1 = time.time()
    calc = 0
    for i in range(17):
        idx = i *126
        filename = "./data/" + str(idx).zfill(3)+ ".hdf5"
        object_pass = "classidx_" + str(idx).zfill(3) 
        try:
            with pd.HDFStore(filename) as store:
                temp =store.get(object_pass)
        except:
            print("dame")
        else:
            print(idx, temp)
            print(idx, temp)
            calc += float(temp[0][str(int(int(idx)/126))])

    print(calc)
    """
                with pd.HDFStore("./data/504.hdf5") as store:
                    temp =store.get("classidx_504")
                    temp =store.select("classidx_504")
                    print(temp[0]["504~630"])
                    293.65325399999983
            

    while count < 17: 
        count += 1
        if True:
            with open('file_'+ str(count) + '.txt', 'r') as f:                           
                try: # 正常に取得するまでループするようになっている
                    a = f.readline()
                    a.rstrip("\n")
                except:
                    with open('f.txt', 'w') as f:
                        f.write("file_"+ str(count)+ ".txt\n")
                    continue
                else:
                    try:
                        float(a)
                    except:
                        pass
                    else:
                        s += float(a)
    print(s)
    """