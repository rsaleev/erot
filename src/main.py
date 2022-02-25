from src.tasks.etl import Application

import time


app = Application(filename='/home/rost/Development/GIS_OK/erot/tests/Реестр_обязательных_требований_21.xlsx')
t1 = time.time()
app.run()
t2 = time.time()
print(t2-t1)
