import pandas as pd
import numpy as np
from XLpandas2 import XLtable, XLseries
from xlwt import Workbook, Worksheet, Style
from copy import deepcopy

from pandas.io.excel import CellStyleConverter

conv = CellStyleConverter()
hstyle_dict = {"font": {"bold": True},
              "border": {"top": "thin",
                        "right": "thin",
                        "bottom": "thin",
                        "left": "thin"},
              "pattern": {"pattern": "solid",
                            "fore_colour": 26},
              "align": {"horiz": "center"}}
hstyle = conv.to_xls(hstyle_dict)

ser = pd.Series([1,2,3,4])
ser1 = XLseries(ser)

df = pd.DataFrame(np.array(np.mat('0 1 0 1; 1 0 2 3; 1 1 2 4')))
arrays = [[1,2,3,4],[5,6,7,8]]
tuples = zip(*arrays)
index = pd.MultiIndex.from_tuples(tuples, names=['First','Second'])

ser2 = deepcopy(ser)
ser2.index = index
ser2 = XLseries(ser2)

df1 = XLtable(df)
df2 = deepcopy(df)
df2.columns = index
df2 = XLtable(df2)


wb = Workbook()
ws_1 = wb.add_sheet('XLseries', cell_overwrite_ok=False)
ws_2 = wb.add_sheet('XLtable', cell_overwrite_ok=False)

ser1.place_series(ws = ws_1)
ser2.place_index(ws = ws_1, row = 10)
ser2.place_data(ws = ws_1, row = 10, col = 3)
ser2.place_series(ws = ws_1, row = 10, col = 6)

ser1.place_series(ws = ws_1, axis = 1, col = 3, istyle = hstyle)

df1.place_table(ws_2)
df2.place_index(ws_2, row = 10)
df2.place_index(ws_2, row = 10, col = 1, axis=1)
df2.place_data(ws_2, row = 15, col = 2)
df2.place_table(ws_2, row = 10, col = 9)
df3 = XLtable(df2)
df3.place_table(ws_2, row = 20, col = 7, rstyle = hstyle, cstyle = hstyle)

wb.save('test.xls')
