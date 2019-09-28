def missing_values(l):
    aa = list(x+1 for x,y in zip(l[:-1],l[1:]) if y-x > 1 )
    return aa
import re 
from datetime import timedelta,datetime,time
import string
import numpy as np
import pandas as pd
def removePunct(stri):
    punctuations = '''!()[]{};:'"\,<>.?@#$%^&*_~'''
    if type(stri) != str:
        print("================"+str(stri))
        return stri
    else:
        if re.match(r'[0-9]{2}[-|\/]{1}[0-9]{2}[-|\/]{1}[0-9]{4}',stri):
            stri=pd.to_datetime(stri)
            return stri
        if re.match((r'^[-+]?([1-9]\d*|0)$'),stri):
            print("integer"+stri)
            stri=float(stri)
            return stri
        # table = str.maketrans(dict.fromkeys("   "))
            # # stri=stri.translate()
            # stri=stri.translate(table)
        else:
                # table = str.maketrans(dict.fromkeys("   "))
            # # stri=stri.translate()
            # stri=stri.translate(table)
            stri=stri.replace(' -   ',"0")
            stri=stri.replace("  ","0")
            print("+++"+stri)
            stri= re.sub(r'[^\w\s]','',stri)
            return stri