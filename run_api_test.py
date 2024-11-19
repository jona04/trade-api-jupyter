from api.fxopen_api import FxOpenApi


if __name__ == "__main__":
    api = FxOpenApi()


    print("\n get account information")
    print(api.get_account())


    print("\n test get account instruments")
    print(api.get_quotehistory())