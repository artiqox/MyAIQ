var coingeckocharts = document.getElementsByClassName("coingecko-line-chart");

for (var ii = 0; ii < coingeckocharts.length; ii++) {
let coinname = coingeckocharts[ii]["id"];
var vs_currency = "btc";
if (coinname == "bitcoin") {vs_currency = "usd"; }
const fetchPromise = fetch('https://api.coingecko.com/api/v3/coins/'+coinname+'/market_chart?vs_currency='+vs_currency+'&days=7');
const datadiv = document.getElementById("div-data-for-coingecko-line-chart-"+coinname);
fetchPromise.then(response => {
  return response.json();
}).then(market_charts_data => {
  var chart_styles = [";rgba(237, 231, 246, 0.5);deep-purple-500;deep-purple-700;2", ";rgba(232, 245, 233, 0.5);blue-500;blue-700;2",";rgba(233, 241, 243, 0.5);red-500;red-700;2"];
  var styles_index = 0;
  var my_div_with_data_text = "";
  for (var key in market_charts_data) {
    var array_with_ts = [];
    var array_with_data = [];
    my_div_with_data_text += "<input type='text' class='chart_serie_data' id='"+key+chart_styles[styles_index]+"' value='";
    for (var newindex = 0; newindex < market_charts_data[key].length; ++newindex) {var tempts = new Date(parseInt(market_charts_data[key][newindex][0]));array_with_ts.push(tempts.toISOString());array_with_data.push(market_charts_data[key][newindex][1]);}
    my_div_with_data_text += array_with_data.toString()+"'>";

    styles_index++;
  }
  my_div_with_data_text += "<input type='text' class='chart_labels' id='chart_labels' value='"+array_with_ts.toString()+"'>";
  datadiv.innerHTML = my_div_with_data_text;
});
}
