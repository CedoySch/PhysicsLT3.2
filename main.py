import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QGridLayout, QMessageBox, QHBoxLayout, QSizePolicy
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=40):
        self.fig, self.axes = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

    def resizeEvent(self, event):
        super(MplCanvas, self).resizeEvent(event)
        self.adjust_plot_elements()

    def adjust_plot_elements(self):
        width, height = self.fig.get_size_inches() * self.fig.dpi
        scaling_factor = min(width, height) / 400

        self.axes.title.set_fontsize(12 * scaling_factor)
        self.axes.xaxis.label.set_fontsize(10 * scaling_factor)
        self.axes.yaxis.label.set_fontsize(10 * scaling_factor)
        self.axes.tick_params(axis='both', which='major', labelsize=8 * scaling_factor)

        if self.axes.get_legend():
            self.axes.legend(fontsize=8 * scaling_factor, loc=(1.01, 0.5))

        self.fig.tight_layout()
        self.draw()


class ProjectileApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Визуализация движения точки на ободе колеса')
        self.setGeometry(100, 100, 700, 700)
        self.setStyleSheet("background-color: #f5f5f5;")
        self.initUI()

    def initUI(self):
        # Лейблы и поля ввода
        label_R = QLabel('Радиус колеса (м)')
        self.input_R = QLineEdit()
        self.input_R.setPlaceholderText('Пример: 1')

        label_V = QLabel('Скорость центра масс (м/с)')
        self.input_V = QLineEdit()
        self.input_V.setPlaceholderText('Пример: 10')

        label_T = QLabel('Время движения (с)')
        self.input_T = QLineEdit()
        self.input_T.setPlaceholderText('Пример: 5')

        # Кнопка для запуска анимации
        self.button_plotting = QPushButton('Запустить динамическую визуализацию')
        self.button_plotting.setStyleSheet("background-color: #2b48ff; color: white; padding: 10px; border-radius: 10px;")
        self.button_plotting.clicked.connect(self.plot_graphs_dynamic)

        # Макет для ввода данных
        grid = QGridLayout()
        grid.addWidget(label_R, 0, 0)
        grid.addWidget(self.input_R, 0, 1)
        grid.addWidget(label_V, 1, 0)
        grid.addWidget(self.input_V, 1, 1)
        grid.addWidget(label_T, 2, 0)
        grid.addWidget(self.input_T, 2, 1)
        grid.addWidget(self.button_plotting, 3, 0, 1, 2)

        self.canvas_trajectory = MplCanvas(self)

        grid.addWidget(self.canvas_trajectory, 4, 0, 2, 2)

        layout_main = QHBoxLayout()
        layout_main.addLayout(grid, 1)

        self.setLayout(layout_main)

    def plot_graphs_dynamic(self):
        try:
            R = float(self.input_R.text())
            V = float(self.input_V.text())
            T = float(self.input_T.text())
        except ValueError:
            QMessageBox.warning(self, 'Ввод данных', 'Введите корректные числовые значения')
            return

        if R <= 0 or V <= 0 or T <= 0:
            QMessageBox.warning(self, 'Ошибка', 'Радиус и скорость должны быть положительными')
            return

        omega = V / R  # Угловая скорость
        t = np.linspace(0, T, 1000)

        x = V * t - R * np.sin(omega * t)
        y = R - R * np.cos(omega * t)

        # Очистка предыдущего графика
        self.canvas_trajectory.axes.cla()

        max_x = np.max(x)
        min_x = np.min(x)
        max_y = np.max(y)
        min_y = np.min(y)

        # Увеличение масштаба по оси Y
        scale_y = 1.5  # Коэффициент увеличения вертикальной оси

        total_animation_time = 3000  # 3 секунды
        frame_interval = 20
        total_frames = total_animation_time // frame_interval

        def update(frame):
            current_frame = int((frame / total_frames) * len(t))
            self.canvas_trajectory.axes.cla()
            self.canvas_trajectory.axes.plot(x[:current_frame], y[:current_frame], color='blue', linewidth=2)
            self.canvas_trajectory.axes.set_xlabel('x (м)', fontsize=14)
            self.canvas_trajectory.axes.set_ylabel('y (м)', fontsize=14)
            self.canvas_trajectory.axes.set_title('Динамическая траектория точки на ободе колеса', fontsize=16)
            self.canvas_trajectory.axes.grid(True, which='both', linestyle='--', linewidth=0.5)

            self.canvas_trajectory.axes.set_xlim(min_x - 0.1 * abs(min_x), max_x + 0.1 * abs(max_x))
            self.canvas_trajectory.axes.set_ylim(scale_y * (min_y - 0.1 * abs(min_y)), scale_y * (max_y + 0.1 * abs(max_y)))
            self.canvas_trajectory.axes.set_aspect('auto', adjustable='box')

        self.ani = FuncAnimation(self.canvas_trajectory.fig, update, frames=total_frames, interval=frame_interval, repeat=False)
        self.canvas_trajectory.fig.tight_layout()
        self.canvas_trajectory.draw()


def main():
    app = QApplication(sys.argv)
    window = ProjectileApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
