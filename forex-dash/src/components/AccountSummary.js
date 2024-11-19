import React, { useEffect, useState } from 'react'
import TitleHead from './TitleHead'
import endPoints from '../app/api';

const DATA_KEYS = [
  { name: "Account Num.", key: "Id", fixed: -1 },
  { name: "Leverage", key: "Leverage", fixed: -1 },
  { name: "Balance", key: "Balance", fixed: -1 },
  { name: "Profit", key: "Profit", fixed: -1 },
  { name: "Commission", key: "Commission", fixed: -1 },
  { name: "Swap", key: "Swap", fixed: -1 },
  { name: "Equity", key: "Equity", fixed: -1 },
  { name: "Margin", key: "Margin", fixed: -1 },
]

function AccountSummary() {

  const [account,setAccount] = useState(null);

  useEffect(() => {
    loadAccount();
  }, [])

  const loadAccount = async () => {
    const data = await endPoints.account();
    setAccount(data);
  }

  return (
    <div>
        <TitleHead title="Account Summary" />
        {
          account && <div className='segment'>
              {
                DATA_KEYS.map(item => {
                  return <div key={item.key} className='account-row'>
                    <div className='bold header'>{item.name}</div>
                    <div>{account[item.key]}</div>
                  </div>
                })
              }
            </div>
        }
    </div>
  )
}

export default AccountSummary