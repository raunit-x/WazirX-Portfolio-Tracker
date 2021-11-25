# WazirX Portfolio Tracker on your Terminal!
<p align="center">
  <img src='/Images/logo.png' width='100'/>
</p>
If you have been investing in cryptocurrencies in India, there is a very good chance that you have been using <a href="https://wazirx.com/">WazirX</a>. If that's the case then you must have also realized that WazirX does <b>not</b> have P&L stats, total gains, which token is doing the best and so on for your portfolio! You can get <a href="https://medium.com/wazirx/trading-report-arrives-on-wazirx-b50ec4f15ecd">comprehensive trading reports</a> but then you would have to open the Excel sheets and study those to get your basic stats!


<h2>Get all the stats right on your Terminal!</h2>
<p align="center">
  <img src='/Images/ss.png' width='800'/>
</p>

<h2>Features</h2>
<ol>
<li>Using the <a href="https://github.com/WazirX/wazirx-api">public WazirX API</a> for exact prices</li>
<li>Get all the current holdings gains/losses</li>
<li>Overall gains/losses for your current portfolio of tokens and deposits</li>
<li>Real time data (updated every 10 seconds)</li>
<li>Multithreading for API Calls (10-15x performance gains)</li>
<li>High precision calculations using <code>Decimal</code> library</li>
<li>All the stats right on your Terminal with one single command</li>
</ol>


<h2>Installation and Usage</h2>
<ol>
<li>Clone the repo and install the dependencies from <code>requirements.txt</code></li>
<li>Download your <a href="https://medium.com/wazirx/trading-report-arrives-on-wazirx-b50ec4f15ecd">Trading Report</a></li>
<li>On your Terminal: <code>export TRADING_REPORT_PATH='YOUR_TRADING_REPORT_ABSOLUTE_PATH'</code></li>
<li>On your Terminal: <code>alias crypto="your_python_path absolute_path_of_repo/main.py"</code></li>
<li>Enjoy real-time stats with just on single command on your Terminal: <code>crypto</code></li>
</ol>

<h2>TODO (TO THE MOON!)</h2>
<ol>
<li>Currently only supports transactions/exchanges from <code>Token/INR or token/USDT</code>; Add support for all exchanges</li>
<li>Parse <code>P2P Trades</code>, <code>OTC Trades</code>, <code>Additional Transfers</code>, <code>STF Trades</code> and <code>Third Party Transfers</code> from the Trading Report xlsx file</li>
<li>Add CL arguments to sort according to different metrics</li>
<li>Automate the addition of all your Trading Reports in one file</li>
<li>Add alerts for different price points; leading to actionable results such as buying/selling on targets</li>
</ol>
