from panopticon import Panopticon, RobotMongo, Robot

""" todo: config and code ought to be de-coupled. Author a .yaml file where these processes will draw their
    configs from other configs can come from the db as well """

#bpl = Robot(hostname='BIW1-BPL010RB1', ip='172.16.22.101')
#dsh = Robot(hostname='BIW1-DSH010RB1', ip='10.176.25.150')
#robots = [bpl, dsh]

#items=['GunWeldCounter', 'TipDressCounter', 'TipDressCountHistory', 'EGWearInitialHistory']
#items=['EGWearInitialHistory']

processes = [RobotMongo('robots', 'kuka_robots'),
             Panopticon(**{'connect':True})]

print("Spooling processes...")
for process in processes:
    process.start()
for process in processes:
    process.join()

# todo: write sigint handler