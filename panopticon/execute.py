from panopticon import Panopticon, RobotMongo, Robot

""" todo: config and code ought to be de-coupled. Author a .yaml file where these processes will draw their
    configs from other configs can come from the db as well """
bpl = Robot(hostname='BIW1-BPL010RB1', ip='172.16.22.101')
robots = [bpl]

items=['GunWeldCounter', 'TipDressCounter', 'TipDressCountHistory', 'EGWearInitialHistory']
#items=['GunWeldCounter']
#items=['GunWeldCounter', 'TipDressCounter']

processes = [RobotMongo('robots', 'kuka_robots'),
             Panopticon(robots=[bpl], items=items,
                        **{'connect':True})]

print("Spooling processes...")
for process in processes:
    process.start()
for process in processes:
    process.join()

# todo: write sigint handler