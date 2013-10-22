#! /usr/bin/env python
import sys
import os
from optparse import OptionParser
import re

import pandas
import matplotlib.pyplot as plt
import XLpandas2
from xlwt import Workbook, Worksheet, Style, easyxf
from pandas.io.excel import CellStyleConverter


def main():
    df = getDf()

def getDf():
# ----------- help--------------------------------------------------
    parser = OptionParser(usage="%prog [options] [datafile_1] [datafile_22]")
    (options, args) = parser.parse_args()
    if len(args) == 0:
        print "=============================================================="
        print "no datafiles are given, plot default sets"
        defaultValue = yesOrNo("?")
        if defaultValue == 'y':
            args.append('excel.xlsx')
        else:
            print 'No argument give, exiting...'
            sys.exit()

        parser.print_help()

    datafiles = {}
    for arg in args:
        figName = arg.split('.')[0]
        datafiles[figName] = arg

    pds = []
    for key in datafiles.keys():
        names = key.split('_')[1:]
        try:
            if re.match(names[0], 'U'):
                names = ['Ux', 'Uy', 'Uz']
        except IndexError:
            pass
        #names = [name + '_' + loc for name in names]
        print names
        pd = pandas.read_excel(datafiles[key],
                               sheetname="cases",
                               header=0,
                               skiprows=0)
        pds.append(pd)

    # plt.hold(True)
    # pd.plot(marker = 'o')
    # pd2.plot(marker = 's')

    pd_conc = pandas.concat(pds)

    #pd_conc['Ux'].plot(marker='s', legend=True)
    #pd_conc['Uy'].plot(marker='s', legend=True)
    #pd_conc['Uz'].plot(marker='s', legend=True)
    pd_conc.plot(marker='o')

    plt.xlabel("distance [m]", fontsize=16)
    plt.ylabel("velocity [m/s]", fontsize=16)
    plt.savefig('%s.pdf' % ('-'.join([arg.split('.')[0] for arg in args])))
#    plt.show()

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
    wb = Workbook()
    ws = wb.add_sheet('test',cell_overwrite_ok = True)
    df = XLpandas2.XLtable(pd_conc)
    df.place_table(ws, rstyle=hstyle)

    [ws.row(i).write(0, i, stylefunc(i)) for i in range(100)]
    df.change_colStyle(ws,5, hstyle)
    wb.save('test.xls')


    return pd_conc

def stylefunc(i):
    conv = CellStyleConverter()
    styledict = {"pattern": {"pattern": "solid", "fore_colour": i}}
    return conv.to_xls(styledict)


def yesOrNo(question):
    answer = ''
    while answer != 'y' and answer != 'n':
        answer = raw_input("%s (y/n)" % question)
    return answer


if __name__ == "__main__":
    main()
