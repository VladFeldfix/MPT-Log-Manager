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

        # test all paths
        self.sc.test_path(self.main_path)

        # display main menu
        self.sc.start()

    def run(self):
        # go over all the files
        for root, dirs, files in os.walk(self.main_path):
            # go over each file
            for file in files:
                # ignore non .lot filetypes
                if ".lot" in file:
                    # read the lot file
                    lotfile = open(root+"/"+file, 'r')
                    lines = lotfile.readlines()
                    lotfile.close()
                    
                    # set variables
                    SerialNumber = ""
                    DateCode = ""
                    PartNumber = ""
                    Log = []
                    IgoneDashedLine = False

                    # go over every line in the lot file
                    for line in lines:
                        # only if Pass variables becomes True save this log
                        Pass = False

                        # strip line from \n
                        line = line.replace("\n", "")
                        
                        # start a log
                        if "+---------------------------------+" in line:
                            if not IgoneDashedLine:
                                Log = ["+---------------------------------+"]
                            IgoneDashedLine = not IgoneDashedLine
                        
                        # get date code
                        if "LOT NUMBER" in line:
                            line = line.split(":")
                            DateCode = line[1].strip()
                        
                        # 

main()