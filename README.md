Trivial graph database
======================

This is a graph database in Python, built on top of Tokyo
Cabinet. It's designed for simplicity, rather than features or speed,
but it should have very reasonable speed anyway, if your needs aren't
too complicated. As you might imagine, that speed derives entirely
from Tokyo Cabinet, rather than from my own efforts.

It supports directed graphs with positive integer weights. Each vertex
is uniquely identified by a string. Vertices have string properties
associated with them; each vertex is essentially a dict. The keys must
be strings, but the values can be anything which can be serialized by
Python's `cPickle` module.

Each database is stored in a file, preferably with the `.tcb`
extension. The rest of the API can be found in `trivialgraphdb.py`.

Example
-------

    from trivialgraphdb import GraphDb
    g = GraphDb('foo.tcb')          # Open database
    # Set weight of edge from node 'foo' to node 'bar'
    g.set_edge_weight('foo', 'bar', 40)
    print g.get_edge_weight('foo', 'bar') # => 40
    g.incr_edge_weight('foo', 'bar', 2)
    print g.get_edge_weight('foo', 'bar') # => 42
    
    harry = g['Harry Potter']       # Get one vertex
    harry['mentor'] = 'Albus Percival Wulfric Brian Dumbledore'
    harry['friends'] = set(['Ronald Weasley', 'Hermione Granger'])
    print harry
    # => {'friends': set(['Hermione Granger', 'Ronald Weasley']), 
    #     'mentor': 'Albus Percival Wulfric Brian Dumbledore'}

Installation
------------

There are two dependencies:

* [Tokyo Cabinet](http://fallabs.com/tokyocabinet/)
* [tc](https://github.com/rsms/tc/), from GitHub or via easy_install.

Once you have these, just `import trivialgraphdb` and use it.

Contributing
------------

This code is public domain. Fork it as much as you like, with my blessing.