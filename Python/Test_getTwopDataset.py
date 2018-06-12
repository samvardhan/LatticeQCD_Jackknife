import argparse as argp
import functions
import numpy as np


#parser = argp.ArgumentParser( description="test" )

#parser.add_argument( "input_filename", action='store', type=str )

#args = parser.parse_args(  )

#filename = args.input_filename

confs_dir = "/home/tuf47161/scratch/L16T32/twop_mesons"

confs_list = [ "1505" ]

fn_template = "twop.*_pion_nsmear1_Qsq10_SS.*.h5"

twop = functions.getTwopDatasets( confs_dir, confs_list, fn_template )

print twop.shape
