import React from 'react'

function Progress({ title, percentage, color }) {

    const style = {
        'width': `${percentage}px`,
        backgroundColor: color
    }

    return (
        <div className='progress-wrap'>
            <div className='progress-holder'>
                <div className='progress' style={style} />
            </div>
            <div className='progress-text' style={{color:color}}>
                {title}
            </div>
        </div>
    )
}

export default Progress