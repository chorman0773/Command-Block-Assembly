
def escape(text):
    return text.replace('\\', '\\\\').replace('"', '\\"')

class Rel:
    def __init__(self, offset=0):
        self.offset = offset

    def __add__(self, other):
        return Rel(self.offset + other)

    def __sub__(self, other):
        return Rel(self.offset - other)

    def __str__(self):
        if self.offset == 0:
            return '~'
        return '~%d' % self.offset

class CommandPlacer:

    def __init__(self, origin):
        self.x, self.y, self.z = origin
        self.commands = []
        self.block_positions = []

    def place(self, line):
        orig_x, orig_z = self.x, self.z
        branch_len = 0
        for main, branch in line:
            setblock = self.create_setblock(main)
            self.commands.append(setblock)
            this_branch_len = 0
            for additional in branch:
                self.x += 1
                setblock = self.create_setblock(additional, True)
                self.commands.append(setblock)
                this_branch_len += 1
            self.x = orig_x
            branch_len = max(branch_len, this_branch_len)
            self.z += 1
        if branch_len > 0: branch_len += 1 # add space after branch
        self.x = orig_x + 1 + branch_len
        self.z = orig_z

    def output(self):
        return self.commands

    def cleanup(self):
        destroyblocks = []
        for pos in self.block_positions:
            destroyblocks.append('setblock %s %s %s air' % pos)
        return destroyblocks

    def create_setblock(self, block, rotate=False):
        block, command = block
        self.block_positions.append((self.x, self.y, self.z))

        if block.mode == 'CHAIN':
            block_type = 'chain_command_block'
        elif block.mode == 'REPEAT':
            block_type = 'repeating_command_block'
        else:
            block_type = 'command_block'

        flags = 0
        if block.cond:
            flags |= 8
        direction = 3 # south
        if rotate:
            direction = 5 # east
        flags |= direction

        data = '{TrackOutput:0,auto:%db,Command:"%s"}' % (
            1 if block.auto else 0, escape(command))

        return 'setblock %s %s %s %s %d replace %s' % (
            self.x, self.y, self.z, block_type, flags, data)
