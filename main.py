# Quartz Crystal Microbalance Software
# iGEM TEC CEM 2021
# Jossan David Cardona Ramírez
# Jairo Enrique Ramírez Sánchez
# Daniela Zavala Melo

# Modules
from tkinter import *  # GUI tools
from tkinter import ttk  # GUI tools
from tkinter.filedialog import asksaveasfilename  # Dialog box extension to save files
from PIL import Image, ImageTk  # Display images
from matplotlib.figure import Figure  # Create plots
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)  # Display figure in the Canvas
import serial.tools.list_ports  # Serial ports
import tkinter.font as tkFont  # Font type and size
import threading  # Threads for different processes
import serial  # Serial communication
import time  # Manage time
import webbrowser  # Open a website
import os  # Obtain user information to run the application

# Global variables (later are explained individually)

global hilo1git
global arduino
global onePortFinal
global cond


# Functions


def nothing():  # Avoid some errors for functions without actions
    pass


def disconnected_error():  # Show an error when the Arduino is disconnected
    xDis = int(widtht / 4)
    yDis = int(heightt / 3)
    Button(command=nothing, fg='black', text="You disconnected the USB port. Run the program again once you have "
                                             "re-established the connection", font=fontStyle4, bg="grey",
           activebackground="grey", border=10).place(x=xDis, y=yDis)   # It is shown a button for a fast handling
    time.sleep(5.0)  # After 5 seconds, everything is closed
    root.quit()
    root.destroy()


def askquit():  # Close Button
    global isRun
    if contArd <= 1:  # Counter to know in which section it goes
        if contArd == 0:
            isRun = False  # Change isRun to false, so other conditionals are also stopped
            root.quit()  # Close everything
            root.destroy()
            webbrowser.open_new("https://2021.igem.org/Team:TecCEM")  # Open our website
        else:
            webbrowser.open_new("https://2021.igem.org/Team:TecCEM")  # Open our website
            try:
                cad = "mot:" + "1"  # "mot" tells Arduino the desired frequency of the AD9833
                arduino.write(cad.encode('ascii'))   # Send a final signal to Arduino, values are the initials again
                time.sleep(0.3)
                deltaT = "del:" + "1.0"  # "del" tells Arduino the desired delta time for each measurement
                arduino.write(deltaT.encode('ascii'))  # Send a final signal to Arduino, values are the initials again
                time.sleep(0.3)
                isRun = False  # Change isRun to false, so other conditionals are also stopped
                time.sleep(1.1)
                arduino.close()  # Close Arduino communication
                root.quit()  # Close everything
                root.destroy()
            except serial.SerialException:  # avoid error when Arduino is disconnected
                root.quit()  # Close everything
                root.destroy()
            except PermissionError:  # avoid error due to permissions
                root.quit()  # Close everything
                root.destroy()

    else:
        webbrowser.open_new("https://2021.igem.org/Team:TecCEM")  # Open our website
        try:
            cad = "mot:" + "1"  # the same as before, reestablish the variables to initial values
            arduino.write(cad.encode('ascii'))
            time.sleep(0.3)
            deltaT = "del:" + "1.0"
            arduino.write(deltaT.encode('ascii'))
            time.sleep(0.3)
            isRun = False
            arduino.close()  # Close serial communication
            hilo1.join(0.1)  # hilo1 joins to the main thread
            root.quit()  # Close everything
            root.destroy()
        except serial.SerialException:  # Avoid error when Arduino is disconnected
            root.quit()  # Close everything
            root.destroy()
        except PermissionError:   # Avoid error due to permissions
            root.quit()  # Close everything
            root.destroy()


number = 0  # This variable counts the amount of iterations
valueF = []  # The frequency values are stored in this list
valueI = []  # The time values are stored in this list
v_setup = 0  # Counter to know if button setup was pressed
p_play = 0  # Counter to know if button setup was pressed
isRun = False  # Condition to run getsensorvalues function


def getsensorvalues():  # Function to interpret information that comes from arduino
    global cond  # global conditions to use them later
    global number
    global valueI
    global valueF

    while isRun:  # cycle to read data
        try:
            cad = arduino.readline().decode('ascii').strip()  # Decode each line
            if cad:
                pos = cad.index(":")  # Look for ":"
                label = cad[:pos]  # Left side gives the label
                value = cad[pos + 1:]  # Right side gives the value
                if label == 'add':  # If it is "add" it means the output of the sensor
                    if v_setup == 0:  # To avoid errors due to skipped steps by the user
                        value_add.set(value)  # Frequency measured
                        number += 1  # Counter of measurements
                        valueI = list(range(1, number + 1))  # Save the time in valueI
                        valueF.append(int(value))  # Save the frequency measured in valueF
                        if len(valueF) > 2:  # Delete a bug in the AD9833
                            valueF[2] = valueF[1]
                        lines.set_data(valueI, valueF)  # Configure the plot axis
                        canvas.draw()  # Draw the plot
                        if p_play == 0:  # To have a sequence in the steps
                            if len(valueI) > int(pTotal / pDelta - 1):  # When the  length is bigger:
                                valueF.clear()  # Reset the lists
                                valueI.clear()
                                number = 0  # Reset counter
                    else:
                        value_add.set(value)  # The same code previously explained
                        number += 1
                        valueI = list(range(1, number + 1))
                        valueF.append(int(value))
                        if len(valueF) > 2:
                            valueF[2] = valueF[1]
                        valueIx = [element * pDelta for element in valueI]  # Reconfigure the x axis to show the time
                        lines.set_data(valueIx, valueF)  # Show the time and not the number of measurements
                        canvas.draw()
                        if p_play == 0:
                            if len(valueI) > int(pTotal / pDelta - 1):
                                valueF.clear()
                                valueI.clear()
                                number = 0
        except serial.SerialException:  # Avoid error due to disconnection
            disconnected_error()  # Close everything and show the error
        except PermissionError:  # Avoid error due to permissions
            disconnected_error()  # Close everything and show the error


def open_ard():  # Function to open file with the Arduino code
    try:
        os.startfile(r'ARDUINO\Arduino_QCM\Arduino_QCM.ino')  # Open the file from folder
        Label(image=circ11, borderwidth=0, bg=bgc2).place(x=xcirc1, y=ycirc1)  # Change color to green
    except FileNotFoundError:
        Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc1, y=ycirc1)  # Change color to orange


def open_teensy():  # Function to open file with the Teensy code
    try:
        os.startfile(r'ARDUINO\Teensy_QCM\Teensy_QCM.ino')
        Label(image=circ11, borderwidth=0, bg=bgc2).place(x=xcirc1, y=ycirc1)
    except FileNotFoundError:
        Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc1, y=ycirc1)


precad = 0  # Variable to be sent to Arduino


def initiate():  # Initiate button
    global contArd
    global precad
    if contArd == 0:  # If it was not pushed in order
        Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc3)  # Display orange circle
    else:
        selectedQuartz = comboQuartz.get()  # Obtain value from combobox default frequency
        if contArd == 1:
            if selectedQuartz == "":
                Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc3)  # Again, order matters
            else:
                if v_setup == 0:
                    contArd = 2
                    global hilo1  # Define the thread, it must be used to run simultaneously with the code
                    hilo1 = threading.Thread(target=getsensorvalues, daemon=True)  # Real time measurement is achieved
                    hilo1.start()  # Begin the thread
                    MHZ = selectedQuartz.index("MHz")  # String handling
                    valueMHZ = selectedQuartz[:MHZ - 1]
                    precad = valueMHZ + "000000"
                    cad = "mot:" + valueMHZ + "000000"  # "mot" gives Arduino the value of the initial frequency
                    time.sleep(0.6)  # Give 0.6 seconds to avoid communication errors
                    try:
                        delta_initial = "del: 1"
                        arduino.write(delta_initial.encode('ascii'))
                        time.sleep(1.0)
                        ax.set_xlim(0, 101)
                        arduino.write(cad.encode('ascii'))
                        time.sleep(0.1)
                        Label(image=circ11, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc3)  # Display green circle
                        ax.set_ylim(int(precad) - 1000000, int(precad) + 1000000)  # Define y axis limits
                    except serial.SerialException:  # Same possible errors to avoid
                        disconnected_error()
                    except PermissionError:
                        disconnected_error()

        else:
            MHZ = selectedQuartz.index("MHz")  # Once user is already connected, thread must not be run again
            valueMHZ = selectedQuartz[:MHZ - 1]
            precad = valueMHZ + "000000"
            cad = "mot:" + valueMHZ + "000000"
            arduino.write(cad.encode('ascii'))
            time.sleep(1.1)
            Label(image=circ11, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc3)
            ax.set_ylim(int(precad) - 1000000, int(precad) + 1000000)


def fenviaadd():  # Function to send information with the calibration button
    global precad
    if contArd <= 1:
        Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc3)
    else:
        total = int(value_mot.get()) + int(precad)  # Previous value plus the new one
        cad = "mot:" + str(total)  # Update cad value
        arduino.write(cad.encode('ascii'))  # send this new value to Arduino
        time.sleep(1.1)
        precad = total
        Label(image=circ11, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc3)


def connectcom():  # Connect to Arduino button
    global contArd
    global arduino
    global isRun
    if contArd == 0:
        selectedCOM = comboCOM.get()
        if selectedCOM == "None":
            Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc2, y=ycirc2)
        else:
            if selectedCOM == "":
                Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc2, y=ycirc2)
            else:
                try:  # serial.Serial is the most important command to make de connection
                    arduino = serial.Serial(selectedCOM, baudV, timeout=1.1)
                    time.sleep(1.1)  # Give enough time to the software
                    contArd = 1
                    isRun = True
                    Label(image=circ11, borderwidth=0, bg=bgc2).place(x=xcirc2, y=ycirc2)
                except:
                    Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc2, y=ycirc2)
    else:
        if not isRun:
            Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc2, y=ycirc2)
        else:
            Label(image=circ11, borderwidth=0, bg=bgc2).place(x=xcirc2, y=ycirc2)


# AVAILABLE PORTS
ports = serial.tools.list_ports.comports()  # Obtain the available ports in the computer
serialInst = serial.Serial()
portlist = []
if not ports:
    ports = "None"
    onePortFinal = " None"
else:
    for onePort in ports:
        portlist.append(str(onePort))
        if ports == "":
            ports = "None"
        else:
            onePort2 = str(onePort)  # Array management
            positionPort = onePort2.find('-')
            onePortFinal = onePort2[0:positionPort - 1]

pDelta = 1
pTotal = 100


def set_up():  # Configure the plot and delta time for acquisition data
    global v_setup
    global valueF
    global valueI
    global number
    global pDelta
    global pTotal
    selectedDelta = comboDelta.get()
    selectedTotal = comboTotal.get()
    if selectedDelta == "":
        Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc4)
    else:
        if selectedTotal == "":
            Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc4)
        else:
            if contArd < 2:
                Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc4)
            else:
                posDelta = selectedTotal.index("s")  # Array handling
                pTotal = int(selectedTotal[:posDelta])
                pDelta = float(selectedDelta[:posDelta + 1])
                canvas.draw()
                deltaT = "del:" + str(pDelta)
                arduino.write(deltaT.encode('ascii'))  # Send the selected delta time to Arduino
                time.sleep(0.1)
                v_setup = 1
                valueF.clear()  # Clear the variables each time that the button is pushed
                valueI.clear()  # Clear the variables each time that the button is pushed
                number = 0
                Label(image=circ11, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc4)
                ax.set_xlim(0, pTotal + 1)  # Define the new x axis limit from the information given by the user


def call_me1():  # Open Arduino icon
    root1 = Toplevel()
    root1.iconbitmap(r'FIGURES\iGEM2021ICO.ico')
    root1.geometry("500x505")
    root1.wm_title("Open Arduino")  # window title
    root1.iconbitmap(r'FIGURES\iGEM2021ICO.ico')
    root1.config(bg=bgc3)
    root1.resizable(0, 0)
    # text
    text100 = StringVar()
    text100.set("First step of the software is to select which microcontroller you are using. Before")
    x100 = 10
    y100 = 10
    Label(root1, textvariable=text100, font=fontStyle2, bg=bgc3).place(x=x100, y=y100)
    text101 = StringVar()
    text101.set("pressing one of the buttons, be sure to complete the following steps:")
    x101 = 10
    y101 = 30
    Label(root1, textvariable=text101, font=fontStyle2, bg=bgc3).place(x=x101, y=y101)
    text102 = StringVar()
    text102.set("1.- Install the Arduino software, the one used is version 1.8.16. You can find")
    x102 = 30
    y102 = 60
    Label(root1, textvariable=text102, font=fontStyle2, bg=bgc3).place(x=x102, y=y102)
    text103 = StringVar()
    text103.set("this program in the folder called 'QCM support files'. Unzip the folder and run the")
    x103 = 30
    y103 = 80
    Label(root1, textvariable=text103, font=fontStyle3, bg=bgc3).place(x=x103, y=y103)
    text104 = StringVar()
    text104.set("'arduino' application. It is also important to set Arduino as the default application")
    x104 = 30
    y104 = 100
    Label(root1, textvariable=text104, font=fontStyle3, bg=bgc3).place(x=x104, y=y104)
    text105 = StringVar()
    text105.set("to open files ending in '.ino'. A quick way to do it is to save an empty Arduino file")
    x105 = 30
    y105 = 120
    Label(root1, textvariable=text105, font=fontStyle3, bg=bgc3).place(x=x105, y=y105)
    text106 = StringVar()
    text106.set("to the desktop, select the properties option by right-clicking, locate the option")
    x106 = 30
    y106 = 140
    Label(root1, textvariable=text106, font=fontStyle3, bg=bgc3).place(x=x106, y=y106)
    text107 = StringVar()
    text107.set("'opens with', select 'change', then 'find another application on the computer', and ")
    x107 = 30
    y107 = 160
    Label(root1, textvariable=text107, font=fontStyle3, bg=bgc3).place(x=x107, y=y107)
    text108 = StringVar()
    text108.set(" select the arduino app in the downloaded folder. ")
    x108 = 30
    y108 = 180
    Label(root1, textvariable=text108, font=fontStyle3, bg=bgc3).place(x=x108, y=y108)
    text109 = StringVar()
    text109.set(" 2.- From the same folder called 'QCM support files', go to 'Libraries' and")
    x109 = 30
    y109 = 210
    Label(root1, textvariable=text109, font=fontStyle3, bg=bgc3).place(x=x109, y=y109)
    text110 = StringVar()
    text110.set("download 'FreqCount', and 'AD9833'. Then, in Arduino select Program> Include ")
    x110 = 30
    y110 = 230
    Label(root1, textvariable=text110, font=fontStyle3, bg=bgc3).place(x=x110, y=y110)
    text111 = StringVar()
    text111.set("library> Add ZIP library, and then select each of the aforementioned folders.")
    x111 = 30
    y111 = 250
    Label(root1, textvariable=text111, font=fontStyle3, bg=bgc3).place(x=x111, y=y111)
    text112 = StringVar()
    text112.set("3.- If you are using an Arduino as a microcontroller, you can continue to step 4.")
    x112 = 30
    y112 = 270
    Label(root1, textvariable=text112, font=fontStyle3, bg=bgc3).place(x=x112, y=y112)
    text113 = StringVar()
    text113.set("It is important to mention that the Arduino is used for quartz crystals less than 5 ")
    x113 = 30
    y113 = 290
    Label(root1, textvariable=text113, font=fontStyle3, bg=bgc3).place(x=x113, y=y113)
    text114 = StringVar()
    text114.set("MHz, if your measurement is greater, for example 10 MHz, you will have to use a")
    x114 = 30
    y114 = 310
    Label(root1, textvariable=text114, font=fontStyle3, bg=bgc3).place(x=x114, y=y114)
    text115 = StringVar()
    text115.set("Teensy. For the latter case, you must install the program that makes it ")
    x115 = 30
    y115 = 330
    Label(root1, textvariable=text115, font=fontStyle3, bg=bgc3).place(x=x115, y=y115)
    text116 = StringVar()
    text116.set("compatible with the Arduino interface, which is called Teensyduino. In the same")
    x116 = 30
    y116 = 350
    Label(root1, textvariable=text116, font=fontStyle3, bg=bgc3).place(x=x116, y=y116)
    text117 = StringVar()
    text117.set("way, you can find it in the 'Libraries' subfolder.")
    x117 = 30
    y117 = 370
    Label(root1, textvariable=text117, font=fontStyle3, bg=bgc3).place(x=x117, y=y117)
    text118 = StringVar()
    text118.set("4.- Now, it is time to select the 'Tools' tab in Arduino software. Select the board")
    x118 = 30
    y118 = 400
    Label(root1, textvariable=text118, font=fontStyle3, bg=bgc3).place(x=x118, y=y118)
    text119 = StringVar()
    text119.set("you are using, for example Teensy 4.1 or Arduino Nano. Then choose the port it")
    x119 = 30
    y119 = 420
    Label(root1, textvariable=text119, font=fontStyle3, bg=bgc3).place(x=x119, y=y119)
    text120 = StringVar()
    text120.set("is connected to. Finally, use the buttons on the Arduino interface to verify the")
    x120 = 30
    y120 = 440
    Label(root1, textvariable=text120, font=fontStyle3, bg=bgc3).place(x=x120, y=y120)
    text121 = StringVar()
    text121.set("program and upload it.")
    x121 = 30
    y121 = 460
    Label(root1, textvariable=text121, font=fontStyle3, bg=bgc3).place(x=x121, y=y121)


def call_me2():  # Arduino information icon
    root1 = Toplevel()
    root1.iconbitmap(r'FIGURES\iGEM2021ICO.ico')
    root1.geometry("500x380")
    root1.wm_title("Arduino Information")  # window title
    root1.iconbitmap(r'FIGURES\iGEM2021ICO.ico')
    root1.config(bg=bgc3)
    root1.resizable(0, 0)
    # text
    text200 = StringVar()
    text200.set("The second step is simpler, you only have to select the port to which your device")
    x200 = 10
    y200 = 10
    Label(root1, textvariable=text200, font=fontStyle2, bg=bgc3).place(x=x200, y=y200)
    text201 = StringVar()
    text201.set("was connected and press the 'Connect' button. ")
    x201 = 10
    y201 = 30
    Label(root1, textvariable=text201, font=fontStyle2, bg=bgc3).place(x=x201, y=y201)
    text202 = StringVar()
    text202.set("You probably won't see the available port until you upload the Arduino program,")
    x202 = 10
    y202 = 60
    Label(root1, textvariable=text202, font=fontStyle2, bg=bgc3).place(x=x202, y=y202)
    text203 = StringVar()
    text203.set("so once you've done that, hit the refresh button and now you'll have the option.")
    x203 = 10
    y203 = 80
    Label(root1, textvariable=text203, font=fontStyle2, bg=bgc3).place(x=x203, y=y203)
    text204 = StringVar()
    text204.set("If the port is not available or is the wrong one, make sure you have the usb")
    x204 = 10
    y204 = 100
    Label(root1, textvariable=text204, font=fontStyle2, bg=bgc3).place(x=x204, y=y204)
    text205 = StringVar()
    text205.set("cable connected correctly, you could also try to disconnect other inputs that are")
    x205 = 10
    y205 = 120
    Label(root1, textvariable=text205, font=fontStyle2, bg=bgc3).place(x=x205, y=y205)
    text206 = StringVar()
    text206.set("time, even having Bluetooth turned on in your computer could show devices that")
    x206 = 10
    y206 = 140
    Label(root1, textvariable=text206, font=fontStyle2, bg=bgc3).place(x=x206, y=y206)
    text207 = StringVar()
    text207.set("you do not want to see.")
    x207 = 10
    y207 = 160
    Label(root1, textvariable=text207, font=fontStyle2, bg=bgc3).place(x=x207, y=y207)
    text208 = StringVar()
    text208.set("The communication speed with the Arduino is also shown, which is in bits per")
    x208 = 10
    y208 = 190
    Label(root1, textvariable=text208, font=fontStyle2, bg=bgc3).place(x=x208, y=y208)
    text209 = StringVar()
    text209.set("second. A relatively high value was chosen for proper communication and more")
    x209 = 10
    y209 = 210
    Label(root1, textvariable=text209, font=fontStyle2, bg=bgc3).place(x=x209, y=y209)
    text210 = StringVar()
    text210.set("accurate real-time values.")
    x210 = 10
    y210 = 230
    Label(root1, textvariable=text210, font=fontStyle2, bg=bgc3).place(x=x210, y=y210)
    text211 = StringVar()
    text211.set("This section is used to mention the importance of properly following the")
    x211 = 10
    y211 = 260
    Label(root1, textvariable=text211, font=fontStyle2, bg=bgc3).place(x=x211, y=y211)
    text212 = StringVar()
    text212.set("sequence of steps, if it is not done in this way, there is some missing data")
    x212 = 10
    y212 = 280
    Label(root1, textvariable=text212, font=fontStyle2, bg=bgc3).place(x=x212, y=y212)
    text213 = StringVar()
    text213.set("or it was not connected properly, a circle on the left will be shown in")
    x213 = 10
    y213 = 300
    Label(root1, textvariable=text213, font=fontStyle2, bg=bgc3).place(x=x213, y=y213)
    text214 = StringVar()
    text214.set("orange, check the information entered. If everything was done correctly, a")
    x214 = 10
    y214 = 320
    Label(root1, textvariable=text214, font=fontStyle2, bg=bgc3).place(x=x214, y=y214)
    text215 = StringVar()
    text215.set("green circle will light up, which means that you can proceed to the next section.")
    x215 = 10
    y215 = 340
    Label(root1, textvariable=text215, font=fontStyle2, bg=bgc3).place(x=x215, y=y215)


def call_me3():  # Quartz crystal icon
    root1 = Toplevel()
    root1.iconbitmap(r'FIGURES\iGEM2021ICO.ico')
    root1.geometry("500x370")
    root1.wm_title("Quartz Crystal")  # window title
    root1.iconbitmap(r'FIGURES\iGEM2021ICO.ico')
    root1.config(bg=bgc3)
    root1.resizable(0, 0)
    # text
    text300 = StringVar()
    text300.set("At this point, the frequency established by the manufacturer must be selected,")
    x300 = 10
    y300 = 10
    Label(root1, textvariable=text300, font=fontStyle2, bg=bgc3).place(x=x300, y=y300)
    text301 = StringVar()
    text301.set("4, 5, and 10 MHz are given as options, since they are the most used in quartz")
    x301 = 10
    y301 = 30
    Label(root1, textvariable=text301, font=fontStyle2, bg=bgc3).place(x=x301, y=y301)
    text302 = StringVar()
    text302.set("crystal microbalances, but others can be added with simple changes in the code.")
    x302 = 10
    y302 = 50
    Label(root1, textvariable=text302, font=fontStyle2, bg=bgc3).place(x=x302, y=y302)
    text303 = StringVar()
    text303.set("Below this data, the frequency measured at that moment is shown. It is here.")
    x303 = 10
    y303 = 80
    Label(root1, textvariable=text303, font=fontStyle2, bg=bgc3).place(x=x303, y=y303)
    text304 = StringVar()
    text304.set("where Hardware and Software become one, since the quartz crystal microbalance")
    x304 = 10
    y304 = 100
    Label(root1, textvariable=text304, font=fontStyle2, bg=bgc3).place(x=x304, y=y304)
    text305 = StringVar()
    text305.set("must be assembled and connected correctly so that the software begins to graph")
    x305 = 10
    y305 = 120
    Label(root1, textvariable=text305, font=fontStyle2, bg=bgc3).place(x=x305, y=y305)
    text306 = StringVar()
    text306.set("the data acquired in real time. A great advantage of this application is that")
    x306 = 10
    y306 = 140
    Label(root1, textvariable=text306, font=fontStyle2, bg=bgc3).place(x=x306, y=y306)
    text307 = StringVar()
    text307.set("it can be used for any QCM, even commercial ones.")
    x307 = 10
    y307 = 160
    Label(root1, textvariable=text307, font=fontStyle2, bg=bgc3).place(x=x307, y=y307)
    text308 = StringVar()
    text308.set("Then, there is one of the most useful tools that we designed, which is the option")
    x308 = 10
    y308 = 190
    Label(root1, textvariable=text308, font=fontStyle2, bg=bgc3).place(x=x308, y=y308)
    text309 = StringVar()
    text309.set("of calibrating the frequency, that is, increasing or decreasing the value of the")
    x309 = 10
    y309 = 210
    Label(root1, textvariable=text309, font=fontStyle2, bg=bgc3).place(x=x309, y=y309)
    text310 = StringVar()
    text310.set("selected crystal. The idea of this is that user manages to resonate the crystal by")
    x310 = 10
    y310 = 230
    Label(root1, textvariable=text310, font=fontStyle2, bg=bgc3).place(x=x310, y=y310)
    text311 = StringVar()
    text311.set("applying the exact frequency of this between its terminals. This was implemented")
    x311 = 10
    y311 = 250
    Label(root1, textvariable=text311, font=fontStyle2, bg=bgc3).place(x=x311, y=y311)
    text312 = StringVar()
    text312.set("because the frequency set by the manufacturer has a certain tolerance, which")
    x312 = 10
    y312 = 270
    Label(root1, textvariable=text312, font=fontStyle2, bg=bgc3).place(x=x312, y=y312)
    text313 = StringVar()
    text313.set("means that it may be slightly above or below the value provided. The resonance ")
    x313 = 10
    y313 = 290
    Label(root1, textvariable=text313, font=fontStyle2, bg=bgc3).place(x=x313, y=y313)
    text314 = StringVar()
    text314.set("can be appreciated because there is a notable decrease in said value and the ")
    x314 = 10
    y314 = 310
    Label(root1, textvariable=text314, font=fontStyle2, bg=bgc3).place(x=x314, y=y314)
    text315 = StringVar()
    text315.set("variations due to any event near the crystal are significant.")
    x315 = 10
    y315 = 330
    Label(root1, textvariable=text315, font=fontStyle2, bg=bgc3).place(x=x315, y=y315)


def call_me4():  # Measurement settings icon
    root1 = Toplevel()
    root1.iconbitmap(r'FIGURES\iGEM2021ICO.ico')
    root1.geometry("500x215")
    root1.wm_title("Measurement Settings")  # window title
    root1.iconbitmap(r'FIGURES\iGEM2021ICO.ico')
    root1.config(bg=bgc3)
    root1.resizable(0, 0)
    # text
    text400 = StringVar()
    text400.set("It is time to configure the measurements to be obtained from the quartz crystal.")
    x400 = 10
    y400 = 10
    Label(root1, textvariable=text400, font=fontStyle2, bg=bgc3).place(x=x400, y=y400)
    text401 = StringVar()
    text401.set("The options you choose depend on the experiment that is being carried out. The")
    x401 = 10
    y401 = 30
    Label(root1, textvariable=text401, font=fontStyle2, bg=bgc3).place(x=x401, y=y401)
    text402 = StringVar()
    text402.set("first thing is to select the time difference between each of the measurements.")
    x402 = 10
    y402 = 50
    Label(root1, textvariable=text402, font=fontStyle2, bg=bgc3).place(x=x402, y=y402)
    text403 = StringVar()
    text403.set("Initially, a measurement of the output frequency of the quartz crystal is made")
    x403 = 10
    y403 = 70
    Label(root1, textvariable=text403, font=fontStyle2, bg=bgc3).place(x=x403, y=y403)
    text404 = StringVar()
    text404.set("1 second. There are several options to select the one that best suits each case.")
    x404 = 10
    y404 = 90
    Label(root1, textvariable=text404, font=fontStyle2, bg=bgc3).place(x=x404, y=y404)
    text405 = StringVar()
    text405.set("Then, the total time of the experiment is selected. It is the amount of information")
    x405 = 10
    y405 = 120
    Label(root1, textvariable=text405, font=fontStyle2, bg=bgc3).place(x=x405, y=y405)
    text406 = StringVar()
    text406.set("that will be shown on the graph and that which can be saved. It is recommended")
    x406 = 10
    y406 = 140
    Label(root1, textvariable=text406, font=fontStyle2, bg=bgc3).place(x=x406, y=y406)
    text407 = StringVar()
    text407.set("to be conservative with this value and choose times higher than the assumptions,")
    x407 = 10
    y407 = 160
    Label(root1, textvariable=text407, font=fontStyle2, bg=bgc3).place(x=x407, y=y407)
    text408 = StringVar()
    text408.set("this in order to have more information, instead of less.")
    x408 = 10
    y408 = 180
    Label(root1, textvariable=text408, font=fontStyle2, bg=bgc3).place(x=x408, y=y408)


def call_me5():  # Pump settings icon
    root1 = Toplevel()
    root1.iconbitmap(r'FIGURES\iGEM2021ICO.ico')
    root1.geometry("500x565")
    root1.wm_title("Pump Settings")  # window title
    root1.iconbitmap(r'FIGURES\iGEM2021ICO.ico')
    root1.config(bg=bgc3)
    root1.resizable(0, 0)
    # text
    text500 = StringVar()
    text500.set("The last step is to select the type of flow that you want to use and the operating")
    x500 = 10
    y500 = 10
    Label(root1, textvariable=text500, font=fontStyle2, bg=bgc3).place(x=x500, y=y500)
    text501 = StringVar()
    text501.set("time. You have the following options:")
    x501 = 10
    y501 = 30
    Label(root1, textvariable=text501, font=fontStyle2, bg=bgc3).place(x=x501, y=y501)
    text502 = StringVar()
    text502.set("a) Manual. This is very useful, since it allows the user to carry out the")
    x502 = 10
    y502 = 60
    Label(root1, textvariable=text502, font=fontStyle2, bg=bgc3).place(x=x502, y=y502)
    text503 = StringVar()
    text503.set("measurement directly by himself, the micropipetting technique can be used,")
    x503 = 10
    y503 = 80
    Label(root1, textvariable=text503, font=fontStyle2, bg=bgc3).place(x=x503, y=y503)
    text504 = StringVar()
    text504.set("which opens up a large number of possible experiments to be carried out. For")
    x504 = 10
    y504 = 100
    Label(root1, textvariable=text504, font=fontStyle2, bg=bgc3).place(x=x504, y=y504)
    text505 = StringVar()
    text505.set("his case, the selected flow time does not matter, as none of the pumps will")
    x505 = 10
    y505 = 120
    Label(root1, textvariable=text505, font=fontStyle2, bg=bgc3).place(x=x505, y=y505)
    text506 = StringVar()
    text506.set("be activated.")
    x506 = 10
    y506 = 140
    Label(root1, textvariable=text506, font=fontStyle2, bg=bgc3).place(x=x506, y=y506)
    text507 = StringVar()
    text507.set("b) Go-no-Go, this option and the next is for liquid biosensing. This name refers")
    x507 = 10
    y507 = 170
    Label(root1, textvariable=text507, font=fontStyle2, bg=bgc3).place(x=x507, y=y507)
    text508 = StringVar()
    text508.set("to activating the inlet pump for a certain time, then leaving the fluid in the")
    x508 = 10
    y508 = 190
    Label(root1, textvariable=text508, font=fontStyle2, bg=bgc3).place(x=x508, y=y508)
    text509 = StringVar()
    text509.set("the chamber in contact with the quartz crystal for another amount of time, and")
    x509 = 10
    y509 = 210
    Label(root1, textvariable=text509, font=fontStyle2, bg=bgc3).place(x=x509, y=y509)
    text510 = StringVar()
    text510.set("finally activating the outlet pump to remove the fluid. It is an excellent option")
    x510 = 10
    y510 = 230
    Label(root1, textvariable=text510, font=fontStyle2, bg=bgc3).place(x=x510, y=y510)
    text511 = StringVar()
    text511.set("to compare the behavior of a fluid and its adhesion with respect to time with a")
    x511 = 10
    y511 = 250
    Label(root1, textvariable=text511, font=fontStyle2, bg=bgc3).place(x=x511, y=y511)
    text512 = StringVar()
    text512.set("biofilm placed on the crystal. In this case, the selected flow time will indicate")
    x512 = 10
    y512 = 270
    Label(root1, textvariable=text512, font=fontStyle2, bg=bgc3).place(x=x512, y=y512)
    text513 = StringVar()
    text513.set("the time that the first pump will last on, the same time for the time inside the")
    x513 = 10
    y513 = 290
    Label(root1, textvariable=text513, font=fontStyle2, bg=bgc3).place(x=x513, y=y513)
    text514 = StringVar()
    text514.set("the chamber, and in the same way for the time of the outlet pump.")
    x514 = 10
    y514 = 310
    Label(root1, textvariable=text514, font=fontStyle2, bg=bgc3).place(x=x514, y=y514)
    text515 = StringVar()
    text515.set("c) Continuous. In this option, both pumps are turned on at the same time, so")
    x515 = 10
    y515 = 340
    Label(root1, textvariable=text515, font=fontStyle2, bg=bgc3).place(x=x515, y=y515)
    text516 = StringVar()
    text516.set("that everything that goes in comes out, this process is almost immediate, an ")
    x516 = 10
    y516 = 360
    Label(root1, textvariable=text516, font=fontStyle2, bg=bgc3).place(x=x516, y=y516)
    text517 = StringVar()
    text517.set("excellent affinity between the analyte and the biofilm is needed to achieve that ")
    x517 = 10
    y517 = 380
    Label(root1, textvariable=text517, font=fontStyle2, bg=bgc3).place(x=x517, y=y517)
    text518 = StringVar()
    text518.set("the changes in frequency can be appreciated. The selected time indicates how")
    x518 = 10
    y518 = 400
    Label(root1, textvariable=text518, font=fontStyle2, bg=bgc3).place(x=x518, y=y518)
    text519 = StringVar()
    text519.set("long both pumps will be working.")
    x519 = 10
    y519 = 420
    Label(root1, textvariable=text519, font=fontStyle2, bg=bgc3).place(x=x519, y=y519)
    text520 = StringVar()
    text520.set("The play button starts the experiment, the stop button restarts the measured")
    x520 = 10
    y520 = 450
    Label(root1, textvariable=text520, font=fontStyle2, bg=bgc3).place(x=x520, y=y520)
    text521 = StringVar()
    text521.set("values. If you want to make a new measurement, you must press stop and play")
    x521 = 10
    y521 = 470
    Label(root1, textvariable=text521, font=fontStyle2, bg=bgc3).place(x=x521, y=y521)
    text522 = StringVar()
    text522.set("again. Once all the data has been plotted, it is possible to download the")
    x522 = 10
    y522 = 490
    Label(root1, textvariable=text522, font=fontStyle2, bg=bgc3).place(x=x522, y=y522)
    text523 = StringVar()
    text523.set("acquired information in txt format for later analysis, as well as the graph")
    x523 = 10
    y523 = 510
    Label(root1, textvariable=text523, font=fontStyle2, bg=bgc3).place(x=x523, y=y523)
    text524 = StringVar()
    text524.set("with 'Save file' and 'Save plot' buttons, respectively.")
    x524 = 10
    y524 = 530
    Label(root1, textvariable=text524, font=fontStyle2, bg=bgc3).place(x=x524, y=y524)


def play():  # PLay button
    global p_play
    selectedType = comboType.get()
    selectedRate = comboRate.get()
    if v_setup == 1:
        if p_play == 1:  # To control if it was pushed previously or not
            pass
        else:
            if selectedType == "":
                Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc5)
            else:
                if selectedRate == "":
                    Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc5)
                else:
                    Label(image=circ11, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc5)
                    if selectedType == "Manual":  # For manual do nothing, user is going to do the measurement
                        pass
                    if selectedType == "Go-No-Go":  # For Go-no-go, the first motor will start when the button is pushed
                        value_type = 2              # and will operate for the flow time selected then the liquid is
                        posFlowT = selectedRate.index("s")  # going to stay in the chamber for the flow time selected
                        pFlowT = int(selectedRate[:posFlowT])  # and finally the outlet motor will empty everything
                        flowArd = "flo:" + str(value_type) + "," + str(pFlowT)  # Send "flow:2,time" is sent to Arduino
                        arduino.write(flowArd.encode('ascii'))

                    if selectedType == "Continuous":  # For continuous flow, both pumps are going to operate since
                        value_type = 1                # the beginning, during the flow time selected
                        posFlowT = selectedRate.index("s")
                        pFlowT = int(selectedRate[:posFlowT])
                        flowArd = "flo:" + str(value_type) + "," + str(pFlowT)  # Send "flow:1,time" is sent to Arduino
                        arduino.write(flowArd.encode('ascii'))

                    set_up()
                    p_play = 1

    else:
        Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc5)


def stop():  # Stop button
    global p_play
    if v_setup == 1:
        if p_play == 1:
            Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc5)
            set_up()  # Resets the values and the plot
            p_play = 0
        else:
            Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc5)
    else:
        Label(image=circ111, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc5)


def save_files():  # Save files button
    if p_play == 1:
        if len(valueI) > int(pTotal / pDelta - 1):  # There will be saved just the first data, even if the measurements
            time_txt1 = [element * pDelta for element in valueI]  # are still running
            time_txt2 = [round(num, 2) for num in time_txt1]  # Counter of measurements is converted to time
            time_txt3 = time_txt2[0: int(pTotal / pDelta)]
            freq_txt1 = valueF[0: int(pTotal / pDelta)]
            b = asksaveasfilename(filetypes=(("Text files", "*.txt"), ("All Files", "*.*")),  # Open dialog box
                                  defaultextension='.txt', title="QCM save data")  # to save the file
            if b:
                file = open(b, "w")  # Write the variables in the txt file
                a = 0
                while a <= int(pTotal / pDelta - 1):
                    file.write(str(time_txt3[a]) + ";" + str(freq_txt1[a]) + "\n")  # Give some format to the data
                    a += 1


def save_plots():  # Save plot button
    a = asksaveasfilename(filetypes=(("PNG Image", "*.png"), ("All Files", "*.*")),  # Default file: png
                          defaultextension='.png', title="QCM save plot")  # Open dialog box to save it
    if a:
        fig.savefig(a)


one_PortFinal = []  # To save the information of the new variable, when refresh button is pushed


def refresh():  # Refresh button
    global one_PortFinal
    ports_1 = serial.tools.list_ports.comports()  # again, obtain the ports when the button is pushed, to refresh data
    if not ports_1:
        one_PortFinal = " None"
    else:
        for one_Port in ports_1:
            portlist.append(str(one_Port))
            if ports_1 == "":
                ports_1 = "None"
            else:
                one_Port2 = str(one_Port)  # Array handling
                position_Port = one_Port2.find('-')
                one_PortFinal = one_Port2[0:position_Port - 1]
    comboCOM['values'] = one_PortFinal  # Display the port found


# initial values
contArd = 0
baudV = 250000

# GUI. From this point on, it's all about shaping and styling the interface
root = Tk()
value_pot = StringVar()
value_add = StringVar()
value_mot = StringVar()
# iGEM icon
root.iconbitmap(r'FIGURES\iGEM2021ICO.ico')
widtht = root.winfo_screenwidth()  # Obtain screen width from computer user
heightt = root.winfo_screenheight()  # Obtain screen height from computer user
root.geometry("%dx%d" % (widtht, heightt))
# Window title
root.wm_title("Quartz Crystal Microbalance - by iGEM TEC CEM 2021 -")  # window title
# ASKQUIT
root.protocol('WM_DELETE_WINDOW', askquit)
# Background color
colorbg = "white"
root.config(bg=colorbg)
# Font
fontStyle1 = tkFont.Font(family="Helvetica", size=11)
fontStyle2 = tkFont.Font(family="Helvetica", size=10)
fontStyle3 = tkFont.Font(family="Helvetica", size=9)
fontStyle4 = tkFont.Font(family="Helvetica", size=14)
# Delta y
delta_y1 = 30
delta_y2 = 45
# FDEBC5
bgc1 = '#D7EDFF'
wbg1 = int(widtht)
hbg1 = int(heightt / 10)
bg1 = ImageTk.PhotoImage(Image.open(r'FIGURES\D7EDFF.png').resize((wbg1, hbg1)))
xbg1 = 0
ybg1 = int(heightt - heightt * 1.6 / 10)
Label(image=bg1, borderwidth=0, bg=bgc1).place(x=xbg1, y=ybg1)
# B1E7EF
bgc2 = '#85D9A1'
wbg2 = int(widtht / 5.5)
hbg2 = int(ybg1)
bg2 = ImageTk.PhotoImage(Image.open(r'FIGURES\85D9A1.png').resize((wbg2, hbg2)))
xbg2 = xbg1
ybg2 = 0
Label(image=bg2, borderwidth=0, bg=bgc2).place(x=xbg2, y=ybg2)
# 00989B
bgc3 = '#00989B'
# TEC Logo
wlogo1 = int(widtht / 10)
hlogo1 = int(heightt / 21.4)
logo1 = ImageTk.PhotoImage(Image.open(r'FIGURES\TEC.png').resize((wlogo1, hlogo1)))
xlogo1 = widtht / 5.1
ylogo1 = heightt - int(heightt * 3 / 21.4)
Label(image=logo1, borderwidth=0, bg=bgc1).place(x=xlogo1, y=ylogo1)
# THERMOFISHER Logo
wlogo2 = int(widtht / 10)
hlogo2 = int(heightt / 25)
logo2 = ImageTk.PhotoImage(Image.open(r'FIGURES\THERMOFISHER.png').
                           resize((wlogo2, hlogo2)))
xlogo2 = xlogo1 + int(widtht * 1.1 / 10)
ylogo2 = heightt - int(heightt * 3.4 / 25)
Label(image=logo2, borderwidth=0, bg=bgc1).place(x=xlogo2, y=ylogo2)
# SNAPGENE Logo
wlogo3 = int(widtht / 10)
hlogo3 = int(heightt / 14.4)
logo3 = ImageTk.PhotoImage(Image.open(r'FIGURES\SNAPGENE.png').resize((wlogo3, hlogo3)))
xlogo3 = xlogo2 + int(widtht * 1.1 / 10)
ylogo3 = heightt - int(heightt * 2.3 / 14.4)
Label(image=logo3, borderwidth=0, bg=bgc1).place(x=xlogo3, y=ylogo3)
# IDT Logo
wlogo4 = int(widtht / 10)
hlogo4 = int(heightt / 21.6)
logo4 = ImageTk.PhotoImage(Image.open(r'FIGURES\IDT.png').resize((wlogo4, hlogo4)))
xlogo4 = xlogo3 + int(widtht * 1.33 / 12)
ylogo4 = heightt - int(heightt * 3.01 / 21.6)
Label(image=logo4, borderwidth=0, bg=bgc1).place(x=xlogo4, y=ylogo4)
# SURVEY Logo
wlogo5 = int(widtht / 12)
hlogo5 = int(heightt / 25)
logo5 = ImageTk.PhotoImage(Image.open(r'FIGURES\SURVEYMETHODS.png').resize((wlogo5, hlogo5)))
xlogo5 = xlogo4 + int(widtht * 1.33 / 12)
ylogo5 = heightt - int(heightt * 2.95 / 21.6)
Label(image=logo5, borderwidth=0, bg=bgc1).place(x=xlogo5, y=ylogo5)
# iGEM OFFICIAL Logo
wlogo6 = int(widtht / 12)
hlogo6 = int(heightt / 17.6)
logo6 = ImageTk.PhotoImage(Image.open(r'FIGURES\IGEMOFF.png').resize((wlogo6, hlogo6)))
xlogo6 = xlogo5 + int(widtht * 1.08 / 12)
ylogo6 = heightt - int(heightt * 2.55 / 17.6)
Label(image=logo6, borderwidth=0, bg=bgc1).place(x=xlogo6, y=ylogo6)
# text Run
textRun = StringVar()
textRun.set("1. Open Arduino")
xRun = int(widtht / 18.3)
yRun = int(heightt / 50)
Label(textvariable=textRun, font=fontStyle1, bg=bgc2).place(x=xRun, y=yRun)
# Open Arduino Button
xOpen = int(widtht / 20)
yOpen = yRun + delta_y1
Button(command=open_ard, text="Arduino", font=fontStyle2, bg=colorbg, activebackground=colorbg, border=1).place(
    x=xOpen, y=yOpen)
# Open Teensy Button
xOpen = int(widtht / 10)
yOpen = yRun + delta_y1
Button(command=open_teensy, text="Teensy", font=fontStyle2, bg=colorbg, activebackground=colorbg, border=1).place(
    x=xOpen, y=yOpen)
# Circles indicators
circ1 = ImageTk.PhotoImage(
    Image.open(r'FIGURES\WHITECIRC.png').resize((int(25), int(25))))
xcirc1 = int(widtht / 60)
ycirc1 = yRun
circ11 = ImageTk.PhotoImage(Image.open(r'FIGURES\GREENCIRC.png')
                            .resize((int(25), int(25))))
circ111 = ImageTk.PhotoImage(Image.open(r'FIGURES\ORANGECIRC.png')
                             .resize((int(25), int(25))))
Label(image=circ1, borderwidth=0, bg=bgc2).place(x=xcirc1, y=ycirc1)
# Information
info1 = ImageTk.PhotoImage(Image.open(r'FIGURES\INFO.png').resize((int(20), int(20))))
xinfo1 = int(widtht / 6.6)
yinfo1 = yRun
Button(root, image=info1, command=call_me1, activebackground=bgc2, bg=bgc2, border=0).place(x=xinfo1, y=yinfo1)
# textArduino
textArduino = StringVar()
textArduino.set("2. Arduino Information")
xArduino = int(widtht / 23)
yArduino = yOpen + delta_y2
Label(textvariable=textArduino, font=fontStyle1, bg=bgc2).place(x=xArduino, y=yArduino)
xcirc2 = xcirc1
ycirc2 = yArduino
Label(image=circ1, borderwidth=0, bg=bgc2).place(x=xcirc2, y=ycirc2)
xinfo2 = xinfo1
yinfo2 = yArduino
Button(root, image=info1, command=call_me2, activebackground=bgc2, bg=bgc2, border=0).place(x=xinfo2, y=yinfo2)
# text Connection Port
textConnection = StringVar()
textConnection.set("Connection Port:")
xConnection = xcirc1
yConnection = yArduino + delta_y1
Label(textvariable=textConnection, font=fontStyle2, bg=bgc2).place(x=xConnection, y=yConnection)
# combo box COM ports
widthcomboCOM = 7
xcomboCOM = xinfo1 - 50
ycomboCOM = yConnection
comboCOM = ttk.Combobox(width=widthcomboCOM, font=fontStyle2, state="readonly")
comboCOM.place(x=xcomboCOM, y=ycomboCOM)
comboCOM['values'] = onePortFinal
# text Baud rate
textbaud = StringVar()
textbaud.set("Baud rate:")
xBaud = xConnection
yBaud = yConnection + delta_y1
Label(textvariable=textbaud, font=fontStyle2, bg=bgc2).place(x=xBaud, y=yBaud)
# text baud value
textbaudv = StringVar()
textbaudv.set(baudV)
xBaudv = xinfo1 - 23
yBaudv = yBaud
Label(textvariable=textbaudv, font=fontStyle2, bg=bgc2).place(x=xBaudv, y=yBaudv)
# Connect button
xConnect = int(widtht / 13.9)
yConnect = yBaud + delta_y1
Button(command=connectcom, text="Connect", font=fontStyle2, bg=colorbg, activebackground=colorbg, border=1).place(
    x=xConnect, y=yConnect)
# Refresh button
b_ref = ImageTk.PhotoImage(Image.open(r'FIGURES\REFRESH.png').resize((int(21), int(20))))
xRef = xinfo1
yRef = yConnect
Button(root, image=b_ref, command=refresh, activebackground=bgc2, bg=bgc2, border=0).place(x=xRef, y=yRef)

# text Quartz Crystal
textQuartz = StringVar()
textQuartz.set("3. Quartz Crystal")
xQuartz = int(widtht / 19.1)
yQuartz = yConnect + delta_y2
Label(textvariable=textQuartz, font=fontStyle1, bg=bgc2).place(x=xQuartz, y=yQuartz)
# text Default
textDefault = StringVar()
textDefault.set("Default frequency: ")
xDefault = xBaud
yDefault = yQuartz + delta_y1
Label(textvariable=textDefault, font=fontStyle2, bg=bgc2).place(x=xDefault, y=yDefault)
# combo box quartz
widthcomboQuartz = 7
xcomboQuartz = xinfo1 - 50
ycomboQuartz = yDefault
comboQuartz = ttk.Combobox(width=widthcomboQuartz, font=fontStyle2, state="readonly")
comboQuartz.place(x=xcomboQuartz, y=ycomboQuartz)
comboQuartz['values'] = ('4 MHz', '5 MHz', '10 MHz')
# text measured
textMeasured = StringVar()
textMeasured.set("Measured frequency: ")
xMeasured = xDefault
yMeasured = yDefault + delta_y1
Label(textvariable=textMeasured, font=fontStyle2, bg=bgc2).place(x=xMeasured, y=yMeasured)
# text Hz
textHz = StringVar()
textHz.set("Hz")
xHz = xinfo1
yHz = yMeasured
Label(textvariable=textHz, font=fontStyle2, bg=bgc2).place(x=xHz, y=yHz)
# Serial Arduino Frequency
xADD = xHz - 84
yADD = yMeasured
Label(width=9, textvariable=value_add, font=fontStyle2, bg=bgc2).place(x=xADD, y=yADD)
# initiate button
xInitiate = int(widtht / 13.3)
yInitiate = yMeasured + delta_y1
Button(command=initiate, text="Initiate", font=fontStyle2, bg=colorbg, border=1, activebackground=colorbg).place(
    x=xInitiate, y=yInitiate)
xinfo3 = xinfo1
yinfo3 = yQuartz
Button(root, image=info1, command=call_me3, activebackground=bgc2, bg=bgc2, border=0).place(x=xinfo3, y=yinfo3)
xcirc3 = xcirc1
ycirc3 = yQuartz
Label(image=circ1, borderwidth=0, bg=bgc2).place(x=xcirc3, y=ycirc3)
# slider
xSlider = xMeasured
ySlider = yInitiate + delta_y1 + 10
Scale(from_=-1000, to=1000, orient='horizontal', tickinterval=500, length=xinfo1 - 7, variable=value_mot,
      font=fontStyle3,
      bg=colorbg, activebackground=colorbg, border=0).place(x=xSlider, y=ySlider)
# Button Calibrate
xCal = int(widtht / 13.9)
yCal = ySlider + delta_y2 + 15
Button(text="Calibrate", command=fenviaadd, font=fontStyle3, bg=colorbg, border=1, activebackground=colorbg) \
    .place(x=xCal, y=yCal)
# Measurement settings
textMeas = StringVar()
textMeas.set("4. Measurement Settings")
xMeas = int(widtht / 26.5)
yMeas = yCal + delta_y2
Label(textvariable=textMeas, font=fontStyle1, bg=bgc2).place(x=xMeas, y=yMeas)
xinfo4 = xinfo1
yinfo4 = yMeas
Button(root, image=info1, command=call_me4, activebackground=bgc2, bg=bgc2, border=0).place(x=xinfo4, y=yinfo4)
xcirc4 = xcirc1
ycirc4 = yMeas
Label(image=circ1, borderwidth=0, bg=bgc2).place(x=xcirc4, y=ycirc4)
# text Delta time
textDelta = StringVar()
textDelta.set("Delta time: ")
xDelta = xcirc1
yDelta = yMeas + delta_y1
Label(textvariable=textDelta, font=fontStyle2, bg=bgc2).place(x=xDelta, y=yDelta)
# combo box delta time
widthcomboDelta = 7
xcomboDelta = xinfo1 - 50
ycomboDelta = yDelta
comboDelta = ttk.Combobox(width=widthcomboDelta, font=fontStyle2, state="readonly")
comboDelta.place(x=xcomboDelta, y=ycomboDelta)
comboDelta['values'] = ['0.10 s', '0.20 s', '0.25 s', '0.50 s', '1.00 s']
# text total time
textTotal = StringVar()
textTotal.set("Total time: ")
xTotal = xcirc1
yTotal = yDelta + delta_y1
Label(textvariable=textTotal, font=fontStyle2, bg=bgc2).place(x=xTotal, y=yTotal)
# combo box time
widthcomboTotal = 7
xcomboTotal = xinfo1 - 50
ycomboTotal = yTotal
comboTotal = ttk.Combobox(width=widthcomboTotal, font=fontStyle2, state="readonly")
comboTotal.place(x=xcomboTotal, y=ycomboTotal)
comboTotal['values'] = ['20 s', '30 s', '60 s', '120 s', '300 s']
# Setup button
xSetup = int(widtht / 13.1)
ySetup = ycomboTotal + delta_y1
Button(command=set_up, text="Set up", font=fontStyle2, bg=colorbg, activebackground=colorbg, border=1).place(
    x=xSetup, y=ySetup)
# Pump settings
textPump = StringVar()
textPump.set("5. Pump Settings")
xPump = int(widtht / 19)
yPump = ySetup + delta_y2
Label(textvariable=textPump, font=fontStyle1, bg=bgc2).place(x=xPump, y=yPump)
xinfo5 = xinfo1
yinfo5 = yPump
Button(root, image=info1, command=call_me5, activebackground=bgc2, bg=bgc2, border=0).place(x=xinfo5, y=yinfo5)
xcirc5 = xcirc1
ycirc5 = yPump
Label(image=circ1, borderwidth=0, bg=bgc2).place(x=xcirc5, y=ycirc5)
# text flow type
textType = StringVar()
textType.set("Flow type: ")
xType = xcirc1
yType = yPump + delta_y1
Label(textvariable=textType, font=fontStyle2, bg=bgc2).place(x=xType, y=yType)
# combo box flow type
widthcomboType = 10
xcomboType = xinfo1 - 70
ycomboType = yType
comboType = ttk.Combobox(width=widthcomboType, font=fontStyle2, state="readonly")
comboType.place(x=xcomboType, y=ycomboType)
comboType['values'] = ['Manual', 'Go-No-Go', 'Continuous']
# text flow rate
textRate = StringVar()
textRate.set("Flow time: ")
xRate = xcirc1
yRate = yType + delta_y1
Label(textvariable=textRate, font=fontStyle2, bg=bgc2).place(x=xRate, y=yRate)
# combo box flow type
widthcomboRate = 7
xcomboRate = xinfo1 - 50
ycomboRate = yRate
comboRate = ttk.Combobox(width=widthcomboRate, font=fontStyle2, state="readonly")
comboRate.place(x=xcomboRate, y=ycomboRate)
comboRate['values'] = ['3 s', '5 s', '10 s', '20 s', '30 s']
# play button
b_play = ImageTk.PhotoImage(Image.open(r'FIGURES\PLAY.png').resize((int(30), int(30))))
xPlay = int(widtht / 20)
yPlay = yRate + delta_y1
Button(root, image=b_play, command=play, activebackground=bgc2, bg=bgc2, border=0).place(x=xPlay, y=yPlay)
# stop button
b_stop = ImageTk.PhotoImage(Image.open(r'FIGURES\STOP.png').resize((int(30), int(30))))
xStop = int(widtht / 9)
yStop = yPlay
Button(root, image=b_stop, command=stop, activebackground=bgc2, bg=bgc2, border=0).place(x=xStop, y=yStop)
# Plot
fig = Figure()
ax = fig.add_subplot(111)
ax.set_title('Real-time quartz crystal frequency measurement')
ax.set_xlabel('Time [s]')
ax.set_ylabel('Frequency [MHz]')
ax.set_xlim(0, 101)
ax.set_ylim(0, 11000000)
lines = ax.plot([], [])[0]
canvas = FigureCanvasTkAgg(fig, master=root)
width_plot = widtht / 1.2
height_plot = heightt / 1.16
canvas.get_tk_widget().place(x=wbg2, y=-heightt / 25, width=width_plot, height=height_plot)
canvas.draw()
root.update()
# save file button
xSave = int(widtht / 1.95)
ySave = height_plot - heightt / 14
Button(command=save_files, text="Save file", font=fontStyle2, bg=colorbg, activebackground=colorbg, border=1).place(
    x=xSave, y=ySave)
# save image button
xSPlot = int(widtht / 1.5)
ySPlot = height_plot - heightt / 14
Button(command=save_plots, text="Save plot", font=fontStyle2, bg=colorbg, activebackground=colorbg, border=1).place(
    x=xSPlot, y=ySPlot)

try:
    mainloop()
except KeyboardInterrupt:  # Avoid errors when closing the window
    pass