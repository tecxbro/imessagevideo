"""Independent source-native Y/opacity profile fitter, no module-level execution."""
from pathlib import Path
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition'
def load(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32)
class Actor:

    def __init__(self, name, ref, box, start, end, sample=None):
        self.name = name
        self.box = box
        self.start = start
        self.end = end
        self.art = load(ref)[box[1]:box[3], box[0]:box[2]].copy()
        self.H = len(self.art)
        self.W = self.art.shape[1]
        self.x = box[0]
        self.sample = sample
        self.rows = []
        if sample is None:
            profile = (255 - self.art).mean(axis=1)
        else:
            profile = (255 - load(ref)[box[1]:box[3], sample[0]:sample[1]]).mean(axis=1)
        self.ys = np.arange(-self.H + 8, 713)
        world = np.arange(720)[None, :]
        idx = world - self.ys[:, None]
        self.valid = ((idx >= 0) & (idx < self.H)).astype(np.float32)
        idx = np.clip(idx, 0, self.H - 1)
        self.models = (profile[idx] * self.valid[:, :, None]).reshape(len(self.ys), -1)
        self.den = np.sum(self.models * self.models, axis=1)
        self.safe = np.maximum(self.den, 1)

    def fit(self, f, a):
        if self.sample is None:
            p = (255 - a[:, self.x:self.x + self.W]).mean(axis=1)
        else:
            p = (255 - a[:, self.sample[0]:self.sample[1]]).mean(axis=1)
        dot = self.models @ p.reshape(-1)
        energy = self.valid @ np.sum(p * p, axis=1)
        alpha = dot / self.safe
        error = np.maximum(0, energy - dot * dot / self.safe) / np.maximum(energy, self.safe * 0.0001)
        error[(alpha < 0.05) | (alpha > 1.6)] = 100000.0
        at = int(np.argmin(error))
        y = float(self.ys[at])
        sub = 0.0
        if 0 < at < len(error) - 1 and max(error[at - 1], error[at + 1]) < 10000.0:
            den = error[at - 1] - 2 * error[at] + error[at + 1]
            if den > 0:
                sub = float(np.clip(0.5 * (error[at - 1] - error[at + 1]) / den, -0.5, 0.5))
        if error[at] > 0.15:
            self.rows.append({'frame': f, 'y': None, 'alpha': 0, 'mse': None})
        else:
            self.rows.append({'frame': f, 'y': y + sub, 'alpha': float(np.clip(alpha[at], 0, 1)), 'mse': float(error[at])})
