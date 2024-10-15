# Download SmartConsole.py from: https://github.com/VladFeldfix/Smart-Console/blob/main/SmartConsole.py
from SmartConsole import *
import os
from functions.create_new_product import CreateNewProduct
from functions.gather_data import GatherData
from functions.create_netlist import CreateNetlist
from functions.create_script import CreateScript
from functions.generate_MPTPRODUCT_file import GenerateMPTPRODUCTfile
from functions.generate_HTML_file import GenerateHTMLfile
from functions.failtest import TestData

class MAIN:
    # constructor
    def __init__(self):
        # load smart console
        self.software_rev = "2.4"
        self.sc = SmartConsole("MPT Manager", self.software_rev)

        # set-up main memu
        self.sc.add_main_menu_item("RUN MPT-5000 L", self.RunMPT5000L)
        self.sc.add_main_menu_item("RUN MPT-5000", self.RunMPT5000)

        # get settings
        self.path_to_products = self.sc.get_setting("Programs location")
        self.path_to_testcables = self.sc.get_setting("Maps location")

        # test all paths
        self.sc.test_path(self.path_to_products)
        self.sc.test_path(self.path_to_testcables)

        # display main menu
        self.sc.start()
    
    def RunMPT5000L(self):
        machine = "MPT5000L"
        self.Run(machine)

    def RunMPT5000(self):
        machine = "MPT5000"
        self.Run(machine)
    
    def Run(self, machine):
        # get product name
        product = self.sc.input("Insert PART NUMBER [Without R-]").upper()
        path_to_product = self.path_to_products+"/"+product
        
        # test if product exists. if not, create a new folder and add basic 5 files
        if not os.path.isdir(path_to_product):
            if self.sc.question("No such folder: "+path_to_product+"\nWould you like to create a new folder?"):
                CreateNewProduct(path_to_product, product)
            else:
                self.sc.warning("Mission aborted")
                self.sc.restart()
                return
        # else, start generating program
        else:
            self.sc.print("Gathering data")
            global_data = GatherData(path_to_product) # gather data
            test = TestData(global_data, self.path_to_testcables)
            if not test[0]:
                self.sc.fatal_error(test[1])
            csv_data = CreateNetlist(global_data, self.path_to_testcables) # generate csv file
            if csv_data[0] == "Error":
                self.sc.fatal_error(csv_data[1]+" "+csv_data[2])
            data_from_script = CreateScript(path_to_product, self.software_rev, product, machine)
            txt_data = data_from_script[0]
            program_ver = data_from_script[1]
            diode_list = data_from_script[2]
            
            # for each machine something else
            if machine == "MPT5000L":
                # create CSV file
                self.sc.print("Generating CSV file")
                path_to_csv_file = path_to_product+"/"+product+".csv"
                csv_file = open(path_to_csv_file, 'w')
                for line in csv_data:
                    csv_file.write(line+"\n")
                csv_file.close()

                # create TXT file
                self.sc.print("Generating TXT file")
                path_to_txt_file = path_to_product+"/"+product+".txt"
                txt_file = open(path_to_txt_file, 'w')
                txt_file.write(txt_data)
                txt_file.close()

                # for html
                outlet_size = (50, 3, 8)

            elif machine == "MPT5000":
                # generate mpt_product file
                self.sc.print("Generating MPT_PRODUCT file")
                GenerateMPTPRODUCTfile(global_data, path_to_product, product, program_ver, txt_data, diode_list)

                # for html
                outlet_size = (50, 3, 13)
            
            self.sc.print("Generating HTML file for machine: "+machine+"")
            GenerateHTMLfile(path_to_product, global_data, product, self.path_to_testcables, outlet_size, machine) # generate html file
        
        # done
        self.sc.open_folder(path_to_product)
        self.sc.restart()
MAIN()