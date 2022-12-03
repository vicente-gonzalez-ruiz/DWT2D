'''Multichannel 2D forward and inverse DWT (Discrete Wavelet Transform).
'''

import numpy as np
import pywt

import logging
logger = logging.getLogger(__name__)
#logging.basicConfig(format="[%(filename)s:%(lineno)s %(funcName)s()] %(message)s")
#logger.setLevel(logging.CRITICAL)
#logger.setLevel(logging.ERROR)
logger.setLevel(logging.WARNING)
#logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)

#_wavelet = pywt.Wavelet("haar")
#_wavelet = pywt.Wavelet("db1")
_wavelet = pywt.Wavelet("db5")
#_wavelet = pywt.Wavelet("db20")
#_wavelet = pywt.Wavelet("bior3.5")
#_wavelet = pywt.Wavelet("bior3.7")
#_wavelet = pywt.Wavelet("bior6.8")
#_wavelet = pywt.Wavelet("rbio6.8")

# Number of levels of the DWT
#N_levels = config.n_levels
_N_levels = 5

# Signal extension mode
#_extension_mode = "symmetric" # default
#_extension_mode = "constant"
#_extension_mode = "reflect"
#_extension_mode = "periodic"
#_extension_mode = "smooth"
#_extension_mode = "antisymmetric"
#_extension_mode = "antireflect"
_extension_mode = "periodization" # Generates the inimal number of coeffs
#_extension_mode = config.dwt_extension_mode

logger.info(f"Wavelet={_wavelet}")
logger.info(f"DWT extension mode={_extension_mode}")

def analyze_step(color_image, wavelet=_wavelet):
    '''Color 1-levels forward 2D-DWT.

    Parameters
    ----------
    color_image : [row, column, component] np.ndarray
        Color image to be analyzed.
    wavelet : pywt.Wavelet
        Wavelet name.

    Returns
    -------
    A 1-levels color decomposition : tuple
        Subbands (LL, (LH, HL, HH)).

    '''
    logger.info(f"wavelet={wavelet}")
    N_comps = color_image.shape[2]
    decomposition_by_component = [None]*N_comps
    # A color decomposition 
    for c in range(N_comps):
        decomposition_by_component[c] = pywt.dwt2(data=color_image[:,:,c], wavelet=wavelet, mode=_extension_mode)
    assert decomposition_by_component[0][0].shape == decomposition_by_component[0][1][0].shape
    N_rows_subband, N_columns_subband = decomposition_by_component[0][0].shape # All subbands have the same shape
    LL = np.empty(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    LH = np.empty(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    HL = np.empty(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    HH = np.empty(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    for c in range(N_comps):
        LL[:,:,c] = decomposition_by_component[c][0][:,:]
        LH[:,:,c] = decomposition_by_component[c][1][0][:,:]
        HL[:,:,c] = decomposition_by_component[c][1][1][:,:]
        HH[:,:,c] = decomposition_by_component[c][1][2][:,:]
    return (LL, (LH, HL, HH)) # Ojo, para ser coherentes, debería
                              # retornarse una lista, no una tupla, y
                              # así tendríamos una descomposición de 1
                              # nivel

def synthesize_step(LL, H, wavelet=_wavelet):
    '''Color 1-levels backward 2D-DWT.

    Parameters
    ----------
    LL : np.ndarray
        Low-pass subband.
    H : tuple
        High-pass subbands.
    wavelet : pywt.Wavelet
        Wavelet name.

    Returns
    -------
    A color image : NumPy array.
      An array with structure [row, column, component]. 

    '''
    logger.info(f"wavelet={wavelet}")
    LH, HL, HH = H
    N_comps = LL.shape[2] #len(LL)
    _color_image = []
    for c in range(N_comps):
        image = pywt.idwt2((LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c])), wavelet=wavelet, mode=_extension_mode)
        #image = pywt.idwt2((LL[:,:,c], np.array(H)[:,:,c]), wavelet=wavelet, mode=_extension_mode)
        _color_image.append(image)
    n_rows, n_columns = _color_image[0].shape
    #n_rows = _color_image[0].shape[0]
    #n_columns = _color_image[0].shape[1]
    color_image = np.ndarray((n_rows, n_columns, N_comps), dtype=np.float64)
    for c in range(N_comps):
        color_image[:,:,c] = _color_image[c][:,:]
    return color_image

def analyze(color_image, wavelet=_wavelet, N_levels=_N_levels):
    '''Color N-levels forward 2D-DWT.

    Parameters
    ----------
    color_image : [A (row, column, component) np.ndarray
        Color image to be analyzed.
    wavelet : pywt.Wavelet
        Wavelet name.
    N_levels : int
        Number of levels of the transform.

    Returns
    -------
        A color decomposition : list

    '''
    logger.debug(f"color_image={color_image}")
    logger.info(f"wavelet={wavelet}")
    logger.info(f"N_levels={N_levels}")
    N_comps = color_image.shape[2]
    decomposition_by_component = [None]*N_comps
    for c in range(N_comps):
        decomposition_by_component[c] = pywt.wavedec2(data=color_image[:,:,c], wavelet=wavelet, mode=_extension_mode, level=N_levels)

    color_decomposition = []
    # LL^N_levels and H^N_levels subbands (both have the same resolution)
    N_rows_subband, N_columns_subband = decomposition_by_component[0][0].shape # All subbands in the SRL with the same shape
    #prev_N_rows_subband = N_rows_subband
    #prev_N_columns_subband = N_columns_subband
    LL = np.empty(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    LH = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    HL = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    HH = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    for c in range(N_comps): # For each color component
        LL[:,:,c] = decomposition_by_component[c][0][:,:]
        LH[:,:,c] = decomposition_by_component[c][1][0][:,:]
        HL[:,:,c] = decomposition_by_component[c][1][1][:,:]
        HH[:,:,c] = decomposition_by_component[c][1][2][:,:]
    color_decomposition.append(LL)
    color_decomposition.append((LH, HL, HH))
    
    # For the rest of SRLs (have increasing resolutions)
    for r in range(2, N_levels+1):
        N_rows_subband, N_columns_subband = decomposition_by_component[0][r][0].shape
        #if prev_N_rows_subband * 2 < N_rows_subband:
        #    N_rows_subband += 1
        #prev_N_rows_subband = N_rows_subband
        #if prev_N_columns_subband * 2 < N_columns_subband:
        #    N_columns_subband += 1
        prev_N_columns_subband = N_columns_subband
        LH = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
        HL = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
        HH = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
        for c in range(N_comps):
            LH[:,:,c] = decomposition_by_component[c][r][0][:,:]
            HL[:,:,c] = decomposition_by_component[c][r][1][:,:]
            HH[:,:,c] = decomposition_by_component[c][r][2][:,:]
        color_decomposition.append((LH, HL, HH))

    return color_decomposition # [LL^n, (LH^n, HL^n, HH^n), ..., (LH^1, HL^1, HH^1)], each subband multicomponent.

def synthesize(color_decomposition, wavelet=_wavelet, N_levels=_N_levels):
    '''Color N-levels backward 2D-DWT.

    Parameters
    ----------
    color_decomposition : list
        A decomposition of color subbands.
    wavelet : pywt.Wavelet
        Wavelet name.
    N_levels : int
        Number of levels of the transform.

    Returns
    -------
        A color image : a [row, column, component] np.ndarray.
    
    '''
    logger.info(f"wavelet={wavelet}")
    logger.info(f"N_levels={N_levels}")
    _color_image = []
    N_comps = color_decomposition[0].shape[2]
    for c in range(N_comps):
        decomposition = [color_decomposition[0][:,:,c]] # LL^n
        # A color decomposition-component == decomposition.
        for l in range(1, N_levels+1):
            decomposition.append((color_decomposition[l][0][:,:,c], color_decomposition[l][1][:,:,c], color_decomposition[l][2][:,:,c])) # (LH^l, HL^l, HH^l)
        _color_image.append(pywt.waverec2(decomposition, wavelet=wavelet, mode=_extension_mode))
    color_image = np.ndarray((_color_image[0].shape[0], _color_image[0].shape[1], N_comps), dtype=_color_image[0].dtype)
    #print(_color_image[0].shape, color_image.shape)
    for c in range(N_comps):
        color_image[:,:,c] = _color_image[c][:,:]
    
    #print(N_comps)
    #_color_image = []
    #for c in range(N_comps):
    #    channel = pywt.waverec2(color_decomposition[c], wavelet=wavelet, mode=_extension_mode)
    #    _color_image.append(channel)
    #n_rows = _color_image[0].shape[0]
    #n_columns = _color_image[0].shape[1]
    #color_image = np.ndarray((n_rows, n_columns, N_comps), np.float64)
    #for c in range(N_comps):
    #    color_image[:,:,c] = _color_image[c][:,:]
    return color_image
