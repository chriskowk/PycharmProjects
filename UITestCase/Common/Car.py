import os
import stat
import sys

class  Car:
    def __init__(self):
        self.speed = 0
        self.odometer = 0
        self.time = 0

    def say_state(self):
        print("I am going {} kph !".format(self.speed))

    def accelerate(self):
        self.speed += 5

    def brake(self):
        self.speed -= 5

    def step(self):
        self.odometer += self.speed
        self.time += 1

    def average_speed(self):
        return  self.odometer / self.time

if __name__ == '__main__':
    print('参数个数为:', len(sys.argv))
    root = 'D:/PycharmProjects/UITestCase'
    filelist = [os.path.join(path, file_name)
        for path, _, file_list in os.walk(root)
        for file_name in file_list]
    for e in filelist:
        os.chmod(e, stat.S_IWRITE)
        print("文件 {} 只读属性已清除".format(e))
    mycar = Car()
    print("I'm a car !")
    while True:
        action = input("What sould I do ? [A]ccelerate, [B]rake, "
                       "show [O]dometer, or show Average [S]peed ?".upper())
        if action not in "ABOS" or len(action) != 1:
            print("I don't know how to do that")
            continue
        if action == "A":
            mycar.accelerate()
        elif action == "B":
            mycar.brake()
        elif action == "O":
            print("The car has driven {} kilometers".format(mycar.odometer))
        elif action == "S":
            print("The car's average speed was {} kps".format(mycar.average_speed()))
        mycar.step()
        mycar.say_state()

