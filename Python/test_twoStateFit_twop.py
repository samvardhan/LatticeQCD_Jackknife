import numpy as np
import argparse as argp
from scipy.optimize import leastsq
import functions as fncs
import readWrite as rw
import physQuants as pq
import lqcdjk_fitting as fit

Z = 1.0

particle_list = [ "pion", "kaon" ]

format_list = [ "gpu", "cpu" ]

#########################
# Parse input arguments #
#########################

parser = argp.ArgumentParser( description="Calculate quark momentum fraction <x>" )

parser.add_argument( "twop_dir", action='store', type=str )

parser.add_argument( "twop_template", action='store', type=str )

parser.add_argument( "bin_size", action='store', type=int )

parser.add_argument( "-o", "--output_template", action='store', type=str, default="./*.dat" )

parser.add_argument( "-f", "--data_format", action='store', help="Data format. Should be 'gpu' or 'cpu'.", type=str, default="gpu" )

parser.add_argument( "-c", "--config_list", action='store', type=str, default="" )

args = parser.parse_args()

#########
# Setup #
#########

twopDir = args.twop_dir

twop_template = args.twop_template

binSize = args.bin_size

output_template = args.output_template

dataFormat = args.data_format

# Get configurations from given list or from given
# threep directory if list not given

configList = fncs.getConfigList( args.config_list, twopDir )

configNum = len( configList )

binNum = configNum / binSize

#######################
# Two-point functions #
#######################

# Get the real part of two-point functions
# twop[ c, t ]

twop = rw.getDatasets( twopDir, configList, twop_template, "twop" )[ :, 0, 0, ..., 0, 0 ]

tNum = twop.shape[ -1 ]

print "Read two-point functions from HDF5 files"

# Jackknife
# twop_jk[ b, t ]

twop_jk = fncs.jackknife( twop, binSize )

twop_avg = np.average( twop_jk, axis=0 )

twop_err = np.std( twop_jk, axis=0 ) * float( binNum - 1 ) / np.sqrt( float( binNum ) )

##################
# Two-state Fit  #
##################

# fitParams[ b, param ]

fitParams = fit.twoStateFit_twop( twop_jk )

c0 = fitParams[ :, 0 ]

c1 = fitParams[ :, 1 ]
        
E0 = fitParams[ :, 2 ]
                
E1 = fitParams[ :, 3 ]

tNum = 50

curve = np.zeros( ( binNum, tNum ) )

t_space = np.linspace( -2, tNum + 2, tNum )

for b in range( binNum ):

    for t in range( tNum ):

        curve[ b, t ] = fit.twoStateTwop( t, \
                                           c0[ b ], c1[ b ], \
                                           E0[ b ], E1[ b ] )

# Average over bins

curve_avg = np.average( curve, axis=0 )

curve_err = np.std( curve, axis=0 ) * float( binNum - 1 ) / np.sqrt( float( binNum ) )
                        
fitParams_avg = np.average( fitParams, axis=0 )

fitParams_err = np.std( fitParams, axis=0 ) * float( binNum - 1 ) / np.sqrt( float( binNum ) )

#####################
# Write output file #
#####################

curveOutputFilename = output_template.replace( "*", "twop_twoStateFit_curve" )

rw.writeAvgDataFile_wX( curveOutputFilename, t_space, curve_avg, curve_err )

twopOutputFilename = output_template.replace( "*", "twop" )

rw.writeAvgDataFile( twopOutputFilename, twop_avg, twop_err )

avgXParamsOutputFilename = output_template.replace( "*", "twop_twoStateFitParams" )

rw.writeTSFParamsFile_twop( avgXParamsOutputFilename, fitParams_avg, fitParams_err )

