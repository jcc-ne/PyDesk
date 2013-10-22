#! /usr/bin/env python
import os
import glob
from string import lowercase
from parseJpg import searchAllPsJpgs, sortGrpPsJpgs
import re

numFig = 0
numTable = 0
numClear = 0
figList = {}


def main():
    global numFig, numTable, numClear, figList

    openDir()
    #--------write appendix figures-----
    makeAppendix()

    #--------read list to move some figures from appendix----
    # list = ['appendix1', 'appendix6']
    list = []

    #--------sections-----------------
    makeSections()

    #-------open main.tex to write----
    f = open('main.tex', 'w')
    print >> f, texStrings('headings')
    print >> f, texStrings('toc')
    for i in range(3):
        print >> f, r"\input{section%s}" % i

    #--------make tables-----
    tables = glob.glob("table/*.csv")
    for table in tables:
        makeTable(table)
        print >> f, r"\include{%s}" % table.replace(".csv", "")

    #-------glob current fig folder
    Dirs = ['../fig/']
    psJpgs = searchAllPsJpgs(Dirs)
    for psJpg in psJpgs:
        psJpg.printAll()

    allSlides = sortGrpPsJpgs(psJpgs)

    slides = slidesAllSeperatePlots(allSlides)
    countFigsNmakeFigs(f, slides)
    appendixToMain(f, list)
    print >> f, texStrings('ending')
    f.close()

    endMain()


def openDir():
    os.system("modifyJpg.py")
    if not glob.glob("texFolder"):
        os.system("mkdir texFolder")
        path = os.environ['TEMPLATES'] + \
            "/ProjectStructure/2_Documentation/1_Reports/Report_latex_template"
        os.system("cp -r %s/* texFolder" % path)
    os.system("cp -r table texFolder")
    os.chdir("texFolder")


def endMain():
    fmake = open("makeTexReport.sh", "w")
    for i in range(4):
        fmake.write("pdflatex main.tex\n")
    fmake.write("cp main.pdf report.pdf\n")
    fmake.write("mv report.pdf ../\n")
    fmake.close()
    os.chdir("../")
    # os.system("modifyJpg.py") # move to the beginning of file
    os.chdir("texFolder")
    os.system("sh makeTexReport.sh")
    os.chdir("../")

def makeTable(tableFile):
    inputTable = open(tableFile, 'r')
    tableName = tableFile.replace('.csv', '')
    nrow = 0
    rows = []
    tableDic = {}
    for line in inputTable:
        line = line.strip()
        if re.match("^#", line):
            line = line.replace("#", "")
            terms = line.split(':')
            tableDic[terms[0]] = terms[1]

        else:
            nrow += 1
            rows.append(line)

    ftable = open('%s.tex' % tableName, 'w')
    print >> ftable, \
        r"""
\begin{table}[h]
    \addtolength{\tabcolsep}{3pt}
    \caption{%s}
    \label{tb:%s}
    \centering
    \renewcommand{\arraystretch}{1.5}
    \begin{tabular}{%s}
    \hline""" % (tableDic['caption'], tableName, tableDic['tableFormat'])

    for i in range(nrow):
        print >> ftable, rows[i],
        if i != nrow - 1 and not re.search("hline", rows[i]):
            print >> ftable, r"\\"
    print >> ftable, \
        r"""
    \end{tabular}"""
    print >> ftable, r"\end{table}"
    inputTable.close()
    ftable.close()


def makeSections():
    if not glob.glob("abstract.tex"):
        fabstract = open("abstract.tex", "w")
        print >> fabstract, r"\begin{abstract}"
        print >> fabstract, r"\end{abstract}"
        fabstract.close()

    if not glob.glob("title.tex"):
        ftit= open("title.tex", "w")
        print >> ftit, r"\title{%s}" % raw_input("please input title:")
        ftit.close()

    sectionText = ['Introduction', 'Method', 'Results and Discussion']
    for i in range(3):
        if not glob.glob("section%s.tex" % i):
            fsec = open("section%s.tex" % i, "w")
            print >> fsec, r"\section{%s}" % sectionText[i]
            fsec.close()


def makeAppendix():
    global numFig, numClear, figList
    fappendix = open('appendix.tex', 'w')

    numFig = 0
    numClear = 0
    #----------all contours in appendix------------------
    print >> fappendix, texStrings('appendix')

    Dirs = [o for o in glob.glob('../../../Run/*') if os.path.isdir(o)]
    for Dir in Dirs:
        Dir = Dir.replace("\\", "/")
    print "Dirs=", Dirs
    psJpgs = searchAllPsJpgs(Dirs)
    allSlides = sortGrpPsJpgs(psJpgs)

    slides = []
    allSlides.filterSlides()  # recover original sets
    allSlides.filterSlides('time', '')
    slides = slidesEachNumTimeField(allSlides)
    print >> fappendix, \
        r"""
\setcounter{figure}{0}
\subsection{Contours of each case and operating point}"""

    countFigsNmakeFigs(fappendix, slides, flagAppendix=True)

    #slides = slidesCompareFields(allSlides)
    #countFigsNmakeFigs(f, slides)

    allSlides.filterSlides()  # recover original sets
    allSlides.filterSlides('time', '')
    slides = slidesCompareNum(allSlides)

    numClear = 0
    print >> fappendix, r"\clearpage"
    print >> fappendix, \
        r"""
\setcounter{figure}{0}
\subsection{Contours of each case with different operating points}"""
    countFigsNmakeFigs(fappendix, slides)

    allSlides.filterSlides()  # recover original sets
    allSlides.filterSlides('case', ['Case01', 'Case05', 'Case06'])
    allSlides.filterSlides('field', 'iso')
    allSlides.filterOutSlides('time', '')
    slides = slidesCompareTime(allSlides)
    numClear = 0
    print >> fappendix, r"\clearpage"
    print >> fappendix, \
        r"""
\setcounter{figure}{0}
\subsection{Iso-surface of gas/liquid interface at different times}"""
    countFigsNmakeFigs(fappendix, slides)

    fappendix.close()


def slidesAllSeperatePlots(allSlides):
    priors = []
    groupKeys = []
    priors.append('case')
    priors.append('num')
    groupKeys.append('case')    # things they have in common
    groupKeys.append('num')     # things they have in common
    groupKeys.append('loc')   # things they have in common
    titleKeys = ['case',
                 'numFull', 'locFull']     # keys to determine
    tabKeys = ['fieldFull', 'unit']  # will determine the text in the table
                                                     # the title of slide
    newTitle = "Plot of %s %s, %s"

    slides = allSlides.sortWithNewKeys(priors, groupKeys,
                                       titleKeys, tabKeys)

    for s in slides:
        s.updateUserText(newTitle, titleKeys)

    return slides


def slidesEachNumTimeField(allSlides):
    priors = []
    groupKeys = []
    priors.append('case')
    priors.append('num')
    priors.append('field')
    groupKeys.append('case')    # things they have in common
    groupKeys.append('num')     # things they have in common
    groupKeys.append('time')     # things they have in common
    groupKeys.append('field')   # things they have in common

    titleKeys = ['case', 'numFull', 'fieldFull', 'timeFull']     # keys to determine
                                                                # the title of slide
    titleKeys2 = ['fieldFull', 'case', 'numFull', 'timeFull']
    tabKeys = ['locFull']  # will determine the text in the table

    slides = allSlides.sortWithNewKeys(priors, groupKeys,
                                       titleKeys, tabKeys)

    newTitle = "%s for %s with %s, at %s"
    for s in slides:
        if not s.flagPlot:
            s.updateUserText(newTitle, titleKeys2)
    return slides


def slidesCompareFields(allSlides):
    priors = []
    groupKeys = []
    priors.append('case')
    priors.append('num')
    groupKeys.append('case')    # things they have in common
    groupKeys.append('num')     # things they have in common
    groupKeys.append('time')     # things they have in common
    titleKey = 'numFull'             # will determine the title of slide
    titleKeys = ['case', 'numFull']     # keys to determine the title of slide
    groupKeys.append(titleKey.replace('Full', ''))

    tabKeys = ['fieldFull', 'unit']  # will determine the text in the table

    slides = allSlides.sortWithNewKeys(priors, groupKeys, titleKeys, tabKeys)

    newTitle = "Plot of %s %s"
    for s in slides:
        if s.flagPlot:
            s.updateUserText(newTitle, titleKeys)

    return slides


def slidesCompareNum(allSlides):
    priors = []
    groupKeys = []
    priors.append('case')
    priors.append('field')
    priors.append('num')
    groupKeys.append('case')    # things they have in common
    groupKeys.append('field')     # things they have in common
    groupKeys.append('loc')     # things they have in common
    groupKeys.append('time')     # things they have in common
    titleKey = 'fieldFull'             # will determine the title of slide
    titleKeys = ['case', 'fieldFull']     # keys to determine
                                          # the title of slide
    groupKeys.append(titleKey.replace('Full', ''))
    tabKeys = ['numFull']  # will determine the text in the table

    slides = allSlides.sortWithNewKeys(priors, groupKeys, titleKeys, tabKeys, flagSS=True)
    # flagSS means only steady-state will be extracted

    titleKeys2 = ['fieldFull', 'case', 'locFull']     # keys to determine
    newTitle = "%s for %s at different operating points at steady state(%s)"
    for s in slides:
        if not s.flagPlot:
            s.updateUserText(newTitle, titleKeys2)
    return slides

def slidesCompareTime(allSlides):
    priors = []
    groupKeys = []
    priors.append('case')
    priors.append('field')
    priors.append('time')
    groupKeys.append('case')    # things they have in common
    groupKeys.append('field')     # things they have in common
    groupKeys.append('loc')     # things they have in common
    groupKeys.append('num')     # things they have in common
    titleKey = 'fieldFull'             # will determine the title of slide
    titleKeys = ['case', 'fieldFull']     # keys to determine
                                          # the title of slide
    tabKeys = ['timeFull']  # will determine the text in the table

    slides = allSlides.sortWithNewKeys(priors, groupKeys, titleKeys, tabKeys)

    if 'locFull'=='':
        titleKeys2 = ['fieldFull', 'case', 'numFull']     # keys to determine
        newTitle = "%s for %s with % at different times"
    else:
        titleKeys2 = ['fieldFull', 'case', 'numFull', 'locFull']     # keys to determine
        newTitle = "%s for %s with %s at different times (%s)"

    for s in slides:
        if not s.flagPlot:
            s.updateUserText(newTitle, titleKeys2)

    return slides

def countFigsNmakeFigs(f, slidepages, flagAppendix=False):
    global numFig, numClear, figList
    numFig = numFig
    for s in slidepages:
        numFig += 1
        numClear += 1
        strNumFig = numFig
        if numClear % 18 == 0:
            print >> f, r"\clearpage"
        if flagAppendix:
            strNumFig = "appendix%s" % numFig
        print "\n +++ slidepage %s: " % strNumFig,
        print [s.frames[j].code for j in range(s.nf)]
        print >> f, texFig(s, strNumFig)
        if flagAppendix:
            figList[strNumFig] = texFig(s, strNumFig)


def appendixToMain(f, list):
    global numFig, figList
    numFig += numFig
    for item in list:
        string = figList[item]
        print >> f, string.replace(item, "%s" % numFig)


def rgbColor(colorName):
    colorlist = {}
    colorlist["ORANGE"] = 'FF6600'
    colorlist["WHITE"] = 'FFFFFF'
    colorlist["BLACK"] = '000000'
    return colorlist[colorName]


def texStrings(searchString):
    string = {}
    string['headings'] = \
        r"""
\documentclass[10.5pt,a4paper]{article}
\usepackage[latin1]{inputenc}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\topmargin = 0.25in
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{multirow}
\usepackage{hyperref}
\usepackage[all]{hypcap}
\usepackage{subfigure}
\usepackage{xcolor}
\usepackage{footnote}
\usepackage[subfigure]{tocloft}
\setcounter{lofdepth}{2}

\hypersetup{pdfpagemode=FullScreen, colorlinks=true, linkcolor=blue}

\input{title}
\author{Janine Cheng (GME/M)}
\date{\today}
\renewcommand{\thetable}{\arabic{table}}
\renewcommand{\thefigure}{\arabic{figure}}
\usepackage{caption}
\usepackage{wallpaper}
\captionsetup[table]{belowskip=12pt,aboveskip=4pt}
\renewcommand{\abstractname}{Executive Summary}

\begin{document}
\setlength{\wpXoffset}{-0.5\paperwidth}
\URCornerWallPaper{0.3}{fig/basf_banner.pdf}
\maketitle
\input{abstract}
"""

    string['toc'] = \
        r"""
\setlength{\cftfignumwidth}{3.2em}
\cleardoublepage
\phantomsection
\addcontentsline{toc}{section}{Table of Contents}
\tableofcontents
\addcontentsline{toc}{section}{List of Figures}
\newpage
\listoffigures
\cleardoublepage
        """

    string['appendix'] = \
        r"""
\clearpage
\appendix
\renewcommand\thefigure{\thesubsection.\arabic{figure}}
\setcounter{figure}{0}
\section{All contour figures}
    """

    string['ending'] = \
        r"""
\include{appendix}
\end{document}
    """
    return string[searchString]


def texFig(slidepage, num):
    nf = slidepage.nf
    searchString = 'fig' + str(nf)
    caption = []
    figs = []
    caption.append(slidepage.titleText)
    for i in range(nf):
        figs.append(slidepage.frames[i].jpgfileFp)
        caption.append(slidepage.tabTextList[i])

    string = {}
    width = ['0holder']
    width.append(0.9)       # fig1width
    width.append(0.45)      # fig2width
    width.append(0.32)      # fig3width
    width.append(0.45)      # fig4width
    width.append(0.45)      # fig5width
    width.append(0.45)      # fig5width

    if slidepage.flagPlot:
        width = 0.9
    else:
        width = width[nf]

    string['figureHeading'] = \
        r"""
%%-----------------------------------------------------------------------------
\begin{figure}[htb]
   \centering
    """

    string['subfigure'] = \
        r"""
   \subfigure[{%s}]{
      \includegraphics[width=%.2f\textwidth]{%s}
      \label{fig:%s%s}
   }"""

    string['figureEnding'] = \
        r"""
   \caption{%s}
   \label{fig:%s}
\end{figure}
    """ % (caption[0], num)

    try:
        string['fig1'] = \
            r"""
%%-----------------------------------------------------------------------------
\begin{figure}[htb]
   \centering
   \includegraphics[width=%.2f\textwidth]{%s}
   \caption{%s}
   \label{fig:%s}
\end{figure}
""" % (width, figs[0], caption[0], num)

        string['fig2'] = \
            string['figureHeading'] + \
            string['subfigure'] % (caption[1], width,
                                   figs[0], num, lowercase[0]) + \
            string['subfigure'] % (caption[2], width,
                                   figs[1], num, lowercase[1]) + \
            string['figureEnding']

        string['fig3'] = \
            string['figureHeading'] + \
            r"  \mbox{" + \
            string['subfigure'] % (caption[1], width,
                                   figs[0], num, lowercase[0]) + \
            string['subfigure'] % (caption[2], width,
                                   figs[1], num, lowercase[1]) + \
            string['subfigure'] % (caption[3], width,
                                   figs[2], num, lowercase[2]) + \
            r"}" + \
            string['figureEnding']

        string['fig4'] = \
            string['figureHeading'] + \
            r"  \mbox{" + \
            string['subfigure'] % (caption[1], width,
                                   figs[0], num, lowercase[0]) + \
            string['subfigure'] % (caption[2], width,
                                   figs[1], num, lowercase[1]) + \
            "}\n    \mbox{" + \
            string['subfigure'] % (caption[3], width,
                                   figs[2], num, lowercase[2]) + \
            string['subfigure'] % (caption[4], width,
                                   figs[3], num, lowercase[3]) + \
            "\n}" + \
            string['figureEnding']

        string['fig5'] = \
            string['figureHeading'] + \
            r"  \mbox{" + \
            string['subfigure'] % (caption[1], width,
                                   figs[0], num, lowercase[0]) + \
            string['subfigure'] % (caption[2], width,
                                   figs[1], num, lowercase[1]) + \
            "}\n    \mbox{" + \
            string['subfigure'] % (caption[3], width,
                                   figs[2], num, lowercase[2]) + \
            string['subfigure'] % (caption[4], width,
                                   figs[3], num, lowercase[3]) + \
            "\n}" + \
            string['subfigure'] % (caption[5], width,
                                   figs[4], num, lowercase[4]) + \
            string['figureEnding']

        string['fig6'] = \
            r"\clearpage" + \
            string['figureHeading'] + \
            r"  \mbox{" + \
            string['subfigure'] % (caption[1], width,
                                   figs[0], num, lowercase[0]) + \
            string['subfigure'] % (caption[2], width,
                                   figs[1], num, lowercase[1]) + \
            "}\n    \mbox{" + \
            string['subfigure'] % (caption[3], width,
                                   figs[2], num, lowercase[2]) + \
            string['subfigure'] % (caption[4], width,
                                   figs[3], num, lowercase[3]) + \
            "}\n    \mbox{" + \
            string['subfigure'] % (caption[5], width,
                                   figs[4], num, lowercase[4]) + \
            string['subfigure'] % (caption[6], width,
                                   figs[5], num, lowercase[5]) + \
            "\n}" + \
            string['figureEnding']

    except IndexError:
        pass

    return string[searchString]


if __name__ == "__main__":
    main()
