'''dyadic_DWT.py

Provides:

1. Multichannel 1-level 2D-DWT and inverse 2D-DWT.
2. Multichannel N-levels 2D-DWT and inverse 2D-DWT.
3. Subbands gains computation.
3. Decomposition I/O.

Terminology:

* Decomposition: a python-list of SRLs (Spatial Resolution Levels)
  where each level, except for the low-pass one, has 3 subbands. Each
  SRL is a tuple (except for the low-pass one) where each element of
  the tuple is a NumPy array.

* Color <structure>: indicates that the <structure> (that can be a
  subband, an image, a {.|glued} decomposition ...) has more than one
  component.
'''

import numpy as np
import pywt
#import config
#import distortion
import image_3
#import L_DWT as L
#import H_DWT as H
#import debug
import os
import sys
HOME = os.environ['HOME']
sys.path.insert(1, HOME + "/repos/information_theory")
import information

#import logging
#logging.basicConfig(
#    level=logging.INFO,
##    format="%(pathname)s:%(lineno)d %(levelname)s %(message)s",
#    format = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
##    handlers=[
##        #logging.FileHandler("debug.log"),
##        logging.StreamHandler()
##    ]
#)

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

def print_shapes(decomposition):
    '''Show the <decomposition> structure.
    '''
    print(decomposition[0].shape, decomposition[0].dtype)
    for resolution in decomposition[1:]:
        for subband in resolution:
            print(subband.shape, subband.dtype)

def compute_gains(wavelet=_wavelet, N_levels=_N_levels, pixels_in_y=512, pixels_in_x=512):
    '''Compute the subband gains (that should be 1.0 for orthonormal filters).
    
    Parameters
    ----------
    wavelet : pywt.Wavelet
        Wavelet name.
    N_levels : int.
        Number of levels of the transform.
    pixels_in_y, pixels_in_x: int, int
        Size of the inverse transform.
        
    Returns
    -------
    A list of tuples with the gain of each subband. 
    
    '''
    zero = np.zeros((pixels_in_y, pixels_in_x))
    DWT_zero = pywt.wavedec2(data=zero, wavelet=wavelet, mode=_extension_mode, level=N_levels)
    DWT_zero[0][DWT_zero[0].shape[1]//2, DWT_zero[0].shape[0]//2] = 1
    img_delta = pywt.waverec2(DWT_zero, wavelet=wavelet, mode=_extension_mode)
    DWT_zero[0][DWT_zero[0].shape[1]//2, DWT_zero[0].shape[0]//2] = 0
    energy = information.energy(img_delta)
    gains = [energy]
    for sr in DWT_zero[1:]:
        sr_gains = []
        for sb in sr:
            sb[sb.shape[1]//2, sb.shape[0]//2] = 1
            img_delta = pywt.waverec2(DWT_zero, wavelet=wavelet, mode=_extension_mode)
            sb[sb.shape[1]//2, sb.shape[0]//2] = 0
            energy = information.energy(img_delta)
            sr_gains.append(energy)
        gains.append(tuple(sr_gains))
    return gains

def extract_decomposition(color_decomposition, component_I):
    '''Extract a component (in form of a decomposition) from a color
decomposition.

    Parameters
    ----------
    color_decomposition : Python-list
        An input list of color SRLs.
    component_index : int
        The component to extract.

    Returns
    -------
    A (monochromatic) decomposition: list

    '''
    decomposition = [color_decomposition[0][..., component_I]]
    for color_resolution in color_decomposition[1:]:
        resolution = [] 
        for color_subband in color_resolution:
            resolution.append(color_subband[..., component_I])
        decomposition.append(tuple(resolution))
    return decomposition

def insert_decomposition(color_decomposition, decomposition, component_I):
    '''Insert a decomposition (a list of tuples of 2D subbands (each one a
(row, column)-np.ndarray) in a color decomposition (a list of tuples
of 3D subbands (each one a (row, column, component)-np.ndarray).

    Parameters
    ----------
    color_decomposition : Python-list
        An output list of color SRLs.
    decomposition : Python-list.
        An input list of (monochromatic) SRLs.
    component_I : int
        The index of the inserted component.

    Returns
    -------
    None.

    '''
    color_decomposition[0][..., component_I] = decomposition[0][:] # LL^n subband
    for color_resolution, resolution in zip(color_decomposition, decomposition):
        color_resolution[..., component_I] = resolution[component_I]
    
def glue_decomposition(decomposition):
    '''Convert a list of (monocromatic) subbands to a (row, column) NumPy array.

    Parameters
    ----------
    decomposition : Python-list
        The input decomposition to convert in a np.ndarray.

    Returns
    -------
    The glued decomposition : a (row, column) np.ndarray.
        A single monochromatic image with all the wavelet coefficients.
    The generated slices : a Python-list.
        The data structure in the "wavedec2" format that describes the original decomposition.
    '''
    glued_decomposition, slices = pywt.coeffs_to_array(decomposition)
    return glued_decomposition, slices

def unglue_decomposition(glued_decomposition, slices):
    '''Convert a glued decomposition (a (row, column) np.array) in a list of tuples
of subbands (each one a (row, column) np.ndarray).
    Parameters
    ----------
    glued_decomposition : np.ndarray
        The glued decomposition to split.
    slices : list
        The structure of the decomposition in "wavdec2" format.
    Returns
    -------
    The decomposition : a Python-list of SRLs.
    '''
    decomposition = pywt.array_to_coeffs(glued_decomposition, coeff_slices=slices, output_format='wavedec2')
    return decomposition

def glue_color_decomposition(color_decomposition):
    '''Convert a list of color SRLs to a (row, column, component) NumPy array.

    Parameters
    ----------
    color_decomposition : Python-list
        The input decomposition to convert in a np.ndarray.

    Returns
    -------
    The glued color decomposition : a [row, column, component] np.ndarray.
        A single color image with all the wavelet coefficients.
    The list of the generated slices : a Python-list (with one item per component).
        The description of the data structure in the "wavedec2" format that describes the original decomposition.
    '''
    N_comps = color_decomposition[0].shape[2]
    dtype = color_decomposition[0].dtype
    glued_decompositions = []
    slices = [None]*3
    for component_I in range(N_comps):
        decomposition  = extract_decomposition(color_decomposition, component_I)
        glued_decomposition, slices[component_I] = glue_decomposition(decomposition)
        glued_decompositions.append(glued_decomposition)
    N_rows = glued_decompositions[0].shape[0]
    N_cols = glued_decompositions[0].shape[1]
    glued_color_decomposition = np.empty(shape=(N_rows, N_cols, N_comps), dtype=dtype)
    for component_I in range(N_comps):
        glued_color_decomposition[..., component_I] = glued_decompositions[component_I][:]
    return glued_color_decomposition, slices

def unglue_color_decomposition(glued_color_decomposition, slices):
    '''Convert a (row, column, component) NumPy array in a list of color
SRLs.

    Parameters
    ----------
    glued_color_decomposition : a (row, column, component) NumPy array.
        The glued color decomposition to split.
    slices : list
        The description of the structures (one per component)  of the decomposition in "wavdec2" format.

    Returns
    -------
    The color decomposition : a Python-list of SRLs.
       The same structure as analyze().
    '''

    #N_levels = len(slices[0]) - 1
    N_levels = len(slices[1]) - 1
    logger.info(f"N_levels={N_levels}")
    #print("---", slices)
    #print("---", len(slices))
    #print("---", slices[0])
    N_comps = glued_color_decomposition.shape[2]
    decompositions = []
    for component_I in range(N_comps):
        decompositions.append(unglue_decomposition(glued_color_decomposition[..., component_I], slices[component_I]))
    # "decompositions" is a list with three decompositions.

    ########### notice that the following code is used also in analyze() ##############
    color_decomposition = []
    # LL^N_levels and H^N_levels subbands (both have the same resolution)
    N_rows_subband, N_columns_subband = decompositions[0][0].shape # All subbands in the SRL with the same shape
    LL = np.empty(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    LH = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    HL = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    HH = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    for component_I in range(N_comps):
        LL[:,:, component_I] = decompositions[component_I][0][:,:]
        LH[:,:, component_I] = decompositions[component_I][1][0][:,:]
        HL[:,:, component_I] = decompositions[component_I][1][1][:,:]
        HH[:,:, component_I] = decompositions[component_I][1][2][:,:]
    color_decomposition.append(LL)
    color_decomposition.append((LH, HL, HH))
    
    # For the rest of SRLs (have increasing resolutions)
    for resolution_I in range(2, N_levels+1):
        N_rows_subband, N_columns_subband = decompositions[0][resolution_I][0].shape
        prev_N_columns_subband = N_columns_subband
        LH = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
        HL = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
        HH = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
        for component_I in range(N_comps):
            LH[:,:, component_I] = decompositions[component_I][resolution_I][0][:,:]
            HL[:,:, component_I] = decompositions[component_I][resolution_I][1][:,:]
            HH[:,:, component_I] = decompositions[component_I][resolution_I][2][:,:]
        color_decomposition.append((LH, HL, HH))
    return color_decomposition

def write_glued(color_decomposition, prefix=str, image_number=0):
    '''Write a color decomposition into disk file, as a single color
image, in glued format.

    Parameters
    ----------
    color_decomposition : A Python-list of color SRLs.
        The color decomposition to write in disk.
    prefix : A Python-string.
        The prefix of the output file.
    image_number : A signed integer.
        The image number in a possible sequence of images (frames).

    Returns
    -------
    output_length : int
        The length (in bytes) of the output file.
    slces : list
        Structure of the decomposition of each component.

    '''
    logger.debug(f"color_decomposition={color_decomposition}")
    logger.debug(f"prefix={prefix}")
    logger.debug(f"image_number={image_number}")
    glued_color_decomposition, slices = glue_color_decomposition(color_decomposition)
    output_length = image_3.write(glued_color_decomposition, prefix, image_number)
    return output_length, slices


def read_glued(slices, prefix, image_number=0):
    '''Read a color decomposition from a (single) disk file.

    Parameters
    ----------
    slices : a Python-list
        The structure of the decomposition of each component.
    prefix : a Python-string
        The prefix of the inputf¡ file.
    image_number : A signed integer.
        The image number in a possible sequence of images (frames).

    Returns
    -------
    A color decomposition : a Python-list of color SRLs.
        The color decomposition read from the disk.
    '''
    logger.debug(f"slices={slices}")
    logger.debug(f"prefix={prefix}")
    logger.debug(f"image_number={image_number}")
    glued_color_decomposition = image_3.read(prefix, image_number)
    color_decomposition = unglue_color_decomposition(glued_color_decomposition, slices)
    return color_decomposition

def write_unglued(color_decomposition, prefix, image_number=0):
    '''Write a color decomposition in several disk files (one per color subband).

    Parameters
    ----------
    color_decomposition : A Python-list of color SRLs.
        The color decomposition to write in disk.
    prefix : A Python-string.
        The prefix of the output files.
    image_number : A signed integer.
        The image number in a possible sequence of images (frames).

    Returns
    -------
    output_length : int
        The total length (in bytes) of the output files.
    slces : list
        Structure of the decomposition of each component.

    '''
    logger.debug(f"color_decomposition={color_decomposition}")
    logger.info(f"prefix={prefix}")
    logger.info(f"image_number={image_number}")
    N_comps = color_decomposition[0].shape[2]
    #_color_image = [None]*N_comps
    #n_resolutions = len(color_decomposition)
    #n_resolutions = N_levels+1
    LL = color_decomposition[0]
    N_levels = len(color_decomposition) - 1
    logger.info(f"N_levels={N_levels}")
    output_length = image_3.write(LL, f"{prefix}LL{N_levels}", image_number)
    resolution_I = N_levels
    aux_decom = [color_decomposition[0][..., 0]]
    for resolution in color_decomposition[1:]:
        subband_names = ["LH", "HL", "HH"]
        sb = 0
        aux_resol = []
        for sbn in subband_names:
            output_length += image_3.write(resolution[sb], f"{prefix}{sbn}{resolution_I}", image_number)
            aux_resol.append(resolution[sb][..., 0])
            sb += 1
        resolution_I -= 1
        aux_decom.append(tuple(aux_resol))
    slices = pywt.coeffs_to_array(aux_decom)[1]
    return output_length, slices

def _add(decomposition, val=32768, dtype=np.uint16):
    '''Add a scalar <val> to the <decomposition>.
    '''
    new_decomp = [(decomposition[0] + val).astype(dtype)]
    for resolution in decomposition[1:]:
        new_resol = []
        for subband in resolution:
            new_resol.append((subband + val).astype(dtype))
        new_decomp.append(tuple(new_resol))
    return new_decomp

def add(decomposition, val=32768):
    '''Add a scalar <val> to the <decomposition>.
    '''
    logger.debug(f"decomposition={decomposition}")
    logger.debug(f"val={val}")
    new_decomp = [decomposition[0] + val]
    for resolution in decomposition[1:]:
        new_resol = []
        for subband in resolution:
            new_resol.append(subband + val)
        new_decomp.append(tuple(new_resol))
    return new_decomp

def set_type(decomposition, dtype=np.uint16):
    '''Change the type of the <decomposition>.
    '''
    logger.debug(f"decomposition={decomposition}")
    logger.debug(f"dtype={dtype}")
    new_decomp = [decomposition[0].astype(dtype)]
    for resolution in decomposition[1:]:
        new_resol = []
        for subband in resolution:
            new_resol.append(subband.astype(dtype))
        new_decomp.append(tuple(new_resol))
    return new_decomp

def copy(decomposition):
    logger.debug(f"decomposition={decomposition}")
    new_decomp = [decomposition[0].copy()]
    for resolution in decomposition[1:]:
        new_resol = []
        for subband in resolution:
            new_resol.append(subband.copy())
    return new_decomp

def read_unglued(slices, prefix, image_number=0):
    '''Read a color decomposition from the disk (one file per color subband).

    Parameters
    ----------
    slices : a Python-list
        The structure of the decomposition of each component.
    prefix : a Python-string.
        The prefix of the input files.
    image_number : a signed integer.
        The image number in a possible sequence of images (frames).

    Returns
    -------
    color_decomposition : a Python-list of color SRLs.
        The color decomposition read from the disk.

    '''
    N_levels = len(slices) - 1
    LL = image_3.read(f"{prefix}LL{N_levels}", image_number)
    color_decomposition = [LL]
    resolution_I = N_levels
    for l in range(N_levels, 0, -1):
        subband_names = ["LH", "HL", "HH"]
        sb = 0
        resolution = []
        for sbn in subband_names:
            resolution.append(image_3.read(f"{prefix}{sbn}{resolution_I}", image_number))
            sb += 1
        color_decomposition.append(tuple(resolution))
        resolution_I -= 1
    return color_decomposition

def entropy(decomposition):
    entro = information.entropy(decomposition[0].flatten().astype(np.int16))
    accumulated_entropy = entro * decomposition[0].size
    image_size = decomposition[0].size
    for sr in y[1:]:
        for sb in sr:
            entro = information.entropy(sb.flatten().astype(np.int16))
            accumulated_entropy += (entro * sb.size)
            image_size += sb.size
    avg_entropy = accumulated_entropy / image_size
    return avg_entropy

#########################################################

# Write each subband of a decomposition in a different PNG file using
# <prefix><image_number><LL|LH|HL|HH><level>.png filename.
def _write_decomposition(color_decomposition, prefix, image_number=0, N_levels=_N_levels):
    '''Write a color decomposition into disk file, as a collection of color subbands.

    Parameters
    ----------
    color_decomposition : A Python-list of color SRLs.
        The color decomposition to write in disk.
    prefix : A Python-string.
        The prefix of the output file.
    image_number : A signed integer.
        The image number in a possible sequence of images (frames).

    Returns
    -------
    The length (in bytes) of the output.

    '''
    N_comps = color_decomposition[0].shape[2]
    #_color_image = [None]*N_comps
    #n_resolutions = len(color_decomposition)
    #n_resolutions = N_levels+1
    LL = color_decomposition[0]
    output_length = L.write(LL, f"{prefix}R{N_levels}", image_number)
    resolution_I = N_levels
    for resolution in color_decomposition[1:]:
        output_length += H.write(resolution, f"{prefix}R{resolution_I}", image_number)
        resolution_I -= 1
    return output_length
        
    #for c in range(N_comps):
    #    decomposition = [color_decomposition[0][:,:,c]]
    #    LL = decomposition[0]
    #    for l in range(1, n_levels+1):
    #        decomp.append((color_decomp[l][0][:,:,c], color_decomp[l][1][:,:,c], color_decomp[l][2][:,:,c]))
    #    _color_image[c], slices = pywt.coeffs_to_array(decomp)
    #color_image = np.ndarray((_color_image[0].shape[0], _color_image[0].shape[1], N_comps), dtype=_color_image[0].dtype)
    #for c in range(N_comps):
    #    color_image[:,:,c] = _color_image[c][:,:]
    #image.write(color_image.astype(np.int16), fn)
    #return slices

#def read(prefix:str, slices:list=None) -> np.ndarray: 
def _read_decomposition(prefix:str, image_number:int=0, N_levels:int=_N_levels) -> np.ndarray:
    #LL = L.read(f"{prefix}_{N_levels+1}", image_number)
    LL = L.read(f"{prefix}R{N_levels}", image_number)
    color_decomposition = [LL]
    shape = list(LL.shape)
    #for l in range(N_levels+1, 0, -1):
    for l in range(N_levels, 0, -1):
        resolution = H.read(f"{prefix}R{l}", image_number, tuple(shape))
        color_decomposition.append(resolution)
        shape[0] *= 2
        shape[1] *= 2
    return color_decomposition
    #color_image = image.read(f)
    #N_comps = color_image.shape[2]
    #color_decomp = [None]*N_comps
    #for c in range(N_comps):
    #    color_decomp[c] = pywt.array_to_coeffs(color_image[:,:,c], slices, output_format='wavedec2')
    #output = []
    #n_rows_subband, n_columns_subband = color_decomposition[0][0].shape
    #LL = np.empty(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #LH = np.zeros(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #HL = np.zeros(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #HH = np.zeros(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #for c in range(N_comps): # For each color component
    #    LL[:,:,c] = color_decomposition[c][0][:,:]
    #    LH[:,:,c] = color_decomposition[c][1][0][:,:]
    #    HL[:,:,c] = color_decomposition[c][1][1][:,:]
    #    HH[:,:,c] = color_decomposition[c][1][2][:,:]
    #output.append(LL)
    #output.append((LH, HL, HH))
    #for r in range(2, n_levels+1):
    #    n_rows_subband, n_columns_subband = color_decomposition[0][r][0].shape
    #    prev_n_columns_subband = n_columns_subband
    #    LH = np.zeros(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #    HL = np.zeros(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #    HH = np.zeros(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #    for c in range(N_comps):
    #        LH[:,:,c] = color_decomposition[c][r][0][:,:]
    #        HL[:,:,c] = color_decomposition[c][r][1][:,:]
    #        HH[:,:,c] = color_decomposition[c][r][2][:,:]
    #    output.append((LH, HL, HH))

    #return output

'''
def normalize_256(color_decomposition:list, n_levels:int) -> (list, float, float):
    #Normalize the decomposition to the range [0, 255]. The maximum n
and the minimum values are also returned.
    N_comps = color_decomposition[0].shape[2]
    #_color_image = [None]*N_comps
    #n_resolutions = len(color_decomposition)
    #n_resolutions = n_levels+1
    max = -100000
    min = 100000
    LL = color_decomposition[0]
    max = 
    L.write(LL, f"{prefix}_{n_levels}", image_number)
    resolution_I = n_levels
    for resolution in color_decomposition[1:]:
        H.write(resolution, f"{prefix}_{resolution_I}", image_number)
        resolution_I -= 1
'''
    
def __compute_deltas(n_levels):
    delta = []
    dims = (512, 512, 3)
    x = np.zeros(dims)
    L = DWT.analyze(x, n_levels)
    L[0][1,1,:] = [100, 100, 100]
    y = DWT.synthesize(L, l)
    e = distortion.average_energy(y)
    for l in range(1, n_levels):
        x = np.zeros(dims)
        L = LP.analyze(x, n_levels)
        L[l][1,1,:] = [100, 100, 100]
        y = DWT.synthesize(L)
        ee = distortion.average_energy(y)
        gain = e/ee
        delta.append(gain)
        print(gain)
        e = ee
    return delta

def __analyze_step(color_image, wavelet=_wavelet):
    n_rows, n_columns, N_comps = color_image.shape[0]//2, color_image.shape[1]//2, color_image.shape[2]
    LL = np.empty(shape=(n_rows, n_columns, N_comps), dtype=np.float64)
    LH = np.empty(shape=(n_rows, n_columns, N_comps), dtype=np.float64)
    HL = np.empty(shape=(n_rows, n_columns, N_comps), dtype=np.float64)
    HH = np.empty(shape=(n_rows, n_columns, N_comps), dtype=np.float64)
    #N_comps = color_image.shape[2]
    #color_decomposition = [None]*N_comps
    for c in range(N_comps):
        #color_decomposition[c] = pywt.dwt2(data=color_image[:,:,c], wavelet=wavelet, mode='per')
        LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c]) = pywt.dwt2(data=color_image[:,:,c], wavelet=wavelet, mode='per')
    #return color_decomposition
    #return np.array([color_decomposition[0][0], color_decomposition[1][0], color_decomposition[2][0]]), ()
    return (LL, (LH, HL, HH))

def __synthesize_step(LL, H, wavelet=_wavelet):
    N_comps = len(color_decomposition)
    color_image = []
    for c in range(N_comps):
        channel = pywt.idwt2(color_decomposition[c], wavelet=wavelet, mode='per')
        color_image.append(channel)
    return np.array(color_image)
def __analyze(color_image, wavelet=_wavelet, levels=_N_levels):
    H = [None]*levels
    L, H[0] = analyze_step(color_image, wavelet)
    for i in range(levels-1):
        L, H[i+1] = analyze_step(L, wavelet)
    #return [L, *H[::-1]]
    return [L, *H]

def __synthesize(color_decomposition, wavelet=_wavelet, N_levels=_N_levels):
    color_image = synthesize_step(color_decomposition[0], color_decomposition[1], wavelet)
    for i in range(N_levels-1):
        color_image = synthesize_step(color_image, color_decomposition[i], wavelet)
    return color_image
