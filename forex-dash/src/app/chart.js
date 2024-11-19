import Plotly from 'plotly.js-dist';

export function drawChart(chartData, p, g, divName, indicadorData) {
    if (indicadorData !== null) {
        chartData = indicadorData   
    }
    
    let trace = {
        x: chartData.sTime,
        close: chartData.mid_c,
        high: chartData.mid_h,
        low: chartData.mid_l,
        open: chartData.mid_o,
        type: 'candlestick',
        xaxis: 'x',
        yaxis: 'y',
        increasing: { line: { width: 1, color: '#24A06B'}, fillColor: "#24A06B" },
        decreasing: { line: { width: 1, color: '#CC2E3C'}, fillColor: "#CC2E3C" }          
    }

    let data = [trace]

    if (indicadorData !== null) {
        let trace_indicator1 = {
            x: chartData.sTime,
            y: chartData.donchian_high,
            type: 'scatter'
        }
        let trace_indicator2 = {
            x: chartData.sTime,
            y: chartData.donchian_mid,
            type: 'scatter'
        }
        let trace_indicator3 = {
            x: chartData.sTime,
            y: chartData.donchian_low,
            type: 'scatter'
        }
        data.push(trace_indicator1);
        data.push(trace_indicator2);
        data.push(trace_indicator3);
    }

    let layout = {
        title: `Data for ${p} ${g}`,
        heigh: '100%',
        autosize: true,
        showlegend: false,
        margin: {
            l: 50, r:50, b:50, t:50
        },
        xaxis: {
            rangeslider: {
                visible: false
            },
            nticks: 10
        },
    };

    Plotly.newPlot(divName, data, layout, { responsive: true });
    Plotly.Plots.resize(document.getElementById(divName));
}