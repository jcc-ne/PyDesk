import locale
locale.setlocale(locale.LC_ALL, "")
import sys
import urllib2
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from designUi import Ui_MainWindow

class Program(QMainWindow,QDialog,Ui_MainWindow):
    def __init__(self,parent=None):
        super(Program,self).__init__(parent)
        self.setupUi(self)

        self.lineEdit  = QLineEdit()



class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        date = self.getdata()
        rates = sorted(self.rates.keys(), key=unicode.lower)

        dateLabel = QLabel(date)
        self.fromComboBox = QComboBox()
        self.fromComboBox.addItems(rates)
        self.fromSpinBox = QDoubleSpinBox()
        self.fromSpinBox.setRange(0.01, 10000000.00)
        self.fromSpinBox.setValue(1.00)
        self.toComboBox = QComboBox()
        self.toComboBox.addItems(rates)
        self.toLabel = QLabel("1.00")
        grid = QGridLayout()
        grid.addWidget(dateLabel, 0, 0)
        grid.addWidget(self.fromComboBox, 1, 0)
        grid.addWidget(self.fromSpinBox, 1, 1)
        grid.addWidget(self.toComboBox, 2, 0)
        grid.addWidget(self.toLabel, 2, 1)
        self.setLayout(grid)
        self.connect(self.fromComboBox,
            SIGNAL("currentIndexChanged(int)"), self.updateUi)
        self.connect(self.toComboBox,
            SIGNAL("currentIndexChanged(int)"), self.updateUi)
        self.connect(self.fromSpinBox,
            SIGNAL("valueChanged(double)"), self.updateUi)
        self.setWindowTitle("Currency")

    def updateUi(self):
        to = unicode(self.toComboBox.currentText())
        from_ = unicode(self.fromComboBox.currentText())
        amount = (self.rates[from_] / self.rates[to]) * \
                 self.fromSpinBox.value()
        #self.toLabel.setText(locale.format("%0.2f", amount, True))
        self.toLabel.setText("%0.4f" %amount)

    def getdata(self): # Idea taken from the Python Cookbook
        self.rates = {}
        try:
            date = "Unknown"
            fh = urllib2.urlopen(
                 "http://www.bankofcanada.ca"
                 "/en/markets/csv/exchange_eng.csv")
            for line in fh:
                line = line.rstrip()
                if not line or line.startswith(("#",
                    "Closing ")):
                    continue
                fields = line.split(",")
                if line.startswith("Date "):
                    date = fields[-1]
                else:
                    try:
                        value = float(fields[-1])
                        self.rates[unicode(fields[0])] = value
                    except ValueError:
                        pass
            self.rates[u"Canadian Dollar"] = 1.00
            return "Exchange Rates Date: " + date
        except Exception, e:
            return "Failed to download:\n%s" % e


app = QApplication(sys.argv)
form = Program()
form.show()
app.exec_()

