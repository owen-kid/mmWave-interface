import json
import struct
import logging
import sys
import time
import numpy as np
import math
import os
import datetime

# Local File Imports

log = logging.getLogger(__name__)



def parseVitalSignsTLV (tlvData, tlvLength, outputDict):
    vitalsStruct = '2H33f'
    vitalsSize = struct.calcsize(vitalsStruct)
    
    # Initialize struct in case of error
    vitalsOutput = {}
    vitalsOutput ['id'] = 999
    vitalsOutput ['rangeBin'] = 0
    vitalsOutput ['breathDeviation'] = 0
    vitalsOutput ['heartRate'] = 0
    vitalsOutput ['breathRate'] = 0
    vitalsOutput ['heartWaveform'] = []
    vitalsOutput ['breathWaveform'] = []

    # Capture data for active patient
    try:
        vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
    except:
        log.error('ERROR: Vitals TLV Parsing Failed')
        outputDict['vitals'] = vitalsOutput
    
    # Parse this patient's data
    vitalsOutput ['id'] = vitalsData[0]
    vitalsOutput ['rangeBin'] = vitalsData[1]
    vitalsOutput ['breathDeviation'] = vitalsData[2]
    vitalsOutput ['heartRate'] = vitalsData[3]
    vitalsOutput ['breathRate'] = vitalsData [4]
    vitalsOutput ['heartWaveform'] = np.asarray(vitalsData[5:20])
    vitalsOutput ['breathWaveform'] = np.asarray(vitalsData[20:35])

    # Advance tlv data pointer to end of this TLV
    tlvData = tlvData[vitalsSize:]
    outputDict['vitals'] = vitalsOutput

MMWDEMO_OUTPUT_MSG_VITALSIGNS                           = 1040
parserFunctions = {
    MMWDEMO_OUTPUT_MSG_VITALSIGNS:                          parseVitalSignsTLV,
}

def parseStandardFrame(frameData):
    # Constants for parsing frame header
    headerStruct = 'Q8I'
    frameHeaderLen = struct.calcsize(headerStruct)
    tlvHeaderLength = 8

    # Define the function's output structure and initialize error field to no error
    outputDict = {}
    outputDict['error'] = 0

    # A sum to track the frame packet length for verification for transmission integrity 
    totalLenCheck = 0   

    # Read in frame Header
    try:
        magic, version, totalPacketLen, platform, frameNum, timeCPUCycles, numDetectedObj, numTLVs, subFrameNum = struct.unpack(headerStruct, frameData[:frameHeaderLen])
    except:
        log.error('Error: Could not read frame header')
        outputDict['error'] = 1

    # Move frameData ptr to start of 1st TLV   
    frameData = frameData[frameHeaderLen:]
    totalLenCheck += frameHeaderLen

    # Save frame number to output
    outputDict['frameNum'] = frameNum

    # Initialize the point cloud struct since it is modified by multiple TLV's
    # Each point has the following: X, Y, Z, Doppler, SNR, Noise, Track index
    outputDict['pointCloud'] = np.zeros((numDetectedObj, 7), np.float64)
    # Initialize the track indexes to a value which indicates no track
    outputDict['pointCloud'][:, 6] = 255
    # Find and parse all TLV's
    for i in range(numTLVs):
        try:
            tlvType, tlvLength = tlvHeaderDecode(frameData[:tlvHeaderLength])
            frameData = frameData[tlvHeaderLength:]
            totalLenCheck += tlvHeaderLength
        except:
            log.warning('TLV Header Parsing Failure: Ignored frame due to parsing error')
            outputDict['error'] = 2
            return {}

        # print(tlvType)

        if (tlvType in parserFunctions):
            parserFunctions[tlvType](frameData[:tlvLength], tlvLength, outputDict)
        else:
            log.info("Invalid TLV type: %d" % (tlvType))

        # Move to next TLV
        frameData = frameData[tlvLength:]
        totalLenCheck += tlvLength
    
    # Pad totalLenCheck to the next largest multiple of 32
    # since the device does this to the totalPacketLen for transmission uniformity
    totalLenCheck = 32 * math.ceil(totalLenCheck / 32)

    # Verify the total packet length to detect transmission error that will cause subsequent frames to dropped
    if (totalLenCheck != totalPacketLen):
        # log.warning('Frame packet length read is not equal to totalPacketLen in frame header. Subsequent frames may be dropped.')
        outputDict['error'] = 3

    return outputDict

# Decode TLV Header
def tlvHeaderDecode(data):
    tlvType, tlvLength = struct.unpack('2I', data)
    return tlvType, tlvLength
