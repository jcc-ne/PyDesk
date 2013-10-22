#! /usr/bin/python
import sys
import os
from optparse import OptionParser
import re

import pandas
import matplotlib.pyplot as plt


def main():
# ----------- help--------------------------------------------------
    parser = OptionParser(usage="%prog [options] [datafile_1] [datafile_22]")
    (options, args) = parser.parse_args()
    if len(args) == 0:
        print "=============================================================="
        print "no datafiles are given, plot default sets"
        defaultValue = yesOrNo("?")
        if defaultValue == 'y':
            args.append('LineX1_U.xy')
            args.append('LineX1_nu_p.xy')
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
        loc = key.split('_')[0]
        names = key.split('_')[1:]
        if re.match(names[0], 'U'):
            names = ['Ux', 'Uy', 'Uz']
        #names = [name + '_' + loc for name in names]
        print names
        pd = pandas.read_csv(datafiles[key],
                             delimiter=" ",
                             index_col=0,
                             names=names)
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
    plt.show()


def yesOrNo(question):
    answer = ''
    while answer != 'y' and answer != 'n':
        answer = raw_input("%s (y/n)" % question)
    return answer


if __name__ == "__main__":
    main()
