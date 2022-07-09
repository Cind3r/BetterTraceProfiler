import csv
from collections import Counter
import re
import tkinter
from tkinter import filedialog
from tkinter.filedialog import asksaveasfilename 
from numpy import empty

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
        self.regexp_id = re.compile(r'\[\w{1,16} \w{1,16}\]')
        
        # SQL statements, DSC lines, and Error messages
        self.regexp_sql = r'(?=Executing SQL)[\S\s]*?(?=SQL execution completed)'
        self.regexp_dsc = r'DefaultServerContext .* [\S\s]*?'
        self.regexp_err = r'ERROR .* [\S\s]*?'

        # Optional user input for regex, mainly for testing purposes
        self.regexp_cus = r''

        # This is for indexing purposes, to point towards the lines it grabbing 
        self.line_index = [0]

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

                    # collect all the sql statements performed in the file
                    outlog = re.findall(self.regexp_sql, slog)
                    
                    return outlog

            case "DSC":
                with open(self.filepath) as fObject:

                    log = fObject.read()
                    
                    # remove date/time information from beginning of each line
                    slog = self.regexp_dt.sub('',log)
                    
                    # remove the tagging brackets from the end of each line
                    slog = self.regexp_id.sub('', slog)

                    # collect all the sql statements performed in the file
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


    def savelogfile(self, edited_log):

        # Again, just to make sure that it doesn't pop up    
        tkinter.Tk().withdraw()
        f = asksaveasfilename(initialfile = 'Untitled', defaultextension=".log",filetypes=[("Log File","*.log"),("Text Documents","*.txt")])
        
        # This is for writing the log file to local storage
        with open(f, 'w') as lObject:
            for item in edited_log:
                lObject.write(item + "\n")

            


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

        # Next, preform the chosen parsing style
        if type == 'CUS':
            lof = self.grabber(type)
        else:
            lof = self.grabber(type)

        # Finally, preform download sequence, by opening a file and writing
        self.savelogfile(lof)
