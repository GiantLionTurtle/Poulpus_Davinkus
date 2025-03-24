from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Button
import numpy as np
import cv2 as cv

class Sliders:
    def __init__(self):
        pass

    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.35)
    r = 0.6
    g = 0.2
    b = 0.5

    # Create and plot a bar chart
    year = ['2002', '2004', '2006', '2008', '2010']
    production = [25, 15, 35, 30, 10]
    plt.bar(year, production, color=(r, g, b),
            edgecolor="black")

    # Create 3 axes for 3 sliders red,green and blue
    axred = plt.axes([0.25, 0.2, 0.65, 0.03])
    axgreen = plt.axes([0.25, 0.15, 0.65, 0.03])
    axblue = plt.axes([0.25, 0.1, 0.65, 0.03])

    # Create a slider from 0.0 to 1.0 in axes axred
    # with 0.6 as initial value.
    red = Slider(axred, 'Red', 0.0, 1.0, 0.6)

    # Create a slider from 0.0 to 1.0 in axes axgreen
    # with 0.2 as initial value.
    green = Slider(axgreen, 'Green', 0.0, 1.0, 0.2)

    # Create a slider from 0.0 to 1.0 in axes axblue
    # with 0.5(default) as initial value
    blue = Slider(axblue, 'Blue', 0.0, 1.0)

    # Create function to be called when slider value is changed

    def update(val):
        r = red.val
        g = green.val
        b = blue.val
        ax.bar(year, production, color=(r, g, b),
                    edgecolor="black")

    # Call update function when slider value is changed
    red.on_changed(update)
    green.on_changed(update)
    blue.on_changed

    #Create axes for reset button and create button
    resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
    button = Button(resetax, 'Reset', color='gold',
                    hovercolor='skyblue')

    # Create a function resetSlider to set slider to
    # initial values when Reset button is clicked

    def resetSlider(event):
        red.reset()
        green.reset()
        blue.reset()

    # Call resetSlider function when clicked on reset button
    button.on_clicked(resetSlider)

    # Display graph
    plt.show()