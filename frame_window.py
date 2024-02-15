# -*- coding: utf-8 -*-
"""Huvudmodul för programmet. Innehåller huvudfönsterklassen."""

import frame_model as fm
import frame_window_res
import sys

from qtpy.QtCore import QObject, Signal
from qtpy.QtWidgets import QApplication, QMainWindow, QFileDialog, QPlainTextEdit, QLineEdit
from qtpy.QtGui import QFont, QTextCursor
from qtpy import uic

sys.path.insert(0, "C:/Users/Jonas Lindemann/Development/calfem-python")


class Stream(QObject):
    """Klass för att omdirigera stdout till textfält"""
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

        uic.loadUi("frame_window.ui", self)

        # --- Font för textfält

        self.text_font = QFont("Courier New")
        self.text_font.setPointSize(12)
        self.text_font.setStyleHint(QFont.Monospace)

        # --- Omdirigera stdout till textfält

        sys.stdout = Stream(newText=self.on_update_text)

        # --- Visa fönster

        self.show()
        self.raise_()

        # --- Skapa modell och visa resultat

        self.init_model()

        # --- Koppla actions till funktioner

        self.execute_action.triggered.connect(self.on_execute_action)
        self.new_action.triggered.connect(self.on_new_action)
        self.open_action.triggered.connect(self.on_open_action)
        # ...

        self.h_edit = QLineEdit(self)
        self.w_edit = QLineEdit(self)
        self.E_edit = QLineEdit(self)
        self.A1_edit = QLineEdit(self)
        self.A2_edit = QLineEdit(self)
        self.I1_edit = QLineEdit(self)
        self.I2_edit = QLineEdit(self)
        self.q0_edit = QLineEdit(self)
        self.P_edit = QLineEdit(self)

        # ...

    def solve_model(self):
        """Lös modellen"""

        # --- Hämta värden från kontroller och uppdatera modellen

        self.update_model()

        # --- Rensa resultat tabbar

        self.remove_result_tabs()

        # --- Skapa textfält för resultat

        self.output_text = QPlainTextEdit(self)
        self.output_text.setFont(self.text_font)
        self.main_tabs.addTab(self.output_text, "Results")

        # --- Lös modellen

        self.model.solve()

        # --- Skapa resultat tabbar för diagram

        self.create_result_tabs()

        # --- Skriv ut resultat

        self.model.print_results()

        # --- Flytta text-markören till början av textfältet

        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.Start)
        self.output_text.setTextCursor(cursor)
        self.output_text.ensureCursorVisible()

        # --- Visa deformationstabben som default

        self.main_tabs.setCurrentIndex(1)

    def init_model(self):
        """Initiera modellen"""

        self.model = fm.FrameModel()

        self.update_controls()
        self.solve_model()

    def update_controls(self):
        """Fyll kontrollerna med värden från modellen"""

        self.w_edit.setText(f'{self.model.w:.3g}')
        self.h_edit.setText(f'{self.model.h:.3g}')
        self.E_edit.setText(f'{self.model.E:.3g}')
        self.A1_edit.setText(f'{self.model.A1:.3g}')
        self.A2_edit.setText(f'{self.model.A2:.3g}')
        self.I1_edit.setText(f'{self.model.I1:.3g}')
        self.I2_edit.setText(f'{self.model.I2:.3g}')
        self.q0_edit.setText(f'{self.model.q3:.3g}')
        self.P_edit.setText(f'{self.model.f1:.3g}')

    def try_float(self, text, default_value=0.0):
        """Konvertera text till float"""

        try:
            return float(text)
        except ValueError:
            return default_value

    def update_model(self):
        """Hämta värden från kontroller och uppdatera modellen"""

        self.model.w = self.try_float(self.w_edit.text(), self.model.w)
        self.model.h = self.try_float(self.h_edit.text(), self.model.h)
        self.model.E = self.try_float(self.E_edit.text(), self.model.E)
        self.model.A1 = self.try_float(self.A1_edit.text(), self.model.A1)
        self.model.A2 = self.try_float(self.A2_edit.text(), self.model.A2)
        self.model.I1 = self.try_float(self.I1_edit.text(), self.model.I1)
        self.model.I2 = self.try_float(self.I2_edit.text(), self.model.I2)
        self.model.q3 = self.try_float(self.q0_edit.text(), self.model.q3)
        self.model.f1 = self.try_float(self.P_edit.text(), self.model.f1)

        self.update_controls()

    def create_result_tabs(self):
        """Skapa result tabbar"""

        self.main_tabs.addTab(self.model.draw_deformed(), "Displacements")
        self.main_tabs.addTab(self.model.draw_normal_forces(), "Normal forces")
        self.main_tabs.addTab(self.model.draw_shear_forces(), "Shear forces")
        self.main_tabs.addTab(self.model.draw_moments(), "Moments")

    def remove_result_tabs(self):
        """Ta bort resultat tabbar"""
        self.main_tabs.clear()

    def on_update_text(self, text):
        """Uppdatera text i status fältet"""

        # --- Lägg till text i textfältet

        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.output_text.setTextCursor(cursor)
        self.output_text.ensureCursorVisible()

    def on_editing_finished(self):
        """Uppdatera modellen när en kontroll ändrats"""

        self.update_model()
        self.solve_model()

    def on_execute_action(self):
        """Kör beräkningen"""

        self.update_model()
        self.solve_model()

    def on_new_action(self):
        """Skapa en ny modell"""

        self.init_model()

    def on_open_action(self):
        """Öppna in indata fil"""

        # --- Fråga efter filnamn

        new_filename, _ = QFileDialog.getOpenFileName(
            self, "Öppna modell", "", "Modell filer (*.json *.jpg *.bmp)")

        # --- Om filnamn finns, ladda modellen

        if new_filename != "":
            self.filename = new_filename
            self.model.load(self.filename)
            self.update_controls()
            self.solve_model()

    def on_save_action(self):
        """Spara modell"""

        # --- Uppdatera modellen

        self.update_model()

        # --- Kontrollera om filnamn finns, annars fråga efter det

        if self.filename == "":
            new_filename, _ = QFileDialog.getSaveFileName(
                self, "Spara modell", "", "Modell filer (*.json)")

        # --- Om filnamn finns, spara modellen

        if new_filename != "":
            self.filename = new_filename
            self.model.save(self.filename)

    def on_save_as_action(self):
        """Spara modell med specifikt filnamn"""

        # --- Uppdatera modellen

        self.update_model()

        # --- Fråga efter filnamn

        new_filename, _ = QFileDialog.getSaveFileName(
            self, "Spara modell", "", "Modell filer (*.json)")

        # --- Om filnamn finns, spara modellen

        if new_filename != "":
            self.filename = new_filename
            self.model.save(self.filename)

    def on_exit_action(self):
        """Stäng programfönster"""

        self.close()


if __name__ == '__main__':

    app = QApplication(sys.argv)

    window = FrameWindow(app)

    sys.exit(app.exec_())
