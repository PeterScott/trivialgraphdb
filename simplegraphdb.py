# Really simple graph database, built on Tokyo Cabinet. Edges have
# numeric weights. Each vertex has a unique name, and zero or more
# named properties, in a key-value structure.
#
# Data for a given vertex will be stored on the same part of disk, so
# this gets good locality and should have decent performance.

import tc
import cPickle as pickle
from UserDict import DictMixin

####################
# Internal functions
####################

def make_link_string(u, v):
    """Make a string for a link from u to v."""
    return "%s\0\0%s" % (u, v)

def uint32_to_string(x):
    """Convert an unsigned 32-bit integer into a four-character
    string, in little-endian mode."""
    byte0 = x & 0xFF
    byte1 = (x >> 8)  & 0xFF
    byte2 = (x >> 16) & 0xFF
    byte3 = (x >> 24) & 0xFF
    return '%c%c%c%c' % (chr(byte0), chr(byte1), chr(byte2), chr(byte3))

def string_to_uint32(str):
    """Convert a four-character string, in little-endian mode, into an
    unsigned 32-bit integer."""
    x  = ord(str[0])
    x |= ord(str[1]) << 8
    x |= ord(str[2]) << 16
    x |= ord(str[3]) << 24
    return x

#####################
# The database itself
#####################

class GraphDb:
    """A graph database. Stores everything in a Tokyo Cabinet B+ tree
    database. Edges have weights. The weight of a nonexistent edge is
    0. This object is self.db, which you may access if you really know
    what you're doing."""

    def __init__(self, filename='graphdb.tcb'):
        """Initialize the graph database, with a given file name. If
        filename is not given, it will default to graphdb.tcb in the
        current directory. The file will be created if it does not
        exist."""
        # Create a B+ tree database
        self.db = tc.BDB()
        # Use defaults for tuning parameters, but enable Deflate
        # compression and large (bigger than 2 GiB) databases.
        self.db.tune(-1, -1, -1, -1, -1, tc.BDBTDEFLATE | tc.BDBTLARGE)
        self.db.open(filename, tc.BDBOWRITER | tc.BDBOCREAT)

    def close(self):
        """Close the database file. This happens automatically when
        the object is garbage collected, but this method is here in
        case you ever need to close it manually."""
        self.db.close()

    def get_edge_weight(self, u, v):
        """Get the weight of the edge from u to v. If the edge does
        not exist, returns 0."""
        link_str = make_link_string(u, v)
        try: return string_to_uint32(self.db[link_str])
        except KeyError: return 0

    def set_edge_weight(self, u, v, weight):
        """Set the weight of the edge from u to v. Weight must be a
        positive 32-bit integer. If the edge does not exist, it will
        be created. If weight is 0, the edge will be deleted."""
        link_str = make_link_string(u, v)
        if weight == 0:
            del self.db[link_str]
        else:
            self.db[link_str] = uint32_to_string(weight)

    def incr_edge_weight(self, u, v, increment=1):
        """Increment the weight of the edge from u to v. Increment
        defaults to 1. If the edge does not exist, it will be created,
        and its weight initialized to zero. The increment can be
        negative."""
        link_str = make_link_string(u, v)
        self.db.addint(link_str, increment)

    def __getitem__(self, v):
        return Vertex(self.db, v)

class Vertex(DictMixin):
    """A vertex in a graph. Provides a dict interface for getting and
    setting properties. These properties are anything which can be
    serialized by cPickle."""
    
    def __init__(self, db, vertex_name):
        self.db = db
        self.v = vertex_name + '\0!'

    def __getitem__(self, key):
        return pickle.loads(self.db[self.v + key])

    def __setitem__(self, key, value):
        self.db[self.v + key] = pickle.dumps(value)

    def __delitem__(self, key):
        del self.db[self.v + key]

    def keys(self):
        return [k.split('\0!')[1] for k in self.db.range(self.v, 0, self.v[:-1]+'"', 0, -1)] # magic
