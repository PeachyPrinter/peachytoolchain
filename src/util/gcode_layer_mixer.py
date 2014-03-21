
class GCodeLayerMixer(object):
    def __init__(self, source):
         self.lines = self.generate(source)
         self.buffer = [ ]

    def generate(self,source):
        for line in source:
            yield line

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()
 
    def next(self):
        if len(self.buffer) == 0:
            self._populate_buffer()
        head, tail  = self.buffer[0], self.buffer[1:]
        self.buffer = tail

        return head

    def _populate_buffer(self):
        layer_data = [ ]
        complete = False

        try:
            current = self.lines.next().rstrip()
        except StopIteration:
            raise StopIteration

        while not complete and not self._is_z_movement(current):
            layer_data.append(current)
            try:
                current = self.lines.next().rstrip()
            except StopIteration:
                complete = True

        mixed_layer = self._mixup(layer_data)
        if not complete:
            mixed_layer.append(current)
        self.buffer = mixed_layer

    def _mixup(self, items):
        if len(items) < 1:
            return items
        head = items[0]
        tail = items[1:]
        tail.append(head)
        return tail
            
    def _is_z_movement(self, gcodeline):
        return gcodeline.startswith('G') and 'Z' in gcodeline 


             