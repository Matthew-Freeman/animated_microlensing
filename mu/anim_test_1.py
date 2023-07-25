import numpy as np
# import model
from BAGLE import model
import matplotlib.pyplot as plt

# Directories:
dw_dir = '/g2/scratch/jlu/microlens/OB110462/a_2021_07_08/model_fits/ogle_hst_phot_ast_gp/base_a/'
ew_dir = '/g2/scratch/jlu/microlens/OB110462/a_2021_12_28/model_fits/ogle_hst_phot_ast/pspl/fixed_weight/'

# DW Fit
t0_dw = 55760.20
u0_dw = -0.07
tE_dw = 289.75 # days
log_thetaE_dw = 0.50
piS_dw = 0.16
piEE_dw = 0.008
piEN_dw = -0.13
xS0_dw = np.array([229.77, -214.29])
muS_dw = np.array([-2.24, -3.59])
b_sff_dw = [0.89]
mag_base_dw = [19.86]
raL = '17:51:40.19'
decL = '-29:53:26.3'


from astropy.table import Table
t = Table.read(dw_dir + 'a0_.fits')

# In the case of these fits, map_idx = mle_idx, so it doesn't matter what we use.
map_idx = np.argmax(t['weights'])
mle_idx = np.argmax(t['logLike'])
params = t[mle_idx]

print(params)

ev1 = model.PSPL_PhotAstrom_Par_Param3(t0_dw, u0_dw, tE_dw, log_thetaE_dw, piS_dw,
                                       piEE_dw, piEN_dw, xS0_dw[0], xS0_dw[1],
                                       muS_dw[0], muS_dw[1],
                                       b_sff_dw, mag_base_dw, raL=raL, decL=decL)

t = np.arange(55000, 57000, 1)

m = ev1.get_photometry(t)

plt.plot(t, m)
plt.gca().invert_yaxis()
plt.show()