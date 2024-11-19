import React from 'react'
import Progress from './Progress'

const HEADERS = [
    "time", "mid_c"
]

function Technicals({data}) {
  return (
    <div className='segment'>
        <Progress title="Bullish"
                  color="#21ba25"
                //   percentage={data.percent_bulish}
                  percentage={20} />
        <Progress title="Bearish"
                  color="#db2828"
                //   percentage={data.percent_bulish}
                  percentage={300} />
        <table>
            <thead>
                <tr>{
                    HEADERS.map(item => {
                        return <th key={item}>{item}</th>
                    })
                }</tr>
                <tr>{
                    HEADERS.map(item => {
                        return <td key={item}>{data[item]}</td>
                    })
                }</tr>
            </thead>
        </table>
    </div>
  )
}

export default Technicals