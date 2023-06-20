from SmartConsole import *

class main:
    # constructor
    def __init__(self):
        # load smart console
        self.sc = SmartConsole("MPT Log Manager", "1.0")

        # set-up main memu
        self.sc.main_menu["RUN"] = self.run

        # get settings
        self.main_path = self.sc.get_setting("MPT Folder")
        self.path_test_results = self.sc.get_setting("Test Results")
        self.path_mpt_links = self.sc.get_setting("Mpt links")

        # test all paths
        self.sc.test_path(self.main_path)
        self.sc.test_path(self.path_test_results)
        self.sc.test_path(self.path_mpt_links)

        # display main menu
        self.sc.start()

    def run(self):
        mptlinks = []
        # go over all the files
        for root, dirs, files in os.walk(self.main_path):
            # go over each file
            for file in files:
                # read lots files
                if ".lot" in file and not ".bak" in file:
                    # read the lot file
                    lotfile = open(root+"/"+file, 'r')
                    lines = lotfile.readlines()
                    lotfile.close()
                    
                    # set variables
                    SerialNumber = ""
                    DateCode = ""
                    PartNumber = file.replace(".lot", "")
                    Log = []
                    IgoneDashedLine = False
                    SaveLog = False
                    lines_qty = 0

                    # go over every line in the lot file
                    for line in lines:
                        # only if Pass variables becomes True save this log
                        Pass = False

                        # strip line from \n
                        line = line.replace("\n", "")
                        
                        # start a log
                        if "+---------------------------------+" in line:
                            if not IgoneDashedLine:
                                Log = []
                                SaveLog = False
                            IgoneDashedLine = not IgoneDashedLine
                        
                        # get date code
                        if "LOT NUMBER".upper() in line.upper():
                            splitted = line.split(":")
                            DateCode = splitted[1].replace("|", "")
                            DateCode = DateCode.strip()
                        
                        # get serial number
                        if "Serial Number".upper() in line.upper():
                            splitted = line.split(":")
                            SerialNumber = splitted[1].strip()
                        
                        # get test result
                        if "TEST PASSED".upper() in line.upper():
                            SaveLog = True
                        
                        Log.append(line)
                        if SaveLog:
                            self.save_log(PartNumber, SerialNumber, DateCode, Log)

                        # count the lines
                        lines_qty += 1
                    
                    # create backup
                    if lines_qty > 100000:
                        oldName = root+"/"+file
                        n = 1
                        newName = oldName.replace(".lot", "("+str(n)+").bakup")
                        while not os.path.isfile(newName):
                            n += 1
                            newName.replace("("+str(n-1)+").bakup", "("+str(n)+").bakup")
                        os.rename(oldName, newName)
                
                # read lots files
                if ".mpt" in file:
                    PartNumber = file.replace(".mpt", "")
                    root = root.replace("/", "\\")
                    tmp = root.split("\\")
                    Group = tmp[-2]
                    mptlinks.append((PartNumber, Group, root, file))
        
        # create mpt links
        MPTlinksfile = open(self.path_mpt_links, 'w')
        for link in mptlinks:
            PartNumber = link[0]
            Group = link[1]
            root = link[2]
            file = link[3]         
            MPTlinksfile.write(PartNumber+".Description="+PartNumber+"\n")
            MPTlinksfile.write(PartNumber+".Description="+PartNumber+"\n")
            MPTlinksfile.write(PartNumber+".LinkGroup="+Group+"\n")
            MPTlinksfile.write(PartNumber+"="+root+"\\"+file+"\n")
            self.sc.print("Added MPT link: "+PartNumber)
        MPTlinksfile.close()

        # restart
        self.sc.restart()

    def save_log(self, PartNumber, SerialNumber, DateCode, Log):
        PartNumber = self.filter(PartNumber)
        SerialNumber = self.filter(SerialNumber)
        DateCode = self.filter(DateCode)
        path = self.path_test_results+"/"+PartNumber
        self.sc.print(path+"/"+SerialNumber+"_"+DateCode+"_"+PartNumber+".html")
        if not os.path.isdir(path):
            os.makedirs(path)
        
        file = open(path+"/"+SerialNumber+"_"+DateCode+"_"+PartNumber+".html", 'w')
        file.write("<html>\n")
        file.write("<head>\n")
        file.write("<style>\n")
        file.write("html{font-family:Courier New; font-size:10pt;}\n")
        file.write("</style>\n")
        file.write("</head>\n")
        file.write("<body>\n")
        for line in Log:
            file.write(line.replace(" ", "&nbsp")+"<br>\n")
        file.write("</body>\n")
        file.write("</html>\n")
        file.close()
    
    def filter(self, txt):
        txt = txt.upper()
        txt = txt.strip()
        return_value = ""
        AllowedChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- "
        for ch in txt:
            if ch in AllowedChars:
                return_value += ch
        return return_value
main()