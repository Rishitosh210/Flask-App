import pandas as pd
from customers.models import Mapping
def add_data():
    df=pd.read_excel('/opt/bench/mapdata.xls')
    for x in range(0,20):
        Mapping.objects.create(erp=df['one'][x],transaction_type=df['two'][x],final_field=df['three'][x],source_filed=df['four'][x])
    print(Mapping.objects.all().count())


def getSchemaName(request):
    return "hi"