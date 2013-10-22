# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 15:36:36 2013

@author: daniel.vianna
"""

import xlwt as xlwt
import pandas as pd
conv = pd.io.parsers.excel.CellStyleConverter()

wb = xlwt.Workbook()
ws = wb.add_sheet('sheet')


def stylefunc(i):
    styledict = {"pattern": {"pattern": "solid", "fore_colour": i}}
    return conv.to_xls(styledict)

[ws.row(i).write(0, i, stylefunc(i)) for i in range(100)]
wb.save('colours.xls')
