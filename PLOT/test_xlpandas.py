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
dstyle_dict = {"border":{"top": "hair",
                        "right": "hair",
                        "bottom": "hair",
                        "left": "hair"}}
dstyle = conv.to_xls(dstyle_dict)
dstyle.num_format_str = '$#,##0.00'

df = pd.read_excel('excel.xlsx', 'cases (2)', index_col=None, na_values=['NA'])


df1 = XLtable(df)


wb = Workbook()
ws_1 = wb.add_sheet('cases', cell_overwrite_ok=False)
ws_2 = wb.add_sheet('XLtable', cell_overwrite_ok=False)

df1.place_table(ws_2)
df1.place_table(ws_1, row = 20, col = 7, rstyle = hstyle, cstyle = dstyle)

wb.save('test.xls')
