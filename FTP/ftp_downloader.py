import sys, os, json
from PyQt5 import QtWidgets, uic
from ftplib import FTP


class MainWindow(QtWidgets.QMainWindow):

    '''ATTRIBUTES
    field
    self.path_line
    self.folder_line
    self.console_field
    self.nonDownloadable_field
    self.ip_line
    self.username_line
    self.password_line

    btn
    self.btn_start
    self.btn_close
    self.btn_files
    self.btn_download

    label
    self.error_label
    
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #LOAD UI
        uic.loadUi("UI/demo.ui", self)

        # EVENTS
        app.aboutToQuit.connect(self.closeEvent) # close btn event
        self.btn_start.clicked.connect(self.startConnection) # btn_start event
        self.btn_close.clicked.connect(self.closeConnection) # btn_close event
        self.btn_files.clicked.connect(self.listFiles) # btn_file event
        self.btn_download.clicked.connect(self.downloadFiles) # btn_download event
        

        #JSON database
        self.intializeFields() # intialize Field using json

        #ATTRIBUTES
        self.jsonDict = {"folder":"", "path":"", "ip":"", "username":"", "password":""} #empty json
        self.ftp = FTP()
        self.localPath = ''
        self.non_downloadable = []

    #JSON FUNCTIONS and folder creation---------------
    def saveJson(self):
        self.jsonDict["path"] = self.path_line.text()
        self.jsonDict["folder"] = self.folder_line.text()
        self.jsonDict["ip"] = self.ip_line.text()
        self.jsonDict["username"] = self.username_line.text()
        self.jsonDict["password"] = self.password_line.text()
        with open('properties.json','w') as file:
            file.write(json.dumps(self.jsonDict))

    def readJson(self):
        with open('properties.json','r+') as file:

            file.seek(0) 
            jsonFile = file.readline()

            if jsonFile == '':
                with open('properties.json','w') as file:
                    file.write(json.dumps(self.jsonDict))
            else:
                self.jsonDict = json.loads(jsonFile)
            
    def intializeFields(self):
        self.readJson()
        self.path_line.setText(self.jsonDict["path"])
        self.folder_line.setText(self.jsonDict["folder"])
        self.ip_line.setText(self.jsonDict["ip"])
        self.username_line.setText(self.jsonDict["username"])
        self.password_line.setText(self.jsonDict["password"])
    
    def createMainFolder(self,path,folder_name):
        try:
            if os.path.exists(path):

                path = path +'/'+ folder_name
                if not(os.path.isdir(path)):
                    os.mkdir(path)
                    self.console('Folder is created')
                else:
                    self.console('Folder already exist')
                return path
            else:
                raise Exception('Path not exist')
            
        except Exception as e:
            print(e)
            self.error('Path not exist')    

    def createFolder(self,path):
        if not(os.path.isdir(self.localPath+path)):
            os.mkdir(self.localPath+path)
            print('Created',self.localPath+path)

    #-------------------------------------------------

    # CONNECTION AND DISCONNECTION--------------------

    def startFtp(self): # start ftp
        self.ftp = FTP(self.jsonDict['ip'])
        self.ftp.login(self.jsonDict['username'], self.jsonDict['password'])
        self.console("Login Sucessfully "+self.ftp.welcome)
 
    def closeFtp(self): # close ftp
        self.ftp.close()
        self.ftp = FTP()

    #-------------------------------------------------

    # BUTTON ACTION-----------------------------------
    # StartConnection button
    def startConnection(self):
        if self.areFieldEmpty():
            self.error('Fields are empty')
            return

        else:
            self.error('')  #no error show label
            self.saveJson() #create jsonDict and also save it locally
            
            try:
                self.startFtp() #start fpt connection
            except Exception as e:
                print(e)
                self.error('Fields are wrong')
                return

            self.localPath = self.createMainFolder(self.path_line.text(), self.folder_line.text())
            self.console(self.localPath)

    # List all files button
    def listFiles(self):
        try:
            self.console("\nALL FILES")
            self.console('-------------------------------------------------')
            self.console("\n".join(self.ftp.nlst()) + '\n')

        except Exception as e:
            print(e)
            self.error("Maybe you haven't made connection yet")

    # Download all files
    def downloadFiles(self):
        self.console("Downloading")
        self.console('-------------------------------------------------')
        self.nonDownloadble() #to get the list of non downloadble content
        def download():
            for file in self.ftp.nlst():

                if file in self.non_downloadable: #things you dont want to download
                    continue

                if self.isFolder(file): #if file is an folder recursion starts
                    previous_folder = self.ftp.pwd()
                    self.ftp.cwd(file)
                    self.createFolder(self.ftp.pwd())
                    download()
                    self.ftp.cwd(previous_folder)
                else:
                    try:
                        self.ftp.retrbinary("RETR " + file ,open(self.localPath + self.ftp.pwd()+'/'+ file, 'wb').write)
                    except Exception as e:
                        print(e)
                        self.console('Error'+self.ftp.pwd()+'/'+ file)
                        continue
                    self.console('Done'+self.ftp.pwd()+'/'+ file)

        self.console("ALL FILES ARE DOWNLOADED\n\n")
        
        try:
            download()
        except Exception as e:
            print(e)
            self.error("Maybe you haven't made connection yet")

    # Close Connection button
    def closeConnection(self):
        self.closeFtp()
        self.console("Connection close")

    # Close red button
    def closeEvent(self,event):
        print('Closing')
        sys.exit(0)
    #-------------------------------------------------

    # ALL CHECKS AND MESSAGE--------------------------
    def areFieldEmpty(self):
        def isFEmpty(T_field):
            return T_field.text() == ''
        return isFEmpty(self.path_line) or isFEmpty(self.folder_line) or isFEmpty(self.ip_line) or isFEmpty(self.username_line) or isFEmpty(self.password_line)
    
    # message on console gui
    def console(self,txt):
        print(txt)
        string = self.console_field.toPlainText() + txt + '\n'
        self.console_field.setPlainText(string)

    # Error message field on gui
    def error(self,txt):
        self.error_label.setText(txt)
    
    # Check whether file name is folder
    def isFolder(self,a):
        if a.find('.') == -1:
            return True
        else:
            return False
    
    def nonDownloadble(self):
        string = self.nonDownloadable_field.toPlainText()
        self.non_downloadable = string.split('\n')
    #-------------------------------------------------


            



app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec_()
