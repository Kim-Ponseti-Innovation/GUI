import tkinter as tk #importing tkinter program and renaming as tk
from datetime import date
import random
import time
from datetime import datetime
from tkinter.filedialog import asksaveasfile
from threading import Thread
from serial import *

port_arduino = 'COM3' #name of serial port
port_loadcell = 'COM7'
# stream of data from singletact is ordered by addresses. This variable maps the 
# output from the single tact to the physical locations
map_sensors = [0,1,2,3,4,5,10,6,7,11,13,9,8,12]
sensor_limit = [7.5*160,7.5*160,7.5*160,25*160,25*160,25*160,600,600,600,600,600,600,600,600]
sensor_yellow = [value * 0.8 for value in sensor_limit]
sensor_red = [value * 0.95 for value in sensor_limit]

# Initialization
labels = [ #prompts for user information
    "Last Name:",
    "First Initial:",
    "Date of Birth (mm/dd/yyyy):"
    ] 
pi_entries = [] #creating empty list for entries in Patient Info
pi_data = ['','','',''] #creating empty list for data in Patient Info
dc_entries = []
sclabels = [ #labels for sensors in Sensor Calibration
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

numbers = [ #column numbers for sensors/labels in Sensor Calibration
    1,
    3,
    4,
    6
    ]

dclabels = [ #labels for data collection
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
        
window= tk.Tk() #creating window
window.title("Club Foot Data Collection") #titling window
window.geometry("800x480")
FILENAME = ''
last_received = ''
#ser = Serial(port,57600)
tare = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# Data collection variables
trials = 0
totalTime = 0
sample_rate = 5 # number of samples per second
current_trial = 0
TRIAL_DONE = 0


def serialSetup():
    lcPort = Serial(port_loadcell,9600)
    lcPort.write(bytes('CD A\r','utf-8'))
    lcPort.write(bytes('CD R\r','utf-8'))
    lcPort.write(bytes('QS\r','utf-8'))
    arduinoPort = Serial(port_arduino, 57600)
    #time.sleep(5)
    return lcPort, arduinoPort

# Get sensor data at this moment. 
def receiving(ser_ard, ser_lc):
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
            #print(last_received_ard)
            #print(type(last_received_ard))
            last_received_lc = lines_lc[-2].replace(' ','')
            last_received_lc = last_received_lc.strip('\r')
            
            #print(type(last_received_lc))
            #print(last_received_lc)
            #ard_list = last_received_ard.split(',')
            #lc_list = last_received_lc.split(',')
            #print(ard_list)
            #print(lc_list)
            last_received_buffer =   last_received_lc + "," + last_received_ard
            #print(last_received_buffer)
            last_received = last_received_buffer
            #print(last_received)
            #print('got here in loop')
            #If the Arduino sends lots of empty lines, you'll lose the
            #last filled line, so you could make the above statement conditional
            #like so: if lines[-2]: last_received = lines[-2]
#                buffer_string_ard = lines_ard[-1]    
            buffer_string_lc = lines_lc[-1]    

def writeFileHeader():
    if pi_data != []:
#        today = date.today()
        file = open(FILENAME,"w")
        file.write('Last Name, First Initial, DOB, Notes \n')
        for entry in pi_data:
            #print(entry)
            file.write(entry)
            file.write(',')
        file.write('\n')
        file.write('Number of Trials: ,' + trials + '\n')
        file.write('Length of Trials [sec]:, ' + totalTime + '\n')
        file.write('Sample rate [#/sec]:, ' + sample_rate + '\n')
        file.write('Sensor offset:,' + str(tare))
        file.write('\n')
        file.close()

#def writeDataToFile():
    



def frame1(): # Patient info window
    global FILENAME
    
    frm_form = tk.Frame(window, relief=tk.RAISED, borderwidth = 7) #master frame for pi
    frm_form.pack(fill="both", expand = True) #putting frame in grid
    frm_title = tk.Button(master = frm_form, text = "Patient Information", pady = 5, width = 20) #titling frame
    frm_title.grid()
    
    # Create Demographic info area
    pi_entries.clear() #ensuring pi_entries is clear so data doesn't get overwritten if frame is run through again
    for idx, text in enumerate(labels): #loop through label list
        label = tk.Label(master=frm_form, text=text) #creating labels using text from the list, labels
        entry = tk.Entry(master=frm_form, width=50) #creating entries for each label
        label.grid(row=idx + 1, column = 0, sticky = 'w', padx = 10, pady = 15) #putting each label in grid to the west with padding for space 
        entry.grid(row=idx + 1, column = 1, sticky = 'w', padx =10, pady = 15) #putting each entry one column to the right of label in grid to the west with padding for space
        pi_entries.append(entry) #adding each entry to pi_entries list
        
    # Create Notes area
    notelabel = tk.Label(master=frm_form, text = "Notes:") #creating prompt for text box
    notelabel.grid(row=4, column = 0, sticky = 'w', padx = 10, pady = 15) #putting prompt in grid below the labels and entries  
    notes = tk.Text(master = frm_form, width = 108, height = 9, bg = "mistyrose", padx = 10) #creating text box
    notes.grid(row = 5, columnspan = 2) #putting text in grid below all previous elements
    pi_entries.append(notes) #adding text box to pi_entries list (which will be used to convert and write info to a file)

    
    def leave(): #function to leave pi frame
        global FILENAME
         
        for i in range (3): #looping through 3 entries
            entry_str = pi_entries[i].get() #getting each entry from the pi_entries list as a string
            pi_data[i] = entry_str #appending each entry into pi_data list    
        pi_data[3] = (pi_entries[3]).get("1.0", "end-1c")#appending text into data list
        #print(pi_data)
        if (pi_data[0] == '' or pi_data[1] == ''):
            error_msg = tk.Label(master = frm_form, text = "Last Name and First Initial are Required.", bg = "red")
            error_msg.grid(row = 15)
           
        else:
#            writeFileHeader()
            today = date.today()
            FILENAME = pi_data[0] + '_' + pi_data[1][0] + '_' + (today.strftime("%d_%m_%Y")) + '.csv'
            # hiding all elements of frame from view
            for widgets in frm_form.winfo_children(): #hide all widgets in frame
                widgets.destroy()
            frm_form.pack_forget()
            creatingscframe() #calling next frame (sc)
            
            
    btn_save = tk.Button(frm_form, text = "Save and Go To Sensor Calibration", command = leave, padx= 5, pady= 15) #creating button
    btn_save.grid(row = 7, columnspan = 2) #placing button beneath all other elements
        


def creatingscframe(): #sensor calibration window
    global last_received

    values = []
    label = []
    scframe = tk.Frame(window, relief=tk.RAISED, borderwidth = 7) #master sensor calibration frame
    scframe.pack(fill = "both", expand = True)
    
    scframe_label = tk.Label(master = scframe, text = "Live Data:") #creating label for Live Data
    scframe_label.grid(row = 1)
    

    window.imag1 = tk.PhotoImage(file="leftfoot.png")#"/Users/charles/Downloads/PonsetiProject 2/rightfoot.png")
    labelimg = tk.Label(scframe, image = window.imag1)
    labelimg.grid(row=7, column=2)
    
    window.imag2 = tk.PhotoImage(file="rightfoot.png")#"/Users/charles/Downloads/PonsetiProject 2/rightfoot.png")
    labelimg = tk.Label(scframe, image = window.imag2)
    labelimg.grid(row=7, column=5)


    
    for idx, text in enumerate(sclabels): #looping through labels in SC
        number = 0 #generating random # just for draft
        frame = tk.Frame(
            master=scframe,
            relief=tk.RAISED,
            width= 70,
            height= 70)
        label.append(tk.Label(master = frame, text = number))
        if idx < 6: #first set of sensors
            label[idx].pack(fill = "both", expand = True, ipadx = 10, ipady = 10)
            frame.grid(row = 0, column = idx + 1, padx = 10, pady = 10) 
            sclabel = tk.Label(master= scframe, text=text) #creating labels using text from the list, sclabels
            sclabel.grid(row=1, column = idx + 1, padx = 10, pady = 10) #adding sclabels below frames
        if idx > 5:
            #frame.config(bg = "lightskyblue")
            #label[idx].config(bg = "lightskyblue") #inserting labels w #s inside frames
            label[idx].pack(fill = "both", expand = True, ipadx = 10, ipady = 10)
            sclabel = tk.Label(master = scframe, text = text)#creating labels using text from the list, sclabels
            if 5 < idx < 10: 
                frame.grid(row = 3, column = numbers[idx-7], padx = 10, pady = 10) #putting first line of the F# frames above the images
                sclabel.grid(row=4, column = numbers[idx-7], padx = 10, pady = 10) #putting corresponding labels below frames
            else:
                frame.grid(row = 8, column = numbers[idx-11], padx = 10, pady = 10) #putting second line of the F# frames below the images
                sclabel.grid(row= 9, column = numbers[idx-11], padx = 10, pady = 10) #corresponding labels below frames

    def backColor(value,index):
        if abs(value) > sensor_red[index]:
            color = '#C82538' #red
        elif abs(value) > sensor_yellow[index]:
            color = '#E6CC00' #yellow
        else: 
            color = '#2E7F18' #green
                
        return color
        

    def update():
        number_list = last_received.split(",") # creates a list of number from csv line
        del number_list[0] # deletes the leading 0 from the loadcell
        for idx in range(14):
            sensorValue = int(number_list[map_sensors[idx]]) - tare[idx]
            addSpace = 5 - len(str(sensorValue))
            label[idx].config(text = " "*addSpace + str(sensorValue))
            label[idx].config(font = "Courier", bg = backColor(sensorValue,idx))
        window.after(1000,update)

                
               
            
        
        
    def goback(): #function to go back to PI
        for widgets in scframe.winfo_children(): #next 5 lines hide all visible elements on scframe 
            widgets.grid_forget()
        scframe.pack_forget()
        
        
        frame1() #calling PI function
        
    def goto(): #function to go to next frame (DC)
        for widgets in scframe.winfo_children(): #next 5 lines hide all visible elements on scframe
            widgets.grid_forget()
        scframe.pack_forget()
        
        datacollection()
        
    def calibrate(): # NEED TO FIX THIS!! 5/3/23
        global tare
        tare = last_received.split(",")
        tare = list(map(int, tare))
        

        
        
        
   
    scframe_title = tk.Button(master = scframe, text = "Zero Sensor", command = calibrate,pady = 10, width = 20) #titling frame
    scframe_title.grid(row = 0)   
    btn_return = tk.Button(scframe, text = "Back", command = goback, padx=5, pady=10) #creating button
    btn_return.grid(row = 10, columnspan = 2) #placing button beneath all other elements
    btn_goto = tk.Button(scframe, text = "Go To", command = goto, padx=5, pady=10) #creating button
    btn_goto.grid(row = 10, column = 5) #placing button beneath all other elements

    update()
        

                
def datacollection(): #data collection function

    
    def collect():
        global trialNumber, TRIAL_DONE
        global trials,totalTime,sample_rate
#        FILENAME = as_entry.get() 
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
            file.write('\n TRIAL'+ str(trialNumber)+'\n')
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
        
 
            
        
        
        '''
        global x
        global j
        while x == 1: 
            window.update_idletasks() #refreshing loop each time
            window.update()
            j = j+1 #updates number each second to demonstrate elapsed time
            if x == 1:
                elapsed_label = tk.Label(master = time_frame, text = str(j) + " sec", width = 20, padx = 10, pady = 10, bd = 3)
                elapsed_label.grid(column = 0 , row = 6)
                if j == numberTrialEntry:
                    j = -1
                    trialLabel.config(text = trials_list[trialNumber+1])
                    trialNumber = trialNumber + 1
                if trialNumber == lengthTrialEntry:
                    trialWindow.destroy()
                    break
            time.sleep(1)
        '''    
            
        
            
 
        
         
            
    '''def goback(): #function to go back to SC
        for widgets in dataframe.winfo_children(): #next 5 lines hide all visible elements on dataframe 
            widgets.grid_forget()
        dataframe.grid_forget()
        btn_return.grid_forget()
        btn_goto.grid_forget()
        
        creatingscframe() #calling SC function
        
    def goto(): #function to go to next frame (DR)
        for widgets in dataframe.winfo_children(): #next 5 lines hide all visible elements on dataframe
            widgets.grid_forget()
        dataframe.grid_forget()
        btn_return.grid_forget()
        btn_goto.grid_forget()
        
        datareview() #calling DR function'''
 
    def exit_command():
        window.destroy()
        quit()  
    
    
    
    
    dataframe = tk.Frame(window, relief = tk.RAISED, borderwidth = 7) #master frame for dc
    
    dataframe_title = tk.Button(master = dataframe, text = "Data Collection", height = 2, width = 20) #titling frame
    
    saveframe = tk.Frame(dataframe, relief = tk.RAISED, borderwidth = 5, padx = 5, pady = 5) #creating a frame for saving information about file
    
    as_label = tk.Label(master=saveframe, text="Save As: ") #creating label to name file (save as)
    as_entry = tk.Entry(master=saveframe, width=20) #creating entries for label
    as_entry.insert(0,FILENAME)
    
#    to_label = tk.Label(master=saveframe, text="Save To: ") #creating label for file location (save to)
#    to_entry = tk.Entry(master=saveframe, width=50) #creating entries for label
    
    #collect_button = tk.Button(master = saveframe, text = "Collect", command = collect)
    
    dataframe.pack(fill = "both", expand = True)
    dataframe_title.grid(padx = 5)
    #collect_button.grid()
    saveframe.grid(row = 4, column = 2) #placing saveframe to the right of all items
    as_label.grid(sticky = 'w', padx = 10, pady = 5) #putting the label in grid to the west with padding for space 
    as_entry.grid(padx = 10, pady = 5)#putting entry below the label
 #   to_label.grid(sticky = 'w', padx = 10, pady = 5) #putting the label in grid to the west with padding for space 
 #   to_entry.grid(padx = 10, pady = 5)#putting entry below the label
    
    
    
    patinfoframe = tk.Frame(dataframe, relief = tk.RAISED, borderwidth = 5) #frame for info from PI
    patinfoframe.grid(row = 0, column = 2, rowspan = 3, ipadx = 50, ipady= 15, padx= 5, pady = 5)
    patinfotitle = tk.Button(patinfoframe, text = "Patient Information", padx =10, pady = 10) #displaying info from PI
    patinfotitle.grid()
    patname_label = tk.Label(patinfoframe, text = (pi_data[1][0] + "." + pi_data[0])) #giving firstinitial.lastname from PI
    patname_label.grid(padx =10, pady = 10, sticky = 'w')
    dob_label = tk.Label(patinfoframe, text = ("DOB: " + pi_data[2]))#date of birth from PI
    dob_label.grid(padx =10, pady = 10, sticky = 'w')
    notes_label = tk.Label(patinfoframe, text = ("Notes: " + pi_data[3]))#notes from PI
    notes_label.grid(padx =10, pady = 10, sticky = 'w')
    
    
    
    for idx, text in enumerate(dclabels): #loop through label list
        dclabel = tk.Label(master=dataframe, text=text) #creating labels using text from the list, labels
        dcentry = tk.Entry(master=dataframe, width=30) #creating entries for each label
        dclabel.grid(row=idx + 1, column = 0, sticky = 'w', padx = 5, pady = 10) #putting each label in grid to the west with padding for space 
        dcentry.grid(row=idx + 1, column = 1, sticky = 'w', padx = 5, pady = 10) #putting each entry one column to the right of label in grid to the west with padding for space
        dc_entries.append(dcentry) #adding each entry to pi_entries list
    
    
    
    collect_button = tk.Button(master = dataframe, text = "COLLECT DATA", command = collect, padx = 10, pady = 10, width = 10)
    collect_button.grid(row = 4, column = 0)
    exit_button = tk.Button(master = dataframe, text = "EXIT", command = exit_command, padx = 10, pady = 10, width = 10)
    exit_button.grid(row = 4, column = 1)
    
    
        
    #btn_return = tk.Button(window, text = "Back to Sensor Calibration", command = goback, padx=5, pady=10) #creating button
    #btn_return.grid(sticky= "s") #placing button beneath all other elements
    #btn_goto = tk.Button(window, text = "Go to Data Review", command = goto, padx=5, pady=10) #creating button
    #btn_goto.grid(sticky = "s") #placing button beneath all other elements
    
        
def datareview():
    datareview = tk.Frame(window,relief = tk.RAISED, borderwidth = 7) #master frame for datareview
    datareview.grid()
    datareview_title = tk.Button(master = datareview, text = "Data Review", pady = 5, width = 20) #titling frame
    datareview_title.grid()
    
    
lc,ard = serialSetup()
Thread(target=receiving, args=(ard,lc,)).start() # start reading from serial. Should make this part of an initialization function?

frame1() #calling first function/frame

window.mainloop() #finishing loop




