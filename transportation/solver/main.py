import numpy as np
import pandas as pd
import random


class Solver():

    def __init__(self, supply=None, demande=None, costs=None, debug=False):

        if all([supply, demande, costs]):
            self.isbalance = True
            self.DN = len(demande)
            self.SN = len(supply)
            costs = np.asarray(costs)
            supply, demande, costs = self.BalanceIt(supply, demande, costs)
            self.supply = supply
            self.demande = demande
            self.costs = costs
            self.setup()

        self.paths = []

        self.qty = 0
        self.x, self.y = 0, 0  # the cordinates of the selected cell
        self.use_debug = debug

    def BalanceIt(self, supply, demande, costs):
        diff = sum(supply) - sum(demande)
        if diff > 0:
            demande += [diff]
            self.isbalance = False
            self.dummy = "y"
            costs = np.c_[costs, np.zeros((self.SN, 1))]
        elif diff < 0:
            supply += [-diff]
            self.isbalance = False
            self.dummy = "x"
            costs = np.r_[costs, np.zeros((1, self.DN))]
        return supply, demande, costs

    def setup(self):
        supids = self.costs.shape[0]
        demids = self.costs.shape[1]
        table_shape = (supids + 2, demids + 2)
        table = np.zeros(table_shape)
        table[1:-1, -1] = self.supply.copy()
        table[-1, 1:-1] = self.demande.copy()
        table[1:-1, 1:-1] = self.costs.copy()

        ridexs = np.arange(0, supids, 1)
        cidexs = np.arange(0, demids, 1)
        table[0, 1:-1] = cidexs.copy()
        table[1:-1, 0] = ridexs.copy()

        self.table = table
        self.ref_supply = self.supply
        self.ref_demande = self.demande
        self.ref_costs = self.costs

        self.new_table = table
        print(f'[i] : SIZE {self.table.shape}')
        print(self.new_table)

    def displayPaths(self):
        table_string = self.table.astype(str)
        for x, y, cost, qty, _ in self.paths:
            table_string[int(x+1), int(y+1)] += f" *{qty}"
        self.printT(table_string)
        return self.printT(table_string)

    def results(self):
        self.displayPaths()
        total_cost = 0
        for _, _, cost, qty, _ in self.paths:
            total_cost += cost*qty
        print('---------------------------------------------')
        print(f'------- TOTAL COST USING METHOD : {self.method}')
        print(f'[===>] : {total_cost}]')
        print('---------------------------------------------')

    def findCell(self):
        self.debug("[*] : Finding the cell to use")
        if self.method == 1:
            new_cords = 1, 1  # self.x + self.i, self.y + self.j
            cell_in_table = new_cords
        elif self.method == 2:
            x, y = self.getIndexMinCost()
            cell_in_table = x+1, y+1
        else:
            # get where is the max regret
            axis, index = self.getRegretMax()
            cell_in_table = self.getMinRegret(axis, index)

        self.x, self.y = cell_in_table
        self.debug(f"=> cell to use [{self.x},{self.y}]")

    def reSetup(self):
        self.paths = []
        self.qty = 0
        self.new_table = self.table
        self.supply = self.ref_supply
        self.demande = self.ref_demande
        self.costs = self.ref_costs

    def solve(self, method):
        # find which row, column to delete
        self.reSetup()
        self.method = method

        self.debug("[BUILDING SOLUTION]")
        progress = "*"
        while self.new_table.shape != (2, 2) and np.sum(self.demande) != 0 and np.sum(self.supply) != 0:
            self.findCell()
            self.qty = self.getQunantity()
            self.savePath()
            self.updateTable()
            self.updateVars()
            # progress = self.progress(progress)

    def setDummy(self, source, dest):
        if self.isbalance:
            return 0
        if self.dummy == "x":
            if source == self.SN:
                return 1
        elif self.dummy == "y":
            if dest == self.DN:
                return 1
        return 0

    def savePath(self,):
        self.debug("[+] : Saving path")
        source = self.new_table[self.x, 0]
        dest = self.new_table[0, self.y]
        cost = self.new_table[self.x, self.y]
        isDummy = self.setDummy(source, dest)
        self.paths.append([source, dest, cost, self.qty, isDummy])
        self.debug(
            f"[+] : path saved with source : {source} , dest : {dest}, cost {cost}, quantity : {self.qty}, isDummy : {isDummy}")

    def updateTable(self):
        self.debug("Updating table")
        if self.new_table[self.x, -1] < self.new_table[-1, self.y]:
            # delete row and supply self.x then change value of demand self.y
            self.new_table = np.delete(self.new_table, self.x, 0)
            self.new_table[-1, self.y] -= self.qty
        elif self.new_table[self.x, -1] > self.new_table[-1, self.y]:
            # delete column and demand self.y then change value of supply self.x
            self.new_table = np.delete(self.new_table, self.y, 1)
            self.new_table[self.x, -1] -= self.qty
            self.j = 1
        else:
            # delete row and supply self.x, column and demand self.y
            self.new_table = np.delete(self.new_table, self.x, 0)
            self.new_table = np.delete(self.new_table, self.y, 1)
        self.debug("new table")
        self.debug(self.new_table)

    def updateVars(self):
        self.debug('[~] : Updating supply , demande, costs')
        self.supply = self.new_table[1:-1, -1]
        self.demande = self.new_table[-1, 1:-1]
        self.costs = self.new_table[1:-1, 1:-1]
        self.debug('supply , demande, costs')
        self.debug(self.supply, self.demande, self.costs)

    def getQunantity(self):
        qty = min(self.supply[self.x-1], self.demande[self.y-1])
        self.debug(f'[~] : quantity to transport is {qty}')
        return qty

    def getRegretMax(self):
        rcol, rrow = [], []
        rrow = np.max(self.costs, axis=1) - np.min(self.costs, axis=1)
        rcol = np.max(self.costs, axis=0) - np.min(self.costs, axis=0)

        r, rmax = np.argmax(rrow), rrow[np.argmax(rrow)]
        c, cmax = np.argmax(rcol), rcol[np.argmax(rcol)]

        if(rmax >= cmax):
            i = (0, r)
        else:
            i = (1, c)
        self.debug(f'[>] : Regret found at {i}')
        return i

    def getMinRegret(self, axis, index):
        if axis == 0:
            vector = self.costs[index, :]
            self.debug(self.getIndexMin(vector))
            cords = np.array([index, self.getIndexMin(vector)[0].item()])
        else:
            vector = self.costs[:, index]
            self.debug(vector)
            self.debug(self.getIndexMin(vector))
            cords = np.array([self.getIndexMin(vector)[0].item(), index])
        gen_cords = cords + 1
        self.debug(
            f'[>>] : Based on regeret the cell with is min is {gen_cords}')
        return gen_cords

    def getIndexMin(self, arr):
        return np.argwhere(arr == np.min(arr))

    def getIndexMinCost(self):
        cells = self.getIndexMin(self.costs)
        Q_trans = []
        for i, j in cells:
            Q_trans.append(min([self.supply[i], self.demande[j]]))
        return cells[np.argmax(Q_trans)]

    def generate(self, mins=5, maxs=10, minc=5, maxc=10, minq=100, maxq=200, mincost=10, maxcost=100):
        Ns = random.randint(mins, maxs)
        Nd = random.randint(minc, maxc)
        Qty = random.randint(minq, maxq)
        self.supply = self.helpGen(Ns, Qty)
        self.demande = self.helpGen(Nd, Qty)
        # self.debug(f'index of zero : {np.argwhere(self.supply == 0)}')
        # self.debug(f'shape : {self.supply.shape}')

        # self.debug(f'TOT S: {self.supply.size}, ZEROS S : {self.supply.size - np.count_nonzero(self.supply)}')
        # self.debug(f'TOT D: {self.demande.size},ZEROS D : {self.demande.size - np.count_nonzero(self.demande)}')

        self.costs = self.genCostMatrix(Ns, Nd, mincost, maxcost)
        self.setup()

    def helpGen(self, maxi, Qty):
        rndnbrs = np.random.randint(2, 10, size=maxi)
        rsum = np.sum(rndnbrs)
        new_nbrs = rndnbrs*Qty//rsum
        new_sum = np.sum(new_nbrs)
        diff = Qty - new_sum
        new_nbrs[0] = new_nbrs[0] + diff
        # zeros_count = new_nbrs.size - np.count_nonzero(new_nbrs)
        return new_nbrs

    def genCostMatrix(self, Ns, Nd, mincost, maxcost):
        return np.random.randint(mincost, maxcost, size=(Ns, Nd))

    def printT(self, data):
        print(data)

    def debug(self, *args, **kwargs):
        if self.use_debug:
            print(*args, **kwargs)

    def progress(self, progress):
        progress = progress + "*"
        print(progress, end="")
        return progress
