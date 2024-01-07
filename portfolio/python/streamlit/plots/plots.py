import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from ta.momentum import RSIIndicator
from ta.trend import MACD


class MacdRsiVolumeCandelstickChart:
    def get_closed_dates(self, df):
        """Return a list containing all dates on which the stock market was closed."""
        # Create a dataframe that contains all dates from the start until today.
        timeline = pd.date_range(
            start=df['Date'].iloc[0], end=df['Date'].iloc[-1])

        # Create a list of the dates existing in the dataframe.
        df_dates = [day.strftime('%Y-%m-%d')
                    for day in pd.to_datetime(df['Date'])]

        # Finally, determine which dates from the 'timeline' do not exist in our dataframe.
        closed_dates = [
            day for day in timeline.strftime('%Y-%m-%d').tolist()
            if not day in df_dates
        ]

        return closed_dates

    def calculate_rsi(self, df):
        df['RSI'] = RSIIndicator(df.Close).rsi()
        return df

    def calculate_macd(self, df):
        macd = MACD(df.Close)
        df['MACD'] = macd.macd()
        df['Signal'] = macd.macd_signal()
        df['Histogram'] = macd.macd_diff()
        return df

    def get_trading_strategy(self, df, column='Close'):
        """Return the Buy/Sell signal on the specified (price) column (Default = 'Close')."""
        buy_list, sell_list = [], []
        flag = False

        for i in range(0, len(df)):
            if df['MACD'].iloc[i] > df['Signal'].iloc[i] and flag == False:
                buy_list.append(df[column].iloc[i])
                sell_list.append(np.nan)
                flag = True

            elif df['MACD'].iloc[i] < df['Signal'].iloc[i] and flag == True:
                buy_list.append(np.nan)
                sell_list.append(df[column].iloc[i])
                flag = False

            else:
                buy_list.append(np.nan)
                sell_list.append(np.nan)

        df['Buy'] = buy_list
        df['Sell'] = sell_list

        return df

    def plot_candlestick_chart(self, fig, df, row, column=1, plot_EMAs=True, plot_strategy=True):
        """Return a graph object figure containing a Candlestick chart in the specified row."""
        fig.add_trace(go.Candlestick(x=df['Date'],
                                     open=df['Open'],
                                     high=df['High'],
                                     low=df['Low'],
                                     close=df['Close'],
                                     name='Candlestick Chart'),
                      row=row,
                      col=column)

        # If the boolean argument plot_EMAs is True, then show the line plots for the two exponential moving averages.
        if (plot_EMAs == True):
            fig.add_trace(go.Scatter(x=df['Date'],
                                     y=df['EMA-12'],
                                     name='12-period EMA',
                                     line=dict(color='dodgerblue', width=2)),
                          row=row,
                          col=column)

            fig.add_trace(go.Scatter(x=df['Date'],
                                     y=df['EMA-26'],
                                     name='26-period EMA',
                                     line=dict(color='whitesmoke', width=2)),
                          row=row,
                          col=column)

        if (plot_strategy == True):
            fig.add_trace(go.Scatter(x=df['Date'],
                                     y=df['Buy'],
                                     name='Buy Signal',
                                     mode='markers',
                                     marker_symbol='triangle-up',
                                     marker=dict(size=9),
                                     line=dict(color='Lime')),
                          row=row,
                          col=column)

            fig.add_trace(go.Scatter(x=df['Date'],
                                     y=df['Sell'],
                                     name='Sell Signal',
                                     mode='markers',
                                     marker_symbol='triangle-down',
                                     marker=dict(size=9, color='Yellow')),
                          row=row,
                          col=column)

        fig.update_xaxes(rangeslider={
            'visible': False
        })
        fig.update_yaxes(title_text='Price (₹)', row=row, col=column)

        return fig

    def plot_MACD(self, fig, df, row, column=1):
        """Return a graph object figure containing the MACD indicator, the signal line, and a histogram in the specified row."""
        df['Hist-Color'] = np.where(df['Histogram'] < 0, 'red', 'green')
        fig.add_trace(go.Bar(x=df['Date'],
                             y=df['Histogram'],
                             name='Histogram',
                             marker_color=df['Hist-Color'],
                             showlegend=True),
                      row=row,
                      col=column)

        fig.add_trace(go.Scatter(x=df['Date'],
                                 y=df['MACD'],
                                 name='MACD',
                                 line=dict(color='darkorange', width=2)),
                      row=row,
                      col=column)

        fig.add_trace(go.Scatter(x=df['Date'],
                                 y=df['Signal'],
                                 name='Signal',
                                 line=dict(color='cyan', width=2)),
                      row=row,
                      col=column)

        fig.update_yaxes(title_text='MACD', row=row, col=column)

        return fig

    def plot_RSI(self, fig, df, row, column=1):
        """Return a graph object figure containing the RSI indicator in the specified row."""
        fig.add_trace(go.Scatter(x=df['Date'].iloc[30:],
                                 y=df['RSI'].iloc[30:],
                                 name='RSI',
                                 line=dict(color='gold', width=2)),
                      row=row,
                      col=column)

        fig.update_yaxes(title_text='RSI', row=row, col=column)

        # Add one red horizontal line at 70% (overvalued) and green line at 30% (undervalued)
        for y_pos, color in zip([70, 30], ['Red', 'Green']):
            fig.add_shape(x0=df['Date'].iloc[1],
                          x1=df['Date'].iloc[-1],
                          y0=y_pos,
                          y1=y_pos,
                          type='line',
                          line=dict(color=color, width=2),
                          row=row,
                          col=column)

        # Add a text box for each line
        for y_pos, text, color in zip([64, 36], ['Overvalued', 'Undervalued'], ['Red', 'Green']):
            fig.add_annotation(x=df['Date'].iloc[int(df['Date'].shape[0] / 10)],
                               y=y_pos,
                               text=text,
                               font=dict(size=14, color=color),
                               bordercolor=color,
                               borderwidth=1,
                               borderpad=2,
                               bgcolor='lightsteelblue',
                               opacity=0.75,
                               showarrow=False,
                               row=row,
                               col=column)

        # Update the y-axis limits
        ymin = 25 if df['RSI'].iloc[30:].min(
        ) > 25 else df['RSI'].iloc[30:].min() - 5
        ymax = 75 if df['RSI'].iloc[30:].max(
        ) < 75 else df['RSI'].iloc[30:].max() + 5
        fig.update_yaxes(range=[ymin, ymax], row=row, col=column)

        return fig

    def plot_volume(self, fig, df, row, column=1):
        """Return a graph object figure containing the volume chart in the specified row."""
        fig.add_trace(go.Bar(x=df['Date'],
                             y=df['Volume'],
                             marker=dict(color='lightskyblue',
                                         line=dict(color='firebrick', width=0.1)),
                             showlegend=False,
                             name='Volume'),
                      row=row,
                      col=column)

        fig.update_xaxes(title_text='Date', row=row, col=column)
        fig.update_yaxes(title_text='Volume (₹)', row=row, col=column)

        return fig

    def plot(self, df, ticker):
        df = self.calculate_macd(df)
        df = self.calculate_rsi(df)
        closed_dates_list = self.get_closed_dates(df)

        df = self.get_trading_strategy(df)
        df['EMA-12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA-26'] = df['Close'].ewm(span=26, adjust=False).mean()

        ########## Plot the four plots ##########
        fig = make_subplots(rows=4,
                            cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.005,
                            row_width=[0.2, 0.3, 0.3, 0.8])

        fig = self.plot_candlestick_chart(fig,
                                          df,
                                          row=1,
                                          plot_EMAs=True,
                                          plot_strategy=True)
        fig = self.plot_MACD(fig, df, row=2)
        fig = self.plot_RSI(fig, df, row=3)
        fig = self.plot_volume(fig, df, row=4)

        ########## Customise the figure ##########
        # Update xaxis properties
        fig.update_xaxes(rangebreaks=[dict(values=closed_dates_list)],
                         range=[df['Date'].iloc[0] - datetime.timedelta(days=3),
                                df['Date'].iloc[-1] + datetime.timedelta(days=3)],
                         title_text='Date',
                         rangeslider_visible=True,
                         )

        # Update basic layout properties (width&height, background color, title, etc.)
        fig.update_layout(
            # width=800,
            # height=800,
            # plot_bgcolor='#0E1117',
            # paper_bgcolor='#0E1117',
            title={
                'text': '{} - Stock Dashboard'.format(ticker),
                'y': 0.98
            },
            hovermode='x unified',
            legend=dict(orientation='h',
                        xanchor='left',
                        x=0.05,
                        yanchor='bottom',
                        y=1.003))

        # Customize axis parameters
        axis_lw, axis_color = 2, 'black'
        fig.update_layout(xaxis1=dict(linewidth=axis_lw,
                                      linecolor=axis_color,
                                      mirror=True,
                                      showgrid=False),
                          yaxis1=dict(linewidth=axis_lw,
                                      linecolor=axis_color,
                                      mirror=True,
                                      showgrid=False),
                          font=dict(color=axis_color))

        fig.update_layout(xaxis2=dict(linewidth=axis_lw,
                                      linecolor=axis_color,
                                      mirror=True,
                                      showgrid=False),
                          yaxis2=dict(linewidth=axis_lw,
                                      linecolor=axis_color,
                                      mirror=True,
                                      showgrid=False),
                          font=dict(color=axis_color))

        fig.update_layout(xaxis3=dict(linewidth=axis_lw,
                                      linecolor=axis_color,
                                      mirror=True,
                                      showgrid=False),
                          yaxis3=dict(linewidth=axis_lw,
                                      linecolor=axis_color,
                                      mirror=True,
                                      showgrid=False),
                          font=dict(color=axis_color))

        fig.update_layout(xaxis4=dict(linewidth=axis_lw,
                                      linecolor=axis_color,
                                      mirror=True,
                                      showgrid=False),
                          yaxis4=dict(linewidth=axis_lw,
                                      linecolor=axis_color,
                                      mirror=True,
                                      showgrid=False),
                          font=dict(color=axis_color))

        fig.update_layout(
            autosize=False,
            width=800,
            height=1200, )
        return fig
