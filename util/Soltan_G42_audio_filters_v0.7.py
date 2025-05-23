# Audio LPF generator for MiSTer 
#  -- adapted from original Matlab code written by Soltan_G42
#  -- python port by Newsdee

# NOTE: if missing, these packages can be installed via "pip install <package>" in cmd line
import numpy as np
from scipy import signal


#  suffix to .txt and .png files, set to '_py' to avoid overriding original filters
SUFFIX = '' 

SR_7MHZ = 2000000

# --------------------------------------------------------------------------- #

def write_filter(b, a, shortName, longName, fs):
    order = len(b)-1
    if order > 3:
        raise ValueError('Filter must be 3rd order or lower')
    if order < 1 or (len(b)!=len(a)):
        raise ValueErrro('Bad filter input')
    fname = shortName + ('%s.txt' % SUFFIX)
    print('%s (%s)' % (longName, fname))
    # --
    f = open(fname, 'w')
    # output version
    f.write('#Version\n')
    f.write('v1\n\n')
    # output original filename (short name)
    f.write('#Original Filename\n')
    f.write('#%s\n\n' % fname)
    # output description (long name)
    f.write('#Filter Description\n')
    f.write('#%s\n\n'%longName.strip())
    # output sample rate (FS)
    f.write('#Sampling Frequency\n')
    f.write(str(fs)+'\n\n')
    # output GAIN
    # Note that on this site: https://www-users.cs.york.ac.uk/~fisher/mkfilter/trad.html
    # GAIN seems to be always 1/min(b) from Soltan's local matlab/octave results
    f.write('#Base gain\n')
    gain = float(sum(b) * 1.39)
    coeff_x = []
    coeff_y = []
    for i in range(1, 4):
        if i<=order:
            coeff_x.append(round(b[i]/min(b)))
        else:
            coeff_x.append(0)
    for i in range(1, 4):
        if i<=order:
            coeff_y.append(a[i])
        else:
            coeff_y.append(0)

            
    f.write('%.20f\n\n' % gain)
    # output X coefficients. Zeros if filter is Order <3
    for i in range(0, 3):
        f.write('#gain scale for X%d\n'%i)
        f.write('%d\n\n' % coeff_x[i])
    # output Y coefficients. Zeros if filter is order < 3
    for i in range(0, 3):
        f.write('#gain scale for Y%d\n'%i)
        f.write('%.20f\n\n'% coeff_y[i])

    f.write('# IIR_filter coeff\n')
    f.write('.coeff_x(%.20f),\n' % gain)
    f.write('.coeff_x0(%d), .coeff_x1(%d), .coeff_x2(%d),\n' % (coeff_x[0], coeff_x[1], coeff_x[2]))
    f.write('.coeff_y0(%.20f), .coeff_y1(%.20f), .coeff_y2(%.20f)\n' % (coeff_y[0], coeff_y[1], coeff_y[2]))

    f.flush()
    f.close()
    return fname
    
# --------------------------------------------------------------------------- #

def addFilter( b, a, fname, fdesc, fs=SR_7MHZ):
    write_filter(b, a, fname, fdesc, fs=fs)
    leg_labels.append(fname)
    [w, h] = signal.freqz(b, a, freqs, fs=fs)
    tf.append( 20. * np.log10(abs(h)) ) # same as matlab's mag2db(abs(h))
    
def addSingleFilter(fname, fdesc, hz, order, ripple=None, fs=SR_7MHZ):
    Nyquist = fs/2.
    if ripple is None:
        [b, a] = signal.butter(order, hz/Nyquist)
    else:
        [b, a] = signal.cheby1(order, ripple, hz/Nyquist)
    addFilter(b, a, fname, fdesc, fs=fs)

def addCombinedFilter(fname, fdesc, hz1, hz2, fs=SR_7MHZ):
    '''combine 1st and 2nd order filters'''
    Nyquist = fs/2.
    [b1, a1] = signal.butter(1, hz1/Nyquist)
    [b2, a2] = signal.butter(2, hz2/Nyquist)
    b = np.convolve(b1, b2)
    a = np.convolve(a1, a2)
    addFilter(b, a, fname, fdesc, fs=fs)

def addMixedFilter(fname, fdesc, fs, hz1, hz2, ripple):
    '''combine 1st and 2nd order filters using Chebyshev as 2nd order'''
    # Not really useful according to Soltan_G42, but here if we want to graph it
    Nyquist = fs/2.
    [b1, a1] = signal.butter(1, hz1/Nyquist)
    [b2, a2] = signal.cheby1(2, ripple, hz2/Nyquist)
    b = np.convolve(b1, b2)
    a = np.convolve(a1, a2)
    addFilter(b, a, fname, fdesc, fs=fs)

# --------------------------------------------------------------------------- #
# main program

freqs = 2.* np.logspace(1, 5, 1001)
leg_labels = []
tf = []

# --------------------------------------------------------------------------- #

addSingleFilter('F2 Pre', '21khz 2nd order', hz=21000, order=2, ripple=5)
addSingleFilter('F2 Main', '4.5khz 2nd order', hz=5000, order=2, ripple=3.5)

# --------------------------------------------------------------------------- #

from matplotlib import pyplot as plt  # for graph output, can be removed (see end of file)

# Graph it all - this can be removed if you don't want graphs
fig, ax1 = plt.subplots()
plt.xscale('log')
ax1.set_title('MiSTer Audio Filter Response')
plt.ylim(-60, 1)     # limit Y to -60db
plt.xlim(20, 22050)  # chop off display at 22hz
for h in tf:
    ax1.plot(freqs, h)
ax1.legend(leg_labels, prop={'size': 8})
plt.grid(True, ls='--', color='gray', which='both', axis='both')
plt.savefig('Filter_Plots%s.png' % SUFFIX)
plt.savefig('Filter_Plots%s.pdf' % SUFFIX)

# EOF
