import math
import numpy as np
import matplotlib.pyplot as plt


def mi_compute(halstead_volume, complexity, sloc, comments):
    '''Compute the Maintainability Index (MI) given the Halstead Volume, the
    Cyclomatic Complexity, the SLOC number and the number of comment lines.
    Usually it is not used directly but instead :func:`~radon.metrics.mi_visit`
    is preferred.
    '''
    if any(metric <= 0 for metric in (halstead_volume, sloc)):
        return 100.0
    sloc_scale = math.log(sloc)
    volume_scale = math.log(halstead_volume)
    comments_scale = math.sqrt(2.46 * math.radians(comments))
    # Non-normalized MI
    nn_mi = (
        171
        - 5.2 * volume_scale
        - 0.23 * complexity
        - 16.2 * sloc_scale
        + 50 * math.sin(comments_scale)
    )
    return min(max(0.0, nn_mi * 100 / 171.0), 100.0)


# ---------------------------------------------------------
# Baseline values
# ---------------------------------------------------------

BASE_HALSTEAD_VOLUME = 500
BASE_COMPLEXITY = 10
BASE_SLOC = 100
BASE_COMMENTS = 10


# ---------------------------------------------------------
# Parameter ranges
# ---------------------------------------------------------

halstead_volumes = np.linspace(10, 5000, 500)
complexities = np.linspace(1, 100, 500)
slocs = np.linspace(10, 5000, 500)
comments = np.linspace(0, 1000, 500)


# ---------------------------------------------------------
# Calculate MI while varying one parameter at a time
# ---------------------------------------------------------

mi_vs_volume = [
    mi_compute(
        halstead_volume=volume,
        complexity=BASE_COMPLEXITY,
        sloc=BASE_SLOC,
        comments=BASE_COMMENTS,
    )
    for volume in halstead_volumes
]

mi_vs_complexity = [
    mi_compute(
        halstead_volume=BASE_HALSTEAD_VOLUME,
        complexity=complexity,
        sloc=BASE_SLOC,
        comments=BASE_COMMENTS,
    )
    for complexity in complexities
]

mi_vs_sloc = [
    mi_compute(
        halstead_volume=BASE_HALSTEAD_VOLUME,
        complexity=BASE_COMPLEXITY,
        sloc=sloc,
        comments=BASE_COMMENTS,
    )
    for sloc in slocs
]

mi_vs_comments = [
    mi_compute(
        halstead_volume=BASE_HALSTEAD_VOLUME,
        complexity=BASE_COMPLEXITY,
        sloc=BASE_SLOC,
        comments=comment,
    )
    for comment in comments
]


# ---------------------------------------------------------
# Create plots
# ---------------------------------------------------------

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Halstead Volume
axes[0, 0].plot(halstead_volumes, mi_vs_volume)
axes[0, 0].set_title("Effect of Halstead Volume on MI")
axes[0, 0].set_xlabel("Halstead Volume")
axes[0, 0].set_ylabel("Maintainability Index")
axes[0, 0].grid(True)

# Cyclomatic Complexity
axes[0, 1].plot(complexities, mi_vs_complexity)
axes[0, 1].set_title("Effect of Cyclomatic Complexity on MI")
axes[0, 1].set_xlabel("Cyclomatic Complexity")
axes[0, 1].set_ylabel("Maintainability Index")
axes[0, 1].grid(True)

# SLOC
axes[1, 0].plot(slocs, mi_vs_sloc)
axes[1, 0].set_title("Effect of SLOC on MI")
axes[1, 0].set_xlabel("Source Lines of Code (SLOC)")
axes[1, 0].set_ylabel("Maintainability Index")
axes[1, 0].grid(True)

# Comments
axes[1, 1].plot(comments, mi_vs_comments)
axes[1, 1].set_title("Effect of Comments on MI")
axes[1, 1].set_xlabel("Comment Lines")
axes[1, 1].set_ylabel("Maintainability Index")
axes[1, 1].grid(True)


# ---------------------------------------------------------
# Improve layout and display
# ---------------------------------------------------------

plt.suptitle(
    "Sensitivity of Maintainability Index to Individual Parameters",
    fontsize=16,
)

plt.tight_layout()
plt.show()