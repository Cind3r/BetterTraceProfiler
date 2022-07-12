import csv
from collections import Counter
from email import parser
from pdb import line_prefix
import re
import tkinter
from tkinter import filedialog
from tkinter.filedialog import asksaveasfilename
from typing import List 
from numpy import empty
from pyparsing import line_start

class parserObj:

    def __init__(self, *args, **kwargs):
        """
        Parser Object is the main class which will return the parsed MOCA trace file with information you select through methods. 

        Attributes:
            - regexp        -> multiple regex expressions predefined based on structure of trace file
            - filepath      -> local path to log file
            - line_index    -> self explanatory

        Methods:
            - parselog()    -> will preform the request to upload, parse, and download sequences. Needs type specification
            - fileselect()  -> adds local file path to class object, used in parselog
            - savelogfile() -> creates a local file which then appends the parsed log data to 
            - grabber()     -> main method for parsing the logfile
        """
        # Define regular expressions for MOCA trace files to parse
        
        # Date/Time & OP id that appears in the log file. These are mainly for removing excess text and are used most frequently 
        self.regexp_dt = re.compile(r'\d{1,4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2},\d{1,3} DEBUG \[\w{1,4} \w{1,4}\]')
        self.regexp_id = re.compile(r'\[\w{5,16} \w{5,16}\]')
        
        # SQL statements, DSC lines, and Error messages
        self.regexp_sql = r'(?=Executing SQL)[\S\s]*?(?=SQL execution completed)'
        self.regexp_sqlt = r'(?=\[\d{1,9999999}\] Executing SQL)[\S\s]*?(?=SQL execution completed)'
        self.regexp_dsc = r'DefaultServerContext .* [\S\s]*?'
        self.regexp_cmd = r'CommandDispatcher .* [\S\s]*?'
        self.regexp_cmd = r'Argument .* [\S\s]*?'
        self.regexp_err = r'ERROR .* [\S\s]*?'

        # Optional user input for regex, mainly for testing purposes
        self.regexp_cus = r''

        # This is for indexing purposes, to point towards the lines it grabbing 
        self.line_ids= dict()
        self.outlog = []

        # This is the file path for the log, ideally on the local system
        self.filepath = ''


    def fileselect(self,**kwargs):
        # Open dialogue box to have user select the file, withdraw() prevents blank tkinter canvas
        tkinter.Tk().withdraw()
        self.filepath = filedialog.askopenfilename(filetypes=[("Log File","*.log"),("Text Documents","*.txt")])
          
    

    def grabber(self, type=str):

        """
        This function is the main parser for quick information. It will not return line indicies that correlate with 
        the gathered information. That has to be done by looping through each line, rather than doing a read().

        Accepted type arguments: 'SQL', 'DSC', 'ERR', 'CUS'
        """

        # Get log file
        if self.filepath is empty:
            self.fileselect()

        match type:

            case "SQL":
                with open(self.filepath) as fObject:

                    log = fObject.read()
                    
                    # remove date/time information from beginning of each line
                    slog = self.regexp_dt.sub('',log)

                    # remove the tagging brackets from the end of each line
                    slog = self.regexp_id.sub('', slog)

                    # collect all the SQL statements performed in the file
                    outlog = re.findall(self.regexp_sql, slog)
                    
                    return outlog

            case "DSC":
                with open(self.filepath) as fObject:

                    log = fObject.read()
                    
                    # remove date/time information from beginning of each line
                    slog = self.regexp_dt.sub('',log)
                    
                    # remove the tagging brackets from the end of each line
                    slog = self.regexp_id.sub('', slog)

                    # collect all the DSC statements performed in the file
                    outlog = re.findall(self.regexp_dsc, slog)
                    
                    return outlog

            case "ERR":
                with open(self.filepath) as fObject:

                    log = fObject.read()
                    
                    # remove date/time information from beginning of each line
                    slog = self.regexp_dt.sub('',log)
                    
                    # remove the tagging brackets from the end of each line
                    slog = self.regexp_id.sub('', slog)

                    # collect all the error statements in the file
                    outlog = re.findall(self.regexp_err, slog)

                    return outlog

            case "CMD":
                with open(self.filepath) as fObject:

                    log = fObject.read()
                    
                    # remove date/time information from beginning of each line
                    slog = self.regexp_dt.sub('',log)
                    
                    # remove the tagging brackets from the end of each line
                    slog = self.regexp_id.sub('', slog)

                    # collect all the command dispatcher statements in the file
                    outlog = re.findall(self.regexp_cmd, slog)
                    
                    return outlog


            case "ARG":
                with open(self.filepath) as fObject:

                    log = fObject.read()
                    
                    # remove date/time information from beginning of each line
                    slog = self.regexp_dt.sub('',log)
                    
                    # remove the tagging brackets from the end of each line
                    slog = self.regexp_id.sub('', slog)

                    # collect all the arguments in the file
                    outlog = re.findall(self.regexp_cmd, slog)
                    
                    return outlog


            case "CUS":
                with open(self.filepath) as fObject:

                    log = fObject.read()
                    
                    # remove date/time information from beginning of each line
                    slog = self.regexp_dt.sub('',log)
                    
                    # remove the tagging brackets from the end of each line
                    slog = self.regexp_id.sub('', slog)

                    # collect all custom repeating statments in the file
                    outlog = re.findall(self.regexp_cus, slog)
                    
                    return outlog        


            case "NULL":
                with open(self.filepath) as fObject:
                    # do nothing (test param)
                    log = fObject.read()
                    return log   
    

    def grouper(self):

        """
        This method groups the id's for MOCA log files, as well as assigns it to the line number in 
        which the id first appears. Example id: [4b174f107297261a dce6436fde737e60]

        This is how MOCA identifies areas of code being 'related by action'

        """

        # Get log file
        if self.filepath is empty:
            self.fileselect()

        # Open the log file and grab all row id's
        with open(self.filepath) as fObject:

            log = fObject.read()
                            
            log = re.sub(self.regexp_dt,'', log)

            outlog = re.findall(self.regexp_id,log)

            # this will grab all the unique row ids
            outlog_unique = set(outlog)

            # Create a dictionary so we can later assign it STARTING indexes 
            self.line_ids = self.line_ids.fromkeys(outlog_unique,0)

        # Temp array to store each line in the file to compare against regex. This is sadly the 
        # best way I could find to do it. I'm sure there is a more effecient way but I could 
        # not find one right now. 
        logf = []

        with open(self.filepath) as lObject:
            
            # Store the temp array with each line
            for line in lObject:
                logf.append(line)

            # Compare the line to our id regex, grab the string through .group() from the search object
            for i, line in enumerate(logf):
                match = re.search(self.regexp_id,line)
                if match is not None:
                    logf[i] = match.group()
                else:
                    logf[i] = ''    # None type object do not have .group() method, this prevents it from breaking

            # Grab the first time each unique id appears using the .index() method
            for id in outlog_unique:
                self.line_ids[id] = logf.index(id)

            # Sort the dictionary by values for simple iteration later
            self.line_ids = sorted(self.line_ids.items(), key=lambda x: x[1])


    def count(parsedLog=List):
        # This is error counting operations
        return Counter(parsedLog)

    def get_line_count(self):
        # This is for assigning row indexes for when preforming more complex parsing operations
        with open(self.filepath,'r') as f:
            num_lines = sum(1 for line in f)
            f.seek(0)
        line_id = [0]*num_lines
        return line_id
        
    def savelogfile(self, edited_log):

        # Again, just to make sure that it doesn't pop up    
        tkinter.Tk().withdraw()
        f = asksaveasfilename(initialfile = 'Untitled', defaultextension=".log",filetypes=[("Log File","*.log"),("Text Documents","*.txt")])
        
        # This is for writing the log file to local storage
        with open(f, 'w') as lObject:
            for item in edited_log:
                lObject.write(item + "\n")

            
    def clrcache(self):
        # for clearing cache if it gets out of hand
        re.purge()

    def print_message(*args):
            print(*args)

    def parselog(self, type=str, *args, **kwargs):

        """
        This is the main method for preforming the parsing operations. Calling this will preform all the other 
        methods in the correct order, including prompt for selecting a file and saving a file. 

        Required: type -> 'SQL', 'DSC', 'ERR', 'CUS'
            - if 'CUS' is selected, regex is not optional

        Optional: regex -> regular expression in the form r'...', see documentation on 're' for more

        """
        self.regexp_cus = kwargs.get('regex', None)

        # First prompt the user to select a log file to parse
        self.fileselect()

        # Get number of lines
        self.line_index = self.get_line_count()

        # Next, preform the chosen parsing style
        if type == 'CUS':
            lof = self.grabber(type)
        else:
            lof = self.grabber(type)

        # Finally, preform download sequence, by opening a file and writing
        self.savelogfile(lof)


class errID(parserObj):

    def __init__(self,*args, **kwargs):
        """
        errID is a class specifically dedicated to error identification in the log files. It is a child class of parserObj
        so it inherits the same regex and methods while adding some custom funcionalities of its own. 
        """

        # REGEX specific to the mls id errors that appear in the system
        self.regex_mls_id = r''
        self.log = []

        parserObj.__init__(self,*args,**kwargs)
        

    def __repr__(self) -> str:
        return str(self.log)

    
    def saveCSVfile(self, edited_log):

        # Again, just to make sure that it doesn't pop up    
        tkinter.Tk().withdraw()
        f = asksaveasfilename(initialfile = 'Untitled', defaultextension=".csv",filetypes=[("Comma Separated Values","*.CSV"),("Text Documents","*.txt")])
        
        # This is for writing the log file to local storage
        with open(f, 'w') as csvObject:
            writer = csv.writer(csvObject)
            writer.writerow(['Error', 'Frequency'])
            for item in Counter:
                writer.writerow((item, Counter[item]))

    
    def getErrors(self):
        
        """
        This is the main method for preforming error counting. Select a file when prompted and then save to CSV. The CSV will
        contain the main error information. 

        """
       

        # First prompt the user to select a log file to parse
        self.fileselect()

        # Get number of lines
        self.line_index = self.get_line_count()

        log = self.grabber("ERR")

        # Preform CSV file operation and save
        self.saveCSVfile()



