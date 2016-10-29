import sys
from panopticon import panopticon
from panopticon import robot, clients

bpl = robot.Robot(hostname = 'BIW1-BPL010RB1', ip='172.16.22.101')
robots = robot.Robots(group='Group1')
robots[bpl.hostname] = bpl

panopticon.watch(robots, ['TipDressCounter'], loud=True)
panopticon.listen(robots)