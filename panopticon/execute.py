from panopticon import Panopticon, Robot, Robots

if __name__ == '__main__':

    bpl = Robot(hostname='BIW1-BPL010RB1', ip='172.16.22.101')
    robots = Robots(group='Group1')
    robots[bpl.hostname] = bpl

    panoptic = Panopticon(robots=robots)
    panoptic.watch(['TipDressCounter'])
    panoptic.listen()
    panoptic.learn()
    panoptic.start()
