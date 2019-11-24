from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from MainWindow import Ui_MainWindow
from SplashScreenController import SplashScreenController
import sys,time

def hhmmss(ms):
    # s = 1000
    # m = 60000
    # h = 3600000000
    h, r = divmod(ms, 3600000000)
    m, r = divmod(r, 60000)
    s, _ = divmod(r, 1000)
    return ("%d:%02d:%02d" % (h,m,s)) if h else ("%d:%02d" % (m,s))

class ViewerWindow(QMainWindow):
    state = pyqtSignal(bool)

    def closeEvent(self, e):
        # Emit the window state, to update the viewer toggle button.
        self.state.emit(False)


class PlaylistModel(QAbstractListModel):
    def __init__(self, playlist, *args, **kwargs):
        super(PlaylistModel, self).__init__(*args, **kwargs)
        self.playlist = playlist

    def data(self, index, role):
        if role == Qt.DisplayRole:
            media = self.playlist.media(index.row())
            return media.canonicalUrl().fileName()

    def rowCount(self, index):
        return self.playlist.mediaCount()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        #displaying splash screen
        self.splash = SplashScreenController(self)
        #self.splash.anim.start()
        QTimer.singleShot(3000,self.setUpMainWindow)

    def setUpMainWindow(self):
        self.splash.close()
        self.setupUi(self)

        self.player = QMediaPlayer()

        self.player.error.connect(self.erroralert)
        #self.player.play()

        # Setup the playlist.
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        # Connect control buttons/slides for media player.
        self.playButton.pressed.connect(self.playMusic)
        self.stopButton.pressed.connect(self.playStop)
        self.volumeSlider.valueChanged.connect(self.player.setVolume)
        self.previousButton.pressed.connect(self.playlist.previous)
        self.nextButton.pressed.connect(self.playlist.next)

        self.model = PlaylistModel(self.playlist)
        self.playlistView.setModel(self.model)
        self.playlist.currentIndexChanged.connect(self.playlist_position_changed)
        selection_model = self.playlistView.selectionModel()
        selection_model.selectionChanged.connect(self.playlist_selection_changed)

        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)
        self.timeSlider.valueChanged.connect(self.player.setPosition)

        # Connect controllers to menu items
        self.menuPlay.triggered.connect(self.open_file)
        self.actionDefault.triggered.connect(self.defaultPalette)
        self.actionFusion.triggered.connect(self.darkPalette)

        self.setAcceptDrops(True)

        self.show()

    def defaultPalette(self):
        self.setStyleSheet("")

    def darkPalette(self):
        stylesheet = "background-color: rgb(150, 150, 150)"
        self.setStyleSheet(stylesheet)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            self.playlist.addMedia(
                QMediaContent(url)
            )

        self.model.layoutChanged.emit()

        # If not playing, seeking to first of newly added + play.
        if self.player.state() != QMediaPlayer.PlayingState:
            i = self.playlist.mediaCount() - len(e.mimeData().urls())
            self.playlist.setCurrentIndex(i)
            self.player.play()

    def playStop(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            icon = QIcon()
            icon.addPixmap(QPixmap("../../resources/images/play.png"), QIcon.Normal, QIcon.Off)
            self.playButton.setIcon(icon)
            self.player.stop()

    def playMusic(self):
        if not self.playlist.isEmpty() :
            if self.player.state() != QMediaPlayer.PlayingState:
                icon = QIcon()
                icon.addPixmap(QPixmap("../../resources/images/pause.png"),QIcon.Normal, QIcon.Off)
                self.playButton.setIcon(icon)
                self.player.play()
            elif self.player.state() == QMediaPlayer.PlayingState:
                icon = QIcon()
                icon.addPixmap(QPixmap("../../resources/images/play.png"),QIcon.Normal, QIcon.Off)
                self.playButton.setIcon(icon)
                self.player.pause()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "mp3 Audio (*.mp3);mp4 Video (*.mp4);Movie files (*.mov);All files (*.*)")

        if path:
            self.playlist.addMedia(
                QMediaContent(
                    QUrl.fromLocalFile(path)
                )
            )

        self.model.layoutChanged.emit()

    def update_duration(self, duration):
        print("!", duration)
        print("?", self.player.duration())

        self.timeSlider.setMaximum(duration)

        if duration >= 0:
            self.totalTimeLabel.setText(hhmmss(duration))

    def update_position(self, position):
        if position >= 0:
            self.currentTimeLabel.setText(hhmmss(position))

        # Disable the events to prevent updating triggering a setPosition event (can cause stuttering).
        self.timeSlider.blockSignals(True)
        self.timeSlider.setValue(position)
        self.timeSlider.blockSignals(False)

    def playlist_selection_changed(self, ix):
        # We receive a QItemSelection from selectionChanged.
        i = ix.indexes()[0].row()
        self.playlist.setCurrentIndex(i)

    def playlist_position_changed(self, i):
        if i > -1:
            ix = self.model.index(i)
            self.playlistView.setCurrentIndex(ix)

    def toggle_viewer(self, state):
        if state:
            self.viewer.show()
        else:
            self.viewer.hide()

    def erroralert(self, *args):
        print(args)

if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName("Jive Music Player")
    app.setStyle("Fusion")
    #app.setStyleSheet(qdarkgraystyle.load_stylesheet())
    window = MainWindow()
    sys.exit(app.exec_())

#end of program

