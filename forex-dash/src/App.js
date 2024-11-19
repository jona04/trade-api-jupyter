import './App.css';
import NavigationBar from "./components/NavigationBar"
import {
  BrowserRouter,
  Route,
  Routes
} from 'react-router-dom';
import Home from "./pages/Home"
import Dashboard from "./pages/Dashboard"
import Footer from './components/Footer';
import Backtest from './pages/Backtest';

function App() {

  return (
    <>
      <BrowserRouter>
        <div id="app-holder">
          <NavigationBar />
          <div className='container'>
            <Routes>
              <Route exact path="/" element={<Home />}/>
              <Route exact path="/dashboard" element={<Dashboard />}/>
              <Route exact path="/backtest" element={<Backtest />}/>
            </Routes>
          </div>
          <Footer />
        </div>
      </BrowserRouter>
    </>
  );
}

export default App;
