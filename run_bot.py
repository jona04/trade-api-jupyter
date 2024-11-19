from bot.bot import Bot
from infrastructure.quotehistory_collection import quotehistoryCollection

if __name__ == "__main__":
    quotehistoryCollection.LoadQuotehistory("./data")
    b = Bot()
    b.run()