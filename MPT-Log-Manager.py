# Download SmartConsole.py from: https://github.com/VladFeldfix/Smart-Console/blob/main/SmartConsole.py
from SmartConsole import *
import shutil
import re

class main:
    # constructor
    def __init__(self):
        # load smart console
        self.sc = SmartConsole("MPT Log Manager", "3.1")

        # set-up main memu
        self.sc.add_main_menu_item("RUN", self.run)
        self.sc.add_main_menu_item("PASS AND FAIL LOGS", self.passfail)

        # get settings
        self.main_path = self.sc.get_setting("MPT Folder")
        self.main_path = self.main_path.replace("\\", "/")
        self.path_test_results = self.sc.get_setting("Test Results")
        self.path_mpt_links = self.sc.get_setting("Mpt links")

        # test all paths
        self.sc.test_path(self.main_path)
        self.sc.test_path(self.path_test_results)
        self.sc.test_path(self.path_mpt_links)

        # set global variables
        self.database = {}
        self.groups = {}
        self.mptlinks = []

        # display main menu
        self.sc.start()

    def passfail(self):
        group = self.sc.choose("Choose a group",("Rafael1","Rafael2"))
        part_number = self.sc.input("Insert part number")
        file_path = self.main_path+"/"+group+"/"+part_number+"/"+part_number+".lot"
        self.sc.test_path(file_path)
        resut_path = self.path_test_results+"/"+part_number+"/"+part_number+" PASS & FAIL"
        if not os.path.exists(resut_path):
            os.makedirs(resut_path)
        file = open(file_path, 'r')
        lines = file.readlines()
        file.close()
        ignore = False
        log = []
        index = 1
        date = ""
        serial_number = ""

        for line in lines:
            if "+---------------------------------+" in line:
                if not ignore:
                    ignore = True # ignore the next line
                    
                    # save log
                    if len(log) > 0:
                        new_file_name = resut_path+"/"+str(index)+"_"+date+"_"+serial_number+".txt"
                        self.sc.print(new_file_name)
                        file = open(new_file_name, 'w')
                        index += 1
                        for l in log:
                            file.write(l)
                        file.close()
                        log = []
                else:
                    ignore = False
            
            log.append(line)

            if "LOT NUMBER" in line:
                date = line
                date = date.replace("|", "").replace(" ", "").replace("\n", "")
                date = date.split(":")
                date = date[1]
            
            if "SERIAL NUMBER" in line.upper():
                serial_number = line
                serial_number = serial_number.replace(" ", "").replace("\n", "")
                serial_number = serial_number.split(":")
                serial_number = serial_number[1]

        self.sc.restart()


    def run(self):
        self.read_logs()
        self.generate_html_files()
        self.backup()
        self.generate_MPTlinks()
        self.sc.restart()
    
    def read_logs(self):
        self.sc.print("Gathering data...")
        # go over every .lot file and read every line
        # while reading the files create a database of logs in the following format
        # { PART_NUMBER : [ (DATECODE, YEAR, OPERATOR, SERIAL_NUMBER, PASSED, LOG_DATA), ] }
        # { PART_NUMBER : GROUP}
        
        # make a database of part numbers
        for root, dirs, files in os.walk(self.main_path):
            root = root.replace("\\", "/")
            for file in files:
                if ".mpt" in file:
                    group = root.replace(self.main_path, "")
                    group = group.split("/")
                    group = group[1]
                    file = file.replace(".mpt", "")
                    self.database[file] = []
                    self.groups[file] = group
        
        # go over every .lot file and read every line
        for part_number in self.database.keys():
            group = self.groups[part_number]
            path = self.main_path+"/"+group+"/"+part_number+"/"+part_number+".lot"
            path_to_mpt_file = self.main_path+"/"+group+"/"+part_number+"/"+part_number+".mpt"
            if os.path.isfile(path_to_mpt_file):
                self.mptlinks.append((part_number, group, path_to_mpt_file))

            # if the file exists
            if os.path.isfile(path):

                # load file data
                file = open(path, 'r')
                lines = file.readlines()
                file.close()
                
                # read file data
                ignore_line = False
                datecode = ""
                log_data = []
                for line in lines:
                    # start a new log
                    if "+---------------------------------+" in line:
                        if not ignore_line:
                            if datecode != "":
                                self.database[part_number].append((datecode, year, operator, serial_number, passed, log_data))
                            datecode = ""
                            year = ""
                            operator = ""
                            serial_number = ""
                            passed = False
                            log_data = []
                        ignore_line = not ignore_line
                    
                    log_data.append(line)
                    
                    # get datecode
                    if "LOT NUMBER" in line.upper():
                        datecode = line.split(":")
                        datecode = datecode[1].replace("|", "")
                        datecode = datecode.strip()
                        year = datecode[-4:]
                    
                    # get serial number
                    if "SERIAL NUMBER" in line.upper():
                        serial_number = line.split(":")
                        serial_number = serial_number[1].strip()
                    
                    # get test result
                    if "TEST PASSED" in line.upper():
                        passed = True
                
                # add last log
                if len(log_data) > 0:
                    self.database[part_number].append((datecode, year, operator, serial_number, passed, log_data))
    
    def generate_html_files(self):
        self.sc.print("Generating HTML files...")
        # for each PART_NUMBER in database for each LOG where PASSED == True
        # save LOG_DATA as an HTML file
        for part_number, logs in self.database.items():
            
            # set file preferences and create a new folder if not exist
            folder = self.path_test_results+"/"+part_number
            if not os.path.isdir(folder):
                os.makedirs(folder)
            
            for log in logs:
                # set variables
                datecode = log[0]
                year = log[1]
                operator = log[2]
                serial_number = log[3]
                passed = log[4]
                log_data = log[5]
                
                serial_number = re.sub(r'[^a-zA-Z0-9-_ ]', '',serial_number)
                datecode = re.sub(r'[^a-zA-Z0-9-_ ]', '',datecode)
                part_number = re.sub(r'[^a-zA-Z0-9-_ ]', '',part_number)

                path = folder+"/"+serial_number+"_"+datecode+"_"+part_number+".html"

                # generate html file
                if passed and serial_number != "" and datecode != "" and part_number != "":
                    if not os.path.isfile(path):
                        self.sc.print(serial_number+"_"+datecode+"_"+part_number+".html")

                        # generate html file
                        htmlfile = open(path, 'w')
                        htmlfile.write("<html>\n")
                        htmlfile.write("<head>\n")
                        htmlfile.write("<style>\n")
                        htmlfile.write("html{font-family:Courier New; font-size:10pt;}\n")
                        htmlfile.write("</style>\n")
                        htmlfile.write("</head>\n")
                        htmlfile.write("<body>\n")
                        for line in log_data:
                            htmlfile.write(line.replace(" ", "&nbsp")+"<br>\n")
                        htmlfile.write("</body>\n")
                        htmlfile.write("</html>\n")
                        htmlfile.close()
                
            # save csv and txt
            group = self.groups[part_number]
            scr = self.main_path+"/"+group+"/"+part_number+"/"+part_number+".txt"
            new = self.path_test_results+"/"+part_number+"/"+part_number+".txt"
            if os.path.isfile(scr):
                shutil.copy(scr, new)

            scr = self.main_path+"/"+group+"/"+part_number+"/"+part_number+".csv"
            new = self.path_test_results+"/"+part_number+"/"+part_number+".csv"
            if os.path.isfile(scr):
                shutil.copy(scr, new)
        
    def backup(self):
        self.sc.print("Generating backup files...")
        # for each PART_NUMBER in database
        # for each LOG
        # if YEAR is not the current year -> save LOG_DATA to a backup list flag that the current .log file must be updated
        # if flag was raised -> save this log to a list for this year overwrite
        # save backup file
        # if flag was raised -> overwrite the current .log file with only this year's logs

        # get current year
        current_year = self.sc.today()[0:4] # "2024"

        # for each PART_NUMBER in database
        for part_number, logs in self.database.items():

            # for each LOG
            backup = {}
            current_log = []
            overwirte = False
            for log in logs:
    
                # set variables
                year = log[1]
                log_data = log[5]

                # save data to log
                if year != current_year:
                    if year != "":
                        if not year in backup:
                            backup[year] = []
                        backup[year].append(log_data)
                        overwirte = True
                else:
                    current_log.append(log_data)
            
            # save backups
            for year, logs in backup.items():
                group = self.groups[part_number]
                path = self.main_path+"/"+group+"/"+part_number+"/"+year+".backup"
                if not os.path.isfile(path):
                    self.sc.print(" - Creating backup file: "+part_number+" "+year)
                    file = open(path, 'w')
                    for log in logs:
                        for line in log:
                            file.write(line)
                    file.close()
            
            # overwrite current log if it contains last years data
            if overwirte:
                path = self.main_path+"/"+group+"/"+part_number+"/"+part_number+".lot"
                self.sc.print(" - Overwriting file: "+part_number+".lot to have only logs from "+current_year)
                file = open(path, 'w')
                for log in current_log:
                    for line in log:
                        file.write(line)
                file.close()
                backpath = self.main_path+"/"+group+"/"+part_number+"/"+part_number+".bak"
                if os.path.isfile(backpath):
                    os.remove(backpath)

    def generate_MPTlinks(self):
        self.sc.print("Updating MPTLINKS...")
        MPTlinksfile = open(self.path_mpt_links, 'w')
        for link in self.mptlinks:
            PartNumber = link[0]
            Group = link[1]
            path_to_mpt_file = link[2]
            Rev = self.get_rev(path_to_mpt_file)
            path_to_mpt_file = path_to_mpt_file.replace("/", "\\")
            MPTlinksfile.write(PartNumber+".Description="+Rev+"\n")
            #MPTlinksfile.write(PartNumber+".Description="+PartNumber+"\n")
            MPTlinksfile.write(PartNumber+".LinkGroup="+Group+"\n")
            MPTlinksfile.write(PartNumber+"="+path_to_mpt_file+"\n")
            #self.sc.print("Added MPT link: "+PartNumber)
        MPTlinksfile.close()
    
    def get_rev(self,path):
        # set default result
        result = "[!] Failed to find software part number"

        # read txt file
        path = path.replace(".mpt",".txt")
        rev = ""
        sw = ""
        if os.path.isfile(path):
            file = open(path, 'r')
            lines = file.readlines()
            file.close()
            
            # read each line to find the relevant rev
            rev = ""
            sw = ""
            for line in lines:
                # get wire diagram rev
                if "Wire Diagram".upper() in line.upper():
                    if rev == "":
                        rev = line.upper()
                
                # get SW part Number
                if "SW part Number".upper() in line.upper():
                    if sw == "":
                        sw = line.upper()

            # if a revision was found extract it from file
            if "REV" in rev:
                rev = rev.split("REV")
                rev = rev[1]
                rev = re.sub(r'[^a-zA-Z0-9]', '',rev)
                rev = rev.strip()

            if ":" in sw:
                sw = sw.split(":")
                sw = sw[1]
                sw = sw.strip()

        if sw != "":
            result = sw+" REV.:"+rev
            
        return result

main()
