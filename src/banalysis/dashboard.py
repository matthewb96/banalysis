# -*- coding: utf-8 -*-
"""
    Module containing the class and functions to create the
    bokeh dashboard.
"""

##### IMPORTS #####
# Standard imports
import io
import base64
import math
import datetime as dt

# Third party imports
import numpy as np
from bokeh import models, layouts, plotting

# Local imports
from . import inputs


##### CONSTANTS #####

##### CLASSES #####
class Dashboard:
    """Class for creating bokeh dashboard for visualising midata transaction data."""

    def __init__(self, doc: plotting.Document):
        """
        Parameters
        ----------
        doc : plotting.Document
            Bokeh Document object for adding the dashboard
            to, usually just `curdoc()`.
        """
        self.doc = doc
        self.source = models.ColumnDataSource(inputs.EMPTY_MIDATA)
        self.file = models.FileInput(accept=".csv,.txt", sizing_mode="fixed")
        self.file.on_change("value", self._update_source)
        self.data_table = self.init_table()
        table_layout = layouts.column(
            self.file, self.data_table, sizing_mode="stretch_height"
        )

        self.all_plot = self.plot_all()
        plot_layout = layouts.column(self.all_plot, sizing_mode="stretch_both")

        layout = layouts.row(table_layout, plot_layout, sizing_mode="stretch_both")
        self.doc.add_root(layout)

    def init_table(self) -> models.DataTable:
        """Initialise the table for displaying the data.

        Returns
        -------
        models.DataTable
            Table object with columns for bank transaction
            data provided in midata format.
        """
        template = """
            <div style="color:<%= 
                (function colorfromint(){
                    if(value < 0){
                        return("red")
                    }
                    else if(value > 0){
                        return("green")
                    }
                    else {
                        return("gray")
                    }
                }()) %>;"> 
            <%= (value).toFixed(2) %></div>
        """
        formatter = models.HTMLTemplateFormatter(template=template)
        table_width = 600
        width = lambda x: int(table_width * x)
        columns = [
            models.TableColumn(
                field="date",
                title="Date",
                formatter=models.DateFormatter(),
                width=width(0.13),
            ),
            models.TableColumn(
                field="type", title="Transaction Type", width=width(0.16)
            ),
            models.TableColumn(
                field="description", title="Merchant/Description", width=width(0.3)
            ),
            models.TableColumn(
                field="amount",
                title="Credit/Debit (£)",
                formatter=formatter,
                width=width(0.15),
            ),
            models.TableColumn(
                field="balance",
                title="Balance (£)",
                formatter=formatter,
                width=width(0.15),
            ),
        ]
        table = models.DataTable(
            source=self.source,
            columns=columns,
            autosize_mode="none",
            width=table_width,
            sizing_mode="stretch_height",
        )
        return table

    def _update_source(self, attr, old, new):  # pylint: disable=unused-argument
        """Function to update the data `source` when new file inputs are given."""
        decoded = base64.b64decode(new)
        f = io.BytesIO(decoded)
        df = inputs.read_midata(f)
        self.source.data = df

        self.all_plot.x_range = models.DataRange1d(bounds=(min(df.date), max(df.date)))
        max_amount = (
            math.ceil(np.max(df[["balance", "abs_amount"]].values) / 1000) * 1000
        )
        self.all_plot.y_range = models.DataRange1d(bounds=(0, max_amount))

    def plot_all(self) -> plotting.Figure:
        """Creates plot containing all transations and balance over time.

        The plot will contain a line showing the balance over time, with
        scatter points to show the absolute value of each transation.

        Returns
        -------
        plotting.Figure
            Figure object with all midata transactions plotted.
        """
        balance_hover = models.HoverTool(
            names=["balance"],
            toggleable=False,
            tooltips=[
                ("Date", "@date{%d/%m/%Y}"),
                ("Balance (£)", "@balance{0,0.00}"),
            ],
            formatters={"@date": "datetime"},
        )
        amount_hover = models.HoverTool(
            names=["abs_amount"],
            toggleable=False,
            tooltips=[
                ("Date", "@date{%d/%m/%Y}"),
                ("Transaction (£)", "@amount{+0,0.00}"),
                ("Balance (£)", "@balance{+0,0.00}"),
                ("Merchant / Description", "@description"),
            ],
            formatters={"@date": "datetime"},
        )

        p = plotting.figure(
            title="All transactions",
            x_axis_label="Date",
            y_axis_label="Amount (£)",
            sizing_mode="stretch_both",
            tools=[
                "pan",
                "box_select",
                "xwheel_zoom",
                "reset",
                "save",
                balance_hover,
                amount_hover,
            ],
        )
        p.xaxis[0].formatter = models.DatetimeTickFormatter()
        p.y_range = models.DataRange1d(bounds=(0, 10000))
        epoch = dt.datetime.utcfromtimestamp(0)
        max_date = (dt.datetime.today() - epoch).total_seconds()
        min_date = max_date - (2 * 365 * 24 * 60 * 60)
        p.x_range = models.DataRange1d(bounds=(min_date * 1000, max_date * 1000))
        p.line(
            x="date",
            y="balance",
            source=self.source,
            legend_label="Balance",
            name="balance",
            line_width=2,
        )
        p.scatter(
            "date",
            "abs_amount",
            size=5,
            color="colour",
            name="abs_amount",
            source=self.source,
            legend_label="Absolute Transaction",
            fill_alpha=0.8,
        )

        p.legend.click_policy = "hide"
        return p
