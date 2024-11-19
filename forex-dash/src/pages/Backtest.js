import React, { useEffect, useState } from 'react'
import TitleHead from '../components/TitleHead';
import { PRE_WINDOWS, STRATEGIES, WINDOWS } from '../app/data';
import Select from '../components/Select';
import Button from '../components/Button';
import endPoints from '../app/api';

function Backtest() {

    const [ selectedPair, setSelectedPair ] = useState(null);
    const [ selectedGranularity, setSelectedGranularity ] = useState(null);
    const [ selectedWindow, setSelectedWindow ] = useState(WINDOWS[0].value);
    const [ selectedPreWindow, setSelectedPreWindow ] = useState(PRE_WINDOWS[0].value);
    const [ selectedStrategy, setSelectedStrategy ] = useState(STRATEGIES[0].value);
    const [ backtestResult, setBacktestResult ] = useState(null);
    const [ options, setOptions ] = useState(null);
    const [ loading, setLoading ] = useState(true);

    useEffect(() => {
        loadOptions();
    }, []);
    
    const loadOptions = async () => {
        const data = await endPoints.options();
        setOptions(data);
        setSelectedGranularity(data.granularities[0].value);
        setSelectedPair(data.pairs[0].value);
        setLoading(false);
    }

    const handleWindowChange = async (value) => {
        setSelectedWindow(value);
    }

    const handlePreWindowChange = async (value) => {
        setSelectedPreWindow(value);
    }

    const handleStrategyChange = async (value) => {
        setSelectedStrategy(value);
    }

    const startBacktest = async () => {
        const data = await endPoints.single_backtest(selectedPair, selectedGranularity, selectedWindow, selectedPreWindow,selectedStrategy);
        setBacktestResult(data);
    }

    if (loading === true) return <h1>Loading...</h1>
  
  return (
    <div>
        <TitleHead title="Backtest configurations" />
        <div className='segment options'>
            <Select 
                name="Currency"
                title="Select currency"
                options={options.pairs}
                defaultValue={selectedPair}
                onSelected={setSelectedPair}
            />
            <Select 
                name="Granularity"
                title="Select granularity"
                options={options.granularities}
                defaultValue={selectedGranularity}
                onSelected={setSelectedGranularity}
            />
            <Select 
                name="Strategy"
                title="Strategy"
                options={ STRATEGIES }
                defaultValue={selectedStrategy}
                onSelected={handleStrategyChange}
            />
            <Select
                name="Window"
                title="Window"
                options={ WINDOWS }
                defaultValue={selectedWindow}
                onSelected={handleWindowChange}
            />
            <Select 
                name="Window"
                title="Window"
                options={ PRE_WINDOWS }
                defaultValue={selectedPreWindow}
                onSelected={handlePreWindowChange}
            />
            <Button text="Start Backtest" handleClick={() => startBacktest()} />
            <div>
                {backtestResult}
            </div>
        </div>
    </div>
  )
}

export default Backtest