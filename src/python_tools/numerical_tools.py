'''
AWP | Astrodynamics with Python by Alfonso Gonzalez
https://github.com/alfonsogonzalez/AWP
https://www.youtube.com/c/AlfonsoGonzalezSpaceEngineering

Numerical Tools Library
'''

from math import acos

import numpy as np
import spiceypy as spice

r2d     = 180.0 / np.pi
d2r     = 1.0  / r2d
sec2day = 1.0 / 3600.0 / 24.0
fps2kms = 0.0003048
mi2km   = 1.60934

frame_transform_dict = {
	3: spice.pxform,
	6: spice.sxform
}

def norm( v ):
	return np.linalg.norm( v )

def normed( v ):
	return v / np.linalg.norm( v )

def frame_transform( arr, ets, frame_from, frame_to ):
	'''
	Calculate length 3 or 6 vectors in frame_from
	to frame_to reference frame
	'''
	transformed = np.zeros( arr.shape )
	dim         = arr.shape[ 1 ]

	for step in range( arr.shape[ 0 ] ):
		matrix = frame_transform_dict[ dim ](
			frame_from, frame_to, ets[ step ] )
		transformed[ step ] = np.dot( matrix, arr[ step ] )
	
	return transformed

def bf2latlon( rs ):
	'''
	Calculate latitude / longitude coordinates
	from body-fixed vectors
	'''

	steps   = rs.shape[ 0 ]
	latlons = np.zeros( rs.shape )

	for step in range( steps ):
		r_norm, lon, lat = spice.reclat( rs[ step ] )
		latlons[ step ]  = [ lat * r2d, lon * r2d, r_norm ]

	return latlons

def inert2latlon( rs, frame_from, frame_to, ets ):
	'''
	Calculate latitude / longitude coordinates
	from inertial vectors
	'''

	bf = frame_transform( rs, ets, frame_from, frame_to )
	return bf2latlon( bf )

def newton_root_single( f, fp, x0, args = {} ):
	'''
	Calculate root of single variable function
	using explicit derivative function
	'''
	_args = {
		'tol'        : 1e-10,
		'max_steps'  : 50
	}
	for key in args.keys():
		_args[ key ] = args[ key ]

	delta_x = f( x0, args ) / fp( x0, args )

	for n in range( _args[ 'max_steps' ] ):
		x0     -= delta_x
		delta_x = f( x0, args ) / fp( x0, args )

		if abs( delta_x ) < _args[ 'tol' ]:
			return x0, n

	raise RuntimeError(
		'Newton\'s root solver single variable did not converge.' )

def newton_root_single_fd( f, x0, args = {} ):
	'''
	Calculate root of single variable function using
	finite differences (no explicit derivative function)
	'''
	_args = {
		'tol'        : 1e-10,
		'max_steps'  : 200,
		'diff_method': 'central',
		'diff_step'  : 1e-6
	}
	for key in args.keys():
		_args[ key ] = args[ key ]

	delta_x = f( x0, _args ) /\
				fdiff_cs( f, x0, _args[ 'diff_step' ], _args )

	for n in range( _args[ 'max_steps' ] ):
		x0     -= delta_x
		delta_x = f( x0, _args ) /\
				  fdiff_cs( f, x0, _args[ 'diff_step' ], _args )

		if abs( delta_x ) < _args[ 'tol' ]:
			return x0, n

	raise RuntimeError( 'Newton\'s root solver FD single variable did not converge. ')

def fdiff_cs( f, x, dx, args = {} ):
	'''
	Calculate central finite difference
	of single variable, scalar valued function
	'''
	return ( f( x + dx, args ) - f( x - dx, args ) ) / ( 2 * dx )

def vecs2angle( v0, v1, deg = True ):
	'''
	Calculate angle between 2 vectors
	'''
	angle = acos( np.dot( v0, v1 ) / norm( v0 ) / norm( v1 ) )
	if deg:
		angle *= r2d
	return angle
