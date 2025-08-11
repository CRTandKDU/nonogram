# Exploratory topic: Nonograms -- Japanese puzzle
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

import dlxplus
import interference

_NONO_DIMS_SEPARATOR = "|"
_NONO_LINE_SEPARATOR = "/"
_NONO_SPEC_SEPARATOR = ","

def plot_examples(colormaps):
    """
    Helper function to plot data with associated colormap.
    """
    np.random.seed(19680801)
    data = np.random.randn(30, 30)
    n = len(colormaps)
    fig, axs = plt.subplots(1, n, figsize=(n * 2 + 2, 3),
                            layout='constrained', squeeze=False)
    for [ax, cmap] in zip(axs.flat, colormaps):
        psm = ax.pcolormesh(data, cmap=cmap, rasterized=True, vmin=0., vmax=1.)
        fig.colorbar(psm, ax=ax)
    plt.show()

    
def nono_default_colors():
    # Get a list of all named colors in Matplotlib
    allcolors = list( mcolors.CSS4_COLORS.keys() )
    lencolors = len(allcolors)
    alphabet  = "abcdefghijklmnopqrstuvwxyz"
    letter_colors = [ allcolors[ (i+i) % lencolors ] for i, c in enumerate(alphabet) ]
    return [ 'white' ] + letter_colors + [ 'black' ]


def nono_parse( str ):
    size, color = "", ""
    for c in str:
        if c.isdigit():
            size += c
        else:
            if c.isalpha():
                color += c 
    return {"size": int(size), "color": color}


def nono_read( fn_puzzle ):
    with open(fn_puzzle, 'r') as file:
        content = file.read()
    dims = content.split( _NONO_DIMS_SEPARATOR )
    rows = dims[0].split( _NONO_LINE_SEPARATOR )
    cols = dims[1].split( _NONO_LINE_SEPARATOR )
    spec = { "rows": [ list(map(lambda str: nono_parse(str),(row.split( _NONO_SPEC_SEPARATOR )))) for row in rows ],
             "cols": [ list(map(lambda str: nono_parse(str),(col.split( _NONO_SPEC_SEPARATOR )))) for col in cols ]
             }
    return spec


def nono_plot( spec ):
    nrows, ncols = len(spec['rows']), len(spec['cols'])
    # plt.style.use('_mpl-gallery-nogrid')
    plt.style.use('classic')
    image = np.zeros(nrows*ncols)
    # Set color here
    image[2*ncols+3] = 1
    # Reshape things into a XxY grid.
    image = image.reshape((nrows, ncols))
    row_labels = range(nrows)
    col_labels = range(ncols)
    plt.matshow(image)
    plt.xticks(range(ncols), col_labels)
    plt.yticks(range(nrows), row_labels)
    plt.show()


def nono_block( iteration, start, blocks, n ):
    def _nono_nextstart( b ):
        if "" == b['color'] :
            # BW
            return b['size']+1
        else:
            # Color
            return b['size']
    
    rows = []
    if( iteration == len(blocks) ):
        return []
    else:
        # print( "Block {} ({}), Start {}".format( iteration, blocks[iteration], start ) )
        for c in range( start, n - blocks[iteration]['size'] + 1 ):
            c_row = []
            # print("  Testing pos {}".format(c) )
            seq = nono_block( iteration+1, c + _nono_nextstart( blocks[iteration] ), blocks, n )
            c_row += [ {"idx":col, "color": blocks[iteration]['color']}  for col in range(c, c+blocks[iteration]['size']) ]
            if 0 == len(seq):
                if iteration == len(blocks)-1:
                    rows += [ c_row ]
            else:
                for sequence in seq:
                    rows += [ c_row + sequence ]

    return rows

    
def nono_setup_row( blocks, n ):
    rows = nono_block( 0, 0, blocks, n )
    # print( blocks, "-->", rows )
    return rows
    
    
def nono_solve( spec ):
    nrows, ncols = len(spec['rows']), len(spec['cols'])
    interf = interference.Interference( nrows, ncols )
    # Set up
    # columns = [ ("VAL_{}_{}".format(row,col), dlx.DLX.PRIMARY ) for row in range(nrows) for col in range(ncols) ]
    columns = []
    columns += [ ("ROW_{}".format(row), dlxplus.dlx.DLX.PRIMARY) for row in range(nrows) ]
    columns += [ ("COL_{}".format(col), dlxplus.dlx.DLX.PRIMARY) for col in range(ncols) ]
    # print( spec )
    d = dlxplus.DLXplus( columns )
    # print( d.interference )
    d.set_interference( interf )
    # print( d.interference )
    # Rows
    total_rows = []
    for row in range( len(spec['rows']) ):
        rows = nono_setup_row( spec['rows'][row], ncols )
        d_rows, d_rownames = [], []
        for r in rows:
            d_rows += [ [row] ]
            d_rownames += [ { "compact": r, "entry": row, "entry_t": 0 } ]
        total_rows += d.appendRows( d_rows, d_rownames )
    #
    for col in range( len(spec['cols']) ):
        rows = nono_setup_row( spec['cols'][col], ncols )
        d_rows, d_rownames = [], []
        for r in rows:
            d_rows += [ [col+nrows] ]
            d_rownames += [ { "compact": r, "entry": col, "entry_t": 1 } ]
        total_rows += d.appendRows( d_rows, d_rownames )
    # Solve
    # print( [ d.N[x] for x in total_rows] )
    # for sol in d.solve():
    #     d.printSolution(sol)
    return d, d.solve()


def nono_print_solution( spec, d, solution ):
    def _nono_color( idx, a ):
        color = 0
        for c in a:
            if c['idx'] == idx :
                color = 1 if "" == c['color'] else c['color']
                break
        return color

    def _nono_to_string( arr ):
        str = ""
        for j in range( len(spec['rows']) ):
            str += "{}".format( _nono_color( j, arr ) )
        return str
    
    rows_only = []
    # Collect solution by rows
    for i in solution:
        item = d.N[i]
        if 0 == item['entry_t']:
            rows_only += [{ 'compact': item['compact'], 'entry': item['entry'] }]
    rows_only = sorted( rows_only, key=lambda elt: elt['entry'] )
    # Convert to string representations
    for i in rows_only:
        print( _nono_to_string( i['compact'] ) )
        
    
def nono_plot_solution( spec, d, solution ):
    def _nono_color( blk ):
        if "" == blk['color']:
            return 1.
        ch = blk['color'][0].lower()
        pt = (ord(ch)-ord('a')+1)/28. # + 1./56.
        return pt
    
    nrows, ncols = len(spec['rows']), len(spec['cols'])
    # plt.style.use('_mpl-gallery-nogrid')
    plt.style.use('classic')
    image = np.zeros(nrows*ncols)
    # Set color here
    rows_only = []
    # Collect solution by rows
    for i in solution:
        item = d.N[i]
        if 0 == item['entry_t']:
            rows_only += [{ 'compact': item['compact'], 'entry': item['entry'] }]
    rows_only = sorted( rows_only, key=lambda elt: elt['entry'] )
    # Convert to image representation
    for i in rows_only:
        x = i['entry'] # Should be == i by the way
        for y in i['compact']:
            compact_color = _nono_color( y )
            image[ x*ncols + y['idx'] ] = compact_color
    # Reshape things into a XxY grid.
    image = image.reshape((nrows, ncols))
    row_labels = range(nrows)
    col_labels = range(ncols)
    # plt.matshow(image, cmap='Greys')
    cmap = ListedColormap( nono_default_colors() )
    plt.matshow( image, cmap=cmap )
    plt.xticks(range(ncols), col_labels)
    plt.yticks(range(nrows), row_labels)
    plt.show()


if __name__ == '__main__':
    # Create the parser
    parser = argparse.ArgumentParser(description="A simple nonogram solver.")
    # Add arguments
    parser.add_argument("puzzle", type=str, help="Puzzle file")
    # Parse the arguments
    args = parser.parse_args()
    #
    spec = nono_read( args.puzzle )
    print( "Puzzle size: {} x {} -- {} colors".format( len(spec['rows']),
                                                       len(spec['cols']),
                                                       len(list( mcolors.CSS4_COLORS.keys() )) ) )
    d, solutions = nono_solve(spec)
    if None != d:
        for sol in solutions:
            print( "Solution:" )
            nono_plot_solution( spec, d, sol )
