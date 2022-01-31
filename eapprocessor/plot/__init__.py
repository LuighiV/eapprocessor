import matplotlib.pyplot as plt


def save_figure(fig, filename, tight=True):
    if tight:
        fig.tight_layout()
    fig.savefig(filename)


def set_tex_enabled(enabled):
    if enabled:
        plt.rcParams.update({
            "text.usetex": True,
            "font.family": "serif",
            "font.serif": ["Palatino"],
        })
    else:
        plt.rcParams.update({
            "text.usetex": False,
            "font.family": "serif",
            "font.serif": ["Palatino"],
        })
