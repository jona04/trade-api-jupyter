class TradeDecision:

    def __init__(self, row):
        self.signal = row.SIGNAL
        self.sl = row.SL
        self.tp = row.TP
        self.pair = row.PAIR
        self.mid_c = row.mid_c
        self.ask_c = row.ask_c
        self.bid_c = row.bid_c
        
    def __repr__(self):
        return f"TradeDecision(): {self.pair} dir:{self.signal} sl:{self.sl:.4f} tp:{self.tp:.4f}"