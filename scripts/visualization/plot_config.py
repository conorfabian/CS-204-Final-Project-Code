import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

plt.style.use('seaborn-v0_8-whitegrid')

COLORS = {'network': 'blue', 'quality': 'purple', 'buffer': 'orange', 'phase_marker': 'red', 'recovery': 'green'}
FIGURE_SIZE = (14, 8)
FIGURE_SIZE_WIDE = (16, 6)
DPI = 300

def save_figure(fig, filename):
    fig.tight_layout()
    fig.savefig(f'figures/{filename}', dpi=DPI, bbox_inches='tight')

def format_time_axis(ax):
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{int(v//60)}:{int(v%60):02d}'))
