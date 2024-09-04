import numpy as np
from enum import Enum, auto

class Params:
    class ReferenceType(Enum):
        STEP = auto()
        COS = auto()
        SIN = auto()

    class ImageType(Enum):
        PDF = auto()
        SVG = auto()
        JPG = auto()
        PNG = auto()

    tf: float = 10.0
    dt: float = 0.01
    T: int = 10
    reference_type: ReferenceType = ReferenceType.STEP
    amplitute: float = np.radians(60.0)
    frequency_hz: float = 1/5
    k_ref: int = 0
    c_list: (float | np.ndarray) = 0.0

    deg: bool = True
    legend: bool = True
    fontsize: int = 12
    fig_size: tuple[int, int] = (800, 600)
    save: bool = True
    image_type: ImageType = ImageType.SVG

    def __init__(self, num_states: int, num_inputs: int):
        self.x0 = np.zeros(num_states)
        self.Q = np.array([1.0, 0.1])

    def __str__(self) -> str:
        s = '# simulation\n'
        s += f'tf: {self.tf}\n'
        s += f'dt: {self.dt}\n'
        s += f'x0: {self.x0}\n'
        s += '\n'
        s += '# control\n'
        s += f'Q: {self.Q}\n'
        s += f'T: {self.T}\n'
        s += f'reference_type: "{self.reference_type.name.lower()}"\n'
        s += f'amplitude: {self.amplitute}\n'
        s += f'frequency_hz: {self.frequency_hz}\n'
        s += f'k_ref: {self.k_ref}\n'
        s += f'c_list: {self.c_list}\n'
        s += '\n'
        s += '# plotting\n'
        s += f'deg: {self.deg}\n'
        s += f'legend: {self.legend}\n'
        s += f'fontsize: "{self.fontsize}"\n'
        s += f'fig_size: {self.fig_size}\n'
        s += f'save: {self.save}\n'
        s += f'image_type: {self.image_type.name.lower()}\n'
        return s

# def loadParams(path: str)
