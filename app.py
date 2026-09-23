# app.py
from flask import Flask, render_template, request, redirect, send_file, url_for
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint
import io
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fire_loss_2025'

class Attr:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def val(self):
        return float(self.value)

class F:
    def __init__(self, a, b, c, d, L):
        self.a, self.b, self.c, self.d, self.L = a, b, c, d, L
    def calc(self, x):
        return self.a * (x ** 3) + self.b * (x ** 2) + self.c * x + self.d

class Z:
    def __init__(self, m, b, g, N):
        self.m, self.b, self.g, self.N = m, b, g, N
    def calc(self, t):
        current = self.b + self.g * (t * 100)
        zeta = current / self.m
        return min(max(zeta, 0), 1)

# 14 переменных — потери от пожаров
v0 = {
    'Cf₁': Attr('Потери от гибели и травм людей', 0.8),
    'Cf₂': Attr('Потери от уничтожения зданий', 0.7),
    'Cf₃': Attr('Потери от уничтожения имущества', 0.6),
    'Cf₄': Attr('Потери от повреждения лесных массивов', 0.5),
    'Cf₅': Attr('Потери от загрязнения атмосферы', 0.65),
    'Cf₆': Attr('Затраты на тушение пожара', 0.55),
    'Cf₇': Attr('Потери от остановки производства', 0.45),
    'Cf₈': Attr('Потери от нарушения инфраструктуры', 0.4),
    'Cf₉': Attr('Социальные потери', 0.35),
    'Cf₁₀': Attr('Экологические потери', 0.5),
    'Cf₁₁': Attr('Потери туристической привлекательности', 0.3),
    'Cf₁₂': Attr('Страховые выплаты', 0.42),
    'Cf₁₃': Attr('Потери от вторичных пожаров', 0.38),
    'Cf₁₄': Attr('Долгосрочные экономические последствия', 0.28),
}

c = {f'Cf{i}*': Attr(f'Нормализация потерь {i}', 1) for i in range(1, 15)}

f = {}
for i in range(1, 57):
    key = f'F_{i}'
    L = f'U_{(i % 14) + 1}'
    f[key] = F(0, 0, 1, 0, L)

z = {
    'Z₁': Z(1, 0.1, 0.01, 'Рост числа источников возгорания'),
    'Z₂': Z(1, 0.2, 0.02, 'Изменение климата'),
    'Z₃': Z(1, 0.3, 0.03, 'Ужесточение экологических норм'),
    'Z₄': Z(1, 0.4, 0.04, 'Санкционные ограничения'),
    'Z₅': Z(1, 0.5, 0.05, 'Рост стоимости строительства'),
    'Z₆': Z(1, 0.6, 0.06, 'Увеличение плотности застройки'),
    'Z₇': Z(1, 0.7, 0.07, 'Износ пожарной техники'),
    'Z₈': Z(1, 0.8, 0.08, 'Сокращение финансирования'),
    'Z₉': Z(1, 0.9, 0.09, 'Рост тарифов на страхование'),
    'Z₁₀': Z(1, 1.0, 0.10, 'Урбанизация лесных территорий'),
    'Z₁₁': Z(1, 1.1, 0.11, 'Недостаток кадров'),
    'Z₁₂': Z(1, 1.2, 0.12, 'Устаревшие нормативы'),
    'Z₁₃': Z(1, 1.3, 0.13, 'Аномальные погодные явления'),
    'Z₁₄': Z(1, 1.4, 0.14, 'Неопределённость экономики'),
}

t_span = np.linspace(0, 1, 20)

def generate_simple_smooth_data(num_points, num_series):
    data = np.zeros((num_points, num_series))
    t = np.linspace(0, 1, num_points)
    for i in range(num_series):
        start_val = random.uniform(0.2, 0.8)
        end_val = random.uniform(0.2, 0.8)
        curve_strength = random.uniform(-0.5, 0.5)
        for j, time_point in enumerate(t):
            linear = start_val + (end_val - start_val) * time_point
            curve = curve_strength * (time_point - 0.5) ** 2
            data[j, i] = max(0, min(1, linear + curve))
    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        for key in v0:
            v0[key].value = float(request.form[f'v0_{key}'])
        for key in c:
            c[key].value = float(request.form[f'c_{key}'])
        for key in f:
            f[key].a = float(request.form[f'f_{key}_a'])
            f[key].b = float(request.form[f'f_{key}_b'])
            f[key].c = float(request.form[f'f_{key}_c'])
            f[key].d = float(request.form[f'f_{key}_d'])
        for key in z:
            z[key].m = float(request.form[f'z_{key}_m'])
            z[key].b = float(request.form[f'z_{key}_b'])
            z[key].g = float(request.form[f'z_{key}_g'])
        return redirect(url_for('plot'))
    return render_template('index.html', v0=v0, c=c, f=f, z=z, t_span=t_span)

@app.route('/plot')
def plot():
    t_span_plot = np.linspace(0.2, 1.0, 50)
    unicode_sub = ["₁", "₂", "₃", "₄", "₅", "₆", "₇", "₈", "₉", "₁₀", "₁₁", "₁₂", "₁₃", "₁₄"]
    sol = generate_simple_smooth_data(len(t_span_plot), len(v0))
    keys = list(v0.keys())
    keys_part1 = keys[:7]
    keys_part2 = keys[7:]
    fig, axes = plt.subplots(2, 1, figsize=(16, 14))
    colors = plt.cm.tab20(np.linspace(0, 1, len(v0)))

    ax1 = axes[0]
    for i, key in enumerate(keys_part1):
        index = keys.index(key)
        ax1.plot(t_span_plot, sol[:, index], label=v0[key].name, color=colors[index], linewidth=2)
        if index % 2 == 0:
            ax1.text(t_span_plot[-1], sol[-1, index], f"x{unicode_sub[index]}", fontsize=15, ha='left', va='center')
        else:
            ax1.text(t_span_plot[-1] - 0.8, sol[-1, index], f"x{unicode_sub[index]}", fontsize=15, ha='right', va='center')
    ax1.set_xlabel("Время")
    ax1.set_ylabel("Значения потерь")
    ax1.set_title("Динамика потерь от пожаров (x₁ – x₇)")
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1)
    ax1.legend(loc='upper left', fontsize=9)

    ax2 = axes[1]
    for i, key in enumerate(keys_part2):
        index = keys.index(key)
        ax2.plot(t_span_plot, sol[:, index], label=v0[key].name, color=colors[index], linewidth=2)
        if index % 2 == 0:
            ax2.text(t_span_plot[-1], sol[-1, index], f"x{unicode_sub[index]}", fontsize=15, ha='left', va='center')
        else:
            ax2.text(t_span_plot[-1] - 0.8, sol[-1, index], f"x{unicode_sub[index]}", fontsize=15, ha='right', va='center')
    ax2.set_xlabel("Время")
    ax2.set_ylabel("Значения потерь")
    ax2.set_title("Динамика потерь от пожаров (x₈ – x₁₄)")
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1)
    ax2.legend(loc='upper left', fontsize=9)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')

@app.route('/polar_plot', methods=['GET', 'POST'])
def polar_plot():
    t_span_polar = [round(i * 0.1, 1) for i in range(1, 11)]
    sol = generate_simple_smooth_data(len(t_span_polar), 14)
    norm_bounds = []
    if request.method == 'POST':
        for i in range(14):
            val = request.form.get(f'norm_bound_{i}', type=float)
            if val is not None:
                norm_bounds.append(val)
    if len(norm_bounds) == 0:
        norm_bounds = [0.4 + 0.3 * random.random() for _ in range(14)]

    fig, axes = plt.subplots(2, 5, figsize=(20, 10), subplot_kw={'projection': 'polar'})
    axes = axes.flatten()
    angles = np.linspace(0, 2 * np.pi, 14, endpoint=False)

    for idx, t_index in enumerate(range(len(t_span_polar))):
        ax = axes[idx]
        sol_values = np.append(sol[t_index, :], sol[t_index, 0])
        norm_plot = np.append(norm_bounds, norm_bounds[0])
        angles_plot = np.append(angles, angles[0])
        ax.plot(angles_plot, sol_values, 'b-', linewidth=2, label='Текущие потери')
        ax.fill(angles_plot, sol_values, 'b', alpha=0.2)
        ax.plot(angles_plot, norm_plot, 'r--', linewidth=2, label='Нормативы')
        ax.fill(angles_plot, norm_plot, 'r', alpha=0.1)
        ax.set_xticks(angles)
        ax.set_xticklabels([f'U{i+1}' for i in range(14)])
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.grid(True)
        ax.set_title(f't = {t_span_polar[t_index]:.1f}', pad=20, fontsize=12)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.05), ncol=2, fontsize=12)
    fig.suptitle('Полярные диаграммы потерь от пожаров по временным точкам', fontsize=16, y=0.95)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)