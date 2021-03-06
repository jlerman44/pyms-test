"""proc.py
"""

import sys, os
sys.path.append("/x/PyMS")

from pyms.GCMS.IO.ANDI.Function import ANDI_reader
from pyms.GCMS.Function import build_intensity_matrix_i
from pyms.Noise.SavitzkyGolay import savitzky_golay
from pyms.Baseline.TopHat import tophat
from pyms.Peak.Class import Peak
from pyms.Peak.Function import peak_sum_area

from pyms.Deconvolution.BillerBiemann.Function import BillerBiemann, \
    rel_threshold, num_ions_threshold

from pyms.Experiment.Class import Experiment
from pyms.Experiment.IO import store_expr


# deconvolution and peak list filtering parameters
points = 9; scans = 2; n = 3; t = 3000; r = 2;

andi_file = "/x/PyMS/data/a0806_077.cdf"

data = ANDI_reader(andi_file)

# integer mass
im = build_intensity_matrix_i(data)

# get the size of the intensity matrix
n_scan, n_mz = im.get_size()

# smooth data
for ii in range(n_mz):
    ic = im.get_ic_at_index(ii)
    ic1 = savitzky_golay(ic)
    ic_smooth = savitzky_golay(ic1)
    ic_base = tophat(ic_smooth, struct="1.5m")
    im.set_ic_at_index(ii, ic_base)

# do peak detection on pre-trimmed data

# get the list of Peak objects
pl = BillerBiemann(im, points, scans)

# trim by relative intensity
apl = rel_threshold(pl, r)

# trim by threshold
peak_list = num_ions_threshold(apl, n, t)

print "Number of Peaks found:", len(peak_list)

# ignore TMS ions and set mass range
for peak in peak_list:
    peak.crop_mass(50,540)
    peak.null_mass(73)
    peak.null_mass(147)
    # find area
    area = peak_sum_area(im, peak)
    peak.set_area(area)

# create an experiment
expr = Experiment("a0806_077", peak_list)

# set time range for all experiments
expr.sele_rt_range(["6.5m", "21m"])

store_expr("output/a0806_077.expr", expr)
