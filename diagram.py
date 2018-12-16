from collections import namedtuple
from typing import List

symbols = dict(
   se='┌',  swe='┬',  sw='┐',
  nse='├', nswe='┼', nsw='┤',
   ne='└',  nwe='┴',  nw='┘',
   ns='│',   we='─',
)

BytesLabel = namedtuple("BytesLabel", ["length", "text"])


class ByteDiagram:

    def __init__(self, labels=[]):
        self.labels = list(labels)

    def add_label(self, text: str, length: int) -> "ByteDiagram":
        self.labels.append(BytesLabel(length, text))
        return self

    def total_byte_length(self) -> int:
        return sum([x.length for x in self.labels])

    def export_diagram(self, bytes_per_line: int, offset: int = 0, was_first_label_printed: bool = False) -> List[str]:
        assert bytes_per_line < 1000

        total_len = self.total_byte_length()
        if total_len <= bytes_per_line:
            bytes_per_line = total_len

            # Top of table
            block = symbols['se'] + ((total_len-1) * (symbols['we'] + symbols['swe'])) + symbols['we'] + symbols['sw'] + "\n"

            # Header labels
            if bytes_per_line > 100:
                for i in range(bytes_per_line):
                    j = i + offset
                    if j % 100 == 0:
                        block += symbols['ns'] + str((j // 100) % 10)
                    else:
                        block += "  "
                block += symbols['ns'] + "\n"

            if bytes_per_line > 10:
                for i in range(bytes_per_line):
                    j = i + offset
                    if j % 10 == 0:
                        block += symbols['ns'] + str((j // 10) % 10)
                    else:
                        block += "  "
                block += symbols['ns'] + "\n"

            block += symbols['ns']
            for i in range(bytes_per_line):
                j = i + offset
                block += str(j % 10) + symbols['ns']
            block += "\n"

            chunk_lengths = list([x.length for x in self.labels])

            # Header underline
            block += symbols['nse']
            for l in chunk_lengths:
                for i in range(l):
                    block += symbols['we']
                    block += symbols['nswe'] if i == l - 1 else symbols['nwe']
            block = block[:len(block) - 1] + symbols['nsw'] + "\n"

            # Text boxes
            has_remaining = True
            line = 0
            while has_remaining:
                any_remaining = False
                is_first = True
                for chunk in self.labels:
                    if is_first:
                        is_first = False
                        curr_frag = " " * len(chunk.text)
                    else:
                        curr_frag = chunk.text
                    frag_len = chunk.length + chunk.length - 1
                    pointer = line * frag_len
                    if len(curr_frag) < pointer:
                        block += symbols['ns']
                        block += frag_len * " "
                    else:
                        last_index = min(len(curr_frag), pointer + frag_len)
                        curr_frag = curr_frag[pointer:last_index]
                        padding = " " * (frag_len - len(curr_frag))
                        block += symbols['ns'] + curr_frag + padding
                        if last_index < len(chunk.text):
                            any_remaining = True
                line += 1
                block += symbols['ns'] + "\n"
                if not any_remaining:
                    has_remaining = False

            # Bottom of table
            block += symbols['ne']
            for l in chunk_lengths:
                for i in range(l):
                    block += symbols['we']
                    block += symbols['nwe'] if i == l - 1 else symbols['we']
            block = block[:len(block) - 1] + symbols['nw']

            return [block]
        else:
            for chunk in self.labels:
                assert chunk.length <= bytes_per_line

            blocks = list()
            count = 0
            offset = 0
            curr_accumulation = list()
            for chunk in self.labels:
                if count + chunk.length <= bytes_per_line:
                    curr_accumulation.append(chunk)
                    count += chunk.length
                    offset += chunk.length
                else:
                    blocks.append(ByteDiagram(curr_accumulation).export_diagram(bytes_per_line, offset)[0])
                    curr_accumulation.clear()
                    count = chunk.length
                    offset += chunk.length
                    curr_accumulation.append(chunk)

            if len(curr_accumulation) > 0:
                blocks.append(ByteDiagram(curr_accumulation).export_diagram(bytes_per_line, offset - sum([x.length for x in curr_accumulation]))[0])

            return blocks
