import os 
import glob 
import re 
from operator import attrgetter 
from itertools import groupby 
  
  
def main(): 
    Dirs = [o for o in glob.glob('../../Run/*') if os.path.isdir(o)] 
    Dirs.append('./') 
    print "Dirs=", Dirs 
  
    psJpgs = [] 
    for Dir in Dirs: 
        print "\n#------ in Dir ", Dir, "------#"
        psJpgs += searchPsJpgs(Dir) 
        for psJpg in psJpgs: 
            psJpg.printAll() 
  
    priors = [] 
    groupKeys = [] 
    priors.append('case') 
    priors.append('num') 
    groupKeys.append('case')    # things they have in common 
    groupKeys.append('num')     # things they have in common 
    titleKeys = ['case', 'numFull']     # keys to determine the title of slide 
  
    tabKeys = ['fieldFull', 'unit']  # will determine the text in the table 
  
    allSlides = sortGrpPsJpgs(psJpgs) 
    slides = allSlides.sortWithNewKeys(priors, groupKeys, titleKeys, tabKeys) 
  
    i = 0
    for s in slides: 
        i += 1
        print "\n +++ slidepage %d: " % i, 
        print [s.frames[j].code for j in range(s.nf)] 
  
  
def sortAllSlides(psJpgs, 
                  priors=['case', 'num'], 
                  groupKeys=['case', 'num', 'field']): 
  
    slidepages = sortGrpPsJpgs(psJpgs, priors, 
                               groupKeys) 
  
    return slidepages 
  
  
def searchAllPsJpgs(Dirs): 
    psJpgs = [] 
    for Dir in Dirs: 
        print "\n#############################################################"
        print "------ in Dir ", Dir, "------"
        print "#############################################################\n"
        psJpgs += searchPsJpgs(Dir) 
  
    print "jpgfiles = ", 
    print [psJpgs[j].fileName for j in range(len(psJpgs))] 
    print "\n"
  
    return psJpgs 
  
  
def searchPsJpgs(Dir): 
    psJpgs = [] 
    jpgfiles = (glob.glob('%s/Pictures/*.jpg' % Dir)) 
    print jpgfiles 
    if jpgfiles != []: 
        psDict = parseDict('%s/Pictures/input.py' % Dir, Dir) 
    elif jpgfiles == []: 
        jpgfiles = (glob.glob('%s/*.jpg' % Dir)) 
        psDict = parseDict('%s/input.py' % Dir, Dir) 
  
    for jpgfile in jpgfiles: 
        psJpg = parseJpgFile(jpgfile, psDict) 
        psJpgs.append(psJpg) 
    return psJpgs 
  
  
class parseJpgFile: 
    def __init__(self, jpgfile, psDict): 
        "initialize attributes, 'Full' means exanded terms"
        self.time = "" 
        self.timeFull = "steady state" 
        self.case = "" 
        self.caseFull = "" 
        self.field = "" 
        self.fieldFull = "" 
        self.num = "" 
        self.numFull = "" 
        self.loc = "" 
        self.locFull = "" 
        self.code = "" 
        self.jpgfileFp = jpgfile.replace("\\", "/")  # prevent path messed 
        self.flagPlot = False
                                                     # up in Windows 
        self.parseDirTerms(self.jpgfileFp) 
        self.fileName = self.jpgfile.rsplit('.', 1)[0] 
        self.terms = self.fileName.split('-') 
        self.parseTerms(psDict) 
        self.parsePlotTerms(psDict) 
        self.unit = self.determineUnit(psDict) 
        self.code = self.case.replace('Case', 'c') + 'n' + \
            self.num + '_' + self.field + '_' + self.loc 
  
    def parseDirTerms(self, jpgfile): 
        terms = jpgfile.split('/') 
        for term in terms: 
            if re.match('.*\.jpg', term): 
                self.jpgfile = term 
            if re.match('.*\.pdf', term): 
                self.jpgfile = term 
            elif re.match('Case\d+', term): 
                self.case = term 
  
    def determineUnit(self, psDict): 
        return psDict.getString("%s-unit" % self.field.lower()) 
  
    def parseTerms(self, psDict): 
        self.num = self.terms.pop(0) 
        if re.match('plot_.*', self.num): 
            self.case = psDict.getString(self.num) 
            self.flagPlot = True
        try: 
            self.numFull = psDict.getString(self.num) 
        except NameError: 
            print 'no parseDict'
        for term in self.terms: 
            term.strip() 
            if re.match("t.*", term): 
                timeString = term.replace('t', '') 
                digits = len(list(timeString.split('_')[0]))
                self.time = (4 - digits) * '0' + timeString 
                if self.time != '':
                    self.timeFull = "%.1f [sec]" % float(self.time.replace('_', '.'))
            elif re.match("[xyz].*\=\d?", term): 
                self.locFull = "%s-plane Cut" % term.split('=')[0].\
                    replace('mult', '').capitalize() 
                self.loc = term 
            elif re.match("f_.*", term): 
                self.field = term 
                self.fieldFull = psDict.getString(term.lower()) 
            else: 
                self.field = term 
                self.fieldFull = psDict.getString(term.lower()) 

            if re.match('iso', self.field):
                self.locFull = "interface of liquid and gas"
  
    def parsePlotTerms(self, psDict): 
        # plot_AlphavsRPM-cond_before-comp_clockwise_counter 
        for term in self.terms: 
            if re.match('plot_.*', term): 
                self.case = psDict.getString(term) 
                self.flagPlot = True
  
            if re.match('cond_.*', term): 
                self.num = term 
                self.numFull = psDict.getString(term) 
  
            if re.match('vs.*', term): 
                self.field = term 
                self.fieldFull = psDict.getString(term) 
  
            if re.match('comp_.*', term): 
                self.loc = term 
                self.locFull = psDict.getString(term) 
  
    def printAll(self): 
        print '\t\t---------------------------'
        print '\t\tnum:                 ', self.num 
        print '\t\top                   ', self.numFull 
        print '\t\ttime:                 ', self.time
        print '\t\ttimeFull:            ', self.timeFull
        print '\t\tjpgfileFp            ', self.jpgfileFp 
        print "\t\tjpgfile:             ", self.jpgfile 
        print "\t\tcase                 ", self.case 
        print "\t\tflagPlot             ", self.flagPlot 
        print "\t\tfield:               ", self.field 
        print "\t\tfieldFull:          ", self.fieldFull 
        print "\t\tunit:                ", self.unit 
        print "\t\tloc:                 ", self.loc 
        print "\t\tlocFull:             ", self.locFull 
  
  
class slidepage: 
    def __init__(self, frames, titleKeys=[], tabKeys=[], boxKeys=[]): 
        self.frames = frames 
        self.flagPlot = False
        self.nf = nf = len(self.frames) 
  
        self.titleKeys = titleKeys 
        self.tabKeys = tabKeys 
        self.boxKeys = boxKeys 
        self.titleTexts = [] 
        self.titleText = self._updateText(frames[0], titleKeys, ': ') 
        self.tabTextList = \
            [self._updateText(frames[i], tabKeys) for i in range(nf)] 
        self.boxText = self._updateText(frames[0], boxKeys, ' ') 
        self._updateFlag() 
  
    def _updateFlag(self): 
        if self.frames[0].flagPlot: 
            self.flagPlot = True
  
    def _updateText(self, psJpg, keys, sep=' '): 
        self.titleTexts = [getattr(psJpg, key) for key in keys] 
        text = sep.join(self.titleTexts) 
        return text 
  
    def updateUserText(self, newText, titleKeys): 
        self.titleKeys = titleKeys 
        self.titleTexts = [getattr(self.frames[0], key) 
                           for key in self.titleKeys] 
        try:
            titleText = newText % tuple([t.lower() for t in self.titleTexts])
        except ValueError:
            print "ValueError: ", self.titleKeys, "text: ", newText
            print "titleTexts: ", self.titleTexts
        # print "titleKeys = ", titleKeys
        # print "titleTexts = ",  self.titleTexts
        # print "new titleText = ", titleText
        self.titleText = titleText.capitalize().replace("case", "Case")\
            .replace("acronal", "Acronal") 
  
  
class sortGrpPsJpgs: 
    def __init__(self, 
                 psJpgs, priors=[], 
                 groupKeys=[], 
                 titleKeys=[], tabKeys=[], boxKeys=[]): 
        self.psJpgs = psJpgs 
        self.psJpgs_0 = psJpgs 
        self.priors = priors 
        self.groupKeys = groupKeys 
        self.titleKeys = titleKeys 
        self.tabKeys = tabKeys 
  
        if priors != []: 
            self._sortPsJpgs() 
        if groupKeys != []: 
            self.slidepages = self._grpPsJpgs() 

    def filterSlides(self, attrkey='', filterKeys=[]):
        if attrkey=='':
            self.psJpgs = self.psJpgs_0
            return 

        newSet = []
        f = attrgetter(attrkey)
        for s in self.psJpgs:
            if f(s) in filterKeys:
                newSet.append(s)
        self.psJpgs = newSet 

    def filterOutSlides(self, attrkey='', filterKeys=[]):
        if attrkey=='':
            self.psJpgs = self.psJpgs_0
            return 

        newSet = []
        f = attrgetter(attrkey)
        for s in self.psJpgs:
            if f(s) not in filterKeys:
                newSet.append(s)
        self.psJpgs = newSet 

    def sortWithNewKeys(self, 
                        priors=[], 
                        groupKeys=[], 
                        titleKeys=[], tabKeys=[], 
                        boxKeys=[],
                        flagSS=False): 
        self.priors = priors 
        self.groupKeys = groupKeys 
        self.titleKeys = titleKeys 
        self.tabKeys = tabKeys 
        self.boxKeys = boxKeys 
        self._sortPsJpgs() 
        self.slidepages = self._grpPsJpgs() 
        newslidepages = []
        if flagSS:
            for s in self.slidepages:
                if s.frames[0].time == '':
                    newslidepages.append(s)
            self.slidepages = newslidepages
                
        return self.slidepages 
  
    def updateSlideTitles(self, newTitle): 
        for slidepage in self.slidepages: 
            slidepage.updateUserText(newTitle) 
        return self.slidepages 
  
    def makeNumSlide(self): 
        pass
  
    def _sortPsJpgs(self): 
        print "priors:", self.priors 
        for i in range(len(self.priors)): 
            self.psJpgs = sorted(self.psJpgs, 
                                 key=attrgetter(self.priors[i]), 
                                 reverse=False) 
  
        print "groupKeys:", self.groupKeys 
        for i in range(len(self.groupKeys)): 
            self.psJpgs = sorted(self.psJpgs, 
                                 key=attrgetter(self.groupKeys[i]), 
                                 reverse=False) 
  
    def _grpPsJpgs(self): 
        psJpgGrp = [self.psJpgs] 
  
        for gk in self.groupKeys: 
            print "gk=", gk 
            subgroups = [] 
            for psJpgs in psJpgGrp: 
                psJpgs = sorted(psJpgs, 
                                key=attrgetter(gk), 
                                reverse=False) 
                groups = groupby(psJpgs, attrgetter(gk)) 
                for (key, group) in groups: 
                    subgroups.append(list(group)) 
            psJpgGrp = subgroups 
  
        slidepages = [] 
        for subgroup in subgroups: 
            slidepages.append(slidepage(subgroup, 
                                        titleKeys=self.titleKeys, 
                                        tabKeys=self.tabKeys, 
                                        boxKeys=self.boxKeys)) 
  
        return slidepages 
  
  
def sortPsJpgs(psJpgs): 
    """sort parsed jpgfiles to decide if they belong to the same frame"""
    stacks = {} 
    frames = {} 
    for psJpg in psJpgs: 
        try: 
            stacks[psJpg.num].append(psJpg) 
        except KeyError: 
            stacks[psJpg.num] = [] 
            stacks[psJpg.num].append(psJpg) 
    i = 0
    frames = {} 
    for key in stacks: 
        i += 1
        print "processing stack ", i, "..."
        for each in stacks[key]: 
            try: 
                frames["%s_%s" % (key, each.field)].append(each) 
            except KeyError: 
                frames["%s_%s" % (key, each.field)] = [] 
                frames["%s_%s" % (key, each.field)].append(each) 
    return frames 
  
  
class parseDict: 
    def __init__(self, finName='input.py', Dir=os.getcwd()): 
        self.Dir = Dir
        self.finName = finName 
        self.dict = {} 
        self.setDefaultDict() 
        try: 
            fin = open(finName, 'r') 
        except IOError: 
            print '#--- Note: cannot find input file,' + \
                  'use default dict strings ---#'
            self.printAll() 
            return
  
        for line in fin: 
            if re.match('\s*#.*', line) or re.match('\s*\n', line): 
                continue
            terms = line.split(':') 
            self.dict[terms[0].strip()] = terms[1].strip() 
        fin.close() 
        self.printAll() 
        return
  
    def printAll(self): 
        print "\n#--- dict terms to expand keywords in jpg filenames ---#\n"
        for key in self.dict: 
            print key, ' : ', self.dict[key] 
        print "\n"
  
    def getString(self, searchString): 
        try: 
            return self.dict[searchString] 
        except KeyError: 
            print "searchString is ", searchString 
            print "Dir is ", self.Dir
            expandString = self.dict[searchString] = raw_input( 
                '\n please expand keyword "%s" in Dir %s '
                % (searchString, self.Dir) +
                '(ex. vel-->velocity): ') 
            fappend = open(self.finName, "a") 
            print >> fappend, "%s\t:\t%s" % (searchString, expandString) 
            fappend.close() 
            return expandString 
  
    def setDefaultDict(self): 
        self.dict['vel'] = "Velocity Field"
        self.dict['vel-unit'] = "[m/s]"
        self.dict['vis'] = "Viscosity Distribution"
        self.dict['vis-unit'] = "[Pa-s]"
        self.dict['shear'] = "Shear Rate Distribution"
        self.dict['shear-unit'] = "[1/s]"
  
if __name__ == "__main__": 
    main() 
