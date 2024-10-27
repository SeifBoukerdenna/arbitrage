# visualization_widget.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar  # Added for toolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


class VisualizationWidget(QWidget):
    """Widget for displaying data visualizations."""

    def __init__(self, strategy=None):
        super().__init__()
        self.strategy = strategy
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Dropdown to select visualization type
        self.chart_selector = QComboBox()
        self.chart_selector.addItems([
            "Odds Distribution",
            "Expected Value Distribution",
            "Risk-Return Plot",
            "Stake Allocation",
            "Cumulative Return",
            "Probability vs. Odds"
        ])
        self.chart_selector.currentIndexChanged.connect(self.update_plot)
        layout.addWidget(QLabel("Select Chart Type:"))
        layout.addWidget(self.chart_selector)

        # Matplotlib Figure and Canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Add navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

        self.setLayout(layout)

    def set_strategy(self, strategy):
        self.strategy = strategy
        self.update_plot()

    def update_plot(self):
        if not self.strategy or not self.strategy.combinations:
            self.figure.clear()
            self.canvas.draw()
            return

        chart_type = self.chart_selector.currentText()
        self.figure.clear()

        if chart_type == "Odds Distribution":
            self.plot_odds_distribution()
        elif chart_type == "Expected Value Distribution":
            self.plot_ev_distribution()
        elif chart_type == "Risk-Return Plot":
            self.plot_risk_return()
        elif chart_type == "Stake Allocation":
            self.plot_stake_allocation()
        elif chart_type == "Cumulative Return":
            self.plot_cumulative_return()
        elif chart_type == "Probability vs. Odds":
            self.plot_probability_vs_odds()

        self.canvas.draw()

    def plot_odds_distribution(self):
        odds = [combo.combined_odds for combo in self.strategy.combinations]
        ax = self.figure.add_subplot(111)
        ax.hist(odds, bins=20, color='skyblue', edgecolor='black')
        ax.set_title('Odds Distribution')
        ax.set_xlabel('Combined Odds')
        ax.set_ylabel('Frequency')

    def plot_ev_distribution(self):
        evs = [combo.ev_per_dollar for combo in self.strategy.combinations]
        ax = self.figure.add_subplot(111)
        ax.hist(evs, bins=20, color='lightgreen', edgecolor='black')
        ax.set_title('Expected Value Distribution')
        ax.set_xlabel('Expected Value per Dollar')
        ax.set_ylabel('Frequency')

    def plot_risk_return(self):
        returns = [combo.ev_per_dollar for combo in self.strategy.combinations]
        risks = [np.sqrt(combo.combined_prob * (1 - combo.combined_prob)) for combo in self.strategy.combinations]
        ax = self.figure.add_subplot(111)
        sc = ax.scatter(risks, returns, c=returns, cmap='coolwarm')
        ax.set_title('Risk-Return Plot')
        ax.set_xlabel('Risk (Standard Deviation)')
        ax.set_ylabel('Expected Return')
        cbar = self.figure.colorbar(sc, ax=ax, label='Expected Return')

        # Annotate function for hover tooltips
        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def update_annot(ind):
            index = ind["ind"][0]
            annot.xy = (risks[index], returns[index])
            text = f"Risk: {risks[index]:.4f}\nReturn: {returns[index]:.4f}"
            annot.set_text(text)
            annot.get_bbox_patch().set_facecolor('lightyellow')
            annot.get_bbox_patch().set_alpha(0.9)

        def on_hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, ind = sc.contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    self.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        self.canvas.draw_idle()

        self.canvas.mpl_connect("motion_notify_event", on_hover)

    def plot_stake_allocation(self):
        allocations = self.strategy.stake_allocation
        labels = [', '.join(bet.name for bet in combo.bets) for combo in self.strategy.combinations]
        # Only plot combinations with non-zero allocations
        allocations_labels = [(alloc, label) for alloc, label in zip(allocations, labels) if alloc > 0]
        if not allocations_labels:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No stake allocations to display.', ha='center', va='center')
            return
        allocations, labels = zip(*allocations_labels)
        ax = self.figure.add_subplot(111)
        ax.pie(allocations, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.set_title('Stake Allocation')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    def plot_cumulative_return(self):
        returns = [combo.ev_per_dollar for combo in self.strategy.combinations]
        cumulative_returns = np.cumsum(returns)
        ax = self.figure.add_subplot(111)
        ax.plot(cumulative_returns)
        ax.set_title('Cumulative Return')
        ax.set_xlabel('Combination Index')
        ax.set_ylabel('Cumulative Expected Return')

    def plot_probability_vs_odds(self):
        probs = [combo.combined_prob for combo in self.strategy.combinations]
        odds = [combo.combined_odds for combo in self.strategy.combinations]
        ax = self.figure.add_subplot(111)
        sc = ax.scatter(probs, odds, color='purple')
        ax.set_title('Combined Probability vs. Combined Odds')
        ax.set_xlabel('Combined Probability')
        ax.set_ylabel('Combined Odds')

        # Annotate function for hover tooltips
        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def update_annot(ind):
            index = ind["ind"][0]
            annot.xy = (probs[index], odds[index])
            text = f"Probability: {probs[index]:.4f}\nOdds: {odds[index]:.2f}"
            annot.set_text(text)
            annot.get_bbox_patch().set_facecolor('lightyellow')
            annot.get_bbox_patch().set_alpha(0.9)

        def on_hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, ind = sc.contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    self.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        self.canvas.draw_idle()

        self.canvas.mpl_connect("motion_notify_event", on_hover)
