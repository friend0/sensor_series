from panopticon import Panopticon
from panopticon import robot
import zmq

context = zmq.Context()
bpl = robot.Robot(hostname = 'BIW1-BPL010RB1', ip='172.16.22.101')
robots = robot.Robots(group='Group1')
robots[bpl.hostname] = bpl

panpotic = Panopticon(context, robots=robots)
panpotic.watch(['TipDressCounter'])
panpotic.learn()

#panopticon.watch(robots, ['TipDressCounter'], loud=True)
#panopticon.listen(robots)

