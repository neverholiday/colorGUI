#!/usr/bin/env python

import cv2
import numpy as np
import argparse
import configparser


class ColorCalibrator( object ):

	'''
		Color calibrator module
		args : 
			pathConfig -> Path of configuration file
	'''

	def __init__( self, pathConfig = 'config.ini' ):
		
		## Set path of config 
		self.__pathConfig = pathConfig

		## Instance of config parser
		self.__config = configparser.ConfigParser()

	def colorSpace( self, image, lowerBound, upperBound ):
		'''
			colorSpace function
			args:
				image -> Image from opencv format ( 0-255 )
				lowerBound -> Lower boundary of HSV format
				upperBound -> Upper boundary of HSV format
			return:
				mask -> Mask of image, binary image
				res -> Image from image ( bitwise_and ) mask
		'''

		## Convert color
		imageHSV = cv2.cvtColor( image, cv2.COLOR_BGR2HSV )

		## Create mask from upper and lower boundary 
		mask = cv2.inRange( imageHSV, lowerBound, upperBound )

		## Create res
		res = cv2.bitwise_and( image, image, mask=mask )

		return mask, res
	
	def generateConfig( self, HSVDict ):
		'''
			createConfig funtion
			This function generate config for using cut region of color HSV format.
			NOTE : This config save only green and orage first
			args:
				HSVDict -> Dict HSV color, format : { "Color" : [  H_low, S_low, V_low, H_high, S_high, V_high ] }
		'''
		
		for color in HSVDict.keys():
		
			self.__config.add_section( color )
			self.__config.set( color, "H_Low", str( HSVDict[ color ][ 0 ] ) )
			self.__config.set( color, "S_Low", str( HSVDict[ color ][ 1 ] ) )
			self.__config.set( color, "V_Low", str( HSVDict[ color ][ 2 ] ) )
			self.__config.set( color, "H_Upper", str( HSVDict[ color ][ 3 ] ) )
			self.__config.set( color, "S_Upper", str( HSVDict[ color ][ 4 ] ) )
			self.__config.set( color, "V_Upper", str( HSVDict[ color ][ 5 ] ) )

	#		self.__config.add_section( "Orange" )
	#		self.__config.set( "Orange", "H_Low", str( HSVDict[ "Orange" ][ 0 ] ) )
	#		self.__config.set( "Orange", "S_Low", str( HSVDict[ "Orange" ][ 1 ] ) )
	#		self.__config.set( "Orange", "V_Low", str( HSVDict[ "Orange" ][ 2 ] ) )
	#		self.__config.set( "Orange", "H_Upper", str( HSVDict[ "Orange" ][ 3 ] ) )
	#		self.__config.set( "Orange", "S_Upper", str( HSVDict[ "Orange" ][ 4 ] ) )
	#		self.__config.set( "Orange", "V_Upper", str( HSVDict[ "Orange" ][ 5 ] ) )

		## Save config
		with open( self.__pathConfig, 'wb' ) as fileConfig:
			self.__config.write( fileConfig )
		
		print "Save eiei"

	def getParameterFromConfig( self ):
		'''
			getParameterFromConfig function
			This function get parameter of HSV value
			args:
				pathConfig -> Path of config file
				colorSection -> Select your color section 
		'''
		## read config file
		self.__config.read( self.__pathConfig )
		
		## Initial HSV dict
		HSVDict = dict()

		for colorSection in self.__config.sections():

			HSVList = [ int( self.__config.get( colorSection, 'h_low' ) ),
						int( self.__config.get( colorSection, 's_low' ) ),
						int( self.__config.get( colorSection, 'v_low' ) ),
						int( self.__config.get( colorSection, 'h_upper' ) ),
						int( self.__config.get( colorSection, 's_upper' ) ),
						int( self.__config.get( colorSection, 'v_upper' ) ), ]

			HSVDict[ str( colorSection ) ] = HSVList 

		return HSVDict

	def setPathConfig( self, pathConfig):
		'''
			Set path of config
			args :
				pathConfig -> Path to save file config
		'''
		self.__pathConfig = pathConfig
		

		
class Trackbar(object):
	"""
		Replace GUI Later
	"""
	def __init__( self, winname, color ):
		
		self.winname = winname
		self.colorMode = color.lower()
		self.__HSVDict = dict()
		
	def nothing(self,x):
		pass

	def createTrackbarHSV( self ):
		cv2.createTrackbar("h_low",self.winname,0,179,self.nothing)
		cv2.createTrackbar("h_high",self.winname,0,179,self.nothing)
		cv2.createTrackbar("s_low",self.winname,0,255,self.nothing)
		cv2.createTrackbar("s_high",self.winname,0,255,self.nothing)
		cv2.createTrackbar("v_low",self.winname,0,255,self.nothing)
		cv2.createTrackbar("v_high",self.winname,0,255,self.nothing)

	def getvalueHSV( self ):
		       
		h_low = cv2.getTrackbarPos('h_low',self.winname)
		h_high = cv2.getTrackbarPos('h_high',self.winname)
		s_low = cv2.getTrackbarPos('s_low',self.winname)
		s_high = cv2.getTrackbarPos('s_high',self.winname)
		v_low = cv2.getTrackbarPos('v_low',self.winname)
		v_high = cv2.getTrackbarPos('v_high',self.winname)

		lower = np.array([h_low,s_low,v_low],dtype=np.uint8)
		upper = np.array([h_high,s_high,v_high],dtype=np.uint8)
		
		HSVList = [ h_low, s_low, v_low, h_high, s_low, v_low ]
		
		self.__HSVDict[ self.colorMode ] = HSVList
		
		#print self.__HSVDict
 
		return ( lower, upper )
	
	def getHSVDict( self ):
		
		return self.__HSVDict

	

def main():

	ap = argparse.ArgumentParser()
	ap.add_argument( "--config",help = "Directory and Name of config file" )
	ap.add_argument( "--color", help = "indicate color na ja", required = True )
	args = vars(ap.parse_args())

	is_pause = 1

	cv2.namedWindow( "img", cv2.WINDOW_NORMAL)
	trackbar = Trackbar( "img", args[ "color" ] )
	trackbar.createTrackbarHSV()

	color_tool = ColorCalibrator()
	# TODO: Fix video capture duay na ja
	cap = cv2.VideoCapture( 0 )
	# print cap.get(cv2.CAP_PROP_AUTOFOCUS)
	# print cap.get(cv2.CAP_PROP_BRIGHTNESS)
	cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
	# print cap.get(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U)
	# print cap.get(cv2.CAP_PROP_WHITE_BALANCE_RED_V)
	
	while True:   
		if(is_pause): 
			ret,img = cap.read()
		if ret:
			(lower,upper) = trackbar.getvalueHSV()
			(mask,res) = color_tool.colorSpace(img,lower,upper)    
			stack_image = np.hstack((img,res))
			hsv_list = np.hstack((lower,upper))
			# print hsv_list
			cv2.imshow("img",stack_image)
			k=cv2.waitKey(5)
			if(k == ord('q')):
				break
			elif(k==ord('p')):
				print 'pause'
				is_pause = (is_pause + 1)%2
			elif(k==ord('r')):
				cap.set(cv2.CAP_PROP_POS_MSEC,0)
			elif(k==ord('s')):
				# hsv_list = np.hstack((lower,upper))
				HSVDict = trackbar.getHSVDict()
				print 'Save as ..' + args[ "config" ]
				color_tool.setPathConfig( args[ "config" ] )
				color_tool.generateConfig( HSVDict )
		else:
			cap.set(cv2.CAP_PROP_POS_MSEC,0)

	cv2.destroyAllWindows


if __name__ == '__main__':
	main()
