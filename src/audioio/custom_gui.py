from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtWidgets import QAbstractButton, QSlider, QWidget, QVBoxLayout, QHBoxLayout,\
    QStyleOptionSlider, QStyle, QDial
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
import pyqtgraph as pg
from pyqtgraph import GraphicsWindow
from processing.variables import dialstyle
from processing.sr_helpers import fftdb
import numpy as np
from scipy.fftpack import fft
from scipy import signal
import logging
import warnings

_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())


class PicButton(QAbstractButton):
    """Picture button class. Redefine a new shape for Sound Refiner Gui. Checkable. 
    """
    def __init__(self, pixmap, pixmap_hover, pixmap_pressed, text="", check=True, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap_hover = pixmap_hover
        self.pixmap_pressed = pixmap_pressed
        self.pressed.connect(self.update)
        super(PicButton, self).setText(text)
        super(PicButton, self).setFixedHeight(60)
        super(PicButton, self).setFixedWidth(60)
        self.setCheckable(check)
        self.released.connect(self.update)
        self.updatecount = 0

    def paintEvent(self, event):
        """Change picture when hovering"""
        pix = self.pixmap_hover if self.underMouse() else self.pixmap
        if self.isChecked():
            pix = self.pixmap_pressed
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return self.pixmap.size()


class MyDial(QDial):

    def __init__(self, v0=100, max=150, min=0):
        """Custom Dial
    
        Parameters:
        -----------
        v0: int
            Initial position
        max: int
            max val
        min: int
            min val
        """
        super().__init__()
        super(MyDial, self).setStyleSheet(dialstyle)
        super(MyDial, self).setWrapping(False)
        super(MyDial, self).setNotchesVisible(True)
        super(MyDial, self).setMinimum(min)
        super(MyDial, self).setMaximum(max)
        super(MyDial, self).setValue(v0)


class LabeledSlider(QWidget):
    def __init__(self, minimum, maximum, interval=1, orientation=Qt.Horizontal, labels=None, p0=0, parent=None):
        """Label slider, used for volume with ticks and numbers next to them
    
        Parameters:
        ------------
        minimum: int

        maximum: int

        interval: int
            step

        orientation: Qt.Horizontal or Qt.Vertical
            orientation of slider

        labels: string
            label

        p0: int
            initial slider position

        parent: class
            a parent class to inherit
        """
        super(LabeledSlider, self).__init__(parent=parent)
        levels = range(minimum, maximum + interval, interval)  # Create a range based on the parameters
        if labels is not None:
            if not isinstance(labels, (tuple, list)):
                raise Exception("<labels> is a list or tuple.")
            if len(labels) != len(levels):
                raise Exception("Size of <labels> doesn't match levels.")
            self.levels = list(zip(levels, labels))
        else:
            self.levels = list(zip(levels, map(str, levels)))

        if orientation == Qt.Horizontal:
            self.layout = QVBoxLayout(self)
        elif orientation == Qt.Vertical:
            self.layout = QHBoxLayout(self)
        else:
            raise Exception("<orientation> wrong.")
        # gives some space to print labels
        self.left_margin = 10
        self.top_margin = 10
        self.right_margin = 10
        self.bottom_margin = 10

        self.layout.setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)

        self.sl = QSlider(orientation, self)
        self.sl.setMinimum(minimum)
        self.sl.setMaximum(maximum)
        self.sl.setValue(minimum)
        self.sl.setSliderPosition(p0)
        if orientation == Qt.Horizontal:
            self.sl.setTickPosition(QSlider.TicksBelow)
            self.sl.setMinimumWidth(300)  # just to make it easier to read
        else:
            self.sl.setTickPosition(QSlider.TicksLeft)
            self.sl.setMinimumHeight(300)  # just to make it easier to read
        self.sl.setTickInterval(interval)
        self.sl.setSingleStep(1)
        self.layout.addWidget(self.sl)

    def paintEvent(self, e):
        super(LabeledSlider, self).paintEvent(e)
        style = self.sl.style()
        painter = QPainter(self)
        st_slider = QStyleOptionSlider()
        st_slider.initFrom(self.sl)
        st_slider.orientation = self.sl.orientation()

        length = style.pixelMetric(QStyle.PM_SliderLength, st_slider, self.sl)
        available = style.pixelMetric(QStyle.PM_SliderSpaceAvailable, st_slider, self.sl)

        for v, v_str in self.levels:
            # get the size of the label
            rect = painter.drawText(QRect(), Qt.TextDontPrint, v_str)
            if self.sl.orientation() == Qt.Horizontal:
                # I assume the offset is half the length of slider, therefore
                # + length//2
                x_loc = QStyle.sliderPositionFromValue(
                    self.sl.minimum(), self.sl.maximum(), v, available) + length // 2

                # left bound of the text = center - half of text width + L_margin
                left = x_loc - rect.width() // 2 + self.left_margin
                bottom = self.rect().bottom()
                # enlarge margins if clipping
                if v == self.sl.minimum():
                    if left <= 0:
                        self.left_marginn = rect.width() // 2 - x_loc
                    if self.bottom_margin <= rect.height():
                        self.bottom_margin = rect.height()
                    self.layout.setContentsMargins(
                        self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)
                if v == self.sl.maximum() and rect.width() // 2 >= self.right_margin:
                    self.right_margin = rect.width() // 2
                    self.layout.setContentsMargins(
                        self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)
            else:
                y_loc = QStyle.sliderPositionFromValue(
                    self.sl.minimum(), self.sl.maximum(), v, available, upsideDown=True)
                bottom = y_loc + length // 2 + rect.height() // 2 + self.top_margin - 3
                # there is a 3 px offset that I can't attribute to any metric
                left = self.left_margin - rect.width()
                if left <= 0:
                    self.left_margin = rect.width() + 2
                    self.layout.setContentsMargins(
                        self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)
            pos = QPoint(left, bottom)
            painter.drawText(pos, v_str)
        return


class Audioplot(GraphicsWindow):  # Not currently in use 
    read_collected = pyqtSignal(np.ndarray)
    def __init__(self, chunk=256, fs=44100, channels=2):
        """A pyqtgraph graphicswindow object for displaying audio signal
        
        Parameters:
        --------------

        read_collected: slot
            a slot for the qtsignal
        
        chunk: int
            buffersize

        fs: int
            sampling frequency

        channels: int
            number of channels

        window: array 
            a hanning window with size of self.chunk

        updatecount: int
            counter for updates

        spectroImgRes: int 
            How many slices on the x scale for the spectrogram image, or the colum size of image. 

        img_array: numpy matrix
            numpy array used as an image. 

        spectroImg: pyqtgraph.ImageItem()
            a pyqtgraph image item 
        """
        super().__init__()  
        self.monitorType = 'Spectrogram'
        self.chunk = chunk
        self.fs = fs
        self.channels = channels
        self.window = np.hanning(self.chunk)
        self.updatecount = 0
        self.spectroImgReso = 1000  # 1000 pieces in time scale.
        self.img_array = np.zeros((self.spectroImgReso, self.chunk // 2 + 1))
        pg.setConfigOptions(antialias=True)  # set pyqtgraph option to enable antialiasing. 
        # self.plotview = pg.GraphicsWindow("Plot")
        self.spectroImg = pg.ImageItem()
        self.setColoMap()
        self._setupaxis()

    def setColoMap(self):
        """
        Define each range:
        from 0 to 1 blue -> dark blue -> black -> red -> yellow.  (red and yellow indicate existence of spectral contents)
        """
        # bipolar colormap
        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        # 0 - 1: light blue , dark blue, black, red , yellow. 
        color = np.array([[0, 255, 255, 255], [255, 255, 0, 255], [0, 0, 0, 255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
        self.cmap = pg.ColorMap(pos, color)
        self.lut = self.cmap.getLookupTable(0.0, 1.0, 256)

    def _setupaxis(self):
        self.wf_xaxis = pg.AxisItem(orientation='bottom')
        self.wf_yaxis = pg.AxisItem(orientation='left')
        self.sp_xaxis = pg.AxisItem(orientation='bottom')

    # This is to prevent is channels/ fs/ chunk changed before the actual monitoring happened resulting a wrong setting
    def updateSettings(self, chunk=256, fs=44100, channels=2):
        self.chunk = chunk
        self.window = np.hanning(self.chunk)
        self.fs = fs
        self.channels = channels
        self.img_array = np.zeros((self.spectroImgReso, self.chunk // 2 + 1))

    def plot(self, sig, chunk=256, fs=44100, channels=2, dtyp='int16', xformat='time'):  # 1 time plot
        self.chunk = chunk
        self.window = np.hanning(self.chunk)
        self.fs = fs
        self.clear()
        self.traces = dict()
        # Get single channel data 
        l = len(sig) // channels  # Of course this should be wrong due to the amount of channels.
        l54 = int(l * 4 / 5); l53 = int(l * 3 / 5); l52 = int(l * 2 / 5); l51 = int(l * 1 / 5)
        if xformat == 'time':
            wf_xlabels = [
                (0, '0'), (l51, '{0:.2f}'.format(l51 / self.fs)), (l52, '{0:.2f}'.format(l52 / self.fs)),
                (l53, '{0:.2f}'.format(l53 / self.fs)), (l54, '{0:.2f}'.format(l54 / self.fs)),
                (l, '{0:.2f}'.format(l / self.fs))]
        elif xformat == 'sample':
            wf_xlabels = [(0, '0'), (l51, str(l51)), (l52, str(l52)), (l53, str(l53)), (l54, str(l54)), (l, str(l))]
        else: 
            warnings.warn("Doesn't recognise xformat ")
        self.wf_xaxis.setTicks([wf_xlabels])
        # Change this based on the data type 
        if dtyp == 'int16':
            ymax = 32768; ymin = -32767
            wf_ylabels = [(ymin, '-1'), (0., '0'), (ymax, '1')]
        elif dtyp == 'float':
            ymax = 1.; ymin = -1.
            wf_ylabels = [(ymin, str(ymin)), (0., '0'), (ymax, str(ymax))]

        self.wf_yaxis.setTicks([wf_ylabels])
        self.waveform = self.addPlot(
            title='WAVEFORM', row=1, col=1, axisItems={'bottom': self.wf_xaxis, 'left': self.wf_yaxis},
        )
        self.spectrum = self.addPlot(
            title='SPECTROGRAM', row=2, col=1, 
        )
        self.traces['waveform'] = self.waveform.plot(pen='y', width=3)
        self.waveform.setYRange(ymin, ymax, padding=0)
        self.waveform.setXRange(0, self.chunk, padding=0.005)
        # Find out the spectrogram of the signal. 
        self.img = pg.ImageItem()
        # set colormap
        self.img.setLookupTable(self.lut)
        self.img.setLevels([-50, 40])
        # setup the correct scaling for y-axis
        freq = np.arange((self.chunk / 2) + 1) / (float(self.chunk) / self.fs)
        yscale = 1.0 / (self.img_array.shape[1] / freq[-1])
        self.img.scale((1. / self.fs) * self.chunk, yscale)

        # sig1c = sig[0::channels]
        sig1c = sig[0::channels]  # single channel data
        img_array = self.getSpectrogramImage(sig1c)
        # f, t, Sxx = signal.spectrogram(sig1c, rate)

        self.img.setImage(img_array, autoLevels=False)

        self.spectrum.addItem(self.img)
        self.spectrum.setLabel('bottom', "Time (s)")
        # If you include the units, Pyqtgraph automatically scales the axis and adjusts the SI prefix (in this case kHz)
        self.spectrum.setLabel('left', "Frequency", units='Hz')

        self.spectrum.setXRange(0, l / self.fs, padding=0.005)

        self.waveform.setXRange(0, l, padding=0.005)
        self.waveform.setLabel('left', "Amplitude")

        self.traces['waveform'].setData(np.arange(0, l), sig[0::channels])
        # self.traces['spectrum'].setData(freq, Y)
        return "Plot recorded data"

    def changeMonitorType(self, text):
        self.monitorType = text
        self.spectroImg = pg.ImageItem()
        self.clear()
        if (self.monitorType == 'Spectrogram'):
            self.traces = dict()
            self.img_array = np.zeros((self.spectroImgReso, self.chunk // 2 + 1))
            self.spectrum = self.addPlot(title='SPECTROGRAM', row=1, col=1,)
            self.spectrum.setLabel('left', "Frequency", units='Hz')
            # self.spectrum.setLogMode(False, True)
            self.spectrum.addItem(self.spectroImg)
            self.spectroImg.setLookupTable(self.lut)
            self.spectroImg.setLevels([-50, 40])
            # setup the correct scaling for y-axis

            freq = np.arange((self.chunk / 2) + 1) / (float(self.chunk) / self.fs)
            yscale = 1.0 / (self.img_array.shape[1] / freq[-1])
            self.spectroImg.scale((1. / self.fs) * self.chunk, yscale)

        elif (self.monitorType == "Spectrum"):
            """
            Currently only has spectrum, waveform is not added yet. 
            """
            self.traces = dict()
            self.spectrum = self.addPlot(title='SPECTROGRAM', row=1, col=1,)
            # self.spectrum.setLogMode(True, False)
            self.spectrum.setMouseEnabled(y=False)
            self.spectrum.setYRange(-150, 0)
            # Axis
            self.specAxis = self.spectrum.getAxis("bottom")
            self.specAxis.setLabel("Frequency [Hz]")
            # Break it down to 16 ticks 
            # self.chunk //2 //(self.chunk//16)
            # loc = np.arange(0, self.chunk//2, self.chunk//2 //len(f))
            f = np.linspace(0, self.fs / 2, 8).astype(int)
            loc = np.arange(0, self.chunk // 2, 8)
            self.specAxis.setTicks([[(a, str(b)) for a, b in zip(loc, f)]])
            self.traces['spectrum'] = self.spectrum.plot(pen='c', width=3)
            self.spectrum_x = np.arange(0, self.chunk // 2 + 1)

    def monitorOn(self):
        """Switch on realtime monitoring"""
        _LOGGER.info("Monitor on")
        self.clear()
        self.spectroImg = pg.ImageItem()
        self.traces = dict()
        if (self.monitorType == 'Spectrogram'):
            self.img_array = np.zeros((self.spectroImgReso, self.chunk // 2 + 1))
            self.spectrum = self.addPlot(title='SPECTROGRAM', row=1, col=1,)
            self.spectrum.setLabel('left', "Frequency", units='Hz')
            # self.spectrum.setLogMode(False, True)
            self.spectrum.addItem(self.spectroImg)
            self.spectroImg.setLookupTable(self.lut)
            self.spectroImg.setLevels([-50, 40])
            # setup the correct scaling for y-axis
            freq = np.arange((self.chunk / 2) + 1) / (float(self.chunk) / self.fs)
            yscale = 1.0 / (self.img_array.shape[1] / freq[-1])
            self.spectroImg.scale((1. / self.fs) * self.chunk, yscale)

        elif (self.monitorType == "Spectrum"):
            """Currently only has spectrum, waveform is not added yet. 
            """
            self.spectrum = self.addPlot(title='SPECTROGRAM', row=1, col=1,)
            # self.spectrum.setLogMode(True, False)
            self.spectrum.setMouseEnabled(y=False)
            # self.spectrum.setYRange(-150 , 0)
            # self.spectrum.setLogMode(x=True, y=False)
            self.spectrum.setYRange(-150, 0)
            # Axis
            self.specAxis = self.spectrum.getAxis("bottom")

            self.specAxis.setLabel("Frequency [Hz]")
            # Linear ticks
            # Break it down to 16 ticks 
            f = np.linspace(0, self.fs / 2, 8).astype(int)
            loc = np.arange(0, self.chunk // 2, self.chunk // 2 // len(f))

            # Log ticks
            # Break it down to 16 ticks 
            # f = np.linspace(0, np.log10(self.fs / 2), 8 ).astype(int)
            # loc = np.arange(0, self.chunk // 2, self.chunk // 2 // len(f))

            ticks = [[(a, str(b)) for a, b in zip(loc, f)]]
            self.specAxis.setTicks(ticks)
            self.traces['spectrum'] = self.spectrum.plot(pen='c', width=3)
            self.spectrum_x = np.arange(0, self.chunk // 2 + 1)

    def update(self, sig):
        """Implement update at fixed frame rate."""

        if (self.updatecount == 4):
            sig = sig[0::self.channels]  # May not need
            if (self.monitorType == 'Spectrogram'):
                spec = np.fft.rfft(sig * self.window) / self.chunk  # TODO bug here when using external interface 
                magni = 20 * np.log10(np.abs(spec))  # to dB
                # roll down one and replace leading edge with new data
                self.img_array = np.roll(self.img_array, -1, 0)
                self.img_array[-1:] = magni
                self.spectroImg.setImage(self.img_array, autoLevels=False)

            elif (self.monitorType == 'Spectrum'):
                freq, spec_db = fftdb(sig, self.fs, win=self.window)
                spec_db[spec_db == -np.inf] = -500
                self.traces['spectrum'].setData(self.spectrum_x, spec_db)  # setdata can only be applied to plot
            self.updatecount = 0
        else:
            self.updatecount += 1

    # Dont have use for it actually. 
    def monitorOff(self):
        _LOGGER.info("Audiplot Class: Switch off monitor!")

    def getSpectrogramImage(self, sig):
        img_array = np.zeros((self.spectroImgReso, self.chunk // 2 + 1))
        for i in range(len(sig) // self.chunk):
            x = sig[i * self.chunk: i * self.chunk + self.chunk]
            spec = np.fft.rfft(x * self.window) / self.chunk
            magni = np.abs(spec)
            # to dB
            magni = 20 * np.log10(magni)
            img_array[i:] = magni
        return img_array
