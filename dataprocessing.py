# -*- coding: utf-8 -*-
"""Posh_S23_Ponseti_BaselineGraphfromPC

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oCBvwO49E-sq2gvATVcPRkls4p8my9CC
"""

'''Parser function:
inputs: trial lables (labels) and the data frame (df)
outputs: a list of the row idices of the trial labels in the data frame
function: finds the locations of the trial markers in the data frame'''

def parser(labels,df): #called in split_trials
  locations=[]

  for label in labels:
    name=f"TRIAL{label}" #making the name to look for in the CSV
    count=0

    for row in df.iterrows(): #parsing through each row to find the Trial
      data = (df.iloc[count,0])

      if isinstance(data, str): #getting rid of extra spaces
        data = data.replace(" ", "")

      if data == name: #found a cell with the correct name
        locations.append(count)

      count+=1 #accumulator

  return locations

'''Split trials function
inputs: trial labels (labels) and the data frame (df)
outputs: a list containing separate dataframes of the separate trials
function: splits up the mega data frame into smaller data frames (1 data frame per trial)'''

def split_trials(labels, df): #calls parser

  split_list=[]

  trial_id=parser(labels,df) #getting the locations of the different trials

  for id in trial_id:
    trial_start=id+1 #one line below the TRIAL# is where the data actually starts
    split_list.append(trial_start)

    if id != trial_id[-1]: #if the trial id is not the last one in the list, we need to find the stop for that data
      stop=trial_id[trial_id.index(id)+1]-1 #back tracks from the next id in the list 
      split_list.append(stop)

  data_list=np.vsplit(df,split_list) #numpy splitting the data frame and storing into a list

  if len(data_list)<=2: #the first dataframe will include the patient information. We don't need to use this in the plots
    del data_list[0]
  else:
    length=len(data_list)

    data_list=[data_list[val] for val in range(len(data_list)) if val not in list(range(0,length,2))] #the data frames on the even numbered indices will be blank or contain info we don't need for plotting
    data_list=[data_list[df].astype(np.float64) for df in range(len(data_list))] #changing all the numbers to float64 so we can plot them

  return  data_list

'''Make plot function
inputs: x axes data, y axes data, dictionary of data categories, list containing dataframes of trials, trial, name of the file, and the figures list
outputs: The updated list with the most recent figure created added
function: creates a plot and stores it as a figure into the figures list'''

def make_plot(xx,yy,dict,df_list,trial,path_name, figures): #called in main function

  #grabbing the correct data frame
  df_index=trial-1
  df=df_list[df_index]

  #creating the figure and axes titles
  title=dict[yy]+" vs "+dict[xx]
  xtitle=dict[xx]
  ytitle=dict[yy]

  #creating the figure subtitle
  return_name = path_name.replace('data/', '')
  return_name = return_name.replace('.csv', '')
  subtitle=f'Trial {trial} from {return_name}'

  #setting plot parameters
  plt.rcParams["figure.figsize"] = [4.50, 3.50]
  plt.rcParams["figure.autolayout"] = True

  #creating lists of the columns we want to use
  x_val=df.iloc[:,xx].tolist()
  y_val=df.iloc[:,yy].tolist()

  #saving the plot as a figure variable and setting it up
  fig1=plt.figure()
  plt.scatter(x_val, y_val,s=2,color='blue')
  plt.title(title)
  plt.suptitle(subtitle)
  plt.xlabel(xtitle)
  plt.ylabel(ytitle)

  figures.append(fig1)
  plt.close()

  return figures

'''save_figures function
inputs: The list of all of the figures created and the name of the file the figures were created from
outputs: the filename
function: Combine all of the figures into one pdf file and save it'''

def save_figures(figures,name):

  #creating the filename
  new_name=name.split(".csv")
  file_name=new_name[0]
  filename = file_name + ".pdf"

  # PdfPages is a wrapper around pdf file
  p = PdfPages(filename)

  # iterating over the numbers in the figures list
  for fig in figures:
    fig.savefig(p,format='pdf')

  p.close()

  return filename

'''open_pdf function
inputs: the name of the pdf file
outputs: none
function: opens the file in a webbrowser '''
def open_pdf(name):
    webbrowser.open(name)

'''make_pdf function
inputs: the name of the csv file we want to graph
outputs: none
function: reads in the csv file, calls helper functions make_plot and split_trials, and open_pdf and plots all of the data in the file against time (separate graphs) '''

def make_pdf(PATH_NAME):

  ##### CSV file !!! also make sure you make it a raw string ###
  return_name = PATH_NAME.replace('data/', '')
  return_name = return_name.replace('.csv', '')
  PATH= 'pdf/' + return_name
  DATA=pd.read_csv(PATH_NAME) #reading in the csv file as a dataframe

  '''Establishing variables'''
  TRIAL_NUM=[1,1] #indices of how many trials in dataframe
  TRIALS=DATA.iloc[TRIAL_NUM[0],TRIAL_NUM[1]] #Number of trials included in the data set
  TRIAL_LABEL=list(range(1,int(TRIALS)+1)) #Trial labels (ex: 1,2,3 for 3 trials)

  #column index for sensor values
  TIME=0
  XFORCE=2
  YFORCE=3
  ZFORCE=4
  XMOMENT=5
  YMOMENT=6
  ZMOMENT=7
  FORCE1=8
  FORCE2=9
  FORCE3=10
  FORCE4=11
  FORCE5=12
  FORCE6=13
  FORCE7=14
  FORCE8=15
  XOR=16
  YOR=17
  ZOR=18
  XACCEL=19
  YACCEL=20
  ZACCEL=21

  #Axes titles
  TIME_T="Time (sec)"
  XFORCE_T="X Force (N)"
  YFORCE_T="Y Force (N)"
  ZFORCE_T="Z Force (N)"
  XMOMENT_T ="X Moment (N*m)"
  YMOMENT_T = "Y Moment (N*m)"
  ZMOMENT_T= "Z Moment (N*m)"
  FORCE1_T= "Pressure 1 (N)"
  FORCE2_T= "Pressure 2 (N)"
  FORCE3_T= "Pressure 3 (N)"
  FORCE4_T= "Pressure 4 (N)"
  FORCE5_T="Pressure 5 (N)"
  FORCE6_T="Pressure 6 (N)"
  FORCE7_T="Pressure 7 (N)"
  FORCE8_T= "Pressure 8 (N)"
  XOR_T= "X Orientation"
  YOR_T= "Y Orientation"
  ZOR_T="Z Orientation"
  XACCEL_T="X Acceleration (m/s^2)"
  YACCEL_T= "Y Acceleration (m/s^2)"
  ZACCEL_T= "Z Acceleration (m/s^2)"

  #Title Dictionary
  INDEXES_TITLES={TIME:TIME_T,XFORCE:XFORCE_T,YFORCE:YFORCE_T,ZFORCE:ZFORCE_T,XMOMENT:XMOMENT_T,YMOMENT:YMOMENT_T,ZMOMENT:ZMOMENT_T,FORCE1:FORCE1_T,FORCE2:FORCE2_T,FORCE3:FORCE3_T,FORCE4:FORCE4_T,FORCE5:FORCE5_T,FORCE6:FORCE6_T,FORCE7:FORCE7_T,FORCE8:FORCE8_T,XOR:XOR_T,YOR:YOR_T,ZOR:ZOR_T,XACCEL:XACCEL_T,YACCEL:YACCEL_T,ZACCEL:ZACCEL_T}

  #creating the data list (split up the trials into their own data frames)
  DATA_LIST=split_trials(TRIAL_LABEL,DATA)

  #initializing the list of the figures
  FIGURE_LIST=[]

  #making plots
  return_list=[]
  for y in INDEXES_TITLES.keys():
    return_list.append(y)
    
  for Y in return_list:
    if Y==TIME:
      continue
    for T in TRIAL_LABEL:
      FIGURE_LIST=make_plot(TIME,Y,INDEXES_TITLES,DATA_LIST,T,PATH_NAME,FIGURE_LIST)

  FILENAME=save_figures(FIGURE_LIST,PATH)

  open_pdf(FILENAME)

###################################################################################################
                          #End of function definitions#
####################################################################################################

'''importing libraries'''

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import webbrowser

from matplotlib.backends.backend_pdf import PdfPages