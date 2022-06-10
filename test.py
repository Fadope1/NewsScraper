from get_all_tickers import get_tickers

tickers = get_tickers.get_tickers(AMEX=False)
save_tickers(NYSE=True, filename="tickers_test.csv")
