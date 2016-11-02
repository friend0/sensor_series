from panopticon import Panopticon, Robot

if __name__ == '__main__':

    bpl = Robot(hostname='BIW1-BPL010RB1', ip='172.16.22.101')
    robots = [bpl]

    panoptic = Panopticon(robots=[bpl])
    panoptic.watch(['TipDressCounter'])
    panoptic.listen()
    panoptic.learn()
    panoptic.start()
