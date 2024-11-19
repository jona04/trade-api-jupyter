import React, { useEffect, useState } from 'react'
import { COUNTS, INDICATORS, WINDOWS } from '../app/data'
import Select from '../components/Select'
import TitleHead from '../components/TitleHead'
import Button from '../components/Button'
import endPoints from '../app/api'
import PriceChart from '../components/PriceChart'

function Dashboard() {

  const [ selectedPair, setSelectedPair ] = useState(null);
  const [ selectedGranularity, setSelectedGranularity ] = useState(null);
  const [ priceData, setPriceData ] = useState(null);
  const [ indicatorData, setIndicatorData ] = useState(null);
  const [ selectedCount, setSelectedCount ] = useState(COUNTS[0].value);
  const [ selectedWindow, setSelectedWindow ] = useState(WINDOWS[0].value);
  const [ selectedIndicator, setSelectedIndicator ] = useState(INDICATORS[0].value);
  const [ options, setOptions ] = useState(null);
  const [ loading, setLoading ] = useState(true);

  useEffect(() => {
    loadOptions();
  }, []);

  const handleIndicatorChange = async (value) => {
    if (value === ''){
      setIndicatorData(null)
    }
    setSelectedIndicator(value);
  }

  const handleWindowChange = async (value) => {
    if (value === ''){
      setIndicatorData(null)
    }
    setSelectedWindow(value);
  }

  const loadIndicator = async () => {
    const data = await endPoints.donchian_indicator(selectedPair, selectedGranularity, selectedCount, selectedWindow);
    setIndicatorData(data);
  }

  const handleCountChange = (count) => {
    setSelectedCount(count);
    loadPricesCandle(count);
  }

  const loadPricesCandle = async (count) => {
    switch (selectedIndicator) {
      case ('Donchian'):
        console.log("Loading Indicator");
        loadIndicator();
        break;
      default:
        console.log("Loading Price data");
        const data = await endPoints.prices_candle_db(selectedPair, selectedGranularity, count);
        setPriceData(data);
        break;
    }
  }

  const loadOptions = async () => {
    const data = await endPoints.options();
    setOptions(data);
    setSelectedGranularity(data.granularities[0].value);
    setSelectedPair(data.pairs[0].value);
    setLoading(false);
  }

  if (loading === true) return <h1>Loading...</h1>
  

  return (
    <div>
        <TitleHead title="Options" />
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
                name="numRows"
                title="Num. Rows."
                options={ COUNTS }
                defaultValue={selectedCount}
                onSelected={handleCountChange}
            />
            <Select 
                name="Indicator"
                title="Indicator"
                options={ INDICATORS }
                defaultValue={selectedIndicator}
                onSelected={handleIndicatorChange}
            />
            <Select 
                name="Window"
                title="Window"
                options={ WINDOWS }
                defaultValue={selectedWindow}
                onSelected={handleWindowChange}
            />
            <Button text="Load" handleClick={() => loadPricesCandle(selectedCount)} />
        </div>
        <TitleHead title="Price Chart" />
        { (priceData || indicatorData) && <PriceChart 
          selectedPair={selectedPair}
          selectedGranularity={selectedGranularity}
          priceData={priceData}
          indicatorData={indicatorData}
        />}
    </div>
  )
}

export default Dashboard