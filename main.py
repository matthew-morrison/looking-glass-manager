import results
import about
import advancedmenu
from emittingstream import EmittingStream

from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import configparser

options = [
    'C',  # PATH    Specify an additional configuration file to load
    'f',  # PATH    Specify the path to the shared memory file [current: /dev/shm/looking-glass]
    'L',  # SIZE    Specify the size in MB of the shared memory file (0 = detect) [current: 0]
    's',  #         Disable spice client
    'c',  # HOST    Specify the spice host or UNIX socket [current: 127.0.0.1]
    'p',  # PORT    Specify the spice port or 0 for UNIX socket [current: 5900]
    'j',  #         Disable cursor position scaling
    'M',  #         Don't hide the host cursor
    'K',  #         Set the FPS limit [current: 200]
    'k',  #         Enable FPS display
    'g',  # NAME    Force the use of a specific renderer
    'o',  # OPTION  Specify a renderer option (ie: opengl:vsync=0) Alternatively specify "list" to list all renderers and their options
    'a',  #         Auto resize the window to the guest
    'n',  #         Don't allow the window to be manually resized
    'r',  #         Don't maintain the aspect ratio
    'd',  #         Borderless mode
    'F',  #         Borderless fullscreen mode
    'x',  # XPOS    Initial window X position [current: center]
    'y',  # YPOS    Initial window Y position [current: center]
    'w',  # WIDTH   Initial window width [current: 1024]
    'b',  # HEIGHT  Initial window height [current: 768]
    'Q',  #         Ignore requests to quit (ie: Alt+F4)
    'l',  #         License information

]

class MainApp(QtWidgets.QMainWindow, results.Ui_MainWindow):

    ICON_GREEN_LED = 'green-led.png'
    ICON_RED_LED = 'red-led.png'

    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        self.setupUi(self)
        self.buttonStart.clicked.connect(self.startButton)
        self.buttonStop.clicked.connect(self.stopButton)
        self.buttonRestart.clicked.connect(self.restartButton)
        self.actionExit.triggered.connect(QtCore.QCoreApplication.quit) # Proper way to quit
        self.actionAbout.triggered.connect(self.showLicense)  # show license
        self.actionAdvanced_Options.triggered.connect(self.showAdvancedOptions)
        #self.graphicsView.setPix
        self.labelStatus.setPixmap(QtGui.QPixmap(self.ICON_RED_LED))
        #self.labelStatus.setGeometry(QtCore.QRect(10,10,100,100))
        #self.labelStatus.setScaledContents(True)
        #self.labelStatus.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lookingGlassProcess = QtCore.QProcess()
        self.lookingGlassProcess.finished.connect(self.updateLCD)

        #sys.stdout = EmittingStream(textWritten=self.appendToTextBox()) # ignore Pycharm's error

        self.out = None
        self.err = None

    def __del__(self):
        print("Writing to config")
        self.writeConfigToFile()
        print("Deleting self")
        # restore stdout
        sys.stdout = sys.__stdout__
        # kill LG subprocess / or does it kill itself?
        #self.lookingGlassProcess.kill()

    def updateLCD(self):
        print("updating")
        #self.lcdNumber.display("0")
        self.labelStatus.setPixmap(QtGui.QPixmap(self.ICON_RED_LED))

    def appendToTextBox(self, text):
        self.textBrowser.insertPlainText(text)
        sb = self.textBrowser.verticalScrollBar()
        sb.setValue(sb.maximum())


    # so necessary, yet so awful. What's the point of a config file if it doesn't keep values updated for you?
    def writeConfigToFile(self):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        config['CHECKBOX']['DisableSpiceClient'] = str(self.checkBoxSpiceClient.isChecked())
        config['CHECKBOX']['DisableCursorPositionScaling'] = str(self.checkBoxCursorPositionScaling.isChecked())
        config['CHECKBOX']['DoNotHideHostCursor'] = str(self.checkBoxHostCursor.isChecked())
        config['CHECKBOX']['EnableFPSDisplay'] = str(self.checkBoxEnableFPS.isChecked())
        config['CHECKBOX']['AutoResizeWindowToGuest'] = str(self.checkBoxAutoResize.isChecked())
        config['CHECKBOX']['DoNotAllowManualResize'] = str(self.checkBoxManualResize.isChecked())
        config['CHECKBOX']['DoNotMaintainAspectRatio'] = str(self.checkBoxAspectRatio.isChecked())
        config['CHECKBOX']['BorderlessMode'] = str(self.checkBoxBorderlessMode.isChecked())
        config['CHECKBOX']['BorderlessFullscreenMode'] = str(self.checkBoxBorderlessFullscreen.isChecked())
        config['CHECKBOX']['IgnoreRequestsToQuit'] = str(self.checkBoxIgnoreQuitRequests.isChecked())

        config['CHECKBOX']['SetFPSLimit'] = str(self.checkBoxFPSLimit.isChecked())
        config['CHECKBOX']['SetInitialXpos'] = str(self.checkBoxXpos.isChecked())
        config['CHECKBOX']['SetInitialYpos'] = str(self.checkBoxYpos.isChecked())
        config['CHECKBOX']['SetInitialWidth'] = str(self.checkBoxWidth.isChecked())
        config['CHECKBOX']['SetInitialHeight'] = str(self.checkBoxHeight.isChecked())

        config['NUMBER']['FPSLimit'] = str(self.spinBoxFPS.value())
        config['NUMBER']['InitialXpos'] = str(self.spinBoxXpos.value())
        config['NUMBER']['InitialYpos'] = str(self.spinBoxYpos.value())
        config['NUMBER']['InitialWidth'] = str(self.spinBoxWidth.value())
        config['NUMBER']['InitialHeight'] = str(self.spinBoxHeight.value())


        # TODO actually save these properly
        config['ADVANCED']['UseCustomLookingGlassConfigFile'] = str(self.advancedSettingsDict['UseCustomLookingGlassConfigFile'])
        config['ADVANCED']['UseCustomSHMPath'] = str(self.advancedSettingsDict['UseCustomSHMPath'])
        config['ADVANCED']['SpecifySHMSize'] = str(self.advancedSettingsDict['SpecifySHMSize'])
        config['ADVANCED']['SpecifySpiceHost'] = str(self.advancedSettingsDict['SpecifySpiceHost'])
        config['ADVANCED']['SpecifySpiceSocket'] = str(self.advancedSettingsDict['SpecifySpiceSocket'])

        config['ADVANCED']['LookingGlassConfigPath'] = str(self.advancedSettingsDict['LookingGlassConfigPath'])
        config['ADVANCED']['SHMPath'] = str(self.advancedSettingsDict['SHMPath'])
        config['ADVANCED']['SHMSize'] = str(self.advancedSettingsDict['SHMSize'])
        config['ADVANCED']['SpiceHost'] = str(self.advancedSettingsDict['SpiceHost'])
        config['ADVANCED']['SpicePort'] = str(self.advancedSettingsDict['SpicePort'])

        # write settings to file
        with open('settings.ini', 'w') as configFile:
            config.write(configFile, space_around_delimiters=True)


    # this function will check/uncheck or fill in values from the config file for this program.
    # reads from settings.ini, and will be saved back to settings.ini if there are changes.
    # default_settings is a backup file of settings.
    def populateFromConfig(self):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        # Basic checkbox settings
        self.checkBoxSpiceClient.setChecked(config['CHECKBOX'].getboolean('DisableSpiceClient'))
        self.checkBoxCursorPositionScaling.setChecked(config['CHECKBOX'].getboolean('DisableCursorPositionScaling'))
        self.checkBoxHostCursor.setChecked(config['CHECKBOX'].getboolean('DoNotHideHostCursor'))
        self.checkBoxEnableFPS.setChecked(config['CHECKBOX'].getboolean('EnableFPSDisplay'))
        self.checkBoxAutoResize.setChecked(config['CHECKBOX'].getboolean('AutoResizeWindowToGuest'))
        self.checkBoxManualResize.setChecked(config['CHECKBOX'].getboolean('DoNotAllowManualResize'))
        self.checkBoxAspectRatio.setChecked(config['CHECKBOX'].getboolean('DoNotMaintainAspectRatio'))
        self.checkBoxBorderlessMode.setChecked(config['CHECKBOX'].getboolean('BorderlessMode'))
        self.checkBoxBorderlessFullscreen.setChecked(config['CHECKBOX'].getboolean('BorderlessFullscreenMode'))
        self.checkBoxIgnoreQuitRequests.setChecked(config['CHECKBOX'].getboolean('IgnoreRequestsToQuit'))

        # Checkboxes for Basic other basic settings
        self.checkBoxFPSLimit.setChecked(config['CHECKBOX'].getboolean('SetFPSLimit'))
        self.checkBoxXpos.setChecked(config['CHECKBOX'].getboolean('SetInitialXpos'))
        self.checkBoxYpos.setChecked(config['CHECKBOX'].getboolean('SetInitialYpos'))
        self.checkBoxWidth.setChecked(config['CHECKBOX'].getboolean('SetInitialWidth'))
        self.checkBoxHeight.setChecked(config['CHECKBOX'].getboolean('SetInitialHeight'))

        # Set Number values for basic settings
        self.spinBoxFPS.setValue(config['NUMBER'].getint('FPSLimit'))
        self.spinBoxXpos.setValue(config['NUMBER'].getint('InitialXpos'))
        self.spinBoxYpos.setValue(config['NUMBER'].getint('InitialYpos'))
        self.spinBoxWidth.setValue(config['NUMBER'].getint('InitialWidth'))
        self.spinBoxHeight.setValue(config['NUMBER'].getint('InitialHeight'))

        # Advanced Values
        self.advancedSettingsDict = dict()
        self.advancedSettingsDict['UseCustomLookingGlassConfigFile'] = config['ADVANCED'].getboolean('UseCustomLookingGlassConfigFile')
        self.advancedSettingsDict['UseCustomSHMPath'] = config['ADVANCED'].getboolean('UseCustomSHMPath')
        self.advancedSettingsDict['SpecifySHMSize'] = config['ADVANCED'].getboolean('SpecifySHMSize')
        self.advancedSettingsDict['SpecifySpiceHost'] = config['ADVANCED'].getboolean('SpecifySpiceHost')
        self.advancedSettingsDict['SpecifySpiceSocket'] = config['ADVANCED'].getboolean('SpecifySpiceSocket')

        self.advancedSettingsDict['LookingGlassConfigPath'] = config['ADVANCED']['LookingGlassConfigPath']
        self.advancedSettingsDict['SHMPath'] = config['ADVANCED']['SHMPath']
        self.advancedSettingsDict['SHMSize'] = config['ADVANCED'].getint('SHMSize')
        self.advancedSettingsDict['SpiceHost'] = config['ADVANCED']['SpiceHost']
        self.advancedSettingsDict['SpicePort'] = config['ADVANCED']['SpicePort']


    def populateAdvancedFromDict(self, advanced):
        advanced.ui.checkBoxLGPath.setChecked(self.advancedSettingsDict['UseCustomLookingGlassConfigFile'])
        advanced.ui.checkBoxSHMPath.setChecked(self.advancedSettingsDict['UseCustomSHMPath'])
        advanced.ui.checkBoxSHMSize.setChecked(self.advancedSettingsDict['SpecifySHMSize'])
        advanced.ui.checkBoxHostSocket.setChecked(self.advancedSettingsDict['SpecifySpiceHost'])
        advanced.ui.checkBoxSpicePort.setChecked(self.advancedSettingsDict['SpecifySpiceSocket'])

        advanced.ui.LGPathLineEdit.setText(self.advancedSettingsDict['LookingGlassConfigPath'])
        advanced.ui.SHMPathLineEdit.setText(self.advancedSettingsDict['SHMPath'])
        advanced.ui.memsizeSpinBox.setValue(self.advancedSettingsDict['SHMSize'])
        advanced.ui.socketLineEdit.setText(self.advancedSettingsDict['SpiceHost'])
        advanced.ui.portSpinBox.setValue(int(self.advancedSettingsDict['SpicePort']))


    #  get and return a list of all options that are checked
    # there will be ten options
    def getCheckOptions(self):
        checkBoxOptions = []
        if(self.checkBoxEnableFPS.isChecked()):
            checkBoxOptions.append('-k')
        if(self.checkBoxHostCursor.isChecked()):
            checkBoxOptions.append('-M')
        if(self.checkBoxCursorPositionScaling.isChecked()):
            checkBoxOptions.append('-j')
        if(self.checkBoxSpiceClient.isChecked()):
            checkBoxOptions.append('-s')
        if(self.checkBoxAspectRatio.isChecked()):
            checkBoxOptions.append('-r')
        if(self.checkBoxAutoResize.isChecked()):
            checkBoxOptions.append('-a')
        if(self.checkBoxBorderlessFullscreen.isChecked()):
            checkBoxOptions.append('-F')
        if(self.checkBoxBorderlessMode.isChecked()):
            checkBoxOptions.append('-d')
        if(self.checkBoxIgnoreQuitRequests.isChecked()):
            checkBoxOptions.append('-Q')
        if(self.checkBoxManualResize.isChecked()):
            checkBoxOptions.append('-n')
        print(checkBoxOptions)
        return checkBoxOptions

    #  get all other regular options that aren't simple boolean values
    def getNumberOptions(self):
        checkNumOptions = []
        if(self.checkBoxXpos.isChecked()):
            xcoords = self.spinBoxXpos.value()
            checkNumOptions.append('-x ' + str(xcoords))
        if(self.checkBoxYpos.isChecked()):
            ycoords = self.spinBoxYpos.value()
            checkNumOptions.append('-y ' + str(ycoords))
        if(self.checkBoxWidth.isChecked()):
            startWidth = self.spinBoxWidth.value()
            checkNumOptions.append('-w ' + str(startWidth))
        if(self.checkBoxHeight.isChecked()):
            startHeight = self.spinBoxHeight.value()
            checkNumOptions.append('-h ' + str(startHeight))
        if(self.checkBoxFPSLimit.isChecked()):
            fpsLimit = self.spinBoxFPS.value()
            checkNumOptions.append('-K ' + str(fpsLimit))
        return checkNumOptions

    # yes. this won't be implemented yet.
    def getAdvancedOptions(self):
        advancedOptions = []
        return advancedOptions

    #  this function checks all checkboxes and inputs.
    #  will return the arguments for the LG command in the format of a list.
    def getOptions(self):
        allOptions = self.getNumberOptions() + self.getAdvancedOptions() + self.getCheckOptions()
        return allOptions

    #  this function takes the list of options and prepends the looking-glass-client program.
    def createCommand(self):
        return ['looking-glass-client'] + self.getOptions() # return in format that QProcess accepts arguments


    def startButton(self):
        startCommand = self.createCommand()
        startArguments = self.getOptions()
        #print(startCommand)
        self.startSubprocess(startCommand)


    def stdoutReady(self):
        text = self.lookingGlassProcess.readAllStandardOutput()
        decoded = text.data().decode('utf-8')
        self.appendToTextBox(decoded)

    def stderrReady(self):
        text = self.lookingGlassProcess.readAllStandardError()  # get QByteArray
        decoded = text.data().decode('utf-8')  # convert QByteArray to string
        self.appendToTextBox(decoded)

    def startSubprocess(self, startArguments):
        print('Starting Subprocess')
        #print(startArguments)
        commandAsString = ' '.join(startArguments)

        #print(type(self.lookingGlassProcess))
        # check if process never started, or if it has exited
        if(None == self.lookingGlassProcess or True):
            #self.lookingGlassProcess = self.startSubprocess(startArguments)
            self.lookingGlassProcess = QtCore.QProcess()
            self.lookingGlassProcess.start(commandAsString)
            self.lookingGlassProcess.readyReadStandardOutput.connect(self.stdoutReady)
            self.lookingGlassProcess.readyReadStandardError.connect(self.stderrReady)
            self.lookingGlassProcess.finished.connect(self.updateLCD)
            self.labelStatus.setPixmap(QtGui.QPixmap(self.ICON_GREEN_LED))
            #self.lcdNumber.display("1")
            #self.lookingGlassProcess = subprocess.Popen(startArguments, stdout=subprocess.PIPE, shell=False)
            #(self.out, self.err) = self.lookingGlassProcess.communicate()

    def subProcessForLicense(self):
        print("Getting license text")
        process = QtCore.QProcess()
        process.start('looking-glass-client -l')

    def stopButton(self):
        print("click stop button")
        if(None != self.lookingGlassProcess):
            print('Attempting to close process')
            self.lookingGlassProcess.kill()

    def restartButton(self):
        print("click restart button")
        self.stopButton()
        self.startButton()

    def showAdvancedOptions(self):
        print("Showing advanced options")
        advancedOptions = QtWidgets.QDialog()
        advancedOptions.ui = advancedmenu.Ui_Dialog()
        advancedOptions.ui.setupUi(advancedOptions)
        advancedOptions.ui.buttonOkay.clicked.connect(advancedOptions.hide)
        advancedOptions.ui.buttonCancel.clicked.connect(advancedOptions.hide)
        self.populateAdvancedFromDict(advancedOptions) # populates options from dict
        advancedOptions.exec_()
        advancedOptions.show()



    def showLicense(self):
        print("showing license")
        showLicense = QtWidgets.QDialog()
        showLicense.ui = about.Ui_Dialog()
        showLicense.ui.setupUi(showLicense)
        showLicense.ui.buttonOkay.clicked.connect(showLicense.hide)
        showLicense.setWindowTitle("About looking-glass-client")
        showLicense.exec_()
        showLicense.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = MainApp()
    form.populateFromConfig()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()