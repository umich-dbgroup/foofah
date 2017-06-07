import cherrypy
import sys
sys.path.append('../')
from foofah_libs.operators import add_ops
from foofah_libs.generate_prog import create_python_prog
import uuid
import foofah
import os
from timeit import default_timer as timer
import time
import json
import numpy as np


class MainPage(object):
    program_cache = {}

    def index(self):
        with open("templates/index.html") as f:
            contents = f.read()
        return contents

    index.exposed = True

    @cherrypy.expose
    def astar(self):
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        body = json.loads(rawbody)

        print
        print body
        print

        raw_data = [map(str, x) for x in body['InputTable']]
        target = [map(str, x) for x in body['OutputTable']]

        start = timer()
        final_node, open_nodes, closed_nodes = foofah.a_star_search(raw_data, target, add_ops(), 0, 100, batch=True,
                                                                    epsilon=1)
        end = timer()

        path = foofah.reconstruct_path(final_node)

        actual_steps = []
        h_steps = []
        states = []

        program = create_python_prog(path, raw_data)

        for i, n in enumerate(reversed(list(path))):
            remaining_steps = len(path) - i - 1
            actual_steps.append(remaining_steps)
            h_steps.append(n.get_h_score())
            states.append(n.contents)

        num_visited = len(closed_nodes)
        nodes_created = open_nodes.qsize() + len(closed_nodes)

        if len(path) > 0:
            poly = np.ones(len(path) + 1)
            poly[len(path)] = -nodes_created
            branch_factor = round(max(np.real(np.roots(poly))), 3)

            unique_id = uuid.uuid4()

            self.program_cache[str(unique_id)] = path

            ret_val = {'actual_steps': actual_steps,
                       'h_steps': h_steps,
                       # 'ops': op_list,
                       'program': program,
                       'serialized_program': str(unique_id),
                       'states': states,
                       'time': '%.3f' % (end - start),
                       'branch_factor': branch_factor,
                       'num_visited': num_visited,
                       'nodes_created': nodes_created
                       }
            return json.dumps(ret_val)

        else:
            poly = np.ones(len(path) + 1)
            poly[len(path)] = -nodes_created

            ret_val = {'actual_steps': actual_steps,
                       'h_steps': h_steps,
                       'program': '',
                       'states': states,
                       'time': '%.3f' % (end - start),
                       'branch_factor': 'n/a',
                       'num_visited': num_visited,
                       'nodes_created': nodes_created
                       }
            return json.dumps(ret_val)

    @cherrypy.expose
    def cache(self):
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        fn = time.strftime("%Y_%m_%d_%H_%M_%S")
        fo = open("./public/log/" + fn, "w")
        fo.write(rawbody)
        fo.close()

    @cherrypy.expose
    def execute(self):
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        body = json.loads(rawbody)

        path = self.program_cache[body['serialized_program']]

        test_table = body['test_table']

        for i, node in enumerate(reversed(path)):
            if i > 0:
                op = node.operation[0]
                if op['num_params'] == 1:
                    test_table = op['fxn'](test_table)

                else:
                    test_table = op['fxn'](test_table, node.operation[1])

        ret_val = {'transformed_table': test_table}
        return json.dumps(ret_val)


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.config.update(
        {'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(MainPage(), '/', conf)
