import axios from "axios";

axios.defaults.baseURL = process.env.REACT_APP_API_URL;

const response = (resp) => resp.data

const requests = {
    get: (url) => axios.get(url).then(response)
}

const endPoints = {
    account: () => requests.get("/account"),
    options: () => requests.get("/options"),
    prices_candle: (p,g,c) => requests.get(`/prices-candle/${p}/${g}/${c}`),
    prices_candle_db: (p,g,c) => requests.get(`/prices-candle-db/${p}/${g}/${c}`),
    donchian_indicator: (p,g,c,window) => requests.get(`/technicals/indicator/donchian/${p}/${g}/${c}/${window}`),
    single_backtest: (p,g,window,prewindow,strategy) => requests.get(`/single-backtest/${p}/${g}/${window}/${prewindow}/${strategy}`)
}

export default endPoints;