from PyQt4 import QtGui, QtCore
import sys, os, json

class RankingBoard(QtGui.QMainWindow):
    def __init__(self, control):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("OWL Rankings")
        self.control = control
        self.tierCount = 0
        for t in self.control.current_ranking:
            if t.startswith("Tier"):
                self.tierCount += 1

        self.refresh()

    def refresh(self):

        font_db = QtGui.QFontDatabase()
        font_id = font_db.addApplicationFont(os.getcwd() + "\\assets\\bignoodletoo.ttf")

        #families = font_db.applicationFontFamilies(font_id)
        #bignoodle = QtGui.QFont("one of your font families")


        self.tierFont = QtGui.QFont("BigNoodleTooOblique", 20)
        self.changeFont = QtGui.QFont("Impact", 13)

        vLayoutWidget = QtGui.QWidget()
        vLayoutWidget.setAutoFillBackground(True)
        p = QtGui.QPalette()
        p.setColor(QtGui.QPalette.Background, QtGui.QColor(200,200,200))
        vLayoutWidget.setPalette(p)

        self.vLayout = QtGui.QVBoxLayout(vLayoutWidget)
        self.vLayout.setAlignment(QtCore.Qt.AlignTop)
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.vLayout.setSpacing(0)

        for item in self.control.current_ranking:
            if item.startswith("Tier"):
                self.add_tier(item)
            else:
                self.add_card(item)

                
        self.setCentralWidget(vLayoutWidget)

    def add_card(self, name):
        card = QtGui.QLabel()
        card.setPixmap(QtGui.QPixmap(os.getcwd() + '\\nameCards\\%s.png'%name))
        self.vLayout.addWidget(card)

        rank_change = self.get_change(name)
        if rank_change > 0:
            change = QtGui.QLabel("+{}".format(rank_change))
            change.setAlignment(QtCore.Qt.AlignRight)
            change.setFont(self.changeFont)
            change.move(220, 5)
            change.setParent(card)
            change.setStyleSheet('color: rgb(50, 255, 50)')

        elif rank_change < 0:
            change = QtGui.QLabel(" -{}".format(rank_change*-1))
            change.setAlignment(QtCore.Qt.AlignRight)
            change.setFont(self.changeFont)
            change.move(220, 5)
            change.setParent(card)
            change.setStyleSheet('color: rgb(255, 0, 0)')

        else:
            change = QtGui.QLabel("  ---")
            change.setAlignment(QtCore.Qt.AlignRight)
            change.setFont(self.changeFont)
            change.move(220, 5)
            change.setParent(card)
            change.setStyleSheet('color: rgb(0, 0, 0)')

        return card

    def add_tier(self, name):
        tier = QtGui.QLabel(name)
        tier.setFont(self.tierFont)
        tier.setAlignment(QtCore.Qt.AlignCenter)
        #tier.setStyleSheet('color: white')
        self.vLayout.addWidget(tier)
        return tier

    def move_up(self, item):
        i = self.control.current_ranking.index(item)
        if i != 0:
            self.control.current_ranking.insert(i-1, self.control.current_ranking.pop(i))
            self.refresh()

    def move_down(self, item):
        i = self.control.current_ranking.index(item)
        self.control.current_ranking.insert(i+1, self.control.current_ranking.pop(i))
        self.refresh()

    def add_new_tier(self):
        self.tierCount += 1
        self.control.current_ranking.append("Tier %i"%self.tierCount)

        #buildInfo["Tier %i"%self.tierCount] = [len(current_ranking), "tier"]
        self.refresh()

    def remove_last_tier(self):
        self.control.current_ranking.remove("Tier %i"%self.tierCount)
        #buildInfo.pop("Tier %i"%self.tierCount)
        self.tierCount -= 1
        self.refresh()

    def get_change(self, team):
        initial_clean = []
        current_clean = []

        for obj in self.control.initial_ranking:
            if not obj.startswith("Tier"):
                initial_clean.append(obj)

        for obj in self.control.current_ranking:
            if not obj.startswith("Tier"):
                current_clean.append(obj)

        

        return initial_clean.index(team) - current_clean.index(team)




class ControlBoard(QtGui.QMainWindow):
    def __init__(self, initial_ranking):
        QtGui.QMainWindow.__init__(self)
        self.initial_ranking = initial_ranking
        self.current_ranking = initial_ranking.copy()
        self.setWindowTitle("Control Board")
        self.setup()

    def setup(self):

        self.displayWindow = RankingBoard(self)
        #self.displayWindow.setFixedHeight(840)
        self.displayWindow.setFixedWidth(280)
        self.displayWindow.show()

        main_menu = self.menuBar()
        file_menu = main_menu.addMenu("File")

        saveAction = QtGui.QAction("Save Rankings", self)
        loadAction = QtGui.QAction("Load Rankings", self)

        file_menu.addAction(saveAction)
        file_menu.addAction(loadAction)

        saveAction.triggered.connect(self.savefile)
        loadAction.triggered.connect(self.openfile)

        vLayoutWidget = QtGui.QWidget()
        vLayout = QtGui.QVBoxLayout(vLayoutWidget)


        dropdown = QtGui.QComboBox()
        for item in initial_ranking:
            if not item.startswith("Tier"):
                dropdown.addItem(item)

        hLayoutWidget = QtGui.QWidget()
        hLayout = QtGui.QHBoxLayout(hLayoutWidget)
        h2LayoutWidget = QtGui.QWidget()
        h2Layout = QtGui.QHBoxLayout(h2LayoutWidget)

        upButton = QtGui.QPushButton("Move Up")
        upButton.clicked.connect(lambda:self.displayWindow.move_up(dropdown.currentText()))

        downButton = QtGui.QPushButton("Move Down")
        downButton.clicked.connect(lambda:self.displayWindow.move_down(dropdown.currentText()))


        addTierButton = QtGui.QPushButton("Add Tier")
        addTierButton.clicked.connect(self.displayWindow.add_new_tier)

        removeTierButton = QtGui.QPushButton("Remove Tier")
        removeTierButton.clicked.connect(self.displayWindow.remove_last_tier)


        vLayout.addWidget(dropdown)
        vLayout.addWidget(hLayoutWidget)
        vLayout.addWidget(h2LayoutWidget)

        hLayout.addWidget(upButton)
        hLayout.addWidget(downButton)

        h2Layout.addWidget(addTierButton)
        h2Layout.addWidget(removeTierButton)


        self.setCentralWidget(vLayoutWidget)

    def savefile(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, 'Save file', 
            os.getcwd(),"json files (*.json)")

        with open(fileName, 'w') as outfile:
            json.dump(self.current_ranking, outfile)

    def openfile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
            os.getcwd(),"json files (*.json)")

        with open(fileName, 'r') as readfile:
            self.initial_ranking = json.load(readfile)

        self.current_ranking = self.initial_ranking.copy()
        self.displayWindow.refresh()


if __name__ == "__main__":


    initial_ranking = ["Tier 1", "Titans", "Shock", "NYXL", "Tier 2", "Gladiators", "Dynasty", "Tier 3", "Spitfire", "Fusion", "Dragons", "Fuel", "Uprising", "Hunters", "Spark", "Defiant", "Outlaws", "Eternal", "Tier 4", "Valiant", "Reign", "Tier Waterloo", "Justice", "Charge", "Mayhem"]

    app = QtGui.QApplication(sys.argv)
    displayWindow = ControlBoard(initial_ranking)
    displayWindow.show()
    sys.exit(app.exec_())