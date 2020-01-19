Array.from(document.getElementsByClassName('coingecko-line-chart')).forEach(chart => {
    const coinName = chart.dataset.coin;
    const vs_currency = coinName === 'bitcoin' ? 'usd' : "btc";

    fetch(`https://api.coingecko.com/api/v3/coins/${coinName}/market_chart?vs_currency=${vs_currency}&days=7`)
        .then(response => response.json())
        .then(({prices, total_volumes, market_caps}) => {
            const data = {
                datasets: [
                    {
                        label: 'Prices',
                        data: prices.map(x => x[1]),
                        backgroundColor: ['rgba(233, 241, 243, 0.5)'],
                        borderColor: ['rgb(0, 0, 255, 0.5)'],
                        borderWidth: 2
                    },
                    {
                        label: 'Total Volumes',
                        data: total_volumes.map(x => x[1]),
                        backgroundColor: ['rgba(233, 241, 243, 0.5)'],
                        borderColor: ['rgb(255, 0, 0, 0.5)'],
                        borderWidth: 2
                    },
                    {
                        label: 'Market caps',
                        data: market_caps.map(x => x[1]),
                        backgroundColor: ['rgba(233, 241, 243, 0.5)'],
                        borderColor: ['rgb(0, 255, 0, 0.5)'],
                        borderWidth: 2
                    },
                ],
                labels: prices.map(x => x[0]) // assume all three data buckets have the same time-values; just pick those from the 1st one
            };

            const options = {
                scales: {
                    xAxes: [{
                        type: 'time',
                        time: {
                            displayFormats: {
                                hour: 'DDD MMM - h a'
                            }
                        }
                    }],
                    yAxes: [
                        {
                            ticks: {
                                beginAtZero: true
                            }
                        }
                    ]
                }
            };

            const ctx = document.getElementById(`coingecko-line-chart-${coinName}`).getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data,
                options,
            });
        });
});
