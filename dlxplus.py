#!/usr/bin/env python
#
# Copyright 2008 Sebastian Raaphorst.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An implementation of Donald Knuth's Dancing Links implementation:

http://lanl.arxiv.org/pdf/cs/0011047

By Sebastian Raaphorst, 2008.

Thanks to the following people for their testing efforts:
   * Winfried Plappert"""
import dlx
import interference

class DLXplus( dlx.DLX ):
    """The DLXplus data structure and relevant operations."""

    interference = None
    

    def set_interference( self, interf ):
        self.interference = interf


    def printSolution(self, solution):
        """A convenience function, which simply writes out each of the chosen
        rows in the covering as a list of column names."""
        for i in solution:
            print(self.N[i], self.getRowList(i))


    def _solve(self, depth, columnselector, columnselectoruserdata, statistics):
        """This is an internal function and should not be called directly."""

        result = None

        # Check to see if we have a complete solution.
        if self.R[self.header] == self.header:
            # Make a copy so that it is preserved.
            yield self.partialsolution[:]
            return

        # Make sure that the statistics are capable of holding the necessary information.
        if len(statistics.nodes) <= depth:
            statistics.nodes += [0] * (depth - len(statistics.nodes) + 1)
        if len(statistics.updates) <= depth:
            statistics.updates += [0] * (depth - len(statistics.updates) + 1)

        # Choose a column object.
        c = columnselector(self, columnselectoruserdata)
        if c == self.header or self.S[c] == 0:
            return

        # Cover the column.
        statistics.updates[depth] += self._cover(c)

        # Extend the solution by trying each possible row in the column.
        r = self.D[c]
        while r != c:
            # print( "Try row {}".format( self.N[r] ) )
            # print( self.N[r]['entry_t'] )
            if None != self.interference:
                if 0 == self.N[r]['entry_t'] :
                    selectable = self.interference.is_xselectable(self.N[r]['entry'], self.N[r]['compact'])
                else:
                    selectable = self.interference.is_yselectable(self.N[r]['entry'], self.N[r]['compact'])
            else:
                selectable = True
            
            if selectable:
                if None != self.interference:
                    if 0 == self.N[r]['entry_t']:
                        self.interference.xselect(self.N[r]['entry'], self.N[r]['compact'])
                    else:
                        self.interference.yselect(self.N[r]['entry'], self.N[r]['compact'])
                # Original processing
                self.partialsolution.append(r)
                statistics.nodes[depth] += 1

                # Now cover the columns that are handled by the inclusion of this row.
                j = self.R[r]
                while j != r:
                    self._cover(self.C[j])
                    j = self.R[j]

                # Recursively search.
                for sol in self._solve(depth+1, columnselector, columnselectoruserdata, statistics):
                    yield sol

                # Reverse the operation.
                self.partialsolution.pop()

                # We are no longer using this row right now, so uncover.
                j = self.L[r]
                while j != r:
                    self._uncover(self.C[j])
                    j = self.L[j]

                if None != self.interference:
                    if 0 == self.N[r]['entry_t']:
                        self.interference.xunselect(self.N[r]['entry'])
                    else:
                        self.interference.yunselect(self.N[r]['entry'])

                # print( "Retract row {}".format( self.N[r] ) );

            # If the result was not None, then terminate prematurely.
            if result != None:
                break

            # Try the next row.
            r = self.D[r]

        self._uncover(c)
        return



# Testing code.
if __name__ == '__main__':
    columns = [({"name":'a', "other":1},dlx.DLX.PRIMARY), ('b',dlx.DLX.PRIMARY), ('c',dlx.DLX.PRIMARY), ('d',dlx.DLX.SECONDARY), ('e',dlx.DLX.PRIMARY)]
    d = DLXplus(columns)
    rows = [[1,2,4],
            [0,1,3],
            [0],
            [0,1,2,3,4]]
    rowNames = ['row%i' % i for i in range(len(rows))]
    d.appendRows(rows, rowNames)
    for sol in d.solve():
        d.printSolution(sol)
