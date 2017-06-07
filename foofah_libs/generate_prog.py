import time


def create_python_prog(path, input_data=None, output_file=None):
    out_prog = "#\n# Synthetic Data Transformation Program\n#\n"
    out_prog += "# Author:\n"
    now = time.strftime("%c")
    out_prog += "# Datetime: %s\n#\n\n" % (now)

    out_prog += "from foofah_libs.operators import *\n\n"

    if input_data:
        out_prog += "#\n# Raw Data\n#\n"
        out_prog += "t = " + str(input_data) + "\n\n"

    out_prog += "#\n# Data Transformation\n#\n"
    for i, n in enumerate(reversed(path)):
        if i > 0:
            params = n.operation[2]
            out_prog += "t = " + n.operation[0]['name'] + "(t"
            for i in range(1, n.operation[0]['num_params']):
                out_prog += ", " + params[i]

            out_prog += ")\n"

    if output_file:
        fo = open("foo.txt", "wb")
        fo.write(out_prog)

    return out_prog
