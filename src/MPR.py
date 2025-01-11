import os
import pydicom
import SimpleITK as sitk
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QSlider
from PyQt5.QtCore import Qt, pyqtSignal, QPointF
import numpy as np


# Load DICOM files
def load_dicom(directory):
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(directory)
    reader.SetFileNames(dicom_names)
    image = reader.Execute()
    return image


class ClickableImageView(pg.ImageView):
    clicked = pyqtSignal(QPointF)

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.getImageItem().mouseClickEvent = self.mouseClickEvent

    def mouseClickEvent(self, event):
        self.clicked.emit(self.getImageItem().mapToView(event.pos()))


class ViewerApp(QMainWindow):
    def _init_(self, image_data):
        super()._init_()
        self.image_data = image_data
        self.image_array = sitk.GetArrayFromImage(self.image_data)
        self.size = self.image_array.shape

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Multiplanar Viewer with Cross-Plane Pointers and Markers")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QGridLayout(central_widget)

        # Add image views for each plane
        self.axial_view = ClickableImageView()
        self.coronal_view = ClickableImageView()
        self.sagittal_view = ClickableImageView()

        self.axial_slider = QSlider(Qt.Horizontal)
        self.axial_slider.setMaximum(self.size[0] - 1)
        self.axial_slider.setValue(self.size[0] // 2)

        self.coronal_slider = QSlider(Qt.Horizontal)
        self.coronal_slider.setMaximum(self.size[1] - 1)
        self.coronal_slider.setValue(self.size[1] // 2)

        self.sagittal_slider = QSlider(Qt.Horizontal)
        self.sagittal_slider.setMaximum(self.size[2] - 1)
        self.sagittal_slider.setValue(self.size[2] // 2)

        # Add views to layout
        layout.addWidget(self.axial_view, 0, 0)
        layout.addWidget(self.axial_slider, 1, 0)
        layout.addWidget(self.coronal_view, 0, 1)
        layout.addWidget(self.coronal_slider, 1, 1)
        layout.addWidget(self.sagittal_view, 2, 0)
        layout.addWidget(self.sagittal_slider, 3, 0)

        # Connect sliders to update functions
        self.axial_slider.valueChanged.connect(self.update_axial_view)
        self.coronal_slider.valueChanged.connect(self.update_coronal_view)
        self.sagittal_slider.valueChanged.connect(self.update_sagittal_view)

        # Create crosshair pointers
        self.axial_pointer = pg.InfiniteLine(angle=90, movable=False)
        self.axial_pointer_x = pg.InfiniteLine(angle=0, movable=False)
        self.coronal_pointer = pg.InfiniteLine(angle=90, movable=False)
        self.coronal_pointer_x = pg.InfiniteLine(angle=0, movable=False)
        self.sagittal_pointer = pg.InfiniteLine(angle=90, movable=False)
        self.sagittal_pointer_x = pg.InfiniteLine(angle=0, movable=False)

        self.axial_view.addItem(self.axial_pointer)
        self.axial_view.addItem(self.axial_pointer_x)
        self.coronal_view.addItem(self.coronal_pointer)
        self.coronal_view.addItem(self.coronal_pointer_x)
        self.sagittal_view.addItem(self.sagittal_pointer)
        self.sagittal_view.addItem(self.sagittal_pointer_x)

        # Connect mouse clicks to update pointers
        self.axial_view.clicked.connect(self.on_axial_click)
        self.coronal_view.clicked.connect(self.on_coronal_click)
        self.sagittal_view.clicked.connect(self.on_sagittal_click)

        # Display initial slices
        self.update_axial_view(self.axial_slider.value())
        self.update_coronal_view(self.coronal_slider.value())
        self.update_sagittal_view(self.sagittal_slider.value())

        self.show()

    def update_axial_view(self, slice_index):
        axial_slice = np.rot90((self.image_array[slice_index, :, :]), k=3)
        self.axial_view.setImage(axial_slice)

    def update_coronal_view(self, slice_index):
        coronal_slice = np.rot90((self.image_array[:, slice_index, :]), k=3)
        self.coronal_view.setImage(coronal_slice)

    def update_sagittal_view(self, slice_index):
        sagittal_slice = np.rot90((self.image_array[:, :, slice_index]), k=3)
        self.sagittal_view.setImage(sagittal_slice)

    def on_axial_click(self, pos):
        x, y = int(pos.x()), int(pos.y())
        z = self.axial_slider.value()
        self.update_crosshair(z, y, x)

    def on_coronal_click(self, pos):
        x, z = int(pos.x()), int(pos.y())
        y = self.coronal_slider.value()
        self.update_crosshair(z, y, x)

    def on_sagittal_click(self, pos):
        y, z = int(pos.x()), int(pos.y())
        x = self.sagittal_slider.value()
        self.update_crosshair(z, y, x)

    def update_crosshair(self, z, y, x):
        """
        Update pointers for all views based on the clicked location.
        """
        self.axial_pointer.setPos(x)
        self.axial_pointer_x.setPos(y)

        self.coronal_pointer.setPos(x)
        self.coronal_pointer_x.setPos(z)

        self.sagittal_pointer.setPos(y)
        self.sagittal_pointer_x.setPos(z)

        self.axial_slider.setValue(z)
        self.coronal_slider.setValue(y)
        self.sagittal_slider.setValue(x)

        self.update_axial_view(z)
        self.update_coronal_view(y)
        self.update_sagittal_view(x)


def main():
    dicom_directory = r'D:\Anatomy\Task1_ITK_Snap\DICOM'
    image_data = load_dicom(dicom_directory)

    app = QApplication([])
    viewer = ViewerApp(image_data)
    app.exec_()


if _name_ == "_main_":
    main()