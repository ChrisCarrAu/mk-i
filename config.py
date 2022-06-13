from turtle import bgcolor
from adafruit_servokit import ServoKit
import json
import tkinter as tk
from tkinter import ttk, messagebox, Spinbox
from tkinter import *
from robot import *


class TestConfig(Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.robot = Robot()

        self.geometry("640x480")
        self.title("Test Configuration")

        self.leglist = Listbox(self)
        self.leglist.place(x=10, y=30, height=80)
        self.leglist.insert(1, "LF")
        self.leglist.insert(2, "RF")
        self.leglist.insert(3, "LR")
        self.leglist.insert(4, "RR")
        
        self.xpos = Scale(self, from_ = -90, to = 90, orient=HORIZONTAL, command=self.legTest)
        self.xpos.place(x=60, y=230)
        self.ypos = Scale(self, from_ = 90, to = -90, command=self.legTest)
        self.ypos.place(x=160, y=230)


    def legTest(self, event=None):
        selectedLeg = self.leglist.get(self.leglist.curselection())
        xpos = self.xpos.get()
        ypos = self.ypos.get()

        print(F'> moving {selectedLeg} to ({xpos}, {ypos})')
        
        leg = self.robot.Legs[selectedLeg]
        leg.IK(xpos, ypos)


class App(Tk):
    def __init__(self):
        super().__init__()

        self.title(string="Robot Servo Configuration Tool")
        self.geometry("800x550")

        tk.Label(self, text="Servo ID").place(x=10, y=10)
        Label(self, text="Min").place(x=10, y=30)
        Label(self, text="Max").place(x=10, y=50)
        Label(self, text="Rot").place(x=10, y=70)
        Label(self, text="Side").place(x=10, y=90)
        Label(self, text="Fore/Aft").place(x=10, y=110)
        Label(self, text="Limb").place(x=10, y=130)

        self.ServoId = Entry(self, state="readonly")
        self.ServoId.place(x=140, y=10)

        self.ServoMin = Spinbox(self, from_ = 0, to = 180, command=self.servoMinTest)
        self.ServoMin.place(x=140, y=30)

        self.ServoMax = Spinbox(self, from_ = 0, to = 180, command=self.servoMaxTest)
        self.ServoMax.place(x=140, y=50)

        self.ServoMinMax = Scale(self, from_ = 0, to = 180, orient=HORIZONTAL, command=self.servoTest, length=300)
        self.ServoMinMax.place(x=360, y=30)

        self.ServoRot = Entry(self, state="readonly")
        self.ServoRot.place(x=140, y=70)

        self.ServoSide = Entry(self, state="readonly")
        self.ServoSide.place(x=140, y=90)

        self.ServoForeAft = Entry(self, state="readonly")
        self.ServoForeAft.place(x=140, y=110)

        self.ServoLimb = Entry(self, state="readonly")
        self.ServoLimb.place(x=140, y=130)

        Button(self, text="Update", command=self.update, height=1, width=13).place(x=40, y=170)
        Button(self, text="TEST", command=self.test_config, height=1, width=13).place(x=190, y=170)
        Button(self, text="power off", command=self.poweroff, height=1, width=13, bg='orange').place(x=340, y=170)
        Button(self, text="STOP ALL POWER", command=self.stop, height=1, width=13, bg='red', fg='white').place(x=490, y=170)

        cols = ('id', 'min', 'max', 'rot', 'side', 'foreaft', 'limb')
        self.listBox = ttk.Treeview(self, columns=cols, show='headings', height=12)

        for col in cols:
            self.listBox.heading(col, text=col, anchor=tk.CENTER)
            self.listBox.column(col, stretch=tk.YES, minwidth=50, width=100)
            self.listBox.grid(row=1, column=0, columnspan=1)
            self.listBox.place(x=10, y=230)

        Button(self, text="Save", command=self.save, height=1, width=13).place(x=140, y=500)

        self.show()
        self.listBox.bind('<Double-Button-1>', self.GetValue)
        self.listBox.bind('<<TreeviewSelect>>', self.GetValue)


    def GetValue(self, event):
        self.ServoId.configure(state="normal")
        self.ServoRot.configure(state="normal")
        self.ServoSide.configure(state="normal")
        self.ServoForeAft.configure(state="normal")
        self.ServoLimb.configure(state="normal")

        self.ServoId.delete(0, END)
        self.ServoMin.delete(0, END)
        self.ServoMax.delete(0, END)
        self.ServoRot.delete(0, END)
        self.ServoSide.delete(0, END)
        self.ServoForeAft.delete(0, END)
        self.ServoLimb.delete(0, END)
        row_id = self.listBox.selection()[0]
        select = self.listBox.set(row_id)
        self.ServoId.insert(0, select['id'])
        self.ServoId.configure(state="readonly")

        self.ServoMin.insert(0, select['min'])
        self.ServoMax.insert(0, select['max'])

        self.ServoRot.insert(0, select['rot'])
        self.ServoRot.configure(state="readonly")
        self.ServoSide.insert(0, select['side'])
        self.ServoSide.configure(state="readonly")
        self.ServoForeAft.insert(0, select['foreaft'])
        self.ServoForeAft.configure(state="readonly")
        self.ServoLimb.insert(0, select['limb'])
        self.ServoLimb.configure(state="readonly")

        self.ServoMinMax.configure(from_ = select["min"], to = select["max"])


    def servoTest(self, event=None):
        servoId = self.ServoId.get()
        servoMinMax = self.ServoMinMax.get()
        kit.servo[int(servoId)].angle = int(servoMinMax)


    def servoMinTest(self, event=None):
        servoId = self.ServoId.get()
        servoMin = self.ServoMin.get()
        kit.servo[int(servoId)].angle = int(servoMin)


    def servoMaxTest(self, event=None):
        servoId = self.ServoId.get()
        servoMax = self.ServoMax.get()
        kit.servo[int(servoId)].angle = int(servoMax)


    def test_config(self, event=None):
        testconfig = TestConfig(self)
        testconfig.mainloop()


    def update(self):
        servoId = self.ServoId.get()
        servoMin = self.ServoMin.get()
        servoMax = self.ServoMax.get()
        servoRot = self.ServoRot.get()
        servoSide = self.ServoSide.get()
        servoForeAft = self.ServoForeAft.get()
        servoLimb = self.ServoLimb.get()

        try:
            selected_item = self.listBox.selection()[0]
            self.listBox.item(selected_item, values=(servoId, servoMin, servoMax, servoRot, servoSide, servoForeAft, servoLimb))
            self.ServoId.focus_set()

        except Exception as e:
            print(e)


    def poweroff(self):
        servoId = self.ServoId.get()
        print(F'> powering off servo {servoId}')
        kit.servo[int(servoId)].angle=None


    def stop(self):
        for i in range(16):
            kit.servo[i].angle=None


    def save(self):
        config = []
        for row_id in self.listBox.get_children():
            id, min, max, rot, side, foreaft, limb = self.listBox.item(row_id)["values"]
            config.append( { "id": id, "min": min, "max": max, "rot": rot, "side": side, "foreaft": foreaft, "limb": limb } )

        with open('config.json', 'w') as f:
            json.dump({"servos": config}, f, indent=4)


    def show(self):
        with open('config.json', 'r') as f:
            config = json.load(f)

        servos = []
        for servo in config["servos"]:
            servos.append(servo)

        for _, value in enumerate(servos, start=1):
            self.listBox.insert("", "end", values=(value["id"], value["min"], value["max"], value["rot"], value["side"], value["foreaft"], value["limb"]))


if __name__ == "__main__":
    app = App()
    app.mainloop()