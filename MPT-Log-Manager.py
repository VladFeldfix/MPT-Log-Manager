# Download SmartConsole.py from: https://github.com/VladFeldfix/Smart-Console/blob/main/SmartConsole.py
from SmartConsole import *
import shutil

class main:
    # constructor
    def __init__(self):
        # load smart console
        self.sc = SmartConsole("MPT Log Manager", "2.0")

        # set-up main memu
        self.sc.add_main_menu_item("RUN", self.run)

        # get settings
        self.main_path = self.sc.get_setting("MPT Folder")
        self.main_path = self.main_path.replace("\\", "/")
        self.path_test_results = self.sc.get_setting("Test Results")
        self.path_mpt_links = self.sc.get_setting("Mpt links")

        # test all paths
        self.sc.test_path(self.main_path)
        self.sc.test_path(self.path_test_results)
        self.sc.test_path(self.path_mpt_links)

        # display main menu
        self.sc.start()

    def run(self):
        self.sc.print("Loading...")

        # global vars
        self.Current_year = self.sc.today()[0:4] # "2024"
        self.Products = [] # [Group,PartNumber]
        self.Logs = [] # a list of [group, part_number, date_code, serial_number, passed, [log_data], year]
        self.Backups = {} # a dict of {group_partnumber_year: [list_of_logs]]
        self.mptlinks = []
        self.csvFiles = []
        self.TextFiles = []
        
        # run commands
        self.create_list_of_products()
        self.read_log_files()
        self.generate_test_reports()
        self.backup_logs()
        self.generate_MPTlinks()
        self.sc.restart()
    
    def create_list_of_products(self):
        self.sc.print("Loading products list")
        for root, dirs, files in os.walk(self.main_path):
            root = root.replace("\\", "/")
            root = root.replace(self.main_path, "")
            root = root.split("/")
            if len(root) == 3:
                group = root[1]
                part_number = root[2]
                if part_number != "__HTML__":
                    self.Products.append([group, part_number])

    def read_log_files(self):
        self.sc.print("Reading log files")
        for data in self.Products:
            # product data
            group = data[0]
            part_number = data[1]
            path_to_lot_file = self.main_path+"/"+group+"/"+part_number+"/"+part_number+".lot"
            path_to_mpt_file = self.main_path+"/"+group+"/"+part_number+"/"+part_number+".mpt"
            path_to_txt_file = self.main_path+"/"+group+"/"+part_number+"/"+part_number+".txt"
            path_to_csv_file = self.main_path+"/"+group+"/"+part_number+"/"+part_number+".csv"
            
            # mpt links
            if os.path.isfile(path_to_mpt_file):
                self.mptlinks.append((part_number, group, path_to_mpt_file))

            # csv links
            if os.path.isfile(path_to_csv_file):
                self.csvFiles.append((part_number, path_to_csv_file))

            # txt links
            if os.path.isfile(path_to_txt_file):
                self.TextFiles.append((part_number, path_to_txt_file))
            
            # read data from each log file
            if os.path.isfile(path_to_lot_file):
                # open file
                lotfile = open(path_to_lot_file, 'r')
                lines = lotfile.readlines()
                lotfile.close()
                
                # analyze each line
                date_code = ""
                serial_number = ""
                passed = False
                log_data = []
                year = ""
                ignore_line = False
                for line in lines:
                    # start a new log
                    if "+---------------------------------+" in line:
                        if not ignore_line:
                            if year != "":
                                self.Logs.append([group, part_number, date_code, serial_number, passed, log_data, year])
                                log_data = []
                                passed = False
                                year = ""
                        ignore_line = not ignore_line

                    # get date_code
                    if "LOT NUMBER" in line.upper():
                        date_code = line.split(":")
                        date_code = date_code[1].replace("|", "")
                        date_code = date_code.strip()
                        year = date_code[-4:]
                    
                    # get serial number
                    if "SERIAL NUMBER" in line.upper():
                        serial_number = line.split(":")
                        serial_number = serial_number[1].strip()
                    
                    # get test result
                    if "TEST PASSED" in line.upper():
                        passed = True
                    
                    # save line
                    log_data.append(line)
                self.Logs.append([group, part_number, date_code, serial_number, passed, log_data, year])

    def generate_test_reports(self):
        self.sc.print("Generating test reports")
        # text files
        for txt in self.TextFiles:
            part_number = txt[0]
            scr = txt[1]
            folder = self.path_test_results+"/"+part_number
            save = folder+"/"+part_number+".txt"
            if not os.path.isdir(folder):
                os.makedirs(folder)
            if os.path.isfile(save):
                os.remove(save)
            shutil.copy(scr, save)
        
        # csv files
        for csv in self.csvFiles:
            part_number = csv[0]
            scr = csv[1]
            folder = self.path_test_results+"/"+part_number
            save = folder+"/"+part_number+".csv"
            if not os.path.isdir(folder):
                os.makedirs(folder)
            if os.path.isfile(save):
                os.remove(save)
            shutil.copy(scr, save)

        # html log files
        for log in self.Logs:
            # get log data
            group = log[0]
            part_number = log[1].upper()
            part_number = self.filter(part_number)
            date_code = log[2].upper()
            serial_number = log[3].upper()
            serial_number = self.filter(serial_number)
            passed = log[4]
            log_data = log[5]
            year = log[6]
            
            # save HTML file
            if passed and group != "" and part_number != "" and date_code != "" and serial_number != "":    
                path = self.path_test_results+"/"+part_number
                path_to_html_file = path+"/"+serial_number+"_"+date_code+"_"+part_number+".html"
                if not os.path.isfile(path_to_html_file):
                    if not os.path.isdir(path):
                        os.makedirs(path)
                    # generate html file
                    htmlfile = open(path_to_html_file, 'w')
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
                    self.sc.print(serial_number+" "+date_code+" "+part_number)

            # save backup
            key = self.main_path+"/"+group+"/"+part_number+"/"+year+".backup"
            if not key in self.Backups:
                self.Backups[key] = []
            self.Backups[key].append(log)

    def backup_logs(self):
        self.sc.print("Generating .backup files")
        previous_path = ""
        save = ""
        for path, logs in self.Backups.items():
            for log in logs:
                # get log data
                group = log[0]
                part_number = log[1].upper()
                part_number = self.filter(part_number)
                date_code = log[2].upper()
                serial_number = log[3].upper()
                serial_number = self.filter(serial_number)
                passed = log[4]
                log_data = log[5]
                year = log[6]
                for line in log_data:
                    save += line
            if previous_path != path:
                if year == self.Current_year:
                    path = self.main_path+"/"+group+"/"+part_number+"/"+part_number+".lot"
                backupFile = open(path, 'w')
                backupFile.write(save)
                backupFile.close()
                save = ""
                previous_path = path
                backpath = self.main_path+"/"+group+"/"+part_number+"/"+part_number+".bak"
                if os.path.isfile(backpath):
                    os.remove(backpath)
            
    def generate_MPTlinks(self):
        self.sc.print("Updating MPTLINKS")
        MPTlinksfile = open(self.path_mpt_links, 'w')
        for link in self.mptlinks:     
            PartNumber = link[0]
            Group = link[1]
            path_to_mpt_file = link[2]
            path_to_mpt_file = path_to_mpt_file.replace("/", "\\")
            MPTlinksfile.write(PartNumber+".Description="+PartNumber+"\n")
            MPTlinksfile.write(PartNumber+".Description="+PartNumber+"\n")
            MPTlinksfile.write(PartNumber+".LinkGroup="+Group+"\n")
            MPTlinksfile.write(PartNumber+"="+path_to_mpt_file+"\n")
            #self.sc.print("Added MPT link: "+PartNumber)
        MPTlinksfile.close()

    def filter(self, txt):
        txt = txt.upper()
        txt = txt.strip()
        return_value = ""
        AllowedChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ "
        for ch in txt:
            if ch in AllowedChars:
                return_value += ch
        return return_value
main()