# -*- coding: utf-8 -*-
"""Main module for the groundwater flow application"""

import sys

from qtpy.QtCore import QObject, Signal
from qtpy.QtWidgets import QApplication, QMainWindow, QFileDialog
from qtpy import uic

#import matplotlib.backends.backend_qt5agg

import frame_window_res
import frame_model as fm    

class Stream(QObject):
    newText = Signal(str)

    def write(self, text):
        self.newText.emit(str(text))


class FrameWindow(QMainWindow):
    """MainWindow-klass som hanterar vårt huvudfönster"""

    def __init__(self, app):
        """Class constructor"""

        super().__init__()

        # --- Lagra en referens till applikationsinstansen i klassen

        self.app = app

        # --- Läs in gränssnitt från fil

        # Läs in gränssnitt från fil

        uic.loadUi("frame_window.ui", self)


        sys.stdout = Stream(newText=self.on_update_text)


        self.show()
        self.raise_()

        self.init_model()

        self.execute_action.triggered.connect(self.on_execute_actio)
        self.new_action.triggered.connect(self.on_new_action)


    def on_update_text(self, text):
        """Uppdatera text i status fältet"""

        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.output_text.setTextCursor(cursor)
        self.output_text.ensureCursorVisible()

    def on_execute_actio(self):
        """Kör beräkningen"""

        print("on_execute_action")

        #self.update_model()
        self.model.solve()
        #self.model.print_results()
        #self.update_controls()

        self.remove_result_tabs()
        self.main_tabs.addTab(self.model.draw_deformed(), "Displacements")
        self.main_tabs.addTab(self.model.draw_normal_forces(), "Normal forces")
        self.main_tabs.addTab(self.model.draw_shear_forces(), "Shear forces")
        self.main_tabs.addTab(self.model.draw_moments(), "Moments")


    def init_model(self):
        """Initiera modellen"""

        self.model = fm.FrameModel()
        self.model.solve()
        self.model.print_results()

    def update_controls(self):
        """Fyll kontrollerna med värden från modellen"""

        self.w_edit.setText(str(self.model.w))
        self.h_edit.setText(str(self.model.h))
        self.E_edit.setText(str(self.model.E))
        self.A1_edit.setText(str(self.model.A1))
        self.A2_edit.setText(str(self.model.A2))
        self.I1_edit.setText(str(self.model.I1))
        self.I2_edit.setText(str(self.model.I2))
        self.q1_edit.setText(str(self.model.q1))
        self.q2_edit.setText(str(self.model.q2))
        self.q3_edit.setText(str(self.model.q3))
        self.f1_edit.setText(str(self.model.f1))

    def update_model(self):
        """Hämta värden från kontroller och uppdatera modellen"""

        self.model.w = float(self.w_edit.text())
        self.model.h = float(self.h_edit.text())
        self.model.E = float(self.E_edit.text())
        self.model.A1 = float(self.A1_edit.text())
        self.model.A2 = float(self.A2_edit.text())
        self.model.I1 = float(self.I1_edit.text())
        self.model.I2 = float(self.I2_edit.text())
        self.model.q1 = float(self.q1_edit.text())
        self.model.q2 = float(self.q2_edit.text())
        self.model.q3 = float(self.q3_edit.text())
        self.model.f1 = float(self.f1_edit.text())

        self.update_controls()

    def create_result_tabs(self):
        """Skapa result tabbar"""

        pass


    def remove_result_tabs(self):
        """Ta bort resultat tabbar"""

        if self.main_tabs.count() > 1:
            for i in range(4):
                self.main_tabs.removeTab(i+1)

    def on_new_action(self):
        """Skapa en ny modell"""

        print("on_new_action")
        self.init_model()
        #self.update_controls()
        #self.remove_result_tabs()

    def on_open_action(self):
        """Öppna in indata fil"""

        self.filename, _ = QFileDialog.getOpenFileName(
            self, "Öppna modell", "", "Modell filer (*.json *.jpg *.bmp)")

        if self.filename != "":
            self.init_model()
            self.update_controls()
            self.update_status()
            self.remove_result_tabs()

    def on_save_action(self):
        """Spara modell"""

        self.update_model()

        if self.filename == "":
            self.filename, _ = QFileDialog.getSaveFileName(
                self, "Spara modell", "", "Modell filer (*.json)")

        self.update_status()

    def on_save_as_action(self):
        """Spara modell med specifikt filnamn"""

        self.update_model()

        new_filename, _ = QFileDialog.getSaveFileName(
            self, "Spara modell", "", "Modell filer (*.json)")

        if new_filename != "":
            self.filename = new_filename

    def on_execute_action(self):
        """Kör beräkningen"""
        pass


    def on_exit_action(self):
        """Stäng programfönster"""
        # --- Stäng programfönster

        self.close()



if __name__ == '__main__':

    app = QApplication(sys.argv)

    window = FrameWindow(app)

    sys.exit(app.exec_())
