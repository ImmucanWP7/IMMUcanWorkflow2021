class FileNavigator():
    def __init__(self, folder) -> None:
        super().__init__()
        self.folder = folder

class WidgetFileSelection(QWidget):
    def __init__(self, viewer, folder) -> None:
        super().__init__()
        self._folder = folder
        self._app = viewer 
        self._current_index = 0

        self._prev_button = QPushButton(parent=self)
        self._prev_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack)
        )
        self._prev_button.clicked.connect(self._on_prev_button_clicked)

        self._next_button = QPushButton(parent=self)
        self._next_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward)
        )
        self._next_button.clicked.connect(self._on_next_button_clicked)
        
        cur_img = os.path.splitext(os.listdir(self._folder + "/IMC" + "/img")[self._current_index])[0]

        layout = QVBoxLayout()

        files_box = QLabel()
        files_box.setText(cur_img)
        layout.addWidget(files_box)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self._prev_button)
        button_layout.addWidget(self._next_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        
    def _on_prev_button_clicked(self, checked: bool = False) -> None:
        self._current_index = self._current_index - 1

    def _on_next_button_clicked(self, checked: bool = False) -> None:
        self._current_index = self._current_index + 1


def napari_comparison_test(folder) -> None:
    
    viewer1 = napari.Viewer(title=folder)

    #hide "layer controls" and "layer list" docks
    viewer1.window._qt_viewer.dockLayerControls.hide()
    viewer1.window._qt_viewer.dockLayerList.hide()
    
    selector = QScrollArea()
    selector.setWidgetResizable(True)
    selector.setWidget(WidgetFileSelection(viewer1, folder))
    viewer1.window.add_dock_widget(selector, area = 'right', name='Select sample')
    
    napari.run()