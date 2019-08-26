# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import clr
clr.AddReference("System")
clr.AddReference("QuantConnect.Algorithm")
clr.AddReference("QuantConnect.Indicators")
clr.AddReference("QuantConnect.Common")

from System import *
from QuantConnect import *
from QuantConnect.Algorithm import *
from QuantConnect.Indicators import *
import decimal as d


class MovingAverageCrossAlgorithm(QCAlgorithm):

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        self.SetStartDate(2008, 1, 1)    #Set Start Date
        self.SetEndDate(2019, 7, 31)      #Set End Date
        self.SetCash(100000)             #Set Strategy Cash
        # Find more symbols here: http://quantconnect.com/data
        self.AddEquity("SPY")

        # create a 15-day exponential moving average
        self.fast = self.EMA("SPY", 15, Resolution.Daily);

        # create a 60-day exponential moving average
        self.slow = self.EMA("SPY", 60, Resolution.Daily);

        self.previous = None


    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.'''
        

        # wait for our slow ema to fully initialize
        if not self.slow.IsReady:
            return

        # only once per day
        if self.previous is not None and self.previous.date() == self.Time.date():
            return

        # define a small tolerance on our checks to avoid bouncing
        tolerance = 0.00015;

        holdings = self.Portfolio["SPY"].Quantity

        # we liquidate the Short and go Long
        if holdings <= 0:
            # if the fast is greater than the slow, we'll go long
            if self.fast.Current.Value > self.slow.Current.Value * d.Decimal(1 + tolerance):
                self.Log("BUY  >> {0}".format(self.Securities["SPY"].Price))
                self.Liquidate("SPY")
                self.Buy("SPY", 1000)

        # we liquidate the Long and go Short
        # if the fast is less than the slow we'll liquidate our long
        if holdings > 0 and self.fast.Current.Value < self.slow.Current.Value:
            self.Log("SELL >> {0}".format(self.Securities["SPY"].Price))
            self.Liquidate("SPY")
            self.Sell("SPY", 1000)

        self.previous = self.Time