class TradeSettings:

    def __init__(self, ob, pair):
        self.maxspread = ob['maxspread']
        self.mingain = ob['mingain']
        self.riskreward = ob['riskreward']
        self.ema1 = ob['ema1']
        self.ema2 = ob['ema2']
        self.ema3 = ob['ema3']
        self.pip_value = ob['pipvalue']
        self.TP = ob['TP']
        self.SL = ob['SL']

    def __repr__(self):
        return str(vars(self))

    @classmethod
    def settings_to_str(cls, settings):
        ret_str = "Trade Settings:\n"
        for _, v in settings.items():
            ret_str += f"{v}\n"

        return ret_str