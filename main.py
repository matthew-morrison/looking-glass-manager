import results
import about
import advancedmenu

from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import configparser


class AdvancedOptions(QtWidgets.QDialog, advancedmenu.Ui_Dialog):

    def __init__(self, advancedSettingsDict, parent=None):
        super(AdvancedOptions, self).__init__(parent)
        self.setupUi(self)
        self.advancedSettingsDict = advancedSettingsDict
        self.buttonOkay.clicked.connect(self.exitAdvancedOptions)
        self.buttonCancel.clicked.connect(self.exitAdvancedOptions)
        self.populateAdvancedFromDict()  # populates options from dict
        self.exec_()
        self.show()

    def populateAdvancedFromDict(self):
        self.checkBoxLGPath.setChecked(self.advancedSettingsDict['UseCustomLookingGlassConfigFile'])
        self.checkBoxSHMPath.setChecked(self.advancedSettingsDict['UseCustomSHMPath'])
        self.checkBoxSHMSize.setChecked(self.advancedSettingsDict['SpecifySHMSize'])
        self.checkBoxHostSocket.setChecked(self.advancedSettingsDict['SpecifySpiceHost'])
        self.checkBoxSpicePort.setChecked(self.advancedSettingsDict['SpecifySpiceSocket'])

        self.LGPathLineEdit.setText(self.advancedSettingsDict['LookingGlassConfigPath'])
        self.SHMPathLineEdit.setText(self.advancedSettingsDict['SHMPath'])
        self.memsizeSpinBox.setValue(int(self.advancedSettingsDict['SHMSize']))
        self.socketLineEdit.setText(self.advancedSettingsDict['SpiceHost'])
        self.portSpinBox.setValue(int(self.advancedSettingsDict['SpicePort']))

    def exitAdvancedOptions(self):
        # also write the advanced options to the object.
        print("Writing advanced options to dict")
        self.advancedSettingsDict['UseCustomLookingGlassConfigFile'] = self.checkBoxLGPath.isChecked()
        self.advancedSettingsDict['UseCustomSHMPath'] = self.checkBoxSHMPath.isChecked()
        self.advancedSettingsDict['SpecifySHMSize'] = self.checkBoxSHMSize.isChecked()
        self.advancedSettingsDict['SpecifySpiceHost'] = self.checkBoxHostSocket.isChecked()
        self.advancedSettingsDict['SpecifySpiceSocket'] = self.checkBoxSpicePort.isChecked()

        self.advancedSettingsDict['LookingGlassConfigPath'] = self.LGPathLineEdit.text()
        self.advancedSettingsDict['SHMPath'] = self.SHMPathLineEdit.text()
        self.advancedSettingsDict['SHMSize'] = self.memsizeSpinBox.text()
        self.advancedSettingsDict['SpiceHost'] = self.socketLineEdit.text()
        self.advancedSettingsDict['SpicePort'] = self.portSpinBox.value()
        self.hide()


class MainApp(QtWidgets.QMainWindow, results.Ui_MainWindow):

    ICON_GREEN_LED = 'green-led.png'
    ICON_RED_LED = 'red-led.png'
    LG_LICENSE_FILE = 'lg-license.txt'

    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        self.setupUi(self)
        self.buttonStart.clicked.connect(self.startButton)
        self.buttonStop.clicked.connect(self.stopButton)
        self.buttonRestart.clicked.connect(self.restartButton)
        self.actionExit.triggered.connect(QtCore.QCoreApplication.quit) # Proper way to quit
        self.actionAbout.triggered.connect(self.showLicense)  # show license
        self.actionAdvanced_Options.triggered.connect(self.showAdvancedOptions)
        self.labelStatus.setPixmap(QtGui.QPixmap(self.ICON_RED_LED))
        self.lookingGlassProcess = QtCore.QProcess()
        self.lookingGlassProcess.finished.connect(self.updateLCD)

        #sys.stdout = EmittingStream(textWritten=self.appendToTextBox()) # ignore Pycharm's error

        self.out = None
        self.err = None

    def __del__(self):
        print("Writing to config")
        self.writeConfigToFile()
        print("Deleting self")
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
        config['CHECKBOX']['EnableMipmapping'] = str(self.checkBoxMipMap.isChecked())
        config['CHECKBOX']['EnableVsync'] = str(self.checkBoxVsync.isChecked())
        config['CHECKBOX']['PreventBuffer'] = str(self.checkBoxPreventBuffer.isChecked())
        config['CHECKBOX']['AMDPinnedMem'] = str(self.checkBoxGLAMD.isChecked())

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
        self.checkBoxMipMap.setChecked(config['CHECKBOX'].getboolean('EnableMipmapping'))
        self.checkBoxVsync.setChecked(config['CHECKBOX'].getboolean('EnableVsync'))
        self.checkBoxPreventBuffer.setChecked(config['CHECKBOX'].getboolean('PreventBuffer'))
        self.checkBoxGLAMD.setChecked(config['CHECKBOX'].getboolean('AMDPinnedMem'))

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
        advanced.ui.memsizeSpinBox.setValue(int(self.advancedSettingsDict['SHMSize']))
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

        #slightly more complicated checks and options
        if(self.checkBoxMipMap.isChecked()):
            checkBoxOptions.append('-o')
            checkBoxOptions.append('opengl:mipmap=1')
        else:
            checkBoxOptions.append('-o')
            checkBoxOptions.append('opengl:mipmap=0')

        if(self.checkBoxVsync.isChecked()):
            checkBoxOptions.append('-o')
            checkBoxOptions.append('opengl:vsync=1')
        else:
            checkBoxOptions.append('-o')
            checkBoxOptions.append('opengl:vsync=0')

        if (self.checkBoxPreventBuffer.isChecked()):
            checkBoxOptions.append('-o')
            checkBoxOptions.append('opengl:preventBuffer=1')
        else:
            checkBoxOptions.append('-o')
            checkBoxOptions.append('opengl:preventBuffer=0')
        if (self.checkBoxGLAMD.isChecked()):
            checkBoxOptions.append('-o')
            checkBoxOptions.append('opengl:amdPinnedMem=1')
        else:
            checkBoxOptions.append('-o')
            checkBoxOptions.append('opengl:amdPinnedMem=0')

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
        commandAsString = ' '.join(startArguments)
        self.showCMDCommand(commandAsString)  # display the full looking-glass-client command to the user

        # check if process never started, or if it has exited
        if(None == self.lookingGlassProcess or True):
            self.lookingGlassProcess = QtCore.QProcess()
            self.lookingGlassProcess.start(commandAsString)
            self.lookingGlassProcess.readyReadStandardOutput.connect(self.stdoutReady)  # redirect standard output
            self.lookingGlassProcess.readyReadStandardError.connect(self.stderrReady)  # redirect errors
            self.lookingGlassProcess.finished.connect(self.updateLCD)
            self.labelStatus.setPixmap(QtGui.QPixmap(self.ICON_GREEN_LED))

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

    def showCMDCommand(self, commandText):
        self.lineEditCMDOutput.setText(commandText)

    def showAdvancedOptions(self):
        print("Showing advanced options")
        dialog = AdvancedOptions(self.advancedSettingsDict)

    def showLicense(self):
        print("showing license")
        showLicense = QtWidgets.QDialog()
        showLicense.ui = about.Ui_Dialog()
        showLicense.ui.setupUi(showLicense)
        showLicense.ui.buttonOkay.clicked.connect(showLicense.hide)
        showLicense.setWindowTitle("About looking-glass-client")
        text = open(self.LG_LICENSE_FILE, 'r').read()
        showLicense.ui.textBrowser.setText(text)
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