# interference.py - Mixin for DLX to handle relationships between rows (in nonograms)
import numpy as np

class Interference:
    def __init__(self, nxs, nys ):
        self.nxs, self.nys = nxs, nys
        self.state = [ {
            "x_color":None,
            "y_color":None,
            "id": i,
            "xid": i // nys,
            "yid": i %  nys
        } for i in range( nxs*nys ) ]


    def __str__( self ):
        str = ""
        for xid in range( self.nxs ):
            for val in self.get_x( xid ):
                if val['x_color'] == None and val['y_color'] == None:
                    str += "."
                else:
                    if val['x_color'] == None or val['y_color'] == None:
                        str += f"{val['x_color']}" if None == val['y_color'] else f"{val['y_color']}"
                    else:
                        if val['x_color'] != val['y_color']:
                            str += "X"
                        else:
                            str += f"{val['x_color']}"
            str += '\n'
        return str
        

    def get_x( self, xid ):
        return self.state[ xid*self.nys:xid*self.nys+self.nys ]


    def get_y( self, yid ):
        return [ self.state[x] for x in range( yid, self.nxs*self.nys, self.nys ) ]


    def get_color( self, val, id , compact ):
        compact_color = 0
        id_a          = ord('a')
        for c in compact:
            if c['idx'] == val[id]:
                if "" == c['color']:
                    compact_color = 1
                else:
                    ch = c['color'][0].lower()
                    compact_color = 2 + ord(ch) - id_a
                break
        return compact_color


    def is_xselectable( self, xid, compact ):
        for val in self.get_x( xid ):
            if( None != val["x_color"] ):
                return False
            #
            # compact_color = 1 if val["yid"] in compact else 0
            compact_color = self.get_color( val, "yid", compact )
            if None != val["y_color"] and compact_color != val["y_color"]:
                return False
        return True


    def xselect( self, xid, compact ):
        for val in self.get_x( xid ):
            # compact_color = 1 if val["yid"] in compact else 0
            compact_color = self.get_color( val, "yid", compact )
            self.state[ val["id"] ] = {
                "x_color": compact_color,
                "y_color": val["y_color"],
                "id":      val["id"],
                "xid":     val["xid"],
                "yid":     val["yid"]
                }
            

    def xunselect( self, xid ):
        for val in self.get_x( xid ):
            self.state[ val["id"] ] = {
                "x_color": None,
                "y_color": val["y_color"],
                "id":      val["id"],
                "xid":     val["xid"],
                "yid":     val["yid"]
                }


    def is_yselectable( self, yid, compact ):
        for val in self.get_y( yid ):
            if( None != val["y_color"] ):
                return False
            #
            # compact_color = 1 if val["xid"] in compact else 0
            compact_color = self.get_color( val, "xid", compact )
            if None != val["x_color"] and compact_color != val["x_color"]:
                return False
        return True


    def yselect( self, yid, compact ):
        for val in self.get_y( yid ):
            # compact_color = 1 if val["xid"] in compact else 0
            compact_color = self.get_color( val, "xid", compact )
            self.state[ val["id"] ] = {
                "x_color": val["x_color"],
                "y_color": compact_color,
                "id":      val["id"],
                "xid":     val["xid"],
                "yid":     val["yid"]
                }


    def yunselect( self, yid ):
        for val in self.get_y( yid ):
            self.state[ val["id"] ] = {
                "x_color": val["x_color"],
                "y_color": None,
                "id":      val["id"],
                "xid":     val["xid"],
                "yid":     val["yid"]
                }


if __name__ == '__main__':
    a = Interference( 5, 5 )
    c = [ {"idx":1, "color":"a"}, {"idx":2, "color":"a"} ]
    print( a.is_xselectable(1,c) )
    a.xselect( 1, c )
    r = [{"idx":0, "color":"a"}, {"idx":1, "color":"a"}]
    print( a.is_yselectable(0,r) )
    print( a.is_yselectable(1,r) )
    a.yselect(1,r)
    print( a )
