import numpy as np

def initialize(context): 
    context.universe = [sid(8554),   #SPY Index - SPY
                        sid(23911),  #1-3 Yr Treasury Bond - SHY
                        sid(33147),  #10-20Yr Tresury Bond - TLH
                        sid(23921),  #20 Yr Tresury Bond - TLT
                        sid(19659),  #Consumer Staples ETF - XLP
                        sid(19662),  #Consumer Discretionary ETF - XLY
                        sid(19655),  #Energy ETF - XLE
                        sid(19656),  #Financials ETF - XLF
                        sid(26807),  #Gold - GLD
                        sid(19661),  #Health Care - XLV
                        sid(19657),  #Industrials ETF - XLI
                        sid(19654),  #Materials ETF - XLB
                        sid(33268),  #Services ETF - UCC
                        sid(19658),  #Technology ETF - XLK
                        sid(19660)]  #Utilities ETF - XLU
    
  
    schedule_function(my_rebalance, date_rules.month_end(), time_rules.market_close(hours=1))
    #Will Run M-F At 10:00
    
    set_slippage(slippage.FixedSlippage(spread=0.00))
    #0 Spread - No Commission To Broker


def my_rebalance(context,data):
    closings = data.history(context.universe, fields = "price", bar_count = 61, frequency = "1d")
    return_20days = closings.ix[-2] / closings.ix[-21] - 1 
    #Closing Price From 2 Bars Divided By Closing 21 Bars Ago Minus One, A Percentage
    return_60days = closings.ix[-2] / closings.ix[-61] - 1
    #Closing Price From 2 Bars Divided By Closing 61 Bars Ago Minus One, A Percentage
    return_daily = closings.pct_change(1)
    #Percent Change Closing Equals Daily Return
    roll_vol_20days = return_daily.ix[-21:-1].std(axis = 0)
    rank_20days_ret = return_20days.rank(ascending=False)
    rank_60days_ret = return_60days.rank(ascending=False)
    rank_20days_roll_vol = roll_vol_20days.rank(ascending=True)
    #If Ascending is T/F, sets Variables
    weighted_rank = rank_20days_ret * 0.3 + rank_60days_ret * 0.4 + rank_20days_roll_vol * 0.3
    # 20 Day Gets Multiplied By 0.3
    # 60 Day Gets Multiplied By 0.4
    # 20 Day Volitility Gets Multiplied By 0.3
    context.to_buy = weighted_rank.sort_values(ascending = True).index[:5].tolist()
    #PERSONAL PREFERENCE: For a more conservative strategy,, lower that ^ number
    #Whereas, for a more risky/rewardy system, make said number closer to XXX
    print(context.to_buy)
    for security in context.universe:
        if (security not in context.to_buy) & (data.can_trade(security)):
            order_target_percent(security,0)
        elif (security in context.to_buy) & (data.can_trade(security)):
            order_target_percent(security, 0.5)
