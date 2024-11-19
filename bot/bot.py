import json
import time
from bot.candle_manager import CandleManager
from bot.technicals_manager import get_trade_decision
from bot.trade_manager import place_trade, trade_is_open, close_trade

from infrastructure.log_wrapper import LogWrapper
from models.trade_settings import TradeSettings
from api.fxopen_api import FxOpenApi
import constants.defs as defs



class Bot:

    ERROR_LOG = "error"
    MAIN_LOG = "main"
    GRANULARITY = "M1"
    SLEEP = 10

    def __init__(self):
        self.load_settings()
        self.setup_logs()

        self.api = FxOpenApi()
        self.candle_manager = CandleManager(self.api, self.trade_settings, self.log_message, Bot.GRANULARITY)

        self.log_to_main("Bot started")
        self.log_to_error("Bot started")

    def load_settings(self):
        with open("./bot/settings.json", "r") as f:
            data = json.loads(f.read())
            self.trade_settings = { k: TradeSettings(v, k) for k, v in data['pairs'].items() }
            self.trade_risk = data['trade_risk']

    def setup_logs(self):
        self.logs = {}
        for k in self.trade_settings.keys():
            self.logs[k] = LogWrapper(k)
            self.log_message(f"{self.trade_settings[k]}", k)
        self.logs[Bot.ERROR_LOG] = LogWrapper(Bot.ERROR_LOG)
        self.logs[Bot.MAIN_LOG] = LogWrapper(Bot.MAIN_LOG)
        self.log_to_main(f"Bot started with {TradeSettings.settings_to_str(self.trade_settings)}")

    def log_message(self, msg, key):
        self.logs[key].logger.debug(msg)

    def log_to_main(self, msg):
        self.log_message(msg, Bot.MAIN_LOG)

    def log_to_error(self, msg):
        self.log_message(msg, Bot.ERROR_LOG)

    def process_candles(self, triggered):
        if len(triggered) > 0:
            self.log_message(f"process_candles triggered:{triggered}", Bot.MAIN_LOG)
            for p in triggered:
                last_time = self.candle_manager.timings[p].last_time
                trade_decision = get_trade_decision(last_time, p, Bot.GRANULARITY, self.api, 
                                                       self.trade_settings[p],  self.log_message)
                if trade_decision is not None and trade_decision.signal != defs.NONE:
                    self.log_message(f"Place Trade: {trade_decision}", p)
                    self.log_to_main(f"Place Trade: {trade_decision}")
                    place_trade(trade_decision, self.api, self.log_message, self.log_to_error, self.trade_risk)


                ot = trade_is_open(trade_decision.pair)
                if ot is not None:

                    min_acumulated_loss = acumulated_loss[0] if len(acumulated_loss) > 0 else 0.0
                    value_loss_trans_cost = self.neg_multiplier*min_acumulated_loss
                    self.count += 1
                    if ot.side == 'Buy':
                        if min_acumulated_loss > 0.0:
                            result = (trade_decision.bid_c - self.start_price) / self.trade_settings[p].pip_value
                            if result >= value_loss_trans_cost:
                                # self.trigger_type = TRIGGER_TYPE_ACUMULATED_LOSS
                                # acumulated_loss = self.close_trade(list_values, index, value_loss_trans_cost, trade_decision.bid_c, acumulated_loss)
                                close_trade()
                            elif ot.side == 'Sell':
                                # self.trigger_type = TRIGGER_TYPE_REVERSED_CROSS
                                # result = (trade_decision.bid_c - self.start_price) / self.trade_settings[p].pip_value
                                # acumulated_loss = self.close_trade(list_values, index, result, trade_decision.bid_c, acumulated_loss)
                                close_trade()
                        elif ot.side == 'Sell':
                            # self.trigger_type = TRIGGER_TYPE_REVERSED_CROSS
                            # result = (trade_decision.bid_c - self.start_price) / self.trade_settings[p].pip_value
                            # acumulated_loss = self.close_trade(list_values, index, result, trade_decision.bid_c, acumulated_loss)
                            close_trade()
                        

                    if ot.side == 'Sell':
                        if min_acumulated_loss > 0.0:
                            result = (self.start_price - trade_decision.ask_c) / self.trade_settings[p].pip_value
                            if result >= value_loss_trans_cost:
                                # self.trigger_type = TRIGGER_TYPE_ACUMULATED_LOSS
                                # acumulated_loss = self.close_trade(list_values, index, value_loss_trans_cost, trade_decision.ask_c, acumulated_loss)
                                close_trade()
                            elif ot.side == 'Buy':
                                # self.trigger_type = TRIGGER_TYPE_REVERSED_CROSS
                                # result = (trade_decision.ask_c - self.start_price) / self.trade_settings[p].pip_value
                                # acumulated_loss = self.close_trade(list_values, index, result, trade_decision.ask_c, acumulated_loss)
                                close_trade()
                        elif ot.side == 'Buy':
                            # self.trigger_type = TRIGGER_TYPE_REVERSED_CROSS
                            # result = (self.start_price - trade_decision.ask_c) / self.trade_settings[p].pip_value
                            # acumulated_loss = self.close_trade(list_values, index, result,trade_decision.ask_c, acumulated_loss)
                            close_trade()
                    










    def run(self):
        while True:
            time.sleep(Bot.SLEEP)
            try:
                self.process_candles(self.candle_manager.update_timings())
            except Exception as error:
                self.log_to_error(f"CRASH: {error}")
                break
    

