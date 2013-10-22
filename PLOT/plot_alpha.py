#! /usr/bin/env python
import sys
from optparse import OptionParser
import re

import pandas
from pandas import pivot_table
import matplotlib.pyplot as plt
import XLpandas2
from xlwt import Workbook  # , Worksheet, Style, easyxf
from pandas.io.excel import CellStyleConverter


def main():
    df = getDf()
    df1 = df.copy()
    al = alphaStir(df1)

    # case01-case03, courer vs. clockwise
    al.sliceCases(['Case%02d' % i for i in range(1, 4)])
    df1 = al.df_pivot
    df1.index = abs(df1.index)
    plotlist = [0, 2, 4, 1, 3, 5]
    plot(df1,
         'plot_alpha-vsRPM-cond_before-comp_clockwise_counter',
         ).plot3vs3(plotlist)

    # P/V as index
    al.update(al.df, row='P/V')
    df1 = al.df_pivot
    plot(df1, 'plot_alpha-vsPV-cond_before-comp_clockwise_counter',
         xlabel=r'P/V [W/m$^3$]').plot3vs3(plotlist)

    # acronal290d vs. acronal s 400
    caselist = ['Case%02d' % i for i in range(1, 7)]
    al.sliceCases(caselist)
    al.update(al.df, row='RPM', cols=['Cases', 'Reactor', 'Material'])
    df2 = al.df_clockwise  # clockwise only
    df2.index = abs(df2.index)  # correct RPM to absolute values
    plot(df2,
         'plot_alpha-vsRPM-cond_before-comp_Acronal290D_S400'
         ).plot3vs3()
    # P/V as index
    al.update(al.df, row='P/V', cols=['Cases', 'Reactor', 'Material'])
    df2 = al.df_clockwise
    plot(df2,
         'plot_alpha-vsPV-cond_before-comp_Acronal290D_S400',
         xlabel=r'P/V [W/m$^3$]'
         ).plot3vs3()

    # before vs. after
    caselist = ['Case01', 'Case02', 'Case03',
                'Case08', 'Case11', 'Case13']
    al.sliceCases(caselist)
    al.update(al.df, row='RPM', cols=['Cases', 'Reactor'])
    df1 = al.df_clockwise
    df1.index = abs(df1.index)
    plot(df1,
         'plot_alpha-vsRPM-cond_clock-comp_before_after',
         ).plot3vs3()

    # after
    caselist = ['Case07', 'Case08', 'Case11', 'Case13']
    al.sliceCases(caselist)
    al.update(al.df, row='RPM', cols=['Cases', 'Reactor', 'Comment'])
    df1 = al.df_pivot
    df1.index = abs(df1.index)
    plotlist = [0, 2, 4, 6, 1, 3, 5, 7]
    plot(df1,
         'plot_alpha-vsRPM-cond_after-comp_clockwise_counter'
         ).plot4vs4(plotlist)

    # P/V as index
    al.update(al.df, row='P/V', cols=['Cases', 'Reactor', 'Comment'])
    df2 = al.df_pivot
    plotlist = [0, 2, 4, 6, 1, 3, 5, 7]
    plot(df2,
         'plot_alpha-vsPV-cond_after-comp_clockwise_counter',
         xlabel=r'P/V [W/m$^3$]'
         ).plot4vs4(plotlist)

    # isothermal vs. adiabatic vs. airconv
    caselist = ['Case08', 'Case09', 'Case10']
    al.sliceCases(caselist)
    df1 = al.df_clockwise
    al.update(al.df, row='RPM', cols=['Cases', 'Reactor', 'Comment'])
    df1.index = abs(df1.index)
    plot(df1, 'plot_Alpha-vsRPM-cond_after-comp_thermalCondi').plot()


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

#    plt.savefig('%s.pdf' % ('-'.join([arg.split('.')[0] for arg in args])))
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
    ws = wb.add_sheet('test', cell_overwrite_ok=True)
    df = XLpandas2.XLtable(pd_conc)
    df.place_table(ws, rstyle=hstyle)

    [ws.row(i).write(0, i, stylefunc(i)) for i in range(100)]
    df.change_colStyle(ws, 5, hstyle)
    wb.save('test.xls')

    return pd_conc


class alphaStir:
    def __init__(self, df, values='alpha_fromInput', row='RPM',
                 cols=['Cases', 'Reactor', 'Comment']):
        self.df0 = df.copy()
        self.df = df
        self.values = values
        self.row = row
        self.cols = cols
        self.update(df, values, row, cols)

    def update(self, df, values=None,
               row=None, cols=None):
        if values is not None:
            self.values = values
        if row is not None:
            self.row = row
        if cols is not None:
            self.cols = cols
        self.df_pivot = self.pivot(df)
        self.df_counter = self.filter_counter()
        self.df_clockwise = self.filter_clockwise()

    def sliceCases(self, caselist=[]):
        df = self.df0.copy()
        if caselist == []:
            start = int(
                raw_input('please enter start location (Case__) integer:'))
            end = int(
                raw_input('please enter end location (Case__) integer:')) + 1
            caselist = ['Case%02d' % i for i in range(start, end)]
        df = df[df['Cases'].isin(caselist)]
        self.df = df
        self.update(df, self.values, self.row, self.cols)
        return self.df_pivot

    def pivot(self, df):
        df = pivot_table(df, values=self.values,
                         rows=[self.row], cols=self.cols)
        return df

    def filter_counter(self):
        # df = self.df_pivot[self.df_pivot.index > 0]
        df = self.df[self.df.RPM > 0]
        return self.pivot(df)

    def filter_clockwise(self):
        # df = self.df_pivot[self.df_pivot.index < 0]
        df = self.df[self.df.RPM < 0]
        return self.pivot(df)

    def plot(self, df, plotName):
        ax = plt.subplot(111)
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width, box.height])
        ax = df.plot(marker='o')
        xmin = min(abs(df.index))
        xmax = max(abs(df.index))
        ymin = df.min()
        ymin = min(ymin)
        ymax = df.max()
        ymax = max(ymax)
        plt.axis((xmin - 0.1 * xmin, xmax + 0.1 * xmax,
                  ymin - 0.3 * ymin, ymax + 0.1 * ymax))

        plt.legend(loc=4, ncol=1, prop={'size': 10})
        plt.xlabel('RPM')
        plt.ylabel(r'$\alpha$ [W/m$^2\cdot$K]')
        plt.rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
        plt.rc('text', usetex=True)

        plt.title(r"%s" % plotName,
                  fontsize=16, color='gray')
        # Make room for the ridiculously large title.
        plt.subplots_adjust(top=0.8)
        plt.show()
        # plt.savefig('%s.pdf' % plotName)


class plot:
    def __init__(self, df, plotName, xlabel=None,
                 ylabel=r'$\alpha$ [W/m$^2\cdot$K]'):
        self.df = df
        self.plotName = plotName
        self.xlabel = xlabel
        self.ylabel = ylabel

    def setplot(self):
        print "\n----%s----\n" % self.plotName
        print self.df, '\n'
        plt.figure()
        ax = plt.subplot(111)
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width, box.height])

    def adjust(self):
        xmin = min(abs(self.df.index))
        xmax = max(abs(self.df.index))
        ymin = self.df.min()
        ymin = min(ymin)
        ymax = self.df.max()
        ymax = max(ymax)
        plt.axis((xmin - 0.1 * xmin, xmax + 0.1 * xmax,
                  ymin - 0.3 * ymin, ymax + 0.1 * ymax))

        plt.legend(loc=4, ncol=1, prop={'size': 10})
        if self.xlabel is not None:
            plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.rc('font', **{'family': 'sans-serif',
                          'sans-serif': ['Helvetica']})
        plt.rc('text', usetex=True)
        plt.savefig('%s.jpg' % self.plotName, dpi=600)
        plt.show()

    def plot3vs3(self,
                 plotlist=[0, 1, 2, 3, 4, 5]):
        #plot 3 vs. 3
        self.setplot()
        colorlist = ['r', 'b', 'g', 'r', 'b', 'g']
        for i in range(0, 3):
            ax = self.df.iloc[:, plotlist[i]].dropna().\
                plot(marker='o',
                     color='%s' % colorlist[i])
        for i in range(3, 6):
            ax = self.df.iloc[:, plotlist[i]].dropna().\
                plot(marker='s',
                     ls='--',
                     color='%s' % colorlist[i])
        self.adjust()

    def plot4vs4(self,
                 plotlist=[0, 1, 2, 3, 4, 5, 6, 7]):
        #plot 4 vs. 4
        self.setplot()
        colorlist = ['r', 'b', 'g', 'Turquoise', 'r', 'b', 'g', 'Turquoise']
        # Orange: #FF6600
        for i in range(0, 4):
            ax = self.df.iloc[:, plotlist[i]].dropna().\
                plot(marker='o',
                     color='%s' % colorlist[i])
        for i in range(4, 8):
            ax = self.df.iloc[:, plotlist[i]].dropna().\
                plot(marker='s',
                     ls='--',
                     color='%s' % colorlist[i])
        self.adjust()

    def plot(self):
        self.setplot()
        ax = self.df.dropna().plot(marker='o')
        self.adjust()


def plot3vs3(df, plotName, plotlist=[0, 1, 2, 3, 4, 5]):
    plt.figure()
    ax = plt.subplot(111)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height])
    #plot 3 vs. 3
    colorlist = ['r', 'b', 'g', 'r', 'b', 'g']
    for i in range(0, 3):
        ax = df.iloc[:, plotlist[i]].dropna().plot(marker='o',
                                                   color='%s' % colorlist[i])
    for i in range(3, 6):
        ax = df.iloc[:, plotlist[i]].dropna().plot(marker='s',
                                                   color='%s' % colorlist[i])
    xmin = min(abs(df.index))
    xmax = max(abs(df.index))
    ymin = df.min()
    ymin = min(ymin)
    ymax = df.max()
    ymax = max(ymax)
    plt.axis((xmin - 0.1 * xmin, xmax + 0.1 * xmax,
              ymin - 0.3 * ymin, ymax + 0.1 * ymax))

    plt.legend(loc=4, ncol=1, prop={'size': 10})
    # plt.xlabel('RPM')
    plt.ylabel(r'$\alpha$ [W/m$^2\cdot$K]')
    plt.rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
    plt.rc('text', usetex=True)

    # plt.title(r"\TeX\ is Number "
    #         r"$\displaystyle\sum_{n=1}^\infty\frac{-e^{i\pi}}{2^n}$!",
    #         fontsize=16, color='gray')
    # Make room for the ridiculously large title.
    # plt.subplots_adjust(top=0.8)
    plt.show()
    # plt.savefig('%s' % plotName)


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
