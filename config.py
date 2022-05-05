from adafruit_servokit import ServoKit
import json
import tkinter as tk
from tkinter import ttk, messagebox, Spinbox
from tkinter import *

def GetValue(event):
    ServoId.configure(state="normal")
    ServoRot.configure(state="normal")
    ServoSide.configure(state="normal")
    ServoForeAft.configure(state="normal")
    ServoLimb.configure(state="normal")

    ServoId.delete(0, END)
    ServoMin.delete(0, END)
    ServoMax.delete(0, END)
    ServoRot.delete(0, END)
    ServoSide.delete(0, END)
    ServoForeAft.delete(0, END)
    ServoLimb.delete(0, END)
    row_id = listBox.selection()[0]
    select = listBox.set(row_id)
    ServoId.insert(0, select['id'])
    ServoId.configure(state="readonly")

    ServoMin.insert(0, select['min'])
    ServoMax.insert(0, select['max'])

    ServoRot.insert(0, select['rot'])
    ServoRot.configure(state="readonly")
    ServoSide.insert(0, select['side'])
    ServoSide.configure(state="readonly")
    ServoForeAft.insert(0, select['foreaft'])
    ServoForeAft.configure(state="readonly")
    ServoLimb.insert(0, select['limb'])
    ServoLimb.configure(state="readonly")


def servoMinTest(event=None):
    servoId = ServoId.get()
    servoMin = ServoMin.get()
    kit.servo[int(servoId)].angle = int(servoMin)


def servoMaxTest(event=None):
    servoId = ServoId.get()
    servoMax = ServoMax.get()
    kit.servo[int(servoId)].angle = int(servoMax)


def update():
    servoId = ServoId.get()
    servoMin = ServoMin.get()
    servoMax = ServoMax.get()
    servoRot = ServoRot.get()
    servoSide = ServoSide.get()
    servoForeAft = ServoForeAft.get()
    servoLimb = ServoLimb.get()

    try:
        selected_item = listBox.selection()[0]
        listBox.item(selected_item, values=(servoId, servoMin, servoMax, servoRot, servoSide, servoForeAft, servoLimb))
        ServoId.focus_set()

    except Exception as e:
        print(e)


def save():
    config = []
    for row_id in listBox.get_children():
        id, min, max, rot, side, foreaft, limb = listBox.item(row_id)["values"]
        config.append( { "id": id, "min": min, "max": max, "rot": rot, "side": side, "foreaft": foreaft, "limb": limb } )

    with open('config2.json', 'w') as f:
        json.dump({"servos": config}, f)


def show():
    for i, value in enumerate(servos, start=1):
        listBox.insert("", "end", values=(value["id"], value["min"], value["max"], value["rot"], value["side"], value["foreaft"], value["limb"]))

kit = ServoKit(channels=16)

servos = []
with open('config.json', 'r') as f:
    config = json.load(f)

for servo in config["servos"]:
    servos.append(servo)

root = Tk()
root.geometry("800x500")

global ServoId
global ServoMin
global ServoMax
global ServoRot
global ServoSide
global ServoForeAft
global ServoLimb

tk.Label(root, text="Servo Config", fg="red", font=(None, 30)).place(x=350, y=5)

tk.Label(root, text="Servo ID").place(x=10, y=10)
Label(root, text="Min").place(x=10, y=30)
Label(root, text="Max").place(x=10, y=50)
Label(root, text="Rot").place(x=10, y=70)
Label(root, text="Side").place(x=10, y=90)
Label(root, text="Fore/Aft").place(x=10, y=110)
Label(root, text="Limb").place(x=10, y=130)

ServoId = Entry(root, state="readonly")
ServoId.place(x=140, y=10)

ServoMin = Spinbox(root, from_ = 0, to = 180, command=servoMinTest)
ServoMin.place(x=140, y=30)

ServoMax = Spinbox(root, from_ = 0, to = 180, command=servoMaxTest)
ServoMax.place(x=140, y=50)

ServoRot = Entry(root, state="readonly")
ServoRot.place(x=140, y=70)

ServoSide = Entry(root, state="readonly")
ServoSide.place(x=140, y=90)

ServoForeAft = Entry(root, state="readonly")
ServoForeAft.place(x=140, y=110)

ServoLimb = Entry(root, state="readonly")
ServoLimb.place(x=140, y=130)

Button(root, text="update", command=update, height=1, width=13).place(x=140, y=170)

cols = ('id', 'min', 'max', 'rot', 'side', 'foreaft', 'limb')
listBox = ttk.Treeview(root, columns=cols, show='headings')

for col in cols:
    listBox.heading(col, text=col, anchor=tk.CENTER)
    listBox.column(col, stretch=tk.YES, minwidth=50, width=100)
    listBox.grid(row=1, column=0, columnspan=1)
    listBox.place(x=10, y=230)

Button(root, text="Save", command=save, height=1, width=13).place(x=140, y=460)

show()
listBox.bind('<Double-Button-1>', GetValue)

root.mainloop()