
def test():
    from diagram import ByteDiagram as d

    di = d()
    di.add_label("head", 3).add_label("metadata", 6).add_label("payload", 26)
    print(di.total_byte_length())
    print(di.export_diagram(35)[0])

    return di.export_diagram(35)

"""
from example import test
test()
"""
