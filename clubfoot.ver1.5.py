import tkinter as tk
from datetime import date
import random
import time
import sys
from datetime import datetime
from tkinter.filedialog import asksaveasfile
from threading import Thread
from serial import *

# Defines Serial Ports
port_arduino = 'COM3' 
port_loadcell = 'COM7'

# Serial data from singletact is ordered by addresses.
# This variable maps the output from the single tact to the physical locations
map_sensors = [0, 1, 2, 3, 4, 5, 10, 6, 7, 11, 13, 9, 8, 12]
sensor_limit = [7.5*160, 7.5*160, 7.5*160, 25*160, 25*160, 25*160, 600, 600, 600, 600, 600, 600, 600, 600]
sensor_yellow = [value * 0.8 for value in sensor_limit]
sensor_red = [value * 0.95 for value in sensor_limit]

# Initialization
labels = [ # Prompts for user information
    "Last Name:",
    "First Initial:",
    "Date of Birth (mm/dd/yyyy):"
    ] 

pi_entries = [] # Creating empty list for entries in Patient Info
pi_data = ['','','',''] # Creating empty list for data in Patient Info
dc_entries = []
sclabels = [ # Labels for sensors in Sensor Calibration
    "Fx",
    "Fy",
    "Fz",
    "Mx",
    "My",
    "Mz",
    "F5",
    "F1",
    "F2",
    "F6",
    "F8",
    "F4",
    "F3",
    "F7"]

numbers = [ # Column numbers for sensors/labels in Sensor Calibration
    1,
    3,
    4,
    6
    ]

dclabels = [ # Labels for data collection
    "Number of Trials:",
    "Length of Trials [sec]:",
    "Sample rate [#/sec]:" ]
trialNumber = -1
trials_list = [ "Trial 1", "Trial 2", "Trial 3", "Trial 4", "Trial 5", "Trial 6", "Trial 7", "Trial 8", "Trial 9", "Trial 10"]
x = 1
j= -1
numberTrialEntry = 0
lengthTrialEntry = 0
sampleRateEntry = 0

# Defining Window
window = tk.Tk() # Creating window
window.title("Clubfoot Data Collection") # Titling window
window.geometry("800x480")
FILENAME = ''
last_received = ''
tare = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
tare = str(tare)[1:-1] # Removes square brackets from list converted to str

# Data collection variables
trials = 0
totalTime = 0
sample_rate = 5
current_trial = 0
TRIAL_DONE = 0


def serialSetup():
    '''
    Initailizes the serial port using pyserial. Also defines the baud rate.

    Returns: lcPort and arduinoPort
    '''
    # Loads the Load Cell Serial port
    lcPort = Serial(port_loadcell, 9600)
    lcPort.write(bytes('CD A\r','utf-8'))
    lcPort.write(bytes('CD R\r','utf-8'))
    lcPort.write(bytes('QS\r','utf-8'))

    # Loads Arduino Serial port
    arduinoPort = Serial(port_arduino, 57600)
    return lcPort, arduinoPort

# Get sensor data at this moment. 
def receiving(ser_ard, ser_lc):
    '''
    Retrieves sensor data.

    Args: ser_ard (serial port of ardunio) and ser_lc (serial port of load cell)
    '''
    global last_received

    buffer_string_ard = ''
    buffer_string_lc = ''
    while True:
        buffer_string_ard = buffer_string_ard + ser_ard.read(ser_ard.inWaiting()).decode(errors = "replace")
        buffer_string_lc = buffer_string_lc + ser_lc.read(ser_lc.inWaiting()).decode(errors = "replace")
        if ('\n' in buffer_string_ard) and ('\n' in buffer_string_lc):
            lines_ard = buffer_string_ard.split('\n') # Guaranteed to have at least 2 entries
            lines_lc = buffer_string_lc.split('\n') # Guaranteed to have at least 2 entries
            last_received_ard = lines_ard[-2]
            last_received_lc = lines_lc[-2].replace(' ','')
            last_received_lc = last_received_lc.strip('\r')
            
            last_received_buffer =   last_received_lc + "," + last_received_ard
            last_received = last_received_buffer  
            buffer_string_lc = lines_lc[-1]    


def writeFileHeader():
    '''
    Writes data to a file. 
    '''
    if pi_data != []:
        file = open(FILENAME,"w")
        file.write('Last Name, First Initial, DOB, Notes \n')
        for entry in pi_data:
            file.write(entry)
            file.write(',')
        file.write('\n')
        file.write('Number of Trials: ,' + trials + '\n')
        file.write('Length of Trials [sec]:, ' + totalTime + '\n')
        file.write('Sample rate [#/sec]:, ' + sample_rate + '\n')
        file.write('Sensor offset:,' + tare)
        file.write('\n')
        file.close()


def frame1():
    '''Initalizes patient info window.'''
    global FILENAME
    
    frm_form = tk.Frame(window, relief=tk.RAISED, borderwidth = 7) # Master frame for pi
    frm_form.pack(fill="both", expand = True) # Putting frame in grid
    frm_title = tk.Button(master = frm_form, text = "Patient Information", pady = 5, width = 20) # Titling frame
    frm_title.grid()
    
    # Create Demographic info area
    pi_entries.clear() # Ensuring pi_entries is clear so data doesn't get overwritten if frame is run through again
    for idx, text in enumerate(labels): # Loop through label list
        label = tk.Label(master=frm_form, text=text) # Creating labels using text from the list, labels
        entry = tk.Entry(master=frm_form, width=50) # Creating entries for each label
        label.grid(row=idx + 1, column = 0, sticky = 'w', padx = 10, pady = 15) # Putting each label in grid to the west with padding for space 
        entry.grid(row=idx + 1, column = 1, sticky = 'w', padx =10, pady = 15) # Putting each entry one column to the right of label in grid to the west with padding for space
        pi_entries.append(entry) # Adding each entry to pi_entries list
        
    # Create Notes area
    notelabel = tk.Label(master=frm_form, text = "Notes:") # Creating prompt for text box
    notelabel.grid(row=4, column = 0, sticky = 'w', padx = 10, pady = 15) # Putting prompt in grid below the labels and entries  
    notes = tk.Text(master = frm_form, width = 108, height = 9, bg = "mistyrose", padx = 10) # Creating text box
    notes.grid(row = 5, columnspan = 2) # Putting text in grid below all previous elements
    pi_entries.append(notes) # Adding text box to pi_entries list (which will be used to convert and write info to a file)

    
    def leave():
        '''To leave pi frame.'''
        global FILENAME
         
        for i in range (3): # Looping through 3 entries
            entry_str = pi_entries[i].get() # Getting each entry from the pi_entries list as a string
            pi_data[i] = entry_str # Appending each entry into pi_data list    
        pi_data[3] = (pi_entries[3]).get("1.0", "end-1c")# Appending text into data list
        if (pi_data[0] == '' or pi_data[1] == ''):
            error_msg = tk.Label(master = frm_form, text = "Last Name and First Initial are Required.", bg = "red")
            error_msg.grid(row = 15)
        else:
            today = date.today()
            FILENAME = pi_data[0] + '_' + pi_data[1][0] + '_' + (today.strftime("%d_%m_%Y")) + '.csv'
            # Hid all elements of frame from view
            for widgets in frm_form.winfo_children(): # Hide all widgets in frame
                widgets.destroy()
            frm_form.pack_forget()
            creatingscframe() # Calling next frame (sc)
            
            
    btn_save = tk.Button(frm_form, text = "Save and Go To Sensor Calibration", command = leave, padx= 5, pady= 15) # Creating button
    btn_save.grid(row = 7, columnspan = 2) # Placing button beneath all other elements
        


def creatingscframe():
    '''Initalizes Sensor Calibration Window'''
    global last_received

    values = []
    label = []
    scframe = tk.Frame(window, relief=tk.RAISED, borderwidth = 7) # Master sensor calibration frame
    scframe.pack(fill = "both", expand = True)
    
    scframe_label = tk.Label(master = scframe, text = "Live Data:") # Creating label for Live Data
    scframe_label.grid(row = 1)
    

    window.imag1 = tk.PhotoImage(file="leftfoot.png")
    labelimg = tk.Label(scframe, image = window.imag1)
    labelimg.grid(row=7, column=2)
    
    window.imag2 = tk.PhotoImage(file="rightfoot.png")
    labelimg = tk.Label(scframe, image = window.imag2)
    labelimg.grid(row=7, column=5)

    for idx, text in enumerate(sclabels): # Looping through labels in SC
        number = 0 # Generating random # just for draft
        frame = tk.Frame(
            master=scframe,
            relief=tk.RAISED,
            width= 70,
            height= 70)
        label.append(tk.Label(master = frame, text = number))

        if idx < 6: # First set of sensors
            label[idx].pack(fill = "both", expand = True, ipadx = 10, ipady = 10)
            frame.grid(row = 0, column = idx + 1, padx = 10, pady = 10) 
            sclabel = tk.Label(master= scframe, text=text) # Creating labels using text from the list, sclabels
            sclabel.grid(row=1, column = idx + 1, padx = 10, pady = 10) # Adding sclabels below frames

        if idx > 5:
            label[idx].pack(fill = "both", expand = True, ipadx = 10, ipady = 10)
            sclabel = tk.Label(master = scframe, text = text)# Creating labels using text from the list, sclabels

            if 5 < idx < 10: 
                frame.grid(row = 3, column = numbers[idx-7], padx = 10, pady = 10) # Putting first line of the F# frames above the images
                sclabel.grid(row=4, column = numbers[idx-7], padx = 10, pady = 10) # Putting corresponding labels below frames
            else:
                frame.grid(row = 8, column = numbers[idx-11], padx = 10, pady = 10) # Putting second line of the F# frames below the images
                sclabel.grid(row= 9, column = numbers[idx-11], padx = 10, pady = 10) # Corresponding labels below frames


    def backColor(value, index):
        '''
        Defines the background color of data box.

        Args: value (Sensor Data) and index
        '''
        if abs(value) > sensor_red[index]:
            color = '#C82538' #red
        elif abs(value) > sensor_yellow[index]:
            color = '#E6CC00' #yellow
        else: 
            color = '#2E7F18' #green
                
        return color
        

    def update():
        '''
        Updates window with most recent values.
        '''
        number_list = last_received.split(",") # Creates a list of number from csv line
        del number_list[0] # Deletes the leading 0 from the loadcell
        for idx in range(14):
            sensorValue = float(number_list[map_sensors[idx]]) - tare[idx]
            addSpace = 5 - len(str(sensorValue))
            label[idx].config(text = " "*addSpace + str(sensorValue))
            label[idx].config(font = "Courier", bg = backColor(sensorValue,idx))
        window.after(1000,update)


    def goback():
        '''
        Exits back to pi window.

        Calls: frame1()
        '''
        for widgets in scframe.winfo_children(): # Next 5 lines hide all visible elements on scframe 
            widgets.grid_forget()
        scframe.pack_forget()
        
        frame1() # Calling PI function
        

    def goto():
        '''
        Goes to next frame.

        Calls: datacollection()
        '''
        for widgets in scframe.winfo_children(): # Next 5 lines hide all visible elements on scframe
            widgets.grid_forget()
        scframe.pack_forget()
        
        datacollection()


    def calibrate():
        '''
        Calibrates Sensors.
        '''
        global tare
        tare = last_received.split(",")
        tare = list(map(float, tare))


    # Defines Buttons
    scframe_title = tk.Button(master = scframe, text = "Zero Sensor", command = calibrate,pady = 10, width = 20) # Titling frame
    scframe_title.grid(row = 0)   
    btn_return = tk.Button(scframe, text = "Back", command = goback, padx=5, pady=10) # Creating button
    btn_return.grid(row = 10, columnspan = 2) # Placing button beneath all other elements
    btn_goto = tk.Button(scframe, text = "Go To", command = goto, padx=5, pady=10) # Creating button
    btn_goto.grid(row = 10, column = 5) # Placing button beneath all other elements
    update()
                   
def datacollection():
    '''
    Saves data from serial ports.
    '''
    def collect():
        global trialNumber, TRIAL_DONE
        global trials, totalTime, sample_rate
        trials = dc_entries[0].get()
        totalTime = dc_entries[1].get()
        sample_rate = dc_entries[2].get()
        writeFileHeader()
        trialWindow = tk.Tk()
        trialWindow.geometry("300x300")
        trialWindow.title("Trial Number")
        time_frame = tk.Frame(
            master = trialWindow,
            relief = tk.RAISED,
            width=100,
            height=100,
            bd = 3,
            bg = "pink"
        )
        time_frame.grid(padx = 10, pady = 10)
        time_label = tk.Label(master = time_frame, text = "Time Elapsed", padx = 5, pady = 5, bg = "pink")
        time_label.grid(sticky = "n")
        trialLabel = tk.Label(master = trialWindow, text = 'Ready to begin')
        trialLabel.grid()
        trialNumber = 0
        
        def complete():
            trialWindow.destroy()
        
        def timed_collection():
            global trialNumber
            trialNumber += 1

            trialLabel.config(text = trials_list[trialNumber - 1] + " of " + str(numberTrialEntry))
            file = open(FILENAME,"a")
            file.write('\nTRIAL' + str(trialNumber) + '\n')
            file.close()
            window.update_idletasks() #refreshing loop each time
            window.update()

            trialStartTime = time.perf_counter()
            elapsedTime = 0.0
            
            while ( elapsedTime < lengthTrialEntry):
                window.update_idletasks() #refreshing loop each time
                window.update()
                elapsedTime = int((time.perf_counter() - (trialStartTime))*(10**3))/(10**3)
                file = open(FILENAME,"a")
                file.write(str(elapsedTime) + ',' + last_received )
                file.close()
                elapsed_label.config(text = str(elapsedTime))
                sampleStartTime = time.perf_counter()
                while (time.perf_counter() - sampleStartTime) < (1/sampleRateEntry):
                    pass 
            elapsed_label.config(text = 'Ready for next trial')
            
        
        
        complete_button = tk.Button(trialWindow, text = "Complete Data Collection", padx = 10, pady = 15, command =complete)
        start_button = tk.Button(trialWindow, text = "Start Trial", padx = 10, pady = 15, command = timed_collection)
        complete_button.grid(row = 3)
        start_button.grid(row = 2)
        
        global numberTrialEntry, lengthTrialEntry, sampleRateEntry
        numberTrialEntry = int(dc_entries[0].get())
        lengthTrialEntry = int(dc_entries[1].get())
        sampleRateEntry = int(dc_entries[2].get())
        
        elapsed_label = tk.Label(master = time_frame, text = "0 sec", width = 20, padx = 10, pady = 10, bd = 3)
        elapsed_label.grid(column = 0 , row = 6)
        
    def exit_command():
        window.destroy()
    

    dataframe = tk.Frame(window, relief = tk.RAISED, borderwidth = 7) # Master frame for dc
    
    dataframe_title = tk.Button(master = dataframe, text = "Data Collection", height = 2, width = 20) # Titling frame
    
    saveframe = tk.Frame(dataframe, relief = tk.RAISED, borderwidth = 5, padx = 5, pady = 5) # Creating a frame for saving information about file
    
    as_label = tk.Label(master=saveframe, text="Save As: ") # Creating label to name file (save as)
    as_entry = tk.Entry(master=saveframe, width=20) # Creating entries for label
    as_entry.insert(0,FILENAME)

    dataframe.pack(fill = "both", expand = True)
    dataframe_title.grid(padx = 5)
    saveframe.grid(row = 4, column = 2) # Placing saveframe to the right of all items
    as_label.grid(sticky = 'w', padx = 10, pady = 5) # Putting the label in grid to the west with padding for space 
    as_entry.grid(padx = 10, pady = 5) # Putting entry below the label
    
    patinfoframe = tk.Frame(dataframe, relief = tk.RAISED, borderwidth = 5) # Frame for info from PI
    patinfoframe.grid(row = 0, column = 2, rowspan = 3, ipadx = 50, ipady= 15, padx= 5, pady = 5)
    patinfotitle = tk.Button(patinfoframe, text = "Patient Information", padx =10, pady = 10) # Fisplaying info from PI
    patinfotitle.grid()
    patname_label = tk.Label(patinfoframe, text = (pi_data[1][0] + "." + pi_data[0])) # Giving firstinitial.lastname from PI
    patname_label.grid(padx =10, pady = 10, sticky = 'w')
    dob_label = tk.Label(patinfoframe, text = ("DOB: " + pi_data[2])) # Date of birth from PI
    dob_label.grid(padx =10, pady = 10, sticky = 'w')
    notes_label = tk.Label(patinfoframe, text = ("Notes: " + pi_data[3])) #Notes from PI
    notes_label.grid(padx =10, pady = 10, sticky = 'w')
    
    for idx, text in enumerate(dclabels): # Loop through label list
        dclabel = tk.Label(master=dataframe, text=text) # Creating labels using text from the list, labels
        dcentry = tk.Entry(master=dataframe, width=30) # Creating entries for each label
        dclabel.grid(row=idx + 1, column = 0, sticky = 'w', padx = 5, pady = 10) # Putting each label in grid to the west with padding for space 
        dcentry.grid(row=idx + 1, column = 1, sticky = 'w', padx = 5, pady = 10) # Putting each entry one column to the right of label in grid to the west with padding for space
        dc_entries.append(dcentry) # Adding each entry to pi_entries list
    
    collect_button = tk.Button(master = dataframe, text = "COLLECT DATA", command = collect, padx = 10, pady = 10, width = 10)
    collect_button.grid(row = 4, column = 0)
    exit_button = tk.Button(master = dataframe, text = "EXIT", command = exit_command, padx = 10, pady = 10, width = 10)
    exit_button.grid(row = 4, column = 1)
    

def datareview():
    datareview = tk.Frame(window,relief = tk.RAISED, borderwidth = 7) # Master frame for datareview
    datareview.grid()
    datareview_title = tk.Button(master = datareview, text = "Data Review", pady = 5, width = 20) # Titling frame
    datareview_title.grid()
    
    
lc, ard = serialSetup()
Thread(target=receiving, args=(ard,lc,)).start() # Start reading from serial.

frame1() # Calling first function/frame
window.mainloop() # Finishing loop
sys.exit()